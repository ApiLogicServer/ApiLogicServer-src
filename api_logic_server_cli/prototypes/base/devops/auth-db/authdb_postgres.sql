DROP DATABASE IF EXISTS authdb;
CREATE DATABASE authdb;
\c authdb;

-- in docker container/terminal
-- psql--username=postgres
-- \l
-- \dt


--
-- Table structure for table Role
--

DROP TABLE IF EXISTS "Role";
CREATE TABLE "Role" (
  name varchar(64) NOT NULL,
  PRIMARY KEY (name)
);

INSERT INTO "Role" VALUES ('sa');

--
-- Table structure for table User
--

DROP TABLE IF EXISTS "User";
CREATE TABLE "User" (
  name varchar(128) DEFAULT NULL,
  notes text,
  id varchar(64) NOT NULL,
  username varchar(128) DEFAULT NULL,
  email varchar(128) DEFAULT NULL,
  password_hash varchar(200) DEFAULT NULL,
  PRIMARY KEY (id)
);

--
-- Dumping data for table User
--

INSERT INTO "User" VALUES ('Administrator',NULL,'admin','Admin User','admin@corp.com','p');


--
-- Table structure for table UserRole
--

DROP TABLE IF EXISTS "UserRole";
CREATE TABLE "UserRole" (
  user_id varchar(64) NOT NULL,
  notes text,
  role_name varchar(32) NOT NULL,
  PRIMARY KEY (user_id,role_name),
  CONSTRAINT in_client FOREIGN KEY (user_id) REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT in_role FOREIGN KEY (role_name) REFERENCES "Role" (name) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO "UserRole" VALUES ('admin',NULL,'sa');
