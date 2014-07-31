******************************
birdhousebuilder.recipe.tomcat
******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.tomcat`` is a `Buildout`_ recipe to install ``apache-tomcat`` application server with `Anaconda`_. It installs the ``apache-tomcat`` package from a conda channel and deploys a `Supervisor`_ configuration in ``~/anaconda/etc/supervisor/conf.d/tomcat.conf``. Supervisor can be started with ``~/anaconda/etc/init.d/supervisord start``.

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://www.continuum.io/
.. _`Supervisor`: http://supervisord.org/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home``.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

This recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

Example usage
=============

The following example ``buildout.cfg`` installs ``tomcat`` as a Supervisor service::

  [buildout]
  parts = tomcat

  anaconda-home = /home/myself/anaconda

  [tomcat]
  recipe = birdhousebuilder.recipe.tomcat



