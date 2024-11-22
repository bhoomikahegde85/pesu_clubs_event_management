
create database pesu_clubs_event_management;

USE pesu_clubs_event_management;

-- 1. Create Department Table
CREATE TABLE DEPARTMENT (
    depart_id VARCHAR(10) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_name VARCHAR(50) NOT NULL
);

-- 2. Create Faculty Advisor Table
CREATE TABLE FACULTY_ADVISOR (
    SRN VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    depart_id VARCHAR(10),
    phone_number VARCHAR(15),
    FOREIGN KEY (depart_id) REFERENCES DEPARTMENT(depart_id)
);

-- 3. Create Club Table
CREATE TABLE CLUB (
    club_email VARCHAR(100),
    instagram_handle VARCHAR(50) UNIQUE,
    club_name VARCHAR(50) UNIQUE,
    logo BLOB,
    number_of_members INT DEFAULT 0,
    faculty_advisor_srn VARCHAR(20),
    depart_id VARCHAR(10),
    PRIMARY KEY (club_email, instagram_handle, club_name),
    FOREIGN KEY (faculty_advisor_srn) REFERENCES FACULTY_ADVISOR(SRN),
    FOREIGN KEY (depart_id) REFERENCES DEPARTMENT(depart_id)
);

-- 4. Create Club Member Table
CREATE TABLE CLUB_MEMBER (
    member_srn VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    cgpa DECIMAL(4, 2),
    depart_id VARCHAR(10),
    FOREIGN KEY (depart_id) REFERENCES DEPARTMENT(depart_id)
);

