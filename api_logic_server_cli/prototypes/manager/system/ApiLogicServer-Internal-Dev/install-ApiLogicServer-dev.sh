#!/bin/bash

contains()
  # echo contains check $1 in $2
  case "$1" in
    (*"$2"*) true;;
    (*) false;;
  esac

sra="venv/lib/python3.13/site-packages/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build"
if [ -d $src ] 
then
    echo "\n(SRA location verified)\n" 
else
    echo "\n(SRA location not found)\n" 
    echo "Please fix variable above"
    exit 1
fi

sra_curl="0.2.9/$sra"

ostype=$(uname -a)
if contains "Ubuntu" $ostype; then
  ostype="ubuntu"
fi
# if contains "ubuntu" $ostype; then
#   echo $ostype contains ubuntu
# fi

# normally true, use false for skipping long clone during testing 
clonedocs=true

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "Installs ApiLogicServer Dev Src and safrs-react-admin on $ostype (version 7.0.15)\n"
    echo "  .. vscode option creates venv, and starts vscode on workspace"
    echo "  .. See: https://apilogicserver.github.io/Docs/Architecture-Internals"
    echo "  .. Installer Version 14.05.04 - copies sra from mgr venv -> dev src"
    echo " "
    echo "   > cd manager # you are probably already there"
    echo "   > sh system/install-ApiLogicServer-dev/install-ApiLogicServer-dev.sh [ vscode | charm | x ]"
    echo " "
    exit 0
  else
    ls
    echo " "
    read -p "Verify ApiLogicServer-dev does not exist, and [Enter] install *dev* version of ApiLogicServer for $1> "
    if [ -d "ApiLogicServer-dev" ] 
    then
        echo "\nReally, ApiLogicServer-dev must not exist\n" 
        exit 1
    fi
    set -x
    mkdir ApiLogicServer-dev
    cd ApiLogicServer-dev
    mkdir servers    # good place to create test ApiLogicProjects
    mkdir build_and_test
    mkdir org_git  # git clones from org ApiLogicServer here

    # persistent home for any docker/podman bind-mount volumes (Kafka data, etc.) that
    # must survive Manager workspace rebuilds - nothing under build_and_test/ is safe for
    # this, since a clean Manager rebuild (or a fresh BLT-created workspace) wipes it.
    mkdir podman
    cat > podman/readme.md << 'EOF'
# podman/

Persistent host directory for docker/podman bind-mount volumes that need to
survive a Manager workspace rebuild (e.g. `genai-logic create-manager --clean`,
or a fresh `build_and_test`/`clean` BLT output).

Sibling of `org_git/`, `build_and_test/`, `servers/` - nothing here is touched
by BLT or Manager rebuilds.

Not tied to any one sample or technology - only use it when a sample's own
compose file default (typically project-relative, e.g. `./.volumes/...`) would
otherwise be wiped by a workspace rebuild. Point that compose file's
`volumes:` entry here instead, e.g.:

  volumes:
    - ${HOME}/dev/genai-logic/ApiLogicServer-dev/podman/kafka/data:/integration/kafka/volume

Organize by service as needed:

  podman/kafka/data
  podman/<other-service>/...

This only matters for this internal dev checkout - general end-user Manager
workspaces aren't repeatedly rebuilt, so their sample compose files keep the
simpler, self-contained project-relative default.
EOF

    cd org_git

    if [ "$clonedocs" = true ]
      then
        git clone https://github.com/ApiLogicServer/Docs
        cd Docs
        python3 -m venv venv       # may require python -m venv venv
        if contains "ubuntu" $ostype; then
          echo $ostype contains ubuntu
          . venv/bin/activate
        else
          echo $ostype does not contain ubuntu
          source venv/bin/activate   # windows venv\Scripts\activate
        fi
        pip install -r requirements.txt
        cd ..
    fi
    
    git clone https://github.com/ApiLogicServer/ApiLogicServer-src.git
    git clone https://github.com/valhuber/LogicBank
    
    cd ApiLogicServer-src
    echo "\ncopying $sra --> ApiLogicServer"
    cp -r ../../../$sra api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
    
    #
    #
    # read -p "Installed - ready to launch IDE..."
    if [ "$1" = "vscode" ]
      then
        python3 -m venv venv       # may require python -m venv venv
        # pwd
        # ls
        . venv/bin/activate
        # read -p "venv created; do optional pre-installs now $1> "
        python3 -m pip install -r requirements.txt    # you may need to use pip3, or restart your terminal session
        code .vscode/ApiLogicServerDev.code-workspace
        set +x
        echo ""
        echo "Workspace opened; use pre-created Launch Configurations:"
        echo "  * Run 1 - Create ApiLogicProject, then..."
        echo "  * Run 2 - RUN ApiLogicProject"
    elif [ "$1" = "charm" ]
    then
        charm .
        set +x
        echo "  * Python Interpreter > Add New Environment (default, to create venv)"
        echo "     IMPORTANT - NOT DOCKER"
        echo "  * then open requirements.txt - PyCharm should **Install Requirements**"
        echo "     If this fails, use a terminal to run pip install -r requirements.txt"
    else
      set +x
    fi
    echo ""
    echo "IDEs are preconfigured with run/launch commands to create and run the sample"
    echo ""
    echo "ApiLogicServer/react-admin contains shell burn-and-rebuild-react-admin"
    echo ""
    echo "If a sample uses docker/podman (e.g. Kafka), see podman/readme.md - it's a"
    echo "rebuild-safe place for volumes that must survive a Manager/BLT rebuild"
    echo ""
    exit 0
fi
