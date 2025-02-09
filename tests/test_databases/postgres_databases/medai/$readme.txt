I have tried for many hours to spin up a docker image that works - 
1. Created a PostGreSQL database (medai.sql)
2. Created a new project from scratch (password check: p vs postgres)
  $als create --project-name=medai --db-url=\
postgresql://postgres:p@127.0.0.1:5432/medai

3. Add Auth
cd medai
$als add-auth --provider-type=sql --db-url=\
postgresql://postgres:p@127.0.0.1:5432/authdb

4. Verify local non-docker operation with security, admin/p

5. Verify local docker-image, no security  FIXME -- created MySql devops, not pg

6. Explore Thos native docker run


6. Once I built the docker image - I tried to connect (black screen)
http://localhost:5656 (it does work locally F5)

Ontimize comes up but cannot connect to http://apilogicserver:5656

What is missing or why does the log show a ton of errors (every single table) over and over
2025-02-09 11:29:29 FROM patient
2025-02-09 11:29:29  LIMIT :param_1
2025-02-09 11:29:29 no user - ok (eg, system initialization) error: You must call `@jwt_required()` or `verify_jwt_in_request()` before using this method

Is there some config I need to add or a reason this no longer works?