-- 5. Create Users Table
CREATE TABLE USERS (
    email VARCHAR(100) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('club_member', 'club_head', 'management') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 6. Create Event Table
CREATE TABLE EVENT (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    budget DECIMAL(10, 2),
    location VARCHAR(100),
    duration INT,
    start_date DATE,
    number_of_participants INT DEFAULT 0,
    club_id VARCHAR(50),
    FOREIGN KEY (club_id) REFERENCES CLUB(club_name)
);

-- 7. Log Tables
CREATE TABLE club_change_log (
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE department_change_log (
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event_change_log (
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE FACULTY_ADVISOR_LOG (
    old_name VARCHAR(100),
    new_name VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_change_log (
    faculty_id VARCHAR(20),
    old_email VARCHAR(100),
    new_email VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Triggers

-- Trigger to ensure Instagram handle starts with '@'
DELIMITER $$
CREATE TRIGGER before_insert_update_instagram
BEFORE INSERT ON CLUB
FOR EACH ROW
BEGIN
    IF LEFT(NEW.instagram_handle, 1) != '@' THEN
        SET NEW.instagram_handle = CONCAT('@', NEW.instagram_handle);
    END IF;
END$$
DELIMITER ;
-- Insert Bhoomika as a club member
INSERT INTO users (email, password, role)
VALUES ('bhoomika@example.com', 'password_1', 'club_member');

-- Insert Adithya as a club head
INSERT INTO users (email, password, role)
VALUES ('adithya@example.com', 'password_2', 'club_head');

-- Insert Eshvar as part of management
INSERT INTO users (email, password, role)
VALUES ('eshvar@example.com', 'password_3', 'management');

INSERT INTO users (email, password, role)
VALUES ('prnaav@example.com', 'password_4', 'club_member');


-- Trigger to validate unique department email
DELIMITER $$
CREATE TRIGGER before_insert_email
BEFORE INSERT ON DEPARTMENT
FOR EACH ROW
BEGIN
    DECLARE email_count INT;
    SELECT COUNT(*) INTO email_count FROM DEPARTMENT WHERE email = NEW.email;
    IF email_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Email address must be unique for each department';
    END IF;
END$$
DELIMITER ;

-- Trigger to auto-generate department email on name update
DELIMITER $$
CREATE TRIGGER before_update_department_name
BEFORE UPDATE ON DEPARTMENT
FOR EACH ROW
BEGIN
    SET NEW.email = CONCAT(LOWER(REPLACE(NEW.department_name, ' ', '')), '@pes.edu');
END$$
DELIMITER ;

-- Trigger to log changes in department name
DELIMITER $$
CREATE TRIGGER after_update_department
AFTER UPDATE ON DEPARTMENT
FOR EACH ROW
BEGIN
    INSERT INTO department_change_log (old_value, new_value, change_timestamp)
    VALUES (OLD.department_name, NEW.department_name, NOW());
END$$
DELIMITER ;

-- Trigger to validate event duration
DELIMITER $$
CREATE TRIGGER before_insert_event_duration
BEFORE INSERT ON EVENT
FOR EACH ROW
BEGIN
    IF NEW.duration <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Event duration must be a positive value';
    END IF;
END$$
DELIMITER ;

-- Trigger to log changes in event details
DELIMITER $$
CREATE TRIGGER after_update_event
AFTER UPDATE ON EVENT
FOR EACH ROW
BEGIN
    INSERT INTO event_change_log (old_value, new_value, change_timestamp)
    VALUES (OLD.title, NEW.title, NOW());
END$$
DELIMITER ;

-- Trigger to log faculty advisor updates
DELIMITER $$
CREATE TRIGGER after_faculty_update
AFTER UPDATE ON FACULTY_ADVISOR
FOR EACH ROW
BEGIN
    INSERT INTO FACULTY_ADVISOR_LOG (old_name, new_name, change_timestamp)
    VALUES (OLD.name, NEW.name, NOW());
END$$
DELIMITER ;

-- Trigger to log email changes in faculty advisor
DELIMITER $$
CREATE TRIGGER after_update_faculty_advisor
AFTER UPDATE ON FACULTY_ADVISOR
FOR EACH ROW
BEGIN
    INSERT INTO email_change_log (faculty_id, old_email, new_email, change_timestamp)
    VALUES (OLD.SRN, OLD.email, NEW.email, NOW());
END$$
DELIMITER ;

USE pesu_clubs_event_management;

-- 1. Insert Departments
INSERT INTO DEPARTMENT (depart_id, email, department_name) VALUES
('pes1ug2201', 'me@pes.edu', 'Mechanical Engineering'),
('pes1ug2202', 'ec@pes.edu', 'Electronics and Communication'),
('pes1ug2203', 'aiml@pes.edu', 'Artificial Intelligence and Machine Learning');

-- 2. Insert Faculty Advisors
INSERT INTO FACULTY_ADVISOR (SRN, name, email, depart_id, phone_number) VALUES
('pes1ug2201', 'Dr. John Doe', 'johndoe@pes.edu', 'pes1ug2201', '9876543210'),
('pes1ug2202', 'Dr. Emily Smith', 'emilysmith@pes.edu', 'pes1ug2202', '9876543211'),
('pes1ug2203', 'Dr. William Brown', 'williambrown@pes.edu', 'pes1ug2203', '9876543212');

-- 3. Insert Clubs
INSERT INTO CLUB (club_email, instagram_handle, club_name, depart_id, faculty_advisor_srn) VALUES
('ninaada@pes.edu', '@ninaada', 'Ninaada', 'pes1ug2201', 'pes1ug2201'),
('aikya@pes.edu', '@aikya', 'Aikya', 'pes1ug2202', 'pes1ug2202'),
('aatmatrisha@pes.edu', '@aatmatrisha', 'Aatmatrisha', 'pes1ug2203', 'pes1ug2203'),
('ecell@pes.edu', '@ecell', 'Ecell', 'pes1ug2202', 'pes1ug2202'),
('csr@pes.edu', '@csr', 'CSR', 'pes1ug2203', 'pes1ug2203');

-- 4. Insert Club Members
INSERT INTO CLUB_MEMBER (member_srn, name, email, phone_number, cgpa, depart_id) VALUES
('pes1ug2201', 'Alice Williams', 'alice@pes.edu', '9123456789', 9.0, 'pes1ug2201'),
('pes1ug2202', 'Bob Johnson', 'bob@pes.edu', '9234567890', 8.5, 'pes1ug2202'),
('pes1ug2203', 'Charlie Davis', 'charlie@pes.edu', '9345678901', 9.2, 'pes1ug2203'),
('pes1ug2204', 'David Martinez', 'david@pes.edu', '9456789012', 8.7, 'pes1ug2202'),
('pes1ug2205', 'Eva Brown', 'eva@pes.edu', '9567890123', 8.9, 'pes1ug2203');

-- 5. Insert Events
INSERT INTO EVENT (title, budget, location, duration, start_date, club_id) VALUES
('Ninaada Musical Night', 5000, 'Main Auditorium', 3, '2024-12-05', 'Ninaada'),
('Aikya Cultural Fest', 7000, 'College Grounds', 2, '2024-12-10', 'Aikya'),
('Aatmatrisha Tech Talk', 4000, 'Seminar Hall', 1, '2024-12-12', 'Aatmatrisha'),
('Ecell Startup Pitch', 8000, 'Conference Room', 4, '2024-12-15', 'Ecell'),
('CSR Community Outreach', 3000, 'Community Center', 1, '2024-12-20', 'CSR');

DELIMITER $$
CREATE PROCEDURE AddClub(
    IN club_email VARCHAR(100), 
    IN instagram_handle VARCHAR(50), 
    IN club_name VARCHAR(50), 
    IN depart_id VARCHAR(10), 
    IN faculty_advisor_srn VARCHAR(20)
)
BEGIN
    IF LEFT(instagram_handle, 1) != '@' THEN
        SET instagram_handle = CONCAT('@', instagram_handle);
    END IF;

    INSERT INTO CLUB (club_email, instagram_handle, club_name, depart_id, faculty_advisor_srn)
    VALUES (club_email, instagram_handle, club_name, depart_id, faculty_advisor_srn);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE LogDepartmentChange(
    IN old_value VARCHAR(100), 
    IN new_value VARCHAR(100)
)
BEGIN
    INSERT INTO department_change_log (old_value, new_value, change_timestamp)
    VALUES (old_value, new_value, NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION GetTotalBudget(club_name VARCHAR(50))
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE total_budget DECIMAL(10, 2);
    SELECT SUM(budget) INTO total_budget
    FROM EVENT
    WHERE club_id = club_name;
    RETURN IFNULL(total_budget, 0);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddEvent(
    IN event_title VARCHAR(100),
    IN event_budget DECIMAL(10, 2),
    IN event_location VARCHAR(100),
    IN event_duration INT,
    IN event_start_date DATE,
    IN event_club_id VARCHAR(50)
)
BEGIN
    IF event_duration <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event duration must be a positive value';
    END IF;

    IF event_budget <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event budget must be a positive value';
    END IF;

    INSERT INTO EVENT (title, budget, location, duration, start_date, club_id)
    VALUES (event_title, event_budget, event_location, event_duration, event_start_date, event_club_id);
END$$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION GetFacultyByDepartment(department_id VARCHAR(10))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE faculty_details VARCHAR(255);
    SELECT GROUP_CONCAT(name SEPARATOR ', ') INTO faculty_details
    FROM FACULTY_ADVISOR
    WHERE depart_id = department_id;
    RETURN faculty_details;
END$$
DELIMITER ;

DELIMITER $$

CREATE PROCEDURE UpdateClubMembershipCount(IN club_name VARCHAR(50))
BEGIN
    -- Calculate the count of members for the given club name
    DECLARE member_count INT;
    
    SELECT COUNT(*)
    INTO member_count
    FROM CLUB_MEMBER
    WHERE depart_id = (SELECT depart_id FROM CLUB WHERE club_name = club_name LIMIT 1);
    
    -- Update the number_of_members for the club
    UPDATE CLUB
    SET number_of_members = member_count
    WHERE club_name = club_name;
END$$

DELIMITER ;



-- First, let's create a table to store club head associations
CREATE TABLE CLUB_HEAD_ASSOCIATION (
    email VARCHAR(100),
    club_name VARCHAR(50),
    PRIMARY KEY (email, club_name),
    FOREIGN KEY (email) REFERENCES USERS(email),
    FOREIGN KEY (club_name) REFERENCES CLUB(club_name)
);

-- Insert the association for Adithya as Ecell's club head
INSERT INTO CLUB_HEAD_ASSOCIATION (email, club_name)
VALUES ('adithya@example.com', 'Ecell');

-- First create a user account for Amit with club_head role
INSERT INTO USERS (email, password, role)
VALUES ('amit@example.com', 'password_amit', 'club_head');

-- Then add the association between Amit and Ninaada in the CLUB_HEAD_ASSOCIATION table
INSERT INTO CLUB_HEAD_ASSOCIATION (email, club_name)
VALUES ('amit@example.com', 'Ninaada');

-- First, fix the SELECT query by removing the extra space after 'role'
SELECT u.email, u.role, cha.club_name 
FROM USERS u 
JOIN CLUB_HEAD_ASSOCIATION cha ON u.email = cha.email 
WHERE u.role = 'club_head';

-- For adding Riya, first create her user account
INSERT INTO USERS (email, password, role)
VALUES ('riya@gmail.com', 'password_riya', 'club_head');


SELECT name FROM CLUB WHERE depart_id = (SELECT depart_id FROM DEPARTMENT WHERE department_name = 'Mechanical Engineering');

SELECT * FROM (SELECT * FROM CLUB WHERE number_of_members > 50) AS LargeClubs;

SELECT name, (SELECT department_name FROM DEPARTMENT WHERE depart_id = CLUB.depart_id) AS DepartmentName FROM CLUB;
