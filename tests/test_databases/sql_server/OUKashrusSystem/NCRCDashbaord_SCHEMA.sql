-- =============================================
-- OU Kashrus Management System - Unified Database Schema
-- MS SQL Server DDL with Comprehensive Mock Data
-- Combines: RFR Dashboard, NCRC Dashboard, Contract Management, and Application Management
-- =============================================

-- Create Database
-- CREATE DATABASE OUKashrusSystem;
-- GO

-- sqlcmd -S localhost,1433 -U sa -P 'Posey3861' -C
-- sqlcmd -S localhost,1433 -U sa -P 'Posey3861' -i tests/test_databases/sql_server/OUKashrusSystem/NCRCDashbaord_SCHEMA.sql -C

SET QUOTED_IDENTIFIER ON;
GO

USE OUKashrusSystem;
GO

-- =============================================
-- DROP EXISTING TABLES (IF THEY EXIST)
-- =============================================

-- Drop tables in reverse dependency order to avoid foreign key conflicts
IF OBJECT_ID('TaskAudit', 'U') IS NOT NULL DROP TABLE TaskAudit;
IF OBJECT_ID('ApplicationAudit', 'U') IS NOT NULL DROP TABLE ApplicationAudit;
IF OBJECT_ID('ApplicationActivity', 'U') IS NOT NULL DROP TABLE ApplicationActivity;
IF OBJECT_ID('ApplicationComments', 'U') IS NOT NULL DROP TABLE ApplicationComments;
IF OBJECT_ID('TaskMessages', 'U') IS NOT NULL DROP TABLE TaskMessages;
IF OBJECT_ID('Messages', 'U') IS NOT NULL DROP TABLE Messages;
IF OBJECT_ID('Tasks', 'U') IS NOT NULL DROP TABLE Tasks;
IF OBJECT_ID('ApplicationTasks', 'U') IS NOT NULL DROP TABLE ApplicationTasks;
IF OBJECT_ID('DocuSignSigners', 'U') IS NOT NULL DROP TABLE DocuSignSigners;
IF OBJECT_ID('DocuSignEnvelopes', 'U') IS NOT NULL DROP TABLE DocuSignEnvelopes;
IF OBJECT_ID('ContractRevisions', 'U') IS NOT NULL DROP TABLE ContractRevisions;
IF OBJECT_ID('ContractApprovals', 'U') IS NOT NULL DROP TABLE ContractApprovals;
IF OBJECT_ID('ContractIngredients', 'U') IS NOT NULL DROP TABLE ContractIngredients;
IF OBJECT_ID('Contracts', 'U') IS NOT NULL DROP TABLE Contracts;
IF OBJECT_ID('InspectionRecommendations', 'U') IS NOT NULL DROP TABLE InspectionRecommendations;
IF OBJECT_ID('InspectionIssues', 'U') IS NOT NULL DROP TABLE InspectionIssues;
IF OBJECT_ID('InspectionRequests', 'U') IS NOT NULL DROP TABLE InspectionRequests;
IF OBJECT_ID('ApplicationAISuggestions', 'U') IS NOT NULL DROP TABLE ApplicationAISuggestions;
IF OBJECT_ID('ApplicationFiles', 'U') IS NOT NULL DROP TABLE ApplicationFiles;
IF OBJECT_ID('ApplicationValidation', 'U') IS NOT NULL DROP TABLE ApplicationValidation;
IF OBJECT_ID('QuoteItems', 'U') IS NOT NULL DROP TABLE QuoteItems;
IF OBJECT_ID('ApplicationQuotes', 'U') IS NOT NULL DROP TABLE ApplicationQuotes;
IF OBJECT_ID('Equipment', 'U') IS NOT NULL DROP TABLE Equipment;
IF OBJECT_ID('ApplicationIngredients', 'U') IS NOT NULL DROP TABLE ApplicationIngredients;
IF OBJECT_ID('ApplicationProducts', 'U') IS NOT NULL DROP TABLE ApplicationProducts;
IF OBJECT_ID('ApplicationStages', 'U') IS NOT NULL DROP TABLE ApplicationStages;
IF OBJECT_ID('ApplicationPrerequisites', 'U') IS NOT NULL DROP TABLE ApplicationPrerequisites;
IF OBJECT_ID('ApplicationContacts', 'U') IS NOT NULL DROP TABLE ApplicationContacts;
IF OBJECT_ID('Applications', 'U') IS NOT NULL DROP TABLE Applications;
IF OBJECT_ID('Ingredients', 'U') IS NOT NULL DROP TABLE Ingredients;
IF OBJECT_ID('Suppliers', 'U') IS NOT NULL DROP TABLE Suppliers;
IF OBJECT_ID('Facilities', 'U') IS NOT NULL DROP TABLE Facilities;
IF OBJECT_ID('Companies', 'U') IS NOT NULL DROP TABLE Companies;
IF OBJECT_ID('NCRCSpecialties', 'U') IS NOT NULL DROP TABLE NCRCSpecialties;
IF OBJECT_ID('NCRCs', 'U') IS NOT NULL DROP TABLE NCRCs;
IF OBJECT_ID('RFRPreferredDays', 'U') IS NOT NULL DROP TABLE RFRPreferredDays;
IF OBJECT_ID('RFRAvailability', 'U') IS NOT NULL DROP TABLE RFRAvailability;
IF OBJECT_ID('RFRCertifications', 'U') IS NOT NULL DROP TABLE RFRCertifications;
IF OBJECT_ID('RFRSpecialties', 'U') IS NOT NULL DROP TABLE RFRSpecialties;
IF OBJECT_ID('RFRProfiles', 'U') IS NOT NULL DROP TABLE RFRProfiles;
IF OBJECT_ID('Users', 'U') IS NOT NULL DROP TABLE Users;
IF OBJECT_ID('Staff', 'U') IS NOT NULL DROP TABLE Staff;
IF OBJECT_ID('UserRoles', 'U') IS NOT NULL DROP TABLE UserRoles;
IF OBJECT_ID('IngredientStatuses', 'U') IS NOT NULL DROP TABLE IngredientStatuses;
IF OBJECT_ID('ScheduleAGroups', 'U') IS NOT NULL DROP TABLE ScheduleAGroups;
IF OBJECT_ID('DairyStatuses', 'U') IS NOT NULL DROP TABLE DairyStatuses;
IF OBJECT_ID('IngredientCategories', 'U') IS NOT NULL DROP TABLE IngredientCategories;
IF OBJECT_ID('ContractTypes', 'U') IS NOT NULL DROP TABLE ContractTypes;
IF OBJECT_ID('TaskStatuses', 'U') IS NOT NULL DROP TABLE TaskStatuses;
IF OBJECT_ID('WorkflowStages', 'U') IS NOT NULL DROP TABLE WorkflowStages;
IF OBJECT_ID('ApplicationStatuses', 'U') IS NOT NULL DROP TABLE ApplicationStatuses;
IF OBJECT_ID('Priorities', 'U') IS NOT NULL DROP TABLE Priorities;
IF OBJECT_ID('Regions', 'U') IS NOT NULL DROP TABLE Regions;

