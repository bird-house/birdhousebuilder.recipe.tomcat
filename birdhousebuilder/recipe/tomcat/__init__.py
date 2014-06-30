# -*- coding: utf-8 -*-
# Copyright (C)2014 DKRZ GmbH

"""Recipe tomcat"""

import os
from mako.template import Template

import zc.buildout
from birdhousebuilder.recipe import conda, supervisor

#templ_config = Template(filename=os.path.join(os.path.dirname(__file__), "nginx.conf"))

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.anaconda_home = b_options.get('anaconda-home', conda.anaconda_home)
        self.options['prefix'] = self.anaconda_home

    def install(self):
        installed = []
        installed += list(self.install_tomcat())
        installed += list(self.install_program())
        return installed

    def install_tomcat(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'apache-tomcat'})

        return script.install()
        
    def install_program(self):
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'program': 'tomcat',
             'command': '%s/bin/catalina.sh run' % (self.anaconda_home),
             })
        return script.install()

    def update(self):
        return self.install()

def uninstall(name, options):
    pass

