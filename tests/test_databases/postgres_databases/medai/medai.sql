-- drop database medai;
-- create database medai;
-- \c media;
-- patient table
create table patient (
	id SERIAL8 PRIMARY KEY,
	name VARCHAR(256) NOT NULL,
	birth_date DATE,
	weight_kg BIGINT, 
	creatine_mg_dl NUMERIC(10,4),
	medical_record_number VARCHAR(256),
	created_date TIMESTAMP DEFAULT NOW()
);

-- blood sugar reading
create table reading (
	id SERIAL8 PRIMARY KEY,
	patient_id BIGINT NOT NULL,
	morning NUMERIC(10,4),
	afternoon NUMERIC(10,4),
	dinner NUMERIC(10,4),
	bedtime NUMERIC(10,4),
	reading_date TIMESTAMP DEFAULT NOW(),
	FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);

-- Drug 

create table drug (
	id SERIAL8 PRIMARY KEY,
	drug_name VARCHAR(256) NOT NULL,
	drug_type VARCHAR(256)

);

-- drug recommendation
create table recommendation (
	id SERIAL8 PRIMARY KEY,
	patient_id BIGINT NOT NULL,
	drug_id BIGINT NOT NULL,
	dosage NUMERIC(10,4),
	recommendation_date TIMESTAMP DEFAULT NOW(),
	FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE,
	FOREIGN KEY (drug_id) REFERENCES drug(id) 
);


-- A drug can have multiple dosages
create table dosage (
	id SERIAL8 PRIMARY KEY,
	drug_id BIGINT NOT NULL,
	drug_name VARCHAR(256), -- parent copy
	drug_type VARCHAR(256), -- parent copy
	min_dose NUMERIC(10,4),
	max_dose NUMERIC(10,4),
	min_age NUMERIC(10,4),
	max_age NUMERIC(10,4),
	min_weight NUMERIC(10,4),
	max_weight NUMERIC(10,4),
	min_creatine NUMERIC(10,4),
	max_creatine NUMERIC(10,4),
	FOREIGN KEY (drug_id) REFERENCES drug(id) ON DELETE CASCADE
);

create table contraindication (
	id SERIAL8 PRIMARY KEY,
	drug_id_1 BIGINT NOT NULL,
	drug_id_2 BIGINT NOT NULL,
	description VARCHAR(256),
	FOREIGN KEY (drug_id_1) REFERENCES drug(id),
	FOREIGN KEY (drug_id_2) REFERENCES drug(id) 
);