-- drop database circles;
-- create database circles;
DROP DATABASE IF EXISTS mycircles;
CREATE DATABASE mycircles;

-- run this from manager
-- ApiLogicServer create --db_url=postgresql://postgres:p@localhost/mycircles --project-name=../../servers/mycircles

-- rebuild the database (if using this script from pg cli, I *think* the comments make it fail)
DROP TABLE IF EXISTS response;
DROP TABLE IF EXISTS daily_reponse_count;
DROP TABLE IF EXISTS card_selection;
DROP TABLE IF EXISTS card;
DROP TABLE IF EXISTS circle;

DROP TABLE IF EXISTS question_tags;
DROP TABLE IF EXISTS cardtype;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS fellowship; 


CREATE TABLE fellowship (
    name VARCHAR(5) PRIMARY KEY,
    full_name VARCHAR(100) ,
    website VARCHAR(1000)
);

-- use tags instead of circle_type

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL,
    fellowship_name VARCHAR(5) NOT NULL REFERENCES fellowship(name),
    UNIQUE (tag_name, fellowship_name)
 
);

INSERT INTO tags (tag_name,fellowship_name) VALUES ('health','SAA');
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(250) NULL,
    password_salt VARCHAR(250) NULL,
    fellowship_name VARCHAR(5) REFERENCES fellowship(name),
    email VARCHAR(255) UNIQUE,
    cell VARCHAR(25)
);



CREATE TABLE circle (
	circle_type VARCHAR(10) NOT NULL CHECK (circle_type in ('Inner','Middle','Outer')),
	decription TEXT,
	PRIMARY KEY (circle_type)
	
);

CREATE TABLE cardtype (
   card_type VARCHAR(20) PRIMARY KEY
);

INSERT INTO cardtype VALUES ('true_false');
INSERT INTO cardtype VALUES ('free');
INSERT INTO cardtype VALUES ('range');

CREATE TABLE card (
    id SERIAL PRIMARY KEY,
    fellowship_name VARCHAR(5) REFERENCES fellowship(name) ON DELETE CASCADE,
    circle_text TEXT NOT NULL,
    card_type VARCHAR(10) REFERENCES cardtype(card_type),
    is_active BOOLEAN DEFAULT TRUE
);



CREATE TABLE card_tag (
    id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES card(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id)
);

INSERT INTO card_tag (card_id, tag_id) VALUES (3,1);
INSERT INTO card_tag  (card_id, tag_id) VALUES (4, 1);

CREATE TABLE card_selection (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    card_id INTEGER REFERENCES card(id),
    circle_type VARCHAR(10) REFERENCES circle(circle_type),
    selected_date DATE NOT NULL DEFAULT current_timestamp,
    UNIQUE (user_id, card_id, circle_type)
);


-- Rule insert paret if none
CREATE TABLE daily_reponse_count (
	user_id INTEGER NOT NULL,
	response_date DATE NOT NULL,
	count_inner  INTEGER DEFAULT 0, -- any
	count_middle INTEGER DEFAULT 0, -- if boolean true
	count_outer  INTEGER DEFAULT 0,  -- any
	PRIMARY KEY (user_id, response_date)
);


CREATE TABLE response (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    card_id INTEGER REFERENCES card_selection(id),
    response_date DATE NOT NULL DEFAULT current_timestamp,
    response_text TEXT,
    response_bool BOOLEAN,
    response_range INTEGER ,
    UNIQUE (user_id, card_id, response_date),
    FOREIGN KEY (user_id, response_date) REFERENCES daily_reponse_count(user_id, response_date)
);