-- =============================================
-- REFERENCE/LOOKUP TABLES
-- =============================================

-- Regions Table
CREATE TABLE Regions (
    RegionID INT IDENTITY(1,1) PRIMARY KEY,
    RegionCode NVARCHAR(20) NOT NULL UNIQUE,
    RegionName NVARCHAR(100) NOT NULL,
    CountryCode NVARCHAR(10) DEFAULT 'US',
    Description NVARCHAR(255),
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Priorities Table
CREATE TABLE Priorities (
    PriorityCode NVARCHAR(20) PRIMARY KEY,
    PriorityLabel NVARCHAR(50) NOT NULL,
    SortOrder INT NOT NULL,
    ColorCode NVARCHAR(20),
    IsActive BIT NOT NULL DEFAULT 1
);

-- Application Statuses Table
CREATE TABLE ApplicationStatuses (
    StatusCode NVARCHAR(50) PRIMARY KEY,
    StatusLabel NVARCHAR(100) NOT NULL,
    StatusDescription NVARCHAR(500),
    SortOrder INT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Workflow Stages Table
CREATE TABLE WorkflowStages (
    StageCode NVARCHAR(50) PRIMARY KEY,
    StageName NVARCHAR(100) NOT NULL,
    StageDescription NVARCHAR(500),
    SortOrder INT NOT NULL,
    IsRequired BIT NOT NULL DEFAULT 1,
    IsActive BIT NOT NULL DEFAULT 1
);

-- Task Statuses Table
CREATE TABLE TaskStatuses (
    StatusCode NVARCHAR(50) PRIMARY KEY,
    StatusLabel NVARCHAR(100) NOT NULL,
    StatusDescription NVARCHAR(500),
    ColorCode NVARCHAR(20),
    IsActive BIT NOT NULL DEFAULT 1
);

-- Contract Types Table
CREATE TABLE ContractTypes (
    ContractTypeId NVARCHAR(50) PRIMARY KEY,
    Label NVARCHAR(100) NOT NULL,
    Description NVARCHAR(255) NOT NULL,
    DefaultDuration INT NOT NULL DEFAULT 12,
    RequiresLegalReview BIT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Ingredient Categories Table
CREATE TABLE IngredientCategories (
    CategoryId NVARCHAR(50) PRIMARY KEY,
    CategoryName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(255),
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Dairy Statuses Table
CREATE TABLE DairyStatuses (
    StatusCode NVARCHAR(20) PRIMARY KEY,
    StatusName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(200)
);

-- Schedule A Groups Table
CREATE TABLE ScheduleAGroups (
    GroupNumber INT PRIMARY KEY,
    GroupName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    SymbolRequired BIT NOT NULL DEFAULT 0
);

-- Ingredient Statuses Table
CREATE TABLE IngredientStatuses (
    StatusCode NVARCHAR(50) PRIMARY KEY,
    StatusLabel NVARCHAR(100) NOT NULL,
    ColorCode NVARCHAR(20),
    IsApproved BIT NOT NULL DEFAULT 0
);

-- User Roles Table
CREATE TABLE UserRoles (
    RoleId INT IDENTITY(1,1) PRIMARY KEY,
    RoleName NVARCHAR(50) NOT NULL UNIQUE,
    Permissions NVARCHAR(MAX) NOT NULL, -- JSON array of permissions
    Description NVARCHAR(500),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- =============================================
-- STAFF AND USERS
-- =============================================

-- Staff Table (OU Personnel)
CREATE TABLE Staff (
    StaffId INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeCode NVARCHAR(50) UNIQUE NOT NULL,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    FullName AS (FirstName + ' ' + LastName) PERSISTED,
    Department NVARCHAR(100) NOT NULL,
    Title NVARCHAR(100),
    Email NVARCHAR(255),
    Phone NVARCHAR(50),
    Specialty NVARCHAR(200),
    WorkloadLevel NVARCHAR(20), -- Light, Medium, Heavy
    RegionID INT,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RegionID) REFERENCES Regions(RegionID)
);

-- Users Table (External/Company Users)
CREATE TABLE Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL UNIQUE,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Role NVARCHAR(50) NOT NULL CHECK (Role IN ('admin', 'dispatcher', 'rfr', 'ncrc', 'company')),
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- =============================================
-- RFR PROFILES AND SPECIALTIES
-- =============================================

-- RFR Profiles Table
CREATE TABLE RFRProfiles (
    RFRID INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeID NVARCHAR(20) NOT NULL UNIQUE,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Phone NVARCHAR(20),
    RegionID INT NOT NULL,
    CurrentLocation NVARCHAR(100),
    YearsExperience INT,
    IsActive BIT NOT NULL DEFAULT 1,
    HomeBaseAddress NVARCHAR(255),
    HomeBaseLat DECIMAL(10,8),
    HomeBaseLng DECIMAL(11,8),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RegionID) REFERENCES Regions(RegionID)
);

-- RFR Specialties Table
CREATE TABLE RFRSpecialties (
    SpecialtyID INT IDENTITY(1,1) PRIMARY KEY,
    RFRID INT NOT NULL,
    SpecialtyName NVARCHAR(100) NOT NULL,
    YearsExperience INT DEFAULT 0,
    CertificationDate DATE,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RFRID) REFERENCES RFRProfiles(RFRID)
);

-- RFR Certifications Table
CREATE TABLE RFRCertifications (
    CertificationID INT IDENTITY(1,1) PRIMARY KEY,
    RFRID INT NOT NULL,
    CertificationName NVARCHAR(100) NOT NULL,
    IssuingBody NVARCHAR(100),
    IssueDate DATE,
    ExpiryDate DATE,
    CertificationNumber NVARCHAR(50),
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RFRID) REFERENCES RFRProfiles(RFRID)
);

-- RFR Availability Table
CREATE TABLE RFRAvailability (
    AvailabilityID INT IDENTITY(1,1) PRIMARY KEY,
    RFRID INT NOT NULL,
    AvailabilityType NVARCHAR(20) NOT NULL,
    Location NVARCHAR(100),
    Address NVARCHAR(255),
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Notes NTEXT,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RFRID) REFERENCES RFRProfiles(RFRID),
    CHECK (AvailabilityType IN ('available', 'unavailable'))
);

