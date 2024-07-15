-- Create the database
DROP DATABASE IF EXISTS aniot;
CREATE DATABASE aniot;

-- Connect to the newly created database
\c aniot;

-- Create the equipment_types table
CREATE TABLE equipment_types (
    unique_id SERIAL PRIMARY KEY,
    equipment_type TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the device_types table
CREATE TABLE device_types (
    unique_id SERIAL PRIMARY KEY,
    device_type TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the event_types table
CREATE TABLE event_types (
    unique_id SERIAL PRIMARY KEY,
    event_type TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the event_subject_types table
CREATE TABLE event_subjects_types (
    unique_id SERIAL PRIMARY KEY,
    event_subject_type TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the log_levels table
CREATE TABLE log_levels (
    unique_id SERIAL PRIMARY KEY,
    log_level TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the customers table
CREATE TABLE customers (
    unique_id SERIAL PRIMARY KEY,
    customer_name TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the vessels table
CREATE TABLE vessels (
    unique_id SERIAL PRIMARY KEY,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vessel_name TEXT NOT NULL,
    imo_number TEXT NOT NULL,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the equipment table
CREATE TABLE equipment (
    unique_id SERIAL PRIMARY KEY,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    equipment_type_id INTEGER REFERENCES equipment_types(unique_id),
    equipment_name TEXT NOT NULL,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the customer_vessels table to manage the relationship between customers and vessels
CREATE TABLE customer_vessels (
    customer_id INTEGER REFERENCES customers(unique_id),
    vessel_id INTEGER REFERENCES vessels(unique_id),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (customer_id, vessel_id)
);

-- Create the vessel_equipment table to manage the relationship between vessels and equipment
CREATE TABLE vessel_equipment (
    vessel_id INTEGER REFERENCES vessels(unique_id),
    equipment_id INTEGER REFERENCES equipment(unique_id),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (vessel_id, equipment_id)
);

-- Create the devices table
CREATE TABLE devices (
    unique_id SERIAL PRIMARY KEY,
    ip_address TEXT UNIQUE NOT NULL,
    device_type_id INTEGER REFERENCES device_types(unique_id),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the sensors_lines table
CREATE TABLE sensors_lines (
    unique_id SERIAL PRIMARY KEY,
    uuid_id UUID DEFAULT gen_random_uuid(),
    is_digital BOOLEAN DEFAULT TRUE,
    sensor_line_label TEXT UNIQUE NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE
);

-- Create the device_sensors_lines table to manage the relationship between devices and sensors
CREATE TABLE device_sensors_lines (
    device_id INTEGER REFERENCES devices(unique_id),
    sensor_line_id INTEGER REFERENCES sensors_lines(unique_id),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (device_id, sensor_line_id)
);

-- Create the events_log table to manage the relationship between change events and assets
CREATE TABLE events_log (
    subject_of_change_id INTEGER,
    subject_of_change_type_id INTEGER,
    event_type_id INTEGER REFERENCES event_types(unique_id),
    previous_state_value TEXT,
    new_state_value TEXT,
    log_level_id INTEGER REFERENCES log_levels(unique_id),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_inactive BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (subject_of_change_id, subject_of_change_type_id)
);

-- Create a trigger to update the update_date field on record update
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.update_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the customers table
CREATE TRIGGER update_customers_update_date
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the equipment_types table
CREATE TRIGGER update_equipment_types_update_date
BEFORE UPDATE ON equipment_types
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the vessels table
CREATE TRIGGER update_vessels_update_date
BEFORE UPDATE ON vessels
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the equipment table
CREATE TRIGGER update_equipment_update_date
BEFORE UPDATE ON equipment
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the customer_vessels table
CREATE TRIGGER update_customer_vessels_update_date
BEFORE UPDATE ON customer_vessels
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the vessel_equipment table
CREATE TRIGGER update_vessel_equipment_update_date
BEFORE UPDATE ON vessel_equipment
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the devices table
CREATE TRIGGER update_devices_update_date
BEFORE UPDATE ON devices
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the device_types table
CREATE TRIGGER update_device_types_update_date
BEFORE UPDATE ON device_types
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the sensors_lines table
CREATE TRIGGER update_sensors_lines_update_date
BEFORE UPDATE ON sensors_lines
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the device_sensors_lines table
CREATE TRIGGER update_device_sensors_lines_update_date
BEFORE UPDATE ON device_sensors_lines
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the event_types table
CREATE TRIGGER update_event_types_update_date
BEFORE UPDATE ON event_types
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the event_subjects_types table
CREATE TRIGGER update_event_subjects_types_update_date
BEFORE UPDATE ON event_subjects_types
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Attach the trigger to the events_log table
CREATE TRIGGER update_events_log_update_date
BEFORE UPDATE ON events_log
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

-- Seed data into customers table
INSERT INTO customers (customer_name) VALUES
    ('Algoma Central Corporation'),
    ('CSL');

-- Seed data into equipment_types table
INSERT INTO equipment_types (equipment_type) VALUES
    ('Gyro'),
    ('Radar'),
    ('ECDIS'),
    ('Autopilot'),
    ('AIS');
    
-- Seed data into vessels table
INSERT INTO vessels (vessel_name, imo_number) VALUES
    ('Algoma Transport', '7711737'),
    ('CSL Niagara', '7128423');

-- Seed data into device_types table
INSERT INTO device_types (device_type) VALUES
    ('cm4-io-wireless-base-b');

-- Seed data into event_types table
INSERT INTO event_types (event_type) VALUES
    ('sensor_state_onstart'),
    ('sensor_state_change'),
    ('system_restarted'),
    ('system_config_change'),
    ('service_restarted'),
    ('service_stopped'),
    ('network_failure');

-- Seed data into event_subjects_types table
INSERT INTO event_subjects_types (event_subject_type) VALUES
    ('network'),
    ('system'),
    ('service'),
    ('configuration'),
    ('sensor');

-- Seed data into log_levels table
INSERT INTO log_levels (log_level) VALUES
    ('info'),
    ('warn'),
    ('alrt'),
    ('fail');
