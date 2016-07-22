#!/bin/bash
# see thredds example for tomcat:
# http://www.unidata.ucar.edu/software/thredds/current/tds/UpgradingTo4.5.html
#
#ulimit -n 2048
#
CATALINA_HOME="${catalina_home}"
export CATALINA_HOME
CATALINA_BASE="${catalina_base}"
export CATALINA_BASE
#
CONTENT_ROOT="-Dtds.content.root.path=${content_directory}"
NORMAL="-d64 -Xmx${Xmx} -Xms${Xms} -server"
MAX_PERM_GEN="-XX:MaxPermSize=${MaxPermSize}"
HEADLESS="-Djava.awt.headless=true"
#             
JAVA_HOME="${java_home}"
JAVA_OPTS="$CONTENT_ROOT $HEADLESS $NORMAL $MAX_PERM_GEN"
export JAVA_OPTS
# start tomcat in foreground
. ${etc_directory}/catalina.sh run