-- RFR Preferred Days Table
CREATE TABLE RFRPreferredDays (
    RFRID INT NOT NULL,
    DayOfWeek NVARCHAR(10) NOT NULL,
    IsPreferred BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    PRIMARY KEY (RFRID, DayOfWeek),
    FOREIGN KEY (RFRID) REFERENCES RFRProfiles(RFRID),
    CHECK (DayOfWeek IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
);

-- =============================================
-- NCRC PROFILES
-- =============================================

-- NCRCs Table
CREATE TABLE NCRCs (
    NCRCID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Phone NVARCHAR(20),
    RegionID INT NOT NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RegionID) REFERENCES Regions(RegionID)
);

-- NCRC Specialties Table
CREATE TABLE NCRCSpecialties (
    NCRCID INT NOT NULL,
    SpecialtyName NVARCHAR(100) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    PRIMARY KEY (NCRCID, SpecialtyName),
    FOREIGN KEY (NCRCID) REFERENCES NCRCs(NCRCID)
);

-- =============================================
-- COMPANIES AND FACILITIES
-- =============================================

-- Companies Table
CREATE TABLE Companies (
    CompanyID INT IDENTITY(1,1) PRIMARY KEY,
    KashrusCompanyId NVARCHAR(50) NOT NULL UNIQUE,
    CompanyName NVARCHAR(200) NOT NULL,
    Category NVARCHAR(100),
    CurrentlyCertified BIT NOT NULL DEFAULT 0,
    EverCertified BIT NOT NULL DEFAULT 0,
    Website NVARCHAR(255),
    AddressStreet NVARCHAR(255),
    AddressLine2 NVARCHAR(255),
    AddressCity NVARCHAR(100),
    AddressState NVARCHAR(50),
    AddressCountry NVARCHAR(50) DEFAULT 'USA',
    AddressZip NVARCHAR(20),
    ContactName NVARCHAR(100),
    ContactPhone NVARCHAR(20),
    ContactEmail NVARCHAR(100),
    KashrusStatus NVARCHAR(100) NOT NULL DEFAULT 'Pending',
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Facilities Table
CREATE TABLE Facilities (
    FacilityID INT IDENTITY(1,1) PRIMARY KEY,
    CompanyID INT NOT NULL,
    NCRCPlantId NVARCHAR(50) UNIQUE,
    FacilityName NVARCHAR(200) NOT NULL,
    FacilityType NVARCHAR(100) NOT NULL,
    Address NVARCHAR(255) NOT NULL,
    AddressLine2 NVARCHAR(255),
    City NVARCHAR(100) NOT NULL,
    State NVARCHAR(50) NOT NULL,
    Country NVARCHAR(100) NOT NULL DEFAULT 'USA',
    Province NVARCHAR(100),
    Region NVARCHAR(100),
    ZipCode NVARCHAR(10),
    Latitude DECIMAL(10,8),
    Longitude DECIMAL(11,8),
    SquareFootage INT,
    EmployeeCount INT,
    ShiftSchedule NVARCHAR(255),
    ContactName NVARCHAR(100),
    ContactTitle NVARCHAR(100),
    ContactPhone NVARCHAR(50),
    ContactEmail NVARCHAR(255),
    ManufacturingProcess NTEXT,
    ClosestMajorCity NVARCHAR(100),
    HasOtherProducts BIT NOT NULL DEFAULT 0,
    OtherProductsList NTEXT,
    HasOtherPlantsProducing BIT NOT NULL DEFAULT 0,
    OtherPlantsLocation NTEXT,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID)
);

-- =============================================
-- SUPPLIERS AND INGREDIENTS
-- =============================================

