# Usage:
#   cd <your-project>
#   .\venv_setup\venv.ps1        # show usage
#   .\venv_setup\venv.ps1 go     # create local venv and pip install
#
# Note: symlink option is not available on Windows (requires Developer Mode + git config).
# Use 'go' to create a local venv, or run via the Manager: als run --project-name=<project>

if ($args.Count -eq 0) {
    Write-Output ""
    Write-Output "Usage:  .\venv_setup\venv.ps1 [go]"
    Write-Output ""
    Write-Output "  go   Creates a local venv/ and runs pip install -r requirements.txt."
    Write-Output ""
    Write-Output "  Note: To avoid venv setup entirely, run from the Manager terminal:"
    Write-Output "        als run --project-name=<your-project>"
    Write-Output ""
    exit 0
}

python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
