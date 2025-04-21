
param(
    [Parameter()]
    [String]$IDE
)

SRA="venv/lib/python3.12/site-packages/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build"

if (Test-Path -Path $SRA) {
    Write-Output " "
    Write-Output "(SRA location verified)"
    Write-Output " "
} else {
    Write-Output " "
    Write-Output "Safrs React Admin (SRA) not found - please fix line above"
    Write-Output " "
    Exit 1
}

$clonedocs = $true
Write-Output "IDE specified as: $IDE"

if($IDE -eq "") {
    Write-Output " "
    Write-Output "Installs dev version of ApiLogicServer and safrs-react-admin (version 7.0.15)"
    Write-Output "   .. vscode option creates venv, and starts vscode on workspace "
    Write-Output "   .. See: https://apilogicserver.github.io/Docs/Architecture-Internals"
    Write-Output " "
    Write-Output " IMPORTANT - create a folder, then install:"
    Write-Output "   > mkdir ApiLogicServer"
    Write-Output " "
    Write-Output "   > .\Install-ApiLogicServer-Dev [ vscode | charm | x ]"
    Write-Output " "
    Exit
}
ls
Write-Output " "
$Ready= Read-Host -Prompt "Verify ApiLogicServer-dev does not exist, and [Enter] install *dev* version of ApiLogicServer for $1> "
Set-PSDebug -Trace 0

if (Test-Path -Path "ApiLogicServer-dev") {
    Write-Output " "
    Write-Output "Really, ApiLogicServer-dev must not exist"
    Write-Output " "
    Exit 1
}

mkdir ApiLogicServer-dev
cd ApiLogicServer-dev
mkdir servers    # good place to create ApiLogicProjects
mkdir build_and_test
mkdir org_git  # git clones from org ApiLogicServer here
cd org_git

if ($clonedocs -eq $true) {
    Write-Output "\n Docs setup (slow) "
    git clone https://github.com/ApiLogicServer/Docs.git
    cd Docs
    python -m venv venv
    venv\Scripts\activate
    pip -m install -r requirements.txt
    cd ..
} else {
    Write-Output "\n Docs setup DECLINED "
}


git clone https://github.com/ApiLogicServer/ApiLogicServer-src.git
cd ApiLogicServer-src
ls
# $Ready= Read-Host -Prompt "Should be at -src - ready to copy sra build $1> "
cp -r ../../../$SRA api_logic_server_cli/create_from_model/safrs-react-admin-npm-build


if ($IDE -eq "vscode") {
    python -m venv venv
    # pwd
    # ls
    venv\Scripts\activate
    python -m pip install -r requirements.txt
    code .vscode/ApiLogicServerDev.code-workspace
    Set-PSDebug -Trace 0
    Write-Output ""
    Write-Output "Workspace opened; use pre-created Launch Configurations:"
    Write-Output "  * Run 1 - Create ApiLogicProject, then..."
    Write-Output "  * Run 2 - RUN ApiLogicProject"
} elseif ($IDE -eq "pycharm") {
    charm .
    Set-PSDebug -Trace 0
    Write-Output "  * Python Interpreter > Add New Environment (default, to create venv)"
    Write-Output "     IMPORTANT - NOT DOCKER"
    Write-Output "  * then open requirements.txt - PyCharm should **Install Requirements**"
    Write-Output "     If this fails, use a terminal to run pip install -r requirements.txt"
} else {
    Write-Output "No IDE started"
}
Write-Output ""
Write-Output "IDEs are preconfigured with run/launch commands to create and run the sample"
Write-Output ""
exit 0