-- Suppliers Table
CREATE TABLE Suppliers (
    SupplierId INT IDENTITY(1,1) PRIMARY KEY,
    SupplierName NVARCHAR(200) NOT NULL,
    ContactEmail NVARCHAR(255),
    ContactPhone NVARCHAR(50),
    ContactInfo NVARCHAR(500),
    CertificationStatus NVARCHAR(50) NOT NULL DEFAULT 'Not Certified',
    OUCertificationNumber NVARCHAR(50),
    CertificationExpirationDate DATETIME2,
    IsApproved BIT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

-- Ingredients Master Table
CREATE TABLE Ingredients (
    IngredientId INT IDENTITY(1,1) PRIMARY KEY,
    IngredientName NVARCHAR(200) NOT NULL,
    CategoryId NVARCHAR(50) NOT NULL,
    Subcategory NVARCHAR(100),
    SupplierId INT NOT NULL,
    DairyStatusCode NVARCHAR(20) NOT NULL DEFAULT 'PAREVE',
    GroupDesignation INT NOT NULL CHECK (GroupDesignation IN (1, 2, 3, 4, 5, 6)),
    SymbolRequired BIT NOT NULL DEFAULT 0,
    OUCertificationNumber NVARCHAR(50),
    CertificationExpirationDate DATETIME2,
    KosherCertification NVARCHAR(50),
    KosherForPassover BIT NOT NULL DEFAULT 0,
    Organic BIT NOT NULL DEFAULT 0,
    GlutenFree BIT NOT NULL DEFAULT 0,
    LotTracking BIT NOT NULL DEFAULT 0,
    Notes NTEXT,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (CategoryId) REFERENCES IngredientCategories(CategoryId),
    FOREIGN KEY (SupplierId) REFERENCES Suppliers(SupplierId),
    FOREIGN KEY (DairyStatusCode) REFERENCES DairyStatuses(StatusCode)
);

-- =============================================
-- APPLICATIONS
-- =============================================

-- Applications Table
CREATE TABLE Applications (
    ApplicationId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationNumber NVARCHAR(50) NOT NULL UNIQUE,
    ApplicationCode NVARCHAR(50) UNIQUE,
    CompanyID INT NOT NULL,
    FacilityID INT,
    ApplicationType NVARCHAR(50) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'submitted',
    StatusCode NVARCHAR(50),
    RegionCode NVARCHAR(20),
    PriorityCode NVARCHAR(20),
    AssignedRCId INT,
    ReviewerID INT,
    SubmissionDate DATE NOT NULL,
    ApplicationDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    PrimaryContactName NVARCHAR(100),
    OwnBrand BIT NOT NULL DEFAULT 0,
    CopackerDirectory BIT NOT NULL DEFAULT 0,
    VeganCertification BIT NOT NULL DEFAULT 0,
    PlantCount INT NOT NULL DEFAULT 1,
    SpecialRequirements NTEXT,
    DaysInStage INT NOT NULL DEFAULT 0,
    IsOverdue BIT NOT NULL DEFAULT 0,
    LastUpdate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    NextAction NVARCHAR(1000),
    DocumentCount INT NOT NULL DEFAULT 0,
    NotesCount INT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CreatedBy INT,
    UpdatedBy INT,
    FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID),
    FOREIGN KEY (FacilityID) REFERENCES Facilities(FacilityID),
    FOREIGN KEY (AssignedRCId) REFERENCES Staff(StaffId),
    FOREIGN KEY (ReviewerID) REFERENCES Staff(StaffId),
    FOREIGN KEY (CreatedBy) REFERENCES Users(UserId),
    FOREIGN KEY (UpdatedBy) REFERENCES Users(UserId),
    FOREIGN KEY (RegionCode) REFERENCES Regions(RegionCode),
    FOREIGN KEY (PriorityCode) REFERENCES Priorities(PriorityCode),
    FOREIGN KEY (StatusCode) REFERENCES ApplicationStatuses(StatusCode),
    CHECK (ApplicationType IN ('New Certification', 'Renewal', 'Modification', 'Re-inspection')),
    CHECK (Status IN ('incomplete', 'complete', 'dispatched', 'under_review', 'approved', 'rejected', 'submitted', 'pending_information'))
);

-- Application Contacts Table
CREATE TABLE ApplicationContacts (
    ContactId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    ContactType NVARCHAR(100) NOT NULL,
    ContactName NVARCHAR(255) NOT NULL,
    ContactRole NVARCHAR(100),
    Email NVARCHAR(255),
    Phone NVARCHAR(50),
    Title NVARCHAR(100),
    IsPrimary BIT NOT NULL DEFAULT 0,
    IsDesignated BIT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE
);

-- Application Prerequisites Table
CREATE TABLE ApplicationPrerequisites (
    PrerequisiteId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    PrerequisiteType NVARCHAR(50) NOT NULL, -- inspection, ingredients, products
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    CompletedDate DATETIME2,
    Reviewer NVARCHAR(100),
    Notes NVARCHAR(1000),
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId)
);

-- Application Stages (workflow progress)
CREATE TABLE ApplicationStages (
    StageId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    StageCode NVARCHAR(50) NOT NULL,
    Status NVARCHAR(50) NOT NULL, -- completed, in_progress, overdue, blocked, not_started
    Progress INT NOT NULL DEFAULT 0, -- 0-100
    CompletedDate DATETIME2 NULL,
    StartedDate DATETIME2 NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (StageCode) REFERENCES WorkflowStages(StageCode),
    CONSTRAINT CK_ApplicationStages_Progress CHECK (Progress >= 0 AND Progress <= 100),
    CONSTRAINT UQ_ApplicationStages_AppStage UNIQUE (ApplicationId, StageCode)
);

