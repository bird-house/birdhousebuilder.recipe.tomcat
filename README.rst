******************************
birdhousebuilder.recipe.tomcat
******************************

.. image:: https://travis-ci.org/bird-house/birdhousebuilder.recipe.tomcat.svg?branch=master
   :target: https://travis-ci.org/bird-house/birdhousebuilder.recipe.tomcat
   :alt: Travis Build

Introduction
************

``birdhousebuilder.recipe.tomcat`` is a `Buildout`_ recipe to install ``Apache Tomcat`` application server with `Anaconda`_. This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://www.continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Apache Tomcat`: https://tomcat.apache.org/
.. _`Birdhouse`: http://bird-house.github.io/

Usage
*****

The recipe requires that Anaconda is already installed. You can use the buildout option ``anaconda-home`` to set the prefix for the anaconda installation. Otherwise the environment variable ``CONDA_PREFIX`` (variable is set when activating a conda environment) is used as conda prefix. 

It installs the ``apache-tomcat`` package from a conda channel in a conda enviroment defined by ``CONDA_PREFIX``. The intallation folder is given by the ``prefix`` buildout option. It deploys a `Supervisor`_ configuration in ``${prefix}/etc/supervisor/conf.d/tomcat.conf``. Supervisor can be started with ``${prefix}/etc/init.d/supervisord start``.

By default Tomcat will be available on http://localhost:8080/.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

This recipe supports the following options:

``anaconda-home``
   Buildout option pointing to the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

``http_port``
   HTTP Port for Tomcat service. Default: 8080

``Xms``
   Initial Java heap size: Default: 128m

``Xmx``
   Maximum Java heap size: Default: 1024m

``MaxPermSize``
   Maximum Java permanent heap size: Default: 128m

``ncwms_password``
   Enable ncWMS2 admin web interface by setting a password: Default: disabled


Example usage
=============

The following example ``buildout.cfg`` installs ``tomcat`` as a Supervisor service::

  [buildout]
  parts = tomcat

  [tomcat]
  recipe = birdhousebuilder.recipe.tomcat
  http_port = 8080
  Xms = 256m
  Xmx = 2048m
  MaxPermSize = 128m



