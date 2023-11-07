
Write-Output "\n Simulate customizations\n"

read -p "Stop Server, and press RETURN to apply customizations, or Ctl-C $1> "
$Ready= Read-Host -Prompt "Stop Server, and press RETURN to apply customizations, or Ctl-C > "

Set-PSDebug -Trace 1

ApiLogicServer add-auth --project_name=. --db_url=auth

cp -r customizations/ .

Write-Output "\n Customizations applied\n\n"