-- Application Products Table
CREATE TABLE ApplicationProducts (
    ProductId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    Source NVARCHAR(100) NOT NULL,
    ProductName NVARCHAR(200) NOT NULL,
    LabelName NVARCHAR(255) NOT NULL,
    BrandName NVARCHAR(255),
    LabelCompany NVARCHAR(255),
    Category NVARCHAR(100),
    Volume NVARCHAR(100),
    ConsumerIndustrial NCHAR(1) CHECK (ConsumerIndustrial IN ('C', 'I')),
    BulkShipped NCHAR(1) CHECK (BulkShipped IN ('Y', 'N')),
    CertificationSymbol NVARCHAR(50),
    Description NTEXT,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE
);

-- Application Ingredients Table
CREATE TABLE ApplicationIngredients (
    ApplicationIngredientId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    IngredientId INT,
    NCRCIngredientId NVARCHAR(50) UNIQUE,
    Source NVARCHAR(100) NOT NULL,
    UKDId NVARCHAR(100),
    RMC NVARCHAR(100),
    IngredientName NVARCHAR(255) NOT NULL,
    Manufacturer NVARCHAR(255) NOT NULL,
    Brand NVARCHAR(255),
    Packaging NVARCHAR(100),
    Supplier NVARCHAR(200),
    CategoryCode NVARCHAR(50),
    DairyStatusCode NVARCHAR(20),
    GroupDesignation INT,
    StatusCode NVARCHAR(50) NOT NULL DEFAULT 'pending_review',
    ScheduleStatus NVARCHAR(50) NOT NULL DEFAULT 'Pending Review',
    AssignedToId INT NULL,
    CertificationAgency NVARCHAR(50),
    KosherCertification NVARCHAR(50),
    LotTracking BIT NOT NULL DEFAULT 0,
    LastUpdated DATETIME2 NOT NULL DEFAULT GETDATE(),
    CommunicationCount INT NOT NULL DEFAULT 0,
    Notes NTEXT,
    IssueType NVARCHAR(255),
    DaysActive INT NOT NULL DEFAULT 0,
    SpecificRequirements NVARCHAR(1000),
    Status NVARCHAR(50) NOT NULL DEFAULT 'Original' CHECK (Status IN ('Original', 'Recent', 'Updated', 'Deleted')),
    AddedBy NVARCHAR(100),
    ApprovedBy NVARCHAR(100),
    ApprovedDate DATETIME2,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (IngredientId) REFERENCES Ingredients(IngredientId),
    FOREIGN KEY (CategoryCode) REFERENCES IngredientCategories(CategoryId),
    FOREIGN KEY (DairyStatusCode) REFERENCES DairyStatuses(StatusCode),
    FOREIGN KEY (StatusCode) REFERENCES IngredientStatuses(StatusCode),
    FOREIGN KEY (AssignedToId) REFERENCES Staff(StaffId),
    CHECK (StatusCode IN ('approved', 'pending_review', 'requires_clarification', 'rejected'))
);

-- Equipment Table
CREATE TABLE Equipment (
    EquipmentID INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationID INT NOT NULL,
    EquipmentType NVARCHAR(100) NOT NULL,
    Brand NVARCHAR(100),
    Model NVARCHAR(100),
    Capacity NVARCHAR(100),
    SerialNumber NVARCHAR(100),
    InstallationDate DATE,
    LastMaintenanceDate DATE,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationID) REFERENCES Applications(ApplicationId)
);

-- Application Quotes Table
CREATE TABLE ApplicationQuotes (
    QuoteId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    QuoteNumber NVARCHAR(50) NOT NULL UNIQUE,
    TotalAmount DECIMAL(10,2) NOT NULL,
    CurrencyCode NCHAR(3) NOT NULL DEFAULT 'USD',
    ValidUntil DATE NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending_acceptance' CHECK (Status IN ('pending_acceptance', 'accepted', 'rejected', 'expired')),
    IsVerified BIT NOT NULL DEFAULT 0,
    VerifiedBy INT,
    VerifiedAt DATETIME2,
    Notes NVARCHAR(MAX),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (VerifiedBy) REFERENCES Users(UserId)
);

-- Quote Items Table
CREATE TABLE QuoteItems (
    QuoteItemId INT IDENTITY(1,1) PRIMARY KEY,
    QuoteId INT NOT NULL,
    ItemDescription NVARCHAR(500) NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    SortOrder INT NOT NULL DEFAULT 0,
    FOREIGN KEY (QuoteId) REFERENCES ApplicationQuotes(QuoteId) ON DELETE CASCADE
);

-- Application Validation Table
CREATE TABLE ApplicationValidation (
    ValidationId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    ValidationCategory NVARCHAR(100) NOT NULL,
    IsValid BIT NOT NULL DEFAULT 0,
    ValidationMessage NVARCHAR(500),
    LastCheckedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CheckedBy INT,
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (CheckedBy) REFERENCES Users(UserId),
    UNIQUE(ApplicationId, ValidationCategory)
);

-- Application Files Table
CREATE TABLE ApplicationFiles (
    FileId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    FileName NVARCHAR(255) NOT NULL,
    FileType NVARCHAR(100) NOT NULL,
    FileSize NVARCHAR(50),
    Tag NVARCHAR(100),
    IsProcessed BIT NOT NULL DEFAULT 0,
    RecordCount INT,
    FilePath NVARCHAR(500),
    UploadedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UploadedBy INT,
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (UploadedBy) REFERENCES Users(UserId)
);

-- Application AI Suggestions Table
CREATE TABLE ApplicationAISuggestions (
    SuggestionId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    TodoItems NVARCHAR(MAX), -- JSON array of todo items
    EmailSuggestion NVARCHAR(1000),
    CriticalPath NVARCHAR(1000),
    GeneratedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    IsActive BIT NOT NULL DEFAULT 1,
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE
);

