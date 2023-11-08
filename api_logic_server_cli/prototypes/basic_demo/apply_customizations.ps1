Write-Output " "
Write-Output "Simulate customizations"
Write-Output " "

$Ready= Read-Host -Prompt "Stop Server, and press RETURN to apply customizations, or Ctl-C > "

Set-PSDebug -Trace 1

ApiLogicServer add-auth --project_name=. --db_url=auth

cp -r -Force customizations/* .

Set-PSDebug -Trace 0
Write-Output " "
Write-Output "Customizations applied"
Write-Output " "
Write-Output " "
