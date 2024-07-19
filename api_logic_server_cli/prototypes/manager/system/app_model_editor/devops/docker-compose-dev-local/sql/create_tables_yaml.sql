DROP DATABASE IF EXISTS yaml;
CREATE DATABASE yaml;
use yaml;

DROP TABLE IF EXISTS entity;
DROP TABLE IF EXISTS entity_attr;
DROP TABLE IF EXISTS tab_group;
DROP TABLE IF EXISTS global_settings;
DROP TABLE IF EXISTS template;

CREATE TABLE entity (
    name varchar(80) not null,
    title varchar(100) not null,
    pkey varchar(100),
    favorite varchar(100),
    info_list text,
    info_show text,
    exclude boolean default false,
    new_template VARCHAR(80), 
    home_template VARCHAR(80), 
    detail_template VARCHAR(80), 
    mode  VARCHAR(10) DEFAULT 'tab', menu_group VARCHAR(25), 
    PRIMARY KEY (name)
);


CREATE TABLE template (
    name varchar(100) not null,
    description text,
    PRIMARY KEY (name)
);


CREATE TABLE entity_attr (
    entity_name varchar(80) not null,
    attr varchar(80) not null,
    label varchar(100),
    issearch boolean default false,
    issort boolean default false,
    thistype varchar(50) not null,
    template_name varchar(100) default 'text',
    tooltip text,
    isrequired boolean default true,
    isenabled boolean default true,
    exclude boolean default false,
    visible boolean default true, default_value VARCHAR(100),
    PRIMARY KEY (entity_name, attr),
    FOREIGN KEY (entity_name) REFERENCES entity(name),
    FOREIGN KEY (template_name) REFERENCES template(name)
);

CREATE TABLE tab_group (
    entity_name varchar(80) not null,
    tab_entity varchar(80) not null,
    direction varchar(6) not null,
    fkeys varchar(80) not null,
    name varchar(80) not null,
    label varchar(80) not null,
    exclude boolean default false,
    PRIMARY KEY (entity_name,tab_entity,direction, label),
    FOREIGN KEY (entity_name) REFERENCES entity(name),
    FOREIGN KEY (tab_entity) REFERENCES entity(name)
    
);

CREATE TABLE yaml_files(
    id INTEGER NOT NULL,    
    name VARCHAR(100) NOT NULL,    
    content TEXT,
    upload_flag BOOLEAN DEFAULT FALSE,
    download_flag    BOOLEAN DEFAULT FALSE, 
    size INT, createDate DATE, 
    directory BOOLEAN NOT NULL DEFAULT FALSE, 
    downloaded text,
    PRIMARY KEY(id)
);

CREATE TABLE root (
    id INTEGER NOT NULL,
    about_changes TEXT,
    api_root VARCHAR(1000),
    api_auth_type VARCHAR(100),
    api_auth VARCHAR(1000),
    about_date VARCHAR(100),
    PRIMARY KEY(id)
);

CREATE TABLE global_settings (
    name varchar(100) not null,
    value varchar(8000) not null,
    description text,
    PRIMARY KEY (name)
);