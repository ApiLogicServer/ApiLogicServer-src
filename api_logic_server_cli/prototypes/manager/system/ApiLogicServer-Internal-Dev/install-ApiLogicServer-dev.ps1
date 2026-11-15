
param(
    [Parameter()]
    [String]$IDE
)

# $SRA="venv/lib/python3.12/site-packages/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build"

$venvPath = "venv\Lib\site-packages"
$SRA = Join-Path $venvPath "api_logic_server_cli\create_from_model\safrs-react-admin-npm-build"

if (Test-Path -Path $SRA) {
    Write-Output " "
    Write-Output "(SRA location verified)"
    Write-Output " "
} else {
    Write-Output " "
    Write-Output "Safrs React Admin (SRA) not found - please fix line above for $SRA"
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
    Write-Output "   > pip install ApiLogicServer"
    Write-Output " "
    Write-Output "   > .\system\install-ApiLogicServer-dev\install-ApiLogicServer-dev.ps1 vscode"
    Write-Output " "
    Exit
}
ls
Write-Output " "
$Ready= Read-Host -Prompt "Verify $((Get-Location).Path)\ApiLogicServer-dev does not exist, and [Enter] install *dev* version of ApiLogicServer for $IDE> "
Set-PSDebug -Trace 0

if (Test-Path -Path "ApiLogicServer-dev") {
    Write-Output " "
    Write-Output "Really, ApiLogicServer-dev must not exist"
    Write-Output " "
    Exit 1
}

$mgrRoot = (Get-Location).Path   # Manager root: holds system/ApiLogicServer-Internal-Dev/container-volumes-template
mkdir ApiLogicServer-dev
cd ApiLogicServer-dev
mkdir servers    # good place to create ApiLogicProjects
mkdir build_and_test
mkdir org_git  # git clones from org ApiLogicServer here

# persistent home for any docker/podman bind-mount volumes (Kafka data, etc.) that
# must survive Manager workspace rebuilds - nothing under build_and_test/ is safe for
# this, since a clean Manager rebuild (or a fresh BLT-created workspace) wipes it.
# copy the template (gold: system/ApiLogicServer-Internal-Dev/container-volumes-template)
mkdir container-volumes
$volumesTemplate = Join-Path $mgrRoot "system/ApiLogicServer-Internal-Dev/container-volumes-template"
if (Test-Path -Path $volumesTemplate) {
    Copy-Item -Path (Join-Path $volumesTemplate "*") -Destination container-volumes -Recurse -Force
} else {
    Write-Output "(container-volumes-template not found under $mgrRoot - container-volumes/ left empty)"
}

# provenance: readme for the dev env, dated now (gold: system/ApiLogicServer-Internal-Dev/readme-ApiLogicServer-dev.md)
$readmeTemplate = Join-Path $mgrRoot "system/ApiLogicServer-Internal-Dev/readme-ApiLogicServer-dev.md"
if (Test-Path -Path $readmeTemplate) {
    (Get-Content -Raw $readmeTemplate).Replace("{{CREATED_DATE}}", (Get-Date -Format "MM/dd/yyyy")).Replace("{{INSTALL_SCRIPT}}", (Join-Path $mgrRoot "system/ApiLogicServer-Internal-Dev/install-ApiLogicServer-dev.ps1")) | Set-Content -NoNewline readme-dev.md
}

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
git clone https://github.com/valhuber/LogicBank

# provenance: record what this dev env was built from (fills {{CLONE_SHAS}} in ..\readme-dev.md)
if (Test-Path -Path ..\readme-dev.md) {
    $dist = Get-ChildItem (Join-Path $mgrRoot "venv\Lib\site-packages") -Directory -Filter "apilogicserver-*.dist-info" -ErrorAction SilentlyContinue | Select-Object -First 1
    $mgrVer = if ($dist) { $dist.Name -replace '^apilogicserver-','' -replace '\.dist-info$','' } else { "unknown" }
    $lines = @("- Manager ApiLogicServer: $mgrVer")
    foreach ($r in "Docs","ApiLogicServer-src","LogicBank") {
        if (Test-Path -Path $r) { $lines += "- ${r}: $(git -C $r rev-parse --short HEAD) ($(git -C $r branch --show-current))" }
    }
    (Get-Content -Raw ..\readme-dev.md).Replace("{{CLONE_SHAS}}", ($lines -join "`n")) | Set-Content -NoNewline ..\readme-dev.md
}

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
Write-Output "If a sample uses docker/podman (Kafka, Keycloak), see container-volumes/readme.md - it's a"
Write-Output "rebuild-safe place for volumes that must survive a Manager/BLT rebuild"
Write-Output ""
exit 0
