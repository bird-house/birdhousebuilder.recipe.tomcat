#!/bin/bash
# see thredds example for tomcat:
# http://www.unidata.ucar.edu/software/thredds/current/tds/UpgradingTo4.5.html
#
ulimit -n 2048
#
CATALINA_HOME="${prefix}/opt/apache-tomcat"
export CATALINA_HOME
CATALINA_BASE="${prefix}/opt/apache-tomcat"
export CATALINA_BASE
#
CONTENT_ROOT="-Dtds.content.root.path=${content_root}"
NORMAL="-d64 -Xmx2048m -Xms512m -server"
MAX_PERM_GEN="-XX:MaxPermSize=256m"
HEADLESS="-Djava.awt.headless=true"
#             
JAVA_OPTS="$CONTENT_ROOT $HEADLESS $NORMAL $MAX_PERM_GEN"
export JAVA_OPTS
# start tomcat in foreground
. ${prefix}/bin/catalina.sh run
