--   ApiLogicServer create --db_url=mysql+pymysql://root:p@localhost:3306/employee_skills --project_name=employee_skills


/*******************************************************************************
   Drop database if it exists
********************************************************************************/
DROP DATABASE IF EXISTS `employee_skills`;


/*******************************************************************************
   Create database
********************************************************************************/
CREATE DATABASE `employee_skills`;


USE `employee_skills`;


-- Create the Employees table
CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hire_date DATE,
    department VARCHAR(50)
);

-- Create the Skills table
CREATE TABLE Skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE
);

-- Create the EmployeeSkills junction table with a rating column
CREATE TABLE EmployeeSkills (
    employee_id INT,
    skill_id INT,
    rating INT, -- You can use an INT to represent skill ratings, such as 1 (low) to 5 (high)
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id)
);
