echo "\nIteration\n"

read -p "Stop Server, and press RETURN to apply iteration, or Ctl-C $1> "

set -x

# get database with Product.CarbonNeutral, rebuilt ui/admin/admin-merge.yaml
cp -r iteration/ .

cd ..  #  project parent directory
ApiLogicServer rebuild-from-database --project_name=basic_demo --db_url=sqlite:///basic_demo/database/db.sqlite
cd basic_demo

set +x
echo "\n Iteration applied"
