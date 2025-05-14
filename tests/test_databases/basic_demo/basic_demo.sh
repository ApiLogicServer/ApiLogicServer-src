# sh tests/test_databases/basic_demo/basic_demo.sh


rm -f tests/test_databases/basic_demo/basic_demo.sqlite;      sqlite3 tests/test_databases/basic_demo/basic_demo.sqlite < tests/test_databases/basic_demo/basic_demo.sql
rm -f tests/test_databases/basic_demo/basic_demo_cust.sqlite; sqlite3 tests/test_databases/basic_demo/basic_demo_cust.sqlite < tests/test_databases/basic_demo/basic_demo_cust.sql
rm -f tests/test_databases/basic_demo/basic_demo_int.sqlite;  sqlite3 tests/test_databases/basic_demo/basic_demo_int.sqlite < tests/test_databases/basic_demo/basic_demo_int.sql

cp tests/test_databases/basic_demo/basic_demo.sqlite        api_logic_server_cli/database/basic_demo.sqlite     
cp tests/test_databases/basic_demo/basic_demo_cust.sqlite   api_logic_server_cli/prototypes/basic_demo/customizations/database/db.sqlite
cp tests/test_databases/basic_demo/basic_demo_int.sqlite    api_logic_server_cli/prototypes/basic_demo/iteration/database/db.sqlite
