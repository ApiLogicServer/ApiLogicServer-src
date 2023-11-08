Write-Output " "
Write-Output "Iteration"
Write-Output " "

$Ready = Read-Host -Prompt "Stop Server, and press RETURN to apply iteration, or Ctl-C > "

Set-PSDebug   -Trace 1

# get database with Product.CarbonNeutral, rebuilt ui/admin/admin.yaml
cp -r -Force iteration/* .

cd ..  #  rebuild project from new database, preserving customizations
ApiLogicServer rebuild-from-database --project_name=basic_demo --db_url=sqlite:///basic_demo\database\db.sqlite
cd basic_demo

Set-PSDebug   -Trace 0
Write-Output " "
Write-Output "\n Iteration applied"
Write-Output " "
Write-Output " "
