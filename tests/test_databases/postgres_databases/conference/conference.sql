DROP DATABASE IF EXISTS conference;
CREATE DATABASE conference;
\c conference;


drop table conference_venue;
drop table session_person;
drop table talk_person;
drop table talk;
drop table session;
drop table location;
drop table venue;
drop table conference_person;
drop table person;
drop table conference;

-- Person Table
CREATE TABLE Person (
    PersonID SERIAL PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Photo VARCHAR(255),
    Pronouns VARCHAR(50),
    Role VARCHAR(255),
    Organization VARCHAR(255),
    City VARCHAR(255),
    Country VARCHAR(255),
    AskMeAbout TEXT,
    Passion TEXT,
    GoodAt TEXT,
    Bio TEXT,
    Email VARCHAR(255),
    Phone VARCHAR(50),
    LinkedInHandle VARCHAR(255),
    TwitterHandle VARCHAR(255),
    InstagramHandle VARCHAR(255),
    URL VARCHAR(255)
);

-- Conference Table
CREATE TABLE Conference (
    ConferenceID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    StartDate DATE,
    EndDate DATE
);

-- Venue Table
CREATE TABLE Venue (
    VenueID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Address VARCHAR(255)
);

-- Conference_Venue Junction Table
CREATE TABLE Conference_Venue (
    ConferenceID INT,
    VenueID INT,
    FOREIGN KEY (ConferenceID) REFERENCES Conference(ConferenceID),
    FOREIGN KEY (VenueID) REFERENCES Venue(VenueID)
);

-- Location Table
CREATE TABLE Location (
    LocationID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Description TEXT,
    VenueID INT,
    FOREIGN KEY (VenueID) REFERENCES Venue(VenueID)
);

-- Session Table
CREATE TABLE Session (
    SessionID SERIAL PRIMARY KEY,
    ConferenceID INT,
    Name VARCHAR(255),
    StartDateTime TIMESTAMP,
    EndDateTime TIMESTAMP,
    LocationID INT,
    FOREIGN KEY (ConferenceID) REFERENCES Conference(ConferenceID),
    FOREIGN KEY (LocationID) REFERENCES Location(LocationID)
);

-- Talk Table
CREATE TABLE Talk (
    TalkID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    SessionID INT,
    FOREIGN KEY (SessionID) REFERENCES Session(SessionID)
);

-- Session_Person Junction Table for facilitators and panelists
CREATE TABLE Session_Participant (
    SessionID INT,
    PersonID INT,
    Role VARCHAR(50),
    FOREIGN KEY (SessionID) REFERENCES Session(SessionID),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    PRIMARY KEY (SessionID, PersonID, Role)
);

-- Talk_Person Junction Table for speakers and participants
CREATE TABLE Talk_Participant (
    TalkID INT,
    PersonID INT,
    Role VARCHAR(50),
    FOREIGN KEY (TalkID) REFERENCES Talk(TalkID),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    PRIMARY KEY (TalkID, PersonID, Role)
);

-- Conference_Person Junction Table
CREATE TABLE Attendee (
    ConferenceID INT,
    PersonID INT,
    FOREIGN KEY (ConferenceID) REFERENCES Conference(ConferenceID),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    PRIMARY KEY (ConferenceID, PersonID)
);



-- Insert a Conference
INSERT INTO Conference (Name, StartDate, EndDate) VALUES ('Test Summit 2024', '2024-10-01', '2024-10-04');

-- Insert a Venue
INSERT INTO Venue (Name, Address) VALUES ('Convention Center', '123 Tech Road, San Francisco');

-- Link the Conference and Venue
INSERT INTO Conference_Venue (ConferenceID, VenueID) VALUES (1, 1);

-- Insert Locations within the Venue
INSERT INTO Location (Name, Description, VenueID) VALUES
('Main Hall', 'The largest hall for keynotes and plenaries', 1),
('Room 101', 'A medium-sized room for workshops', 1),
('Room 102', 'A medium-sized room for workshops', 1),
('Room 103', 'A medium-sized room for workshops', 1),
('Outdoor Arena', 'Open area for social gatherings', 1);

-- Insert Sessions
INSERT INTO Session (ConferenceID, Name, StartDateTime, EndDateTime, LocationID) VALUES
-- Complete Session Insertion
(1, 'Tech Trends 2024', '2024-10-01 11:00:00', '2024-10-01 12:30:00', 1),
(1, 'Future of Work', '2024-10-01 14:00:00', '2024-10-01 15:30:00', 3),
(1, 'Sustainable Tech Innovations', '2024-10-01 16:00:00', '2024-10-01 17:30:00', 4),
(1, 'Company Culture in the New Era', '2024-10-02 09:00:00', '2024-10-02 10:30:00', 2),
(1, 'Profit & Ethics', '2024-10-02 11:00:00', '2024-10-02 12:30:00', 3),
(1, 'Business Beyond Profit', '2024-10-02 14:00:00', '2024-10-02 15:30:00', 4),
(1, 'The Economy of Diversity', '2024-10-02 16:00:00', '2024-10-02 17:30:00', 5),
(1, 'Advancements in Profit Sharing', '2024-10-03 09:00:00', '2024-10-03 10:30:00', 2),
(1, 'Globalization: The Next Frontier', '2024-10-03 11:00:00', '2024-10-03 12:30:00', 3),
(1, 'Panel Discussion: The Future of Economy', '2024-10-03 14:00:00', '2024-10-03 15:30:00', 1);

-- Insert Attendees
INSERT INTO Person (FirstName, LastName, Pronouns, Role, Organization, City, Country, Email) VALUES
('Don', 'Zack', 'they/them', 'Host', 'One Palm', 'Walnut Creek', 'USA', 'don@zack.org'),
('Sam', 'Lee', 'she/her', 'Product Manager', 'TechSolutions', 'New York', 'USA', 'sam.l@techsolutions.com'),
('Jordan', 'Diaz', 'he/him', 'CEO', 'StartupGen', 'Austin', 'USA', 'jordan.d@startupgen.com'),
('Casey', 'Wong', 'they/them', 'Designer', 'CreativeMinds', 'Toronto', 'Canada', 'casey.w@creativeminds.ca');

-- Link Attendees to the Conference
INSERT INTO Attendee (ConferenceID, PersonID) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4);

-- Assuming Sessions are already inserted, insert Talks
INSERT INTO Talk (Name, SessionID) VALUES
('Innovating the Future', 2),
('The Role of Ethics in Modern Economy', 3);

-- Assign Speakers and Participants to Talks
-- Assuming Alex Johnson and Sam Lee are speakers, and Jordan Diaz and Casey Wong are participants
INSERT INTO Talk_Participant (TalkID, PersonID, Role) VALUES
(1, 1, 'Speaker'),
(2, 2, 'Speaker'),
(1, 3, 'Participant'),
(2, 4, 'Participant');

-- Assign Facilitators and Panelists to Sessions
-- Assuming Alex and Sam are facilitators for the first two sessions, Jordan and Casey are panelists
INSERT INTO Session_Participant (SessionID, PersonID, Role) VALUES
(1, 1, 'Host'),
(2, 2, 'Facilitator'),
(1, 3, 'Panelist'),
(2, 4, 'Panelist');