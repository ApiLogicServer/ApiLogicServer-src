
# sh tests/test_databases/basic_demo/basic_demo.sh

# may require: als rebuild-from-database --project_name=./ --db_url=sqlite:///database/db.sqlite
# also: export APILOGICSERVER_HOME=/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/lib/ApiLogicServer

rm -f tests/test_databases/basic_demo/basic_demo.sqlite;      sqlite3 tests/test_databases/basic_demo/basic_demo.sqlite < tests/test_databases/basic_demo/basic_demo.sql
rm -f tests/test_databases/basic_demo/basic_demo_cust.sqlite; sqlite3 tests/test_databases/basic_demo/basic_demo_cust.sqlite < tests/test_databases/basic_demo/basic_demo_cust.sql
rm -f tests/test_databases/basic_demo/basic_demo_int.sqlite;  sqlite3 tests/test_databases/basic_demo/basic_demo_int.sqlite < tests/test_databases/basic_demo/basic_demo_int.sql

cp tests/test_databases/basic_demo/basic_demo.sqlite        api_logic_server_cli/database/basic_demo.sqlite     
cp tests/test_databases/basic_demo/basic_demo_cust.sqlite   api_logic_server_cli/prototypes/basic_demo/customizations/database/db.sqlite
cp tests/test_databases/basic_demo/basic_demo_int.sqlite    api_logic_server_cli/prototypes/basic_demo/iteration/database/db.sqlite