-- =============================================
-- INSPECTION MANAGEMENT
-- =============================================

-- Inspection Requests Table
CREATE TABLE InspectionRequests (
    RequestID INT IDENTITY(1,1) PRIMARY KEY,
    RequestNumber NVARCHAR(20) NOT NULL UNIQUE,
    ApplicationID INT NOT NULL,
    RFRID INT,
    NCRCID INT NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending_response',
    Priority NVARCHAR(20) NOT NULL DEFAULT 'medium',
    RequestedStartDate DATE NOT NULL,
    RequestedEndDate DATE NOT NULL,
    ScheduledDate DATE,
    ScheduledStartTime TIME,
    ScheduledEndTime TIME,
    CompletedDate DATE,
    EstimatedDuration NVARCHAR(50),
    ActualDuration NVARCHAR(50),
    DistanceFromRFR NVARCHAR(20),
    WhySelected NTEXT,
    InspectionResult NVARCHAR(100),
    ReportSubmittedDate DATE,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationID) REFERENCES Applications(ApplicationId),
    FOREIGN KEY (RFRID) REFERENCES RFRProfiles(RFRID),
    FOREIGN KEY (NCRCID) REFERENCES NCRCs(NCRCID),
    CHECK (Status IN ('pending_response', 'scheduled', 'completed', 'declined', 'info_requested', 'pending_conditions')),
    CHECK (Priority IN ('low', 'medium', 'high', 'urgent'))
);

-- Inspection Issues Table
CREATE TABLE InspectionIssues (
    IssueID INT IDENTITY(1,1) PRIMARY KEY,
    RequestID INT NOT NULL,
    IssueDescription NTEXT NOT NULL,
    Severity NVARCHAR(20) NOT NULL DEFAULT 'minor',
    Status NVARCHAR(50) NOT NULL DEFAULT 'open',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    ResolvedAt DATETIME2,
    FOREIGN KEY (RequestID) REFERENCES InspectionRequests(RequestID),
    CHECK (Severity IN ('minor', 'major', 'critical')),
    CHECK (Status IN ('open', 'in_progress', 'resolved', 'deferred'))
);

-- Inspection Recommendations Table
CREATE TABLE InspectionRecommendations (
    RecommendationID INT IDENTITY(1,1) PRIMARY KEY,
    RequestID INT NOT NULL,
    RecommendationText NTEXT NOT NULL,
    Priority NVARCHAR(20) NOT NULL DEFAULT 'medium',
    ImplementationDeadline DATE,
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (RequestID) REFERENCES InspectionRequests(RequestID),
    CHECK (Priority IN ('low', 'medium', 'high')),
    CHECK (Status IN ('pending', 'in_progress', 'completed', 'not_applicable'))
);

-- =============================================
-- CONTRACT MANAGEMENT
-- =============================================

-- Contracts Table
CREATE TABLE Contracts (
    ContractId NVARCHAR(50) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    ContractTypeId NVARCHAR(50) NOT NULL,
    EffectiveDate DATETIME2 NOT NULL,
    ExpirationDate DATETIME2 NOT NULL,
    ContractDuration INT NOT NULL, -- in months
    Status NVARCHAR(50) NOT NULL DEFAULT 'draft',
    AnnualFee DECIMAL(10,2) NOT NULL,
    Currency NVARCHAR(3) NOT NULL DEFAULT 'USD',
    PaymentTerms NVARCHAR(50) NOT NULL DEFAULT 'Net 30',
    InvoicingSchedule NVARCHAR(50) NOT NULL DEFAULT 'Annual',
    AdditionalRequirements NVARCHAR(2000),
    CreatedBy NVARCHAR(100) NOT NULL DEFAULT 'system',
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedBy NVARCHAR(100) NOT NULL DEFAULT 'system',
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId),
    FOREIGN KEY (ContractTypeId) REFERENCES ContractTypes(ContractTypeId)
);

-- Contract Ingredients Table
CREATE TABLE ContractIngredients (
    ContractIngredientId INT IDENTITY(1,1) PRIMARY KEY,
    ContractId NVARCHAR(50) NOT NULL,
    IngredientId INT NOT NULL,
    ScheduleType NVARCHAR(10) NOT NULL CHECK (ScheduleType IN ('A', 'B')),
    IncludeInContract BIT NOT NULL DEFAULT 1,
    Notes NVARCHAR(1000),
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ContractId) REFERENCES Contracts(ContractId),
    FOREIGN KEY (IngredientId) REFERENCES Ingredients(IngredientId)
);

-- Contract Approvals Table
CREATE TABLE ContractApprovals (
    ApprovalId INT IDENTITY(1,1) PRIMARY KEY,
    ContractId NVARCHAR(50) NOT NULL,
    ApprovalType NVARCHAR(50) NOT NULL, -- rc_approval, legal_approval
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    ApprovedBy NVARCHAR(100),
    ApprovedDate DATETIME2,
    Notes NVARCHAR(1000),
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ContractId) REFERENCES Contracts(ContractId)
);

-- Contract Revisions Table
CREATE TABLE ContractRevisions (
    RevisionId INT IDENTITY(1,1) PRIMARY KEY,
    ContractId NVARCHAR(50) NOT NULL,
    RevisionNumber INT NOT NULL,
    ChangeDescription NVARCHAR(2000) NOT NULL,
    RequestedBy NVARCHAR(100) NOT NULL,
    RequestedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ResolvedBy NVARCHAR(100),
    ResolvedDate DATETIME2,
    Status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (ContractId) REFERENCES Contracts(ContractId)
);

-- =============================================
-- DOCUSIGN INTEGRATION
-- =============================================

