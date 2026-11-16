#!/bin/bash

# To build container for your ApiLogicProject:
#    create / customize your project as you normally would
#    edit this file: change your_account/your_repository as appropriate
#    be sure to add security (already done for demo)

#    in terminal
#    $ cd <your project>
#    $ sh devops/docker-image/build_image.sh .

CONTAINER_CLI=${CONTAINER_CLI:-docker}   # docker or podman:  export CONTAINER_CLI=podman
projectname="studentscourses"  # lower case, only
repositoryname="apilogicserver"
version="1.0.0"

debug() {
  debug="disabled"
  # echo "$1"
}

debug "\n"
debug "build_image here 1.0"
if [ $# -eq 0 ]; then
  echo "\nBuilds docker image for API Logic Project\n"
  echo "  cd <project home directory>"
  echo "  sh devops/docker/build_image.sh [ . | <docker-id> ]"
  echo "    . means use defaults:"
  echo "        ${repositoryname}/${projectname}:${version}"
  echo "    <docker-id> means use explicit args: <repository-name> <project-name> <version> eg,"
  echo "        sh build_image.sh myrepository myproject 1.0.1"
  echo " "
  exit 0
fi

echo " "
if [ "$1" = "." ]; then
  debug "..using defaults"
else
  debug "using arg overrides"
  repositoryname="$1"
  projectname="$2"
  version="$3"
fi

echo "Building ${repositoryname}/${projectname}\n"

$CONTAINER_CLI build -f devops/docker-image/build_image.dockerfile -t ${repositoryname}/${projectname} --rm .

status=$?
if [ $status -eq 0 ]; then
  echo "\nImage built successfully.. test:\n"
  echo "  sh devops/docker-image/run_image.sh"
  echo " "
  echo "\nNext steps:"
  echo "  $CONTAINER_CLI tag ${repositoryname}/${projectname} ${repositoryname}/${projectname}:${version}"
  echo "  $CONTAINER_CLI push ${repositoryname}/${projectname}:${version}  # requires registry login"
  echo " "
  echo "  $CONTAINER_CLI tag ${repositoryname}/${projectname} ${repositoryname}/${projectname}:latest"
  echo "  $CONTAINER_CLI push ${repositoryname}/${projectname}:latest"
  echo " "
  echo "Image ready to deploy; e.g. on Azure: https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy"
else
  echo "$CONTAINER_CLI build unsuccessful\n"
  exit 1
fi
echo " "
exit 0
