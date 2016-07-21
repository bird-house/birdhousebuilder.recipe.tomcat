# -*- coding: utf-8 -*-

"""Recipe tomcat"""

import os
import stat
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

catalina_sh = Template(filename=os.path.join(os.path.dirname(__file__), "catalina-wrapper.sh"))
users_xml = Template(filename=os.path.join(os.path.dirname(__file__), "tomcat-users.xml"))
server_xml = Template(filename=os.path.join(os.path.dirname(__file__), "server.xml"))

def unzip(prefix, warfile):
    warname = os.path.basename(warfile)
    dirname = warname[0:-4]
    appspath = os.path.join(prefix, 'webapps')
    dirpath = os.path.join(appspath, dirname)
    if not os.path.isdir(dirpath):
        try:
            check_call(['unzip', '-q', os.path.join(appspath, warname), '-d', dirpath])
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
        self.options['content-directory'] = self.options['content_directory'] =os.path.join(self.options['lib-directory'], 'content')
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

        # tomcat folders
        self.options['catalina_home'] = os.path.join(self.options['conda-prefix'], 'opt', 'apache-tomcat')
        self.options['catalina_base'] = self.options['lib-directory']

        # config options
        self.options['http_port'] = self.options.get('http_port', '8080')
        self.options['https_port'] = self.options.get('https_port', '8443')
        self.options['Xmx'] = self.options.get('Xmx', '1024m')
        self.options['Xms'] = self.options.get('Xms', '128m')
        self.options['MaxPermSize'] = self.options.get('MaxPermSize', '128m')
        self.options['ncwms_password'] = self.options.get('ncwms_password', '')

        # make folders
        make_dirs(self.options['content-directory'], self.options['user'], mode=0o755)

    def install(self, update=False):
        installed = []
        if not update:
            installed += list(self.deployment.install())
        installed += list(self.conda.install(update))
        installed += list(self.install_catalina_wrapper())
        installed += list(self.setup_users_config())
        installed += list(self.setup_server_config())
        installed += list(self.install_supervisor(update))
        return installed

    def install_catalina_wrapper(self):
        text = catalina_sh.render(**self.options)
        config = Configuration(self.buildout, 'catalina-wrapper.sh', {
            'deployment': self.deployment_name,
            'text': text})
        return [config.install()]

    def setup_users_config(self):
        text = users_xml.render(**self.options)
        config = Configuration(self.buildout, 'tomcat-users.xml', {
            'deployment': self.deployment_name,
            'text': text})
        return [config.install()]

    def setup_server_config(self):
        text = server_xml.render(**self.options)
        config = Configuration(self.buildout, 'server.xml', {
            'deployment': self.deployment_name,
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
             'command': '{0}/catalina-wrapper.sh'.format(self.options['etc-directory']),
             })
        return script.install(update)

    def update(self):
        return self.install(update=True)

def uninstall(name, options):
    pass