-- DocuSign Envelopes Table
CREATE TABLE DocuSignEnvelopes (
    EnvelopeId NVARCHAR(100) PRIMARY KEY,
    ContractId NVARCHAR(50) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'created',
    SentDate DATETIME2,
    CompletedDate DATETIME2,
    DocumentUrl NVARCHAR(500),
    EmbeddedUrl NVARCHAR(500),
    EmbeddedUrlExpires DATETIME2,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ContractId) REFERENCES Contracts(ContractId)
);

-- DocuSign Signers Table
CREATE TABLE DocuSignSigners (
    SignerId INT IDENTITY(1,1) PRIMARY KEY,
    EnvelopeId NVARCHAR(100) NOT NULL,
    SignerRole NVARCHAR(50) NOT NULL, -- company_representative, ou_representative
    SignerName NVARCHAR(100) NOT NULL,
    SignerEmail NVARCHAR(255) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'not_sent',
    SignedDate DATETIME2,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (EnvelopeId) REFERENCES DocuSignEnvelopes(EnvelopeId)
);

-- =============================================
-- TASKS AND COMMUNICATIONS
-- =============================================

-- Application Tasks Table
CREATE TABLE ApplicationTasks (
    TaskId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    StageCode NVARCHAR(50) NOT NULL,
    TaskCode NVARCHAR(100) NOT NULL, -- initial-1, nda-2, etc.
    TaskName NVARCHAR(255) NOT NULL,
    StatusCode NVARCHAR(50) NOT NULL,
    AssigneeId INT NULL,
    AssigneeName NVARCHAR(255), -- For cases where assignee is not in Staff table
    DaysActive INT NOT NULL DEFAULT 0,
    IsRequired BIT NOT NULL DEFAULT 1,
    CompletedDate DATETIME2 NULL,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (StageCode) REFERENCES WorkflowStages(StageCode),
    FOREIGN KEY (StatusCode) REFERENCES TaskStatuses(StatusCode),
    FOREIGN KEY (AssigneeId) REFERENCES Staff(StaffId),
    CONSTRAINT UQ_ApplicationTasks_AppTask UNIQUE (ApplicationId, TaskCode)
);

-- Standalone Tasks Table
CREATE TABLE Tasks (
    TaskId INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(255) NOT NULL,
    Plant NVARCHAR(255) NOT NULL,
    AssignedToId INT NOT NULL,
    AssignedById INT NOT NULL,
    StatusCode NVARCHAR(50) NOT NULL,
    PriorityCode NVARCHAR(20) NOT NULL,
    DaysActive INT NOT NULL DEFAULT 0,
    ApplicationCode NVARCHAR(50),
    WorkflowStageCode NVARCHAR(50),
    Description NVARCHAR(MAX),
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    LastUpdated DATETIME2 NOT NULL DEFAULT GETDATE(),
    CompletedDate DATETIME2 NULL,
    FOREIGN KEY (AssignedToId) REFERENCES Staff(StaffId),
    FOREIGN KEY (AssignedById) REFERENCES Staff(StaffId),
    FOREIGN KEY (StatusCode) REFERENCES TaskStatuses(StatusCode),
    FOREIGN KEY (PriorityCode) REFERENCES Priorities(PriorityCode),
    FOREIGN KEY (WorkflowStageCode) REFERENCES WorkflowStages(StageCode)
);

-- Messages Table
CREATE TABLE Messages (
    MessageID INT IDENTITY(1,1) PRIMARY KEY,
    RequestID INT,
    ApplicationId INT,
    SenderType NVARCHAR(20) NOT NULL,
    SenderID INT NOT NULL,
    SenderName NVARCHAR(100) NOT NULL,
    FromUser NVARCHAR(100) NOT NULL,
    ToUser NVARCHAR(100) NOT NULL,
    MessageText NTEXT NOT NULL,
    MessageType NVARCHAR(50) NOT NULL DEFAULT 'outgoing' CHECK (MessageType IN ('outgoing', 'incoming')),
    IsRead BIT NOT NULL DEFAULT 0,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    ReadAt DATETIME2,
    FOREIGN KEY (RequestID) REFERENCES InspectionRequests(RequestID),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    CHECK (SenderType IN ('RFR', 'NCRC', 'SYSTEM', 'USER'))
);

-- Task Messages Table
CREATE TABLE TaskMessages (
    MessageId INT IDENTITY(1,1) PRIMARY KEY,
    TaskId INT NOT NULL,
    SenderId INT NULL,
    SenderName NVARCHAR(255) NOT NULL, -- For system messages
    MessageText NVARCHAR(MAX) NOT NULL,
    IsSystemMessage BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (TaskId) REFERENCES Tasks(TaskId) ON DELETE CASCADE,
    FOREIGN KEY (SenderId) REFERENCES Staff(StaffId)
);

-- Application Comments Table
CREATE TABLE ApplicationComments (
    CommentId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    Author NVARCHAR(100) NOT NULL,
    CommentText NVARCHAR(MAX) NOT NULL,
    CommentType NVARCHAR(50) NOT NULL DEFAULT 'internal' CHECK (CommentType IN ('internal', 'external')),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE
);

-- Application Activity Log Table
CREATE TABLE ApplicationActivity (
    ActivityId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    Action NVARCHAR(255) NOT NULL,
    Details NVARCHAR(MAX),
    ActivityType NVARCHAR(100) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'approved' CHECK (Status IN ('approved', 'pending', 'rejected')),
    UserId INT,
    UserDisplayName NVARCHAR(100),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId) ON DELETE CASCADE,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

-- =============================================
-- AUDIT AND HISTORY TABLES
-- =============================================

