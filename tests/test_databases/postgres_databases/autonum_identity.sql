--
-- Revised for als from  https://github.com/pthom/northwind_psql/blob/master/northwind.sql
-- See https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-identity-column/
--
DROP DATABASE IF EXISTS autonum;
CREATE DATABASE autonum;
\c autonum;

-- in docker container/terminal
-- psql--username=postgres
-- \l
-- \dt

-- or docker exec -it postgresql-container bash

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET default_tablespace = '';

SET default_with_oids = false;

DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id INTEGER GENERATED ALWAYS AS IDENTITY, 
    -- category_id INTEGER SERIAL NOT NULL, 
    category_name character varying(15) NOT NULL,
    description text,
    picture bytea,
     PRIMARY KEY (category_id)
);


-- these all fail: ERROR:  cannot insert into column "category_id"
INSERT INTO categories VALUES (1, 'Beverages', 'Soft drinks, coffees, teas, beers, and ales', '\x');
INSERT INTO categories VALUES (2, 'Condiments', 'Sweet and savory sauces, relishes, spreads, and seasonings', '\x');
INSERT INTO categories VALUES (3, 'Confections', 'Desserts, candies, and sweet breads', '\x');
INSERT INTO categories VALUES (4, 'Dairy Products', 'Cheeses', '\x');
INSERT INTO categories VALUES (5, 'Grains/Cereals', 'Breads, crackers, pasta, and cereal', '\x');
INSERT INTO categories VALUES (6, 'Meat/Poultry', 'Prepared meats', '\x');
INSERT INTO categories VALUES (7, 'Produce', 'Dried fruit and bean curd', '\x');
INSERT INTO categories VALUES (8, 'Seafood', 'Seaweed and fish', '\x');

-- FWIW (not much), this does work
INSERT INTO categories(category_name, description, picture) VALUES ('AutoNum', 'From SQL', '\x');