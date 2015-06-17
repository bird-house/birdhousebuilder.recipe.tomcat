# -*- coding: utf-8 -*-

"""Recipe tomcat"""

import os
import stat
from mako.template import Template

import zc.buildout
from birdhousebuilder.recipe import conda, supervisor

catalina_sh = Template(filename=os.path.join(os.path.dirname(__file__), "catalina-wrapper.sh"))
users_xml = Template(filename=os.path.join(os.path.dirname(__file__), "tomcat-users.xml"))
server_xml = Template(filename=os.path.join(os.path.dirname(__file__), "server.xml"))

def content_root(prefix):
    root_path = os.path.join(prefix, 'var', 'lib', 'tomcat', 'content')
    conda.makedirs(os.path.dirname(root_path))
    return root_path
                
class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs apache-tomcat as conda package and setups tomcat configuration"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        self.options['http_port'] = self.options.get('http_port', '8080')
        self.options['https_port'] = self.options.get('https_port', '8080')
        self.options['content_root'] = content_root(self.prefix)

    def install(self):
        installed = []
        installed += list(self.install_tomcat())
        installed += list(self.setup_catalina_wrapper())
        installed += list(self.setup_users_config())
        installed += list(self.setup_server_config())
        installed += list(self.setup_service())
        return tuple()

    def install_tomcat(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'apache-tomcat'})

        return script.install()

    def setup_catalina_wrapper(self):
        result = catalina_sh.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'bin', 'catalina-wrapper.sh')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        # add exec permission
        st = os.stat(output)
        os.chmod(output, st.st_mode | stat.S_IEXEC)
        return [output]

    def setup_users_config(self):
        result = users_xml.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'tomcat-users.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def setup_server_config(self):
        result = server_xml.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'server.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]
    
    def setup_service(self):
        content_path = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'content')
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'program': 'tomcat',
             'command': '{0}/opt/apache-tomcat/bin/catalina-wrapper.sh'.format(self.prefix),
             })
        return script.install()

    def update(self):
        #self.install_tomcat()
        self.setup_catalina_wrapper()
        self.setup_users_config()
        self.setup_server_config()
        self.setup_service()
        return tuple()

def uninstall(name, options):
    pass