-- Application Audit Trail Table
CREATE TABLE ApplicationAudit (
    AuditId INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationId INT NOT NULL,
    Action NVARCHAR(100) NOT NULL, -- INSERT, UPDATE, DELETE, STATUS_CHANGE, etc.
    OldValues NVARCHAR(MAX), -- JSON
    NewValues NVARCHAR(MAX), -- JSON
    ChangedById INT,
    ChangedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ApplicationId) REFERENCES Applications(ApplicationId),
    FOREIGN KEY (ChangedById) REFERENCES Staff(StaffId)
);

-- Task Audit Trail Table
CREATE TABLE TaskAudit (
    AuditId INT IDENTITY(1,1) PRIMARY KEY,
    TaskId INT NOT NULL,
    Action NVARCHAR(100) NOT NULL,
    OldValues NVARCHAR(MAX), -- JSON
    NewValues NVARCHAR(MAX), -- JSON
    ChangedById INT,
    ChangedDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (TaskId) REFERENCES Tasks(TaskId),
    FOREIGN KEY (ChangedById) REFERENCES Staff(StaffId)
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Applications indexes
CREATE INDEX IX_Applications_CompanyID ON Applications(CompanyID);
CREATE INDEX IX_Applications_Status ON Applications(Status);
CREATE INDEX IX_Applications_StatusCode ON Applications(StatusCode);
CREATE INDEX IX_Applications_Priority ON Applications(PriorityCode);
CREATE INDEX IX_Applications_AssignedRC ON Applications(AssignedRCId);
CREATE INDEX IX_Applications_LastUpdate ON Applications(LastUpdate);
CREATE INDEX IX_Applications_SubmissionDate ON Applications(SubmissionDate);
CREATE INDEX IX_Applications_RegionCode ON Applications(RegionCode);

-- Application stages indexes
CREATE INDEX IX_ApplicationStages_Status ON ApplicationStages(Status);
CREATE INDEX IX_ApplicationStages_Progress ON ApplicationStages(Progress);

-- Inspection requests indexes
CREATE INDEX IX_InspectionRequests_Status ON InspectionRequests(Status);
CREATE INDEX IX_InspectionRequests_RFRID ON InspectionRequests(RFRID);
CREATE INDEX IX_InspectionRequests_NCRCID ON InspectionRequests(NCRCID);
CREATE INDEX IX_InspectionRequests_Priority ON InspectionRequests(Priority);
CREATE INDEX IX_InspectionRequests_RequestedStartDate ON InspectionRequests(RequestedStartDate);

-- Messages indexes
CREATE INDEX IX_Messages_RequestID_CreatedAt ON Messages(RequestID, CreatedAt);
CREATE INDEX IX_Messages_ApplicationId ON Messages(ApplicationId);
CREATE INDEX IX_Messages_IsRead ON Messages(IsRead);

-- RFR Availability indexes
CREATE INDEX IX_RFRAvailability_RFRID_Dates ON RFRAvailability(RFRID, StartDate, EndDate);

-- Tasks indexes
CREATE INDEX IX_Tasks_AssignedTo ON Tasks(AssignedToId);
CREATE INDEX IX_Tasks_Status ON Tasks(StatusCode);
CREATE INDEX IX_Tasks_Priority ON Tasks(PriorityCode);
CREATE INDEX IX_Tasks_Plant ON Tasks(Plant);
CREATE INDEX IX_Tasks_CreatedDate ON Tasks(CreatedDate);

-- Application tasks indexes
CREATE INDEX IX_ApplicationTasks_Status ON ApplicationTasks(StatusCode);
CREATE INDEX IX_ApplicationTasks_Assignee ON ApplicationTasks(AssigneeId);
CREATE INDEX IX_ApplicationTasks_Stage ON ApplicationTasks(StageCode);

-- Ingredients indexes
CREATE INDEX IX_ApplicationIngredients_ApplicationId ON ApplicationIngredients(ApplicationId);
CREATE INDEX IX_ApplicationIngredients_Status ON ApplicationIngredients(StatusCode);
CREATE INDEX IX_ApplicationIngredients_AssignedTo ON ApplicationIngredients(AssignedToId);
CREATE INDEX IX_Ingredients_CategoryId ON Ingredients(CategoryId);
CREATE INDEX IX_Ingredients_SupplierId ON Ingredients(SupplierId);
CREATE INDEX IX_Ingredients_GroupDesignation ON Ingredients(GroupDesignation);

-- Contracts indexes
CREATE INDEX IX_Contracts_ApplicationId ON Contracts(ApplicationId);
CREATE INDEX IX_Contracts_Status ON Contracts(Status);
CREATE INDEX IX_Contracts_EffectiveDate ON Contracts(EffectiveDate);

-- Contract Ingredients indexes
CREATE INDEX IX_ContractIngredients_ContractId ON ContractIngredients(ContractId);
CREATE INDEX IX_ContractIngredients_ScheduleType ON ContractIngredients(ScheduleType);

-- Companies and Facilities indexes
CREATE INDEX IX_Companies_KashrusCompanyId ON Companies(KashrusCompanyId);
CREATE INDEX IX_Companies_CompanyName ON Companies(CompanyName);
CREATE INDEX IX_Facilities_CompanyID ON Facilities(CompanyID);
CREATE INDEX IX_Facilities_NCRCPlantId ON Facilities(NCRCPlantId);

-- Activity and audit indexes
CREATE INDEX IX_ApplicationActivity_ApplicationId ON ApplicationActivity(ApplicationId);
CREATE INDEX IX_ApplicationActivity_CreatedAt ON ApplicationActivity(CreatedAt);
CREATE INDEX IX_ApplicationValidation_ApplicationId ON ApplicationValidation(ApplicationId);

-- =============================================
-- INSERT REFERENCE DATA
-- =============================================
