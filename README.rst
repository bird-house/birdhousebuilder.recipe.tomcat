******************************
birdhousebuilder.recipe.tomcat
******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.tomcat`` is a `Buildout`_ recipe to install ``Apache Tomcat`` application server with `Anaconda`_. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://www.continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Apache Tomcat`: https://tomcat.apache.org/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home``.

It installs the ``apache-tomcat`` package from a conda channel and deploys a `Supervisor`_ configuration in ``~/anaconda/etc/supervisor/conf.d/tomcat.conf``. Supervisor can be started with ``~/anaconda/etc/init.d/supervisord start``.

By default Tomcat will be available on http://localhost:8080/thredds.

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



