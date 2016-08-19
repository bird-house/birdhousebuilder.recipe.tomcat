# -*- coding: utf-8 -*-

"""Recipe tomcat"""

import os
import pwd
import logging
from mako.template import Template
from subprocess import check_call, CalledProcessError

import zc.buildout
import zc.recipe.deployment
from zc.recipe.deployment import Configuration
from zc.recipe.deployment import make_dir
import birdhousebuilder.recipe.conda
from birdhousebuilder.recipe import supervisor

setenv_sh = Template(filename=os.path.join(os.path.dirname(__file__), "setenv.sh"))
tomcat_users_xml = Template(filename=os.path.join(os.path.dirname(__file__), "tomcat-users.xml"))
server_xml = Template(filename=os.path.join(os.path.dirname(__file__), "server.xml"))
logging_props = Template(filename=os.path.join(os.path.dirname(__file__), "logging.properties"))

def unzip(prefix, warfile):
    warname = os.path.basename(warfile)
    dirname = warname[0:-4]
    dirpath = os.path.join(prefix, 'webapps', dirname)
    if not os.path.isdir(dirpath):
        try:
            check_call(['unzip', '-q', warfile, '-d', dirpath])
        except CalledProcessError:
            raise
        except:
            raise

def make_dirs(name, user, mode=0o755):
    etc_uid, etc_gid = pwd.getpwnam(user)[2:4]
    created = []
    make_dir(name, etc_uid, etc_gid, mode, created)
        
class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs apache-tomcat as conda package and setups tomcat configuration"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']

        self.options['name'] = self.options.get('name', self.name)
        self.name = self.options['name']

        self.logger = logging.getLogger(name)

        # deployment layout
        def add_section(section_name, options):
            if section_name in buildout._raw:
                raise KeyError("already in buildout", section_name)
            buildout._raw[section_name] = options
            buildout[section_name] # cause it to be added to the working parts

        self.deployment_name = self.name + "-tomcat-deployment"
        self.deployment = zc.recipe.deployment.Install(buildout, self.deployment_name, {
            'name': "tomcat",
            'prefix': self.options['prefix'],
            'user': self.options['user'],
            'etc-user': self.options['etc-user']})
        add_section(self.deployment_name, self.deployment.options)
        
        self.options['etc-prefix'] = self.options['etc_prefix'] = self.deployment.options['etc-prefix']
        self.options['var-prefix'] = self.options['var_prefix'] = self.deployment.options['var-prefix']
        self.options['etc-directory'] = self.options['etc_directory'] = self.deployment.options['etc-directory']
        self.options['lib-directory'] = self.options['lib_directory'] = self.deployment.options['lib-directory']
        self.options['log-directory'] = self.options['log_directory'] = self.deployment.options['log-directory']
        self.options['run-directory'] = self.options['run_directory'] = self.deployment.options['run-directory']
        self.options['cache-directory'] = self.options['cache_directory'] = self.deployment.options['cache-directory']
        self.prefix = self.options['prefix']

        # conda packages
        self.options['env'] = self.options.get('env', '')
        self.options['pkgs'] = self.options.get('pkgs', 'apache-tomcat')
        self.options['channels'] = self.options.get('channels', 'defaults birdhouse')
        self.conda = birdhousebuilder.recipe.conda.Recipe(self.buildout, self.name, {
            'env': self.options['env'],
            'pkgs': self.options['pkgs'],
            'channels': self.options['channels'] })
        self.options['conda-prefix'] = self.options['conda_prefix'] = self.conda.options['prefix']

        # tomcat options
        self.options['catalina_home'] = self.options['catalina-home'] = self.options.get(
            'catalina-home',
            os.path.join(self.options['conda-prefix'], 'opt', 'apache-tomcat'))
        self.options['catalina_base'] = self.options['catalina-base'] = self.options['lib-directory']

        # java options
        self.options['java_home'] = self.options['java-home'] = self.options.get('java-home', self.options['conda-prefix'])
        self.options['Xmx'] = self.options.get('Xmx', '1024m')
        self.options['Xms'] = self.options.get('Xms', '128m')
        self.options['MaxPermSize'] = self.options.get('MaxPermSize', '128m')

        # config options
        self.options['http_port'] = self.options.get('http_port', '8080')
        self.options['https_port'] = self.options.get('https_port', '8443')
        self.options['ncwms_password'] = self.options.get('ncwms_password', '')

        # make folders
        make_dirs(os.path.join(self.options['catalina-base'], 'bin' ), self.options['etc-user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], 'conf' ), self.options['etc-user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], 'logs' ), self.options['user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], 'temp' ), self.options['user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], 'webapps' ), self.options['user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], 'work' ), self.options['user'], mode=0o755)

        # prepare java prefs folders
        # http://stackoverflow.com/questions/15004954/java-setting-preferences-backingstore-directory
        make_dirs(os.path.join(self.options['catalina-base'], "java_prefs", ".java"), self.options['user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], "java_prefs", ".java", ".systemPrefs"), self.options['user'], mode=0o755)
        make_dirs(os.path.join(self.options['catalina-base'], "java_prefs", ".java", ".userPrefs"), self.options['user'], mode=0o755)

    def install(self, update=False):
        installed = []
        if not update:
            installed += list(self.deployment.install())
        installed += list(self.conda.install(update))
        installed += list(self.install_catalina_sh())
        installed += list(self.install_setenv_sh())
        installed += list(self.install_web_xml())
        installed += list(self.install_tomcat_users_xml())
        installed += list(self.install_server_xml())
        installed += list(self.install_logging_props())
        installed += list(self.install_supervisor(update))
        return installed

    def install_catalina_sh(self):
        config = Configuration(self.buildout, 'catalina.sh', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'bin' ),
            'mode': '0o755',
            'file': os.path.join(self.options['catalina-home'], 'bin', 'catalina.sh')})
        installed = [config.install()]
        # fix permission
        os.chmod(os.path.join(self.options['catalina-base'], 'bin', 'catalina.sh'), 0o755)
        return installed

    def install_setenv_sh(self):
        text = setenv_sh.render(**self.options)
        config = Configuration(self.buildout, 'setenv.sh', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'bin' ),
            'text': text})
        return [config.install()]

    def install_web_xml(self):
        config = Configuration(self.buildout, 'web.xml', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'conf' ),
            'file': os.path.join(self.options['catalina-home'], 'conf', 'web.xml')})
        return [config.install()]

    def install_tomcat_users_xml(self):
        text = tomcat_users_xml.render(**self.options)
        config = Configuration(self.buildout, 'tomcat-users.xml', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'conf' ),
            'text': text})
        return [config.install()]

    def install_server_xml(self):
        text = server_xml.render(**self.options)
        config = Configuration(self.buildout, 'server.xml', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'conf' ),
            'text': text})
        return [config.install()]

    def install_logging_props(self):
        text = logging_props.render(**self.options)
        config = Configuration(self.buildout, 'logging.properties', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['catalina-base'], 'conf' ),
            'text': text})
        return [config.install()]
    
    def install_supervisor(self, update=False):
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'prefix': self.options['prefix'],
             'user': self.options.get('user'),
             'etc-user': self.options['etc-user'],
             'program': 'tomcat',
             'command':  '{0} run'.format(os.path.join(self.options['catalina-base'], 'bin', 'catalina.sh')),
             })
        return script.install(update)

    def update(self):
        return self.install(update=True)

def uninstall(name, options):
    pass

