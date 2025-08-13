-- =============================================
-- OU Kashrus Management System - Unified Database Schema
-- MS SQL Server DDL with Comprehensive Mock Data
-- Combines: RFR Dashboard, NCRC Dashboard, Contract Management, and Application Management
-- =============================================

-- Create Database

USE OUKashrusSystem;
GO


-- =============================================
-- INSERT REFERENCE DATA
-- =============================================

-- Insert Regions
INSERT INTO Regions (RegionCode, RegionName, CountryCode, Description) VALUES
('NE', 'Northeast Region', 'US', 'Covering NY, NJ, CT, MA, PA'),
('SE', 'Southeast Region', 'US', 'Covering FL, GA, SC, NC, VA'),
('MW', 'Midwest Region', 'US', 'Covering IL, IN, OH, MI, WI'),
('WE', 'West Region', 'US', 'Covering CA, WA, OR, NV, AZ'),
('NY_METRO', 'NY Metro', 'US', 'New York Metropolitan Area'),
('WEST_COAST', 'West Coast', 'US', 'Pacific Coast States'),
('SOUTHEAST', 'Southeast', 'US', 'Southeastern States'),
('INTERNATIONAL', 'International', 'INTL', 'International Markets');

-- Insert Priorities
INSERT INTO Priorities (PriorityCode, PriorityLabel, SortOrder, ColorCode) VALUES
('urgent', 'Urgent', 1, '#ef4444'),
('high', 'High', 2, '#f97316'),
('medium', 'Medium', 3, '#3b82f6'),
('low', 'Low', 4, '#6b7280');

-- Insert Application Statuses
INSERT INTO ApplicationStatuses (StatusCode, StatusLabel, StatusDescription, SortOrder) VALUES
('incomplete', 'Incomplete', 'Application is incomplete and requires additional information', 1),
('complete', 'Complete', 'Application is complete and ready for review', 2),
('submitted', 'Submitted', 'Application has been submitted for review', 3),
('under_review', 'Under Review', 'Application is currently under review', 4),
('dispatched', 'Dispatched', 'Application has been dispatched to field personnel', 5),
('contract_sent', 'Contract Sent', 'Certification contract has been sent to the company', 6),
('inspection_scheduled', 'Inspection Scheduled', 'Inspection has been scheduled', 7),
('payment_pending', 'Payment Pending', 'Waiting for payment from company', 8),
('approved', 'Approved', 'Application has been approved', 9),
('certified', 'Certified', 'Company has been certified', 10),
('rejected', 'Rejected', 'Application has been rejected', 11),
('pending_information', 'Pending Information', 'Waiting for additional information from applicant', 12);

-- Insert Workflow Stages
INSERT INTO WorkflowStages (StageCode, StageName, StageDescription, SortOrder) VALUES
('initial', 'Initial', 'Initial application processing', 1),
('nda', 'NDA', 'Non-disclosure agreement processing', 2),
('inspection', 'Inspection', 'Facility inspection process', 3),
('ingredients', 'Ingredients', 'Ingredient approval review', 4),
('products', 'Products', 'Product review and approval', 5),
('contract', 'Contract', 'Contract finalization', 6),
('certification', 'Certification', 'Final certification', 7);

-- Insert Task Statuses
INSERT INTO TaskStatuses (StatusCode, StatusLabel, ColorCode) VALUES
('new', 'New', '#3b82f6'),
('in_progress', 'In Progress', '#f59e0b'),
('overdue', 'Overdue', '#ef4444'),
('completed', 'Completed', '#10b981'),
('blocked', 'Blocked', '#6b7280'),
('pending', 'Pending', '#8b5cf6');

-- Insert Contract Types
INSERT INTO ContractTypes (ContractTypeId, Label, Description, DefaultDuration, RequiresLegalReview) VALUES
('new_company', 'New Company Certification', 'First-time certification for a new company', 12, 0),
('plant_addendum', 'Plant Addendum (Existing Company)', 'Additional plant for existing certified company', 12, 0),
('pla', 'PLA (Private Label Agreement)', 'Private label manufacturing agreement', 24, 1),
('renewal', 'Contract Renewal', 'Renewal of existing certification contract', 12, 0);

-- Insert Ingredient Categories
INSERT INTO IngredientCategories (CategoryId, CategoryName, Description) VALUES
('BASE_INGREDIENTS', 'Base Ingredients', 'Primary ingredients used in food production'),
('SWEETENERS', 'Sweeteners', 'Sugar, syrups, and alternative sweeteners'),
('FLAVORING', 'Flavoring', 'Natural and artificial flavoring agents'),
('PRESERVATIVES', 'Preservatives', 'Food preservation agents'),
('EMULSIFIERS', 'Emulsifiers', 'Lecithin and other emulsifying agents'),
('HERBS_SPICES', 'Herbs & Spices', 'Fresh and dried herbs and spices'),
('FRUIT_PRODUCTS', 'Fruit Products', 'Fruit-based ingredients and extracts'),
('LEAVENING_AGENTS', 'Leavening Agents', 'Baking powders and yeasts'),
('GRAINS', 'Grains', 'Wheat, rice, corn and other grain products'),
('SEASONINGS', 'Seasonings', 'Salt, pepper, and seasoning blends');

-- Insert Dairy Statuses
INSERT INTO DairyStatuses (StatusCode, StatusName, Description) VALUES
('PAREVE', 'Pareve', 'Neither dairy nor meat'),
('DAIRY', 'Dairy', 'Contains dairy ingredients'),
('MEAT', 'Meat', 'Contains meat ingredients');

-- Insert Schedule A Groups
INSERT INTO ScheduleAGroups (GroupNumber, GroupName, Description, SymbolRequired) VALUES
(1, 'Group 1 (No Symbol)', 'Ingredients that do not require OU symbol', 0),
(2, 'Group 2 (Internal/Confidential)', 'Internal use ingredients', 0),
(3, 'Group 3 (OU Symbol Required)', 'Ingredients requiring OU symbol', 1),
(4, 'Group 4 (Bulk/Special)', 'Bulk or special handling ingredients', 1),
(5, 'Group 5 (Specialized)', 'Specialized ingredients', 1),
(6, 'Group 6 (Restricted)', 'Restricted ingredients', 1);

-- Insert Ingredient Statuses
INSERT INTO IngredientStatuses (StatusCode, StatusLabel, ColorCode, IsApproved) VALUES
('approved', 'Approved', '#10b981', 1),
('pending_review', 'Pending Review', '#f59e0b', 0),
('pending_schedule_approval', 'Pending Schedule A', '#f59e0b', 0),
('supplier_not_approved', 'Supplier Not Approved', '#ef4444', 0),
('name_verification', 'Name Verification', '#3b82f6', 0),
('requires_inspection', 'Requires Inspection', '#8b5cf6', 0),
('requires_clarification', 'Requires Clarification', '#f97316', 0),
('missing_kosher_code', 'Missing Kosher Code', '#f97316', 0),
('rejected', 'Rejected', '#ef4444', 0);

-- Insert User Roles
INSERT INTO UserRoles (RoleName, Permissions, Description) VALUES
('admin', '["view_all", "edit_all", "complete_application", "dispatch_application", "manage_validation", "send_messages", "add_comments"]', 'Full system administrator access'),
('dispatcher', '["view_dispatched", "edit_limited", "receive_messages", "add_comments"]', 'Dispatcher with limited editing rights'),
('rfr', '["view_assigned", "edit_ingredients", "edit_products", "add_comments"]', 'RFR with ingredient and product editing'),
('ncrc', '["view_all", "edit_ingredients", "validate_data", "add_comments"]', 'NCRC with validation and ingredient editing'),
('company', '["view_own", "edit_own", "submit_application", "send_messages"]', 'Company user with limited access');

-- =============================================
-- INSERT MOCK DATA
-- =============================================

-- Insert Staff Members
INSERT INTO Staff (EmployeeCode, FirstName, LastName, Department, Email, Phone, Specialty, WorkloadLevel, RegionID) VALUES
('a.gottesman', 'A.', 'Gottesman', 'Admin', 'agottesman@ou.org', '(212) 555-0150', 'General Administration', 'Medium', 1),
('r.gorelik', 'R.', 'Gorelik', 'NCRC', 'rgorelik@ou.org', '(212) 555-0151', 'Dairy Products', 'Light', 1),
('d.herbsman', 'David', 'Herbsman', 'IAR', 'dherbsman@ou.org', '(212) 555-0152', 'Ingredients Review', 'Medium', 1),
('r.epstein', 'R.', 'Epstein', 'NCRC', 'repstein@ou.org', '(212) 555-0153', 'General', 'Medium', 1),
('j.torres', 'Jennifer', 'Torres', 'RFR', 'jtorres@ou.org', '(212) 555-0154', 'Field Inspections', 'Light', 1),
('r.klein', 'R.', 'Klein', 'NCRC', 'rklein@ou.org', '(212) 555-0100', 'Bakery, Dairy', 'Medium', 1),
('r.goldstein', 'R.', 'Goldstein', 'NCRC', 'rgoldstein@ou.org', '(212) 555-0101', 'Food Processing, Distribution', 'Medium', 1),
('r.stern', 'R.', 'Stern', 'NCRC', 'rstern@ou.org', '(212) 555-0102', 'Vegetables, Emergency Inspections', 'Heavy', 1),
('r.weiss', 'R.', 'Weiss', 'NCRC', 'rweiss@ou.org', '(201) 555-0103', 'Meat Processing, Snack Foods', 'Medium', 1);

-- Insert Users
INSERT INTO Users (Username, Email, FirstName, LastName, Role) VALUES
('j.mitchell', 'john@happycowmills.com', 'John', 'Mitchell', 'company'),
('g.magder', 'gmagder@happycowmills.com', 'Gary', 'Magder', 'company'),
('system', 'system@ncrc.org', 'System', 'Import', 'admin'),
('auto-sync', 'autosync@ncrc.org', 'Auto', 'Sync', 'admin'),
('j.baker', 'john@brooklynbread.com', 'John', 'Baker', 'company'),
('s.johnson', 'sarah@metrofoods.com', 'Sarah', 'Johnson', 'company'),
('d.miller', 'david@artisanbaking.com', 'David', 'Miller', 'company');

-- Insert RFR Profiles
INSERT INTO RFRProfiles (EmployeeID, FirstName, LastName, Email, Phone, RegionID, CurrentLocation, YearsExperience, HomeBaseAddress, HomeBaseLat, HomeBaseLng) VALUES
('RFR-2025-001', 'R.', 'Stone', 'rstone@ou.org', '(212) 555-0123', 1, 'Manhattan, NY', 8, '123 Main St, Manhattan, NY 10001', 40.7589, -73.9851),
('RFR-2025-002', 'S.', 'Cohen', 'scohen@ou.org', '(201) 555-0124', 1, 'Newark, NJ', 5, '456 Oak Ave, Newark, NJ 07102', 40.7357, -74.1724),
('RFR-2025-003', 'M.', 'Rosen', 'mrosen@ou.org', '(718) 555-0125', 1, 'Brooklyn, NY', 12, '789 Elm St, Brooklyn, NY 11220', 40.6231, -74.0154);

-- Insert RFR Specialties
INSERT INTO RFRSpecialties (RFRID, SpecialtyName, YearsExperience, CertificationDate) VALUES
(1, 'Bakery', 8, '2017-03-15'),
(1, 'Food Processing', 6, '2019-06-20'),
(2, 'Distribution Center', 5, '2020-01-10'),
(2, 'Cold Storage', 3, '2022-04-05'),
(3, 'Dairy Processing', 12, '2013-08-30'),
(3, 'Meat Processing', 10, '2015-11-12');

-- Insert RFR Certifications
INSERT INTO RFRCertifications (RFRID, CertificationName, IssuingBody, IssueDate, ExpiryDate, CertificationNumber) VALUES
(1, 'Food Safety', 'FDA', '2023-01-15', '2026-01-15', 'FS-2023-001'),
(1, 'HACCP', 'NSF International', '2023-03-20', '2026-03-20', 'HACCP-2023-045'),
(1, 'Kosher Law', 'Orthodox Union', '2017-03-15', NULL, 'KL-2017-012'),
(2, 'Food Safety', 'FDA', '2022-11-10', '2025-11-10', 'FS-2022-089'),
(2, 'Cold Chain Management', 'IACET', '2023-02-28', '2026-02-28', 'CCM-2023-067'),
(3, 'Advanced HACCP', 'NSF International', '2023-05-15', '2026-05-15', 'AHACCP-2023-023'),
(3, 'Dairy Processing Specialist', 'ADPI', '2021-09-30', '2024-09-30', 'DPS-2021-156');

-- Insert NCRCs
INSERT INTO NCRCs (FirstName, LastName, Email, Phone, RegionID) VALUES
('R.', 'Klein', 'rklein@ou.org', '(212) 555-0100', 1),
('R.', 'Goldstein', 'rgoldstein@ou.org', '(212) 555-0101', 1),
('R.', 'Stern', 'rstern@ou.org', '(212) 555-0102', 1),
('R.', 'Weiss', 'rweiss@ou.org', '(201) 555-0103', 1);

-- Insert NCRC Specialties
INSERT INTO NCRCSpecialties (NCRCID, SpecialtyName) VALUES
(1, 'Bakery'), (1, 'Dairy'),
(2, 'Food Processing'), (2, 'Distribution'),
(3, 'Vegetables'), (3, 'Emergency Inspections'),
(4, 'Meat Processing'), (4, 'Snack Foods');

-- Insert Suppliers
INSERT INTO Suppliers (SupplierName, ContactEmail, ContactPhone, CertificationStatus, OUCertificationNumber, CertificationExpirationDate, IsApproved) VALUES
('King Arthur Flour Co.', 'kosher@kingarthurflour.com', '(802) 649-3881', 'OU Certified', 'OU-12345', '2026-12-31', 1),
('Cargill Inc.', 'kosher@cargill.com', '(952) 742-7575', 'OU Certified', 'OU-67890', '2026-08-15', 1),
('McCormick & Co.', 'kosher@mccormick.com', '(410) 771-7301', 'Pending Verification', 'OU-PENDING', NULL, 0),
('Jones Farms Organics', 'contact@jonesfarms.com', '(555) 123-4567', 'OU Certified', 'OU-11111', '2026-10-30', 1),
('ADM', 'kosher@adm.com', '(312) 634-8100', 'OU Certified', 'OU-22222', '2026-10-30', 1),
('Wholesome Sweeteners', 'kosher@wholesomesweeteners.com', '(281) 240-6306', 'OU Certified', 'OU-33333', '2027-01-15', 1),
('Celtic Sea Salt', 'kosher@celticseasalt.com', '(800) 867-7258', 'OU Certified', 'OU-44444', '2028-06-30', 1),
('Premium Flavor Co', 'kosher@premiumflavor.com', '(555) 987-6543', 'OU Certified', 'OU-55555', '2026-12-31', 1),
('Andean Grains Ltd', 'kosher@andeangrains.com', '(555) 555-0199', 'OU-P Certified', 'OUP-66666', '2027-03-15', 1),
('Tropical Oils Inc', 'kosher@tropicaloils.com', '(555) 444-3333', 'OU Certified', 'OU-77777', '2026-09-30', 1);

-- Insert Ingredients
INSERT INTO Ingredients (IngredientName, CategoryId, Subcategory, SupplierId, DairyStatusCode, GroupDesignation, SymbolRequired, OUCertificationNumber, CertificationExpirationDate, KosherForPassover, Organic, GlutenFree, LotTracking) VALUES
('Wheat Flour', 'GRAINS', 'Wheat Products', 1, 'PAREVE', 1, 0, 'OU-12345', '2026-12-31', 0, 0, 0, 1),
('High Fructose Corn Syrup', 'SWEETENERS', 'Corn Syrups', 2, 'PAREVE', 3, 1, 'OU-67890', '2026-08-15', 0, 0, 1, 1),
('Natural Vanilla Flavoring', 'FLAVORING', 'Natural Extracts', 8, 'PAREVE', 3, 1, 'OU-55555', '2026-12-31', 1, 1, 1, 1),
('Ryman Rye Grain', 'GRAINS', 'Rye Products', 4, 'PAREVE', 2, 0, 'OU-11111', '2026-10-30', 0, 1, 0, 1),
('Yecora Rojo Grain', 'GRAINS', 'Wheat Products', 4, 'PAREVE', 2, 0, 'OU-11111', '2026-10-30', 0, 1, 0, 1),
('Soy Lecithin', 'EMULSIFIERS', 'Soy Products', 5, 'PAREVE', 1, 0, 'OU-22222', '2026-10-30', 0, 0, 1, 1),
('Organic Sugar', 'SWEETENERS', 'Cane Sugar', 6, 'PAREVE', 1, 0, 'OU-33333', '2027-01-15', 1, 1, 1, 1),
('Sea Salt', 'SEASONINGS', 'Salt', 7, 'PAREVE', 2, 0, 'OU-44444', '2028-06-30', 1, 1, 1, 0),
('Organic Quinoa Flour', 'GRAINS', 'Alternative Grains', 9, 'PAREVE', 3, 1, 'OUP-66666', '2027-03-15', 1, 1, 1, 1),
('Coconut Oil (Refined)', 'EMULSIFIERS', 'Plant Oils', 10, 'PAREVE', 1, 0, 'OU-77777', '2026-09-30', 1, 0, 1, 1);

-- Insert Companies
INSERT INTO Companies (KashrusCompanyId, CompanyName, Category, CurrentlyCertified, EverCertified, Website, AddressStreet, AddressLine2, AddressCity, AddressState, AddressCountry, AddressZip, ContactName, ContactPhone, ContactEmail, KashrusStatus) VALUES
('KC-2025-4829', 'Happy Cow Mills Inc.', 'Pharmaceutical / Nutraceutical', 0, 0, 'www.happycowmills.com', '1250 Industrial Parkway', 'Building A, Suite 100', 'Rochester', 'NY', 'USA', '14624', 'John Mitchell', '(585) 555-0123', 'john@happycowmills.com', 'Company Created'),
('KC-2025-001', 'Brooklyn Bread Co.', 'Commercial Bakery', 1, 1, 'www.brooklynbread.com', '125 Bay Ridge Ave', NULL, 'Brooklyn', 'NY', 'USA', '11220', 'John Baker', '(718) 555-0199', 'john@brooklynbread.com', 'Certified'),
('KC-2025-002', 'Metro Foods Inc.', 'Distribution Center', 1, 1, 'www.metrofoods.com', '450 Industrial Ave', NULL, 'Newark', 'NJ', 'USA', '07102', 'Sarah Johnson', '(201) 555-0200', 'sarah@metrofoods.com', 'Certified'),
('KC-2025-003', 'Artisan Baking Company', 'Artisan Bakery', 1, 1, 'www.artisanbaking.com', '88 Spring Street', NULL, 'New York', 'NY', 'USA', '10012', 'David Miller', '(212) 555-0201', 'david@artisanbaking.com', 'Certified'),
('KC-2025-004', 'Sunshine Snacks LLC', 'Snack Food Manufacturing', 0, 0, 'www.sunshinesnacks.com', '2847 Industrial Blvd', NULL, 'Los Angeles', 'CA', 'USA', '90023', 'Maria Rodriguez', '(323) 555-0202', 'maria@sunshinesnacks.com', 'Under Review'),
('KC-2025-005', 'Garden Fresh Foods', 'Vegetable Processing', 1, 1, 'www.gardenfresh.com', '156 Harvest Lane', NULL, 'Freehold', 'NJ', 'USA', '07728', 'Robert Chen', '(732) 555-0203', 'robert@gardenfresh.com', 'Certified'),
('KC-2025-006', 'Fresh Valley Dairy', 'Dairy Processing', 1, 1, 'www.freshvalley.com', '245 Farm Road', NULL, 'Middletown', 'NY', 'USA', '10940', 'Lisa Anderson', '(845) 555-0204', 'lisa@freshvalley.com', 'Certified'),
('KC-2025-007', 'Golden Grain Mills', 'Flour Milling', 1, 1, 'www.goldengrain.com', '1205 Mill Street', NULL, 'Yonkers', 'NY', 'USA', '10701', 'Michael Davis', '(914) 555-0205', 'michael@goldengrain.com', 'Certified');

-- Insert Facilities
INSERT INTO Facilities (CompanyID, NCRCPlantId, FacilityName, FacilityType, Address, AddressLine2, City, State, Country, ZipCode, Latitude, Longitude, SquareFootage, EmployeeCount, ShiftSchedule, ContactName, ContactTitle, ContactPhone, ContactEmail, ManufacturingProcess, ClosestMajorCity, HasOtherProducts, OtherProductsList, HasOtherPlantsProducing, OtherPlantsLocation) VALUES
(1, 'PLT-KC-2025-4829-001', 'Happy Cow Mills Production Facility', 'Pharmaceutical Manufacturing', '1250 Industrial Parkway', 'Building A, Suite 100', 'Rochester', 'NY', 'USA', '14624', 43.1566, -77.6088, 15000, 25, '6 AM - 6 PM, Monday-Friday', 'John Mitchell', 'Plant Manager', '(585) 555-0123', 'j.mitchell@happycowmills.com', 'Grain cleaning, milling, and flour production. Raw grains are received in bulk, cleaned using mechanical separators, ground using stone mills, sifted through mesh screens, and packaged in food-grade containers. All processes follow HACCP guidelines.', 'Rochester, NY (15 miles)', 1, 'Animal feed supplements, grain storage services', 1, 'Secondary facility at 425a Commerce Drive, Rochester NY'),
(2, 'PLT-KC-2025-001-001', 'Brooklyn Main Facility', 'Commercial Bakery', '125 Bay Ridge Ave', NULL, 'Brooklyn', 'NY', 'USA', '11220', 40.6231, -74.0154, 5000, 12, '6 AM - 6 PM, Monday-Saturday', 'John Baker', 'Production Manager', '(718) 555-0199', 'john@brooklynbread.com', 'Commercial bread and pastry production', 'Brooklyn, NY', 0, NULL, 0, NULL),
(3, 'PLT-KC-2025-002-001', 'Distribution Center', 'Distribution Center', '450 Industrial Ave', NULL, 'Newark', 'NJ', 'USA', '07102', 40.7357, -74.1724, 25000, 45, '24/7 Operations', 'Sarah Johnson', 'Operations Manager', '(201) 555-0200', 'sarah@metrofoods.com', 'Food distribution and cold storage', 'Newark, NJ', 0, NULL, 0, NULL),
(4, 'PLT-KC-2025-003-001', 'Manhattan Location', 'Artisan Bakery', '88 Spring Street', NULL, 'New York', 'NY', 'USA', '10012', 40.7223, -74.0030, 3500, 8, '5 AM - 5 PM, Tuesday-Sunday', 'David Miller', 'Head Baker', '(212) 555-0201', 'david@artisanbaking.com', 'Artisan bread and pastry production', 'Manhattan, NY', 0, NULL, 0, NULL),
(5, 'PLT-KC-2025-004-001', 'West Coast Facility', 'Snack Food Manufacturing', '2847 Industrial Blvd', NULL, 'Los Angeles', 'CA', 'USA', '90023', 34.0522, -118.2437, 15000, 75, '6 AM - 10 PM, Monday-Friday', 'Maria Rodriguez', 'Plant Manager', '(323) 555-0202', 'maria@sunshinesnacks.com', 'Snack food manufacturing and packaging', 'Los Angeles, CA', 0, NULL, 0, NULL),
(6, 'PLT-KC-2025-005-001', 'Processing Center', 'Vegetable Processing', '156 Harvest Lane', NULL, 'Freehold', 'NJ', 'USA', '07728', 40.2677, -74.2736, 8000, 25, '7 AM - 7 PM, Monday-Saturday', 'Robert Chen', 'Processing Manager', '(732) 555-0203', 'robert@gardenfresh.com', 'Fresh vegetable processing and packaging', 'Freehold, NJ', 0, NULL, 0, NULL),
(7, 'PLT-KC-2025-006-001', 'Processing Facility', 'Dairy Processing', '245 Farm Road', NULL, 'Middletown', 'NY', 'USA', '10940', 41.4459, -74.4229, 12000, 35, '4 AM - 8 PM, Monday-Saturday', 'Lisa Anderson', 'Dairy Manager', '(845) 555-0204', 'lisa@freshvalley.com', 'Dairy processing and packaging', 'Middletown, NY', 0, NULL, 0, NULL),
(8, 'PLT-KC-2025-007-001', 'Flour Mill #3', 'Flour Milling', '1205 Mill Street', NULL, 'Yonkers', 'NY', 'USA', '10701', 40.9312, -73.8988, 20000, 18, '6 AM - 6 PM, Monday-Friday', 'Michael Davis', 'Mill Manager', '(914) 555-0205', 'michael@goldengrain.com', 'Grain milling and flour production', 'Yonkers, NY', 0, NULL, 0, NULL);

-- Insert Applications
INSERT INTO Applications (ApplicationNumber, ApplicationCode, CompanyID, FacilityID, ApplicationType, Status, StatusCode, RegionCode, PriorityCode, AssignedRCId, SubmissionDate, ApplicationDate, PrimaryContactName, OwnBrand, CopackerDirectory, VeganCertification, PlantCount, SpecialRequirements, CreatedBy, UpdatedBy) VALUES
('APP-2025-0717-001', 'APP-2025-001', 1, 1, 'New Certification', 'incomplete', 'incomplete', 'NE', 'medium', 1, '2025-07-17', '2025-07-17 16:30:00', 'John Mitchell', 1, 1, 1, 1, 'Multi-day inspection required for pharmaceutical facility', 1, 1),
('APP-2025-001', 'APP-2025-002', 2, 2, 'New Certification', 'under_review', 'under_review', 'NE', 'high', 2, '2025-07-15', '2025-07-15 10:30:00', 'John Baker', 1, 0, 0, 1, 'Pas Yisroel supervision required; Yoshon compliance needed', 5, 5),
('APP-2025-002', 'APP-2025-003', 4, 4, 'New Certification', 'approved', 'approved', 'NE', 'medium', 3, '2025-07-10', '2025-07-10 14:15:00', 'David Miller', 1, 0, 0, 1, 'Artisan bread specialty certification', 6, 6),
('APP-2025-003', 'APP-2025-004', 7, 7, 'Renewal', 'approved', 'approved', 'NE', 'medium', 2, '2025-07-08', '2025-07-08 09:45:00', 'Lisa Anderson', 1, 0, 0, 1, 'Dairy processing renewal with expanded product line', 7, 7),
('APP-2025-004', 'APP-2025-005', 3, 3, 'Modification', 'under_review', 'under_review', 'NE', 'medium', 1, '2025-07-12', '2025-07-12 11:20:00', 'Sarah Johnson', 0, 1, 0, 1, 'Addition of frozen storage capability', 6, 6),
('APP-2025-005', 'APP-2025-006', 8, 8, 'Re-inspection', 'under_review', 'under_review', 'NE', 'high', 3, '2025-07-05', '2025-07-05 13:30:00', 'Michael Davis', 1, 0, 0, 1, 'Follow-up after equipment upgrade', 7, 7),
('APP-2025-006', 'APP-2025-007', 5, 5, 'New Certification', 'submitted', 'submitted', 'WE', 'medium', NULL, '2025-07-20', '2025-07-20 16:00:00', 'Maria Rodriguez', 1, 0, 0, 1, 'Multi-day inspection required for large facility', 1, 1),
('APP-2025-007', 'APP-2025-008', 5, 5, 'Modification', 'under_review', 'under_review', 'WE', 'high', 2, '2025-07-18', '2025-07-18 10:15:00', 'Maria Rodriguez', 1, 0, 0, 1, 'Facility expansion certification', 1, 1),
('APP-2025-009', 'APP-2025-009', 6, 6, 'Re-inspection', 'under_review', 'under_review', 'NE', 'urgent', 4, '2025-07-22', '2025-07-22 08:45:00', 'Robert Chen', 1, 0, 1, 1, 'Emergency re-inspection after equipment modification', 1, 1);

-- Insert Application Contacts
INSERT INTO ApplicationContacts (ApplicationId, ContactType, ContactName, ContactRole, Email, Phone, Title, IsPrimary, IsDesignated) VALUES
(1, 'Primary Contact', 'John Mitchell', 'Primary Contact', 'john@happycowmills.com', '9176966517', 'Plant Manager', 1, 1),
(1, 'Additional Contact', 'Gary Magder', 'Quality Contact', 'gmagder@happycowmills.com', '9176966517', 'Quality Assurance Manager', 0, 0),
(2, 'Primary Contact', 'John Baker', 'Primary Contact', 'john@brooklynbread.com', '(718) 555-0199', 'Production Manager', 1, 1),
(3, 'Primary Contact', 'David Miller', 'Primary Contact', 'david@artisanbaking.com', '(212) 555-0201', 'Head Baker', 1, 1),
(4, 'Primary Contact', 'Lisa Anderson', 'Primary Contact', 'lisa@freshvalley.com', '(845) 555-0204', 'Dairy Manager', 1, 1),
(5, 'Primary Contact', 'Sarah Johnson', 'Primary Contact', 'sarah@metrofoods.com', '(201) 555-0200', 'Operations Manager', 1, 1),
(6, 'Primary Contact', 'Michael Davis', 'Primary Contact', 'michael@goldengrain.com', '(914) 555-0205', 'Mill Manager', 1, 1),
(7, 'Primary Contact', 'Maria Rodriguez', 'Primary Contact', 'maria@sunshinesnacks.com', '(323) 555-0202', 'Plant Manager', 1, 1),
(8, 'Primary Contact', 'Maria Rodriguez', 'Primary Contact', 'maria@sunshinesnacks.com', '(323) 555-0202', 'Plant Manager', 1, 1),
(9, 'Primary Contact', 'Robert Chen', 'Primary Contact', 'robert@gardenfresh.com', '(732) 555-0203', 'Processing Manager', 1, 1);

-- Insert Application Products
INSERT INTO ApplicationProducts (ApplicationId, Source, ProductName, LabelName, BrandName, LabelCompany, Category, Volume, ConsumerIndustrial, BulkShipped, CertificationSymbol, Description) VALUES
(1, 'Form Data', 'Nutritional Supplements', 'Happy Cow Supplements', 'Happy Cow', 'Happy Cow Mills Inc.', 'Pharmaceuticals', '1000 bottles/day', 'C', 'N', 'OU', 'Kosher nutritional supplements'),
(1, 'Form Data', 'Protein Powder', 'Happy Cow Protein', 'Happy Cow', 'Happy Cow Mills Inc.', 'Supplements', '500 containers/day', 'C', 'Y', 'OU', 'Kosher protein powder for athletes'),
(2, 'Brands File 1', 'Artisan Breads', 'Brooklyn Artisan', 'Brooklyn Bread Co.', 'Brooklyn Bread Co.', 'Baked Goods', '500 loaves/day', 'C', 'N', 'OU', 'Traditional artisan breads using ancient grains'),
(2, 'Brands File 1', 'Pastries', 'Brooklyn Pastries', 'Brooklyn Bread Co.', 'Brooklyn Bread Co.', 'Baked Goods', '200 items/day', 'C', 'N', 'OU', 'Danish pastries, croissants, and specialty items'),
(3, 'Form Data', 'Sourdough Bread', 'Artisan Sourdough', 'Artisan Baking', 'Artisan Baking Company', 'Artisan Bread', '300 loaves/day', 'C', 'N', 'OU', 'Traditional sourdough with 48-hour fermentation'),
(4, 'Form Data', 'Whole Milk', 'Fresh Valley Milk', 'Fresh Valley', 'Fresh Valley Dairy', 'Dairy', '5000 gallons/day', 'C', 'Y', 'OU-D', 'Fresh whole milk from local farms'),
(4, 'Form Data', 'Greek Yogurt', 'Fresh Valley Greek', 'Fresh Valley', 'Fresh Valley Dairy', 'Dairy', '2000 containers/day', 'C', 'N', 'OU-D', 'Premium Greek yogurt with live cultures'),
(5, 'Form Data', 'Frozen Vegetables', 'Metro Fresh', 'Metro Foods', 'Metro Foods Inc.', 'Frozen Foods', '10000 packages/day', 'C', 'Y', 'OU', 'Quick-frozen vegetables for distribution'),
(6, 'Form Data', 'Wheat Flour', 'Golden Grain', 'Golden Grain', 'Golden Grain Mills', 'Flour Products', '50 tons/day', 'I', 'Y', 'OU', 'Premium wheat flour for commercial baking'),
(7, 'Form Data', 'Potato Chips', 'Sunshine Chips', 'Sunshine', 'Sunshine Snacks LLC', 'Snack Foods', '100000 bags/day', 'C', 'N', 'OU', 'Kettle-cooked potato chips in various flavors'),
(8, 'Form Data', 'Tortilla Chips', 'Sunshine Tortilla', 'Sunshine', 'Sunshine Snacks LLC', 'Snack Foods', '75000 bags/day', 'C', 'N', 'OU', 'Corn tortilla chips with natural ingredients'),
(9, 'Form Data', 'Fresh Vegetables', 'Garden Fresh', 'Garden Fresh', 'Garden Fresh Foods', 'Fresh Produce', '5000 packages/day', 'C', 'N', 'OU', 'Fresh processed vegetables');

-- Insert Application Ingredients
INSERT INTO ApplicationIngredients (ApplicationId, IngredientId, NCRCIngredientId, Source, UKDId, RMC, IngredientName, Manufacturer, Brand, Packaging, Supplier, CategoryCode, DairyStatusCode, GroupDesignation, StatusCode, ScheduleStatus, CertificationAgency, KosherCertification, LotTracking, Status, AddedBy, ApprovedBy, ApprovedDate) VALUES
(1, 1, 'ING-2025-1001', 'File 1', '', '', 'Wheat Flour', 'King Arthur Flour Co.', 'King Arthur', 'bulk', 'King Arthur Flour Co.', 'GRAINS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-18'),
(1, 2, 'ING-2025-1002', 'File 1', '', '', 'High Fructose Corn Syrup', 'Cargill Inc.', 'Cargill', 'bulk', 'Cargill Inc.', 'SWEETENERS', 'PAREVE', 3, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-18'),
(1, 3, 'ING-2025-1003', 'Manual Entry', 'OUE9-VAN2024', '', 'Natural Vanilla Extract', 'Premium Flavor Co', 'Premium Flavor Co', 'Packaged', 'Premium Flavor Co', 'FLAVORING', 'PAREVE', 3, 'pending_review', 'Pending Schedule A', 'OU', 'OU', 1, 'Recent', 'J. Mitchell', NULL, NULL),
(1, 9, 'ING-2025-1004', 'Manual Entry', '', '', 'Organic Quinoa Flour', 'Andean Grains Ltd', 'Andean Grains', 'bulk', 'Andean Grains Ltd', 'GRAINS', 'PAREVE', 3, 'pending_review', 'Pending Schedule A', 'OU-P', 'OU-P', 1, 'Recent', 'G. Magder', NULL, NULL),
(1, 10, 'ING-2025-1005', 'Supplier Update', '', '', 'Coconut Oil (Refined)', 'Tropical Oils Inc', 'TropicalPure', 'Packaged', 'Tropical Oils Inc', 'EMULSIFIERS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Recent', 'Auto-Sync', 'D. Herbsman', '2025-07-18'),
(2, 1, 'ING-2025-2001', 'File 1', '', '', 'Wheat Flour', 'King Arthur Flour Co.', 'King Arthur', 'bulk', 'King Arthur Flour Co.', 'GRAINS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-15'),
(2, 7, 'ING-2025-2002', 'File 1', '', '', 'Organic Sugar', 'Wholesome Sweeteners', 'Wholesome', 'bulk', 'Wholesome Sweeteners', 'SWEETENERS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-15'),
(2, 8, 'ING-2025-2003', 'File 1', '', '', 'Sea Salt', 'Celtic Sea Salt', 'Celtic', 'bulk', 'Celtic Sea Salt', 'SEASONINGS', 'PAREVE', 2, 'approved', 'On Schedule A', 'OU', 'OU', 0, 'Original', 'System Import', 'Rabbi Torres', '2025-07-15'),
(3, 1, 'ING-2025-3001', 'File 1', '', '', 'Wheat Flour', 'King Arthur Flour Co.', 'King Arthur', 'bulk', 'King Arthur Flour Co.', 'GRAINS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-10'),
(3, 6, 'ING-2025-3002', 'File 1', '', '', 'Soy Lecithin', 'ADM', 'ADM', 'bulk', 'ADM', 'EMULSIFIERS', 'PAREVE', 1, 'approved', 'On Schedule A', 'OU', 'OU', 1, 'Original', 'System Import', 'D. Herbsman', '2025-07-10');

-- Insert Application Prerequisites
INSERT INTO ApplicationPrerequisites (ApplicationId, PrerequisiteType, Status, CompletedDate, Reviewer, Notes) VALUES
(1, 'inspection', 'pending', NULL, NULL, 'Inspection required for pharmaceutical facility'),
(1, 'ingredients', 'completed', '2025-07-18', 'D. Herbsman', '5 ingredients reviewed and categorized'),
(1, 'products', 'completed', '2025-07-18', 'Products Dept', '2 products approved for certification'),
(2, 'inspection', 'completed', '2025-07-15', 'Rabbi Torres', 'Facility meets all kosher requirements'),
(2, 'ingredients', 'completed', '2025-07-15', 'D. Herbsman', 'All ingredients reviewed and categorized'),
(2, 'products', 'completed', '2025-07-15', 'Products Dept', 'Product list approved for certification'),
(3, 'inspection', 'completed', '2025-07-10', 'Rabbi Stone', 'Artisan bakery inspection completed'),
(3, 'ingredients', 'completed', '2025-07-10', 'D. Herbsman', 'Ingredients approved'),
(3, 'products', 'completed', '2025-07-10', 'Products Dept', 'Products approved for certification');

-- Insert Application Quotes
INSERT INTO ApplicationQuotes (ApplicationId, QuoteNumber, TotalAmount, ValidUntil, Status, IsVerified) VALUES
(1, 'QT-2025-HC-001', 2850.00, '2025-08-17', 'pending_acceptance', 0),
(2, 'QT-2025-BB-001', 1800.00, '2025-08-15', 'accepted', 1),
(3, 'QT-2025-AB-001', 1500.00, '2025-08-10', 'accepted', 1),
(7, 'QT-2025-SS-001', 3200.00, '2025-08-20', 'pending_acceptance', 0);

-- Insert Quote Items
INSERT INTO QuoteItems (QuoteId, ItemDescription, Amount, SortOrder) VALUES
(1, 'Initial Certification - 1 Plant', 1500.00, 1),
(1, 'Product Review (2 products)', 800.00, 2),
(1, 'Ingredient Analysis (5 ingredients)', 550.00, 3),
(2, 'Initial Certification - 1 Plant', 1200.00, 1),
(2, 'Product Review (2 products)', 600.00, 2),
(3, 'New Certification - Artisan Bakery', 1500.00, 1),
(4, 'Initial Certification - Large Facility', 2000.00, 1),
(4, 'Product Review (2 products)', 800.00, 2),
(4, 'Extended Inspection', 400.00, 3);

-- Insert Application Validation
INSERT INTO ApplicationValidation (ApplicationId, ValidationCategory, IsValid, ValidationMessage, CheckedBy) VALUES
(1, 'company', 1, 'Company KC-2025-4829 verified in Kashrus DB', 1),
(1, 'plant', 1, 'Plant PLT-KC-2025-4829-001 created and linked', 1),
(1, 'contacts', 1, 'Primary contact John Mitchell designated for initial communication', 1),
(1, 'products', 1, '2 products identified and categorized', 1),
(1, 'ingredients', 1, '5 ingredients processed and validated', 1),
(1, 'quote', 0, 'Quote not found - needs verification', NULL),
(1, 'documentation', 1, 'All required documents uploaded and processed', 1),
(2, 'company', 1, 'Company KC-2025-001 verified', 1),
(2, 'plant', 1, 'Plant facility approved', 1),
(2, 'contacts', 1, 'Contact information verified', 1),
(2, 'products', 1, 'Products approved', 1),
(2, 'ingredients', 1, 'Ingredients approved', 1),
(2, 'quote', 1, 'Quote accepted and verified', 1),
(2, 'documentation', 1, 'Documentation complete', 1);

-- Insert Application Files
INSERT INTO ApplicationFiles (ApplicationId, FileName, FileType, FileSize, Tag, IsProcessed, RecordCount, UploadedBy) VALUES
(1, 'Application for OU Kosher Certification - HappyCow.pdf', 'application', '245 KB', 'Application Form', 1, NULL, 1),
(1, 'happycow IngredientOUKosher.xlsx', 'ingredients', '12 KB', 'Ingredient List', 1, 2, 1),
(1, 'happycow ProductsOUKosher.xlsx', 'products', '8 KB', 'Product List', 1, 2, 1),
(1, 'Facility Layout.pdf', 'facility', '156 KB', 'Facility Documentation', 1, NULL, 1),
(2, 'Brooklyn Bread Application.pdf', 'application', '198 KB', 'Application Form', 1, NULL, 5),
(2, 'Ingredient List - Brooklyn.xlsx', 'ingredients', '15 KB', 'Ingredient List', 1, 3, 5),
(2, 'Product List - Brooklyn.xlsx', 'products', '9 KB', 'Product List', 1, 2, 5),
(3, 'Artisan Baking Application.pdf', 'application', '167 KB', 'Application Form', 1, NULL, 6),
(3, 'Artisan Ingredients.xlsx', 'ingredients', '8 KB', 'Ingredient List', 1, 2, 6);

-- Insert Equipment
INSERT INTO Equipment (ApplicationID, EquipmentType, Brand, Model, Capacity, SerialNumber, InstallationDate, LastMaintenanceDate) VALUES
(1, 'Pharmaceutical Mill', 'Fitzpatrick', 'L1A', '100 kg/hr', 'FP-L1A-2024-001', '2024-03-15', '2025-06-20'),
(1, 'Tablet Press', 'Korsch', 'XL400', '400,000 tablets/hr', 'KO-XL-2024-002', '2024-03-18', '2025-06-18'),
(2, 'Commercial Oven', 'Blodgett', 'DFG-200', 'Double deck', 'BL-DFG-2024-001', '2024-03-15', '2025-06-20'),
(2, 'Spiral Mixer', 'Hobart', 'HSL180', '180 quart', 'HB-HSL-2024-002', '2024-03-18', '2025-06-18'),
(3, 'Stone Deck Oven', 'Bongard', 'Cyclothermic', '3 deck', 'BG-CT-2023-005', '2023-11-10', '2025-07-05'),
(4, 'Pasteurizer', 'APV', 'Pasilac', '5000 L/hr', 'APV-PS-2022-008', '2022-05-20', '2025-05-15'),
(4, 'Separator', 'Alfa Laval', 'CLARA', '3000 L/hr', 'AL-CL-2022-009', '2022-05-22', '2025-05-12'),
(6, 'Hammer Mill', 'Bliss Industries', 'Eliminator', '50 TPH', 'BI-EL-2024-010', '2024-01-15', '2025-07-01'),
(7, 'Fryer System', 'Heat and Control', 'FastLane', '5000 lbs/hr', 'HC-FL-2023-012', '2023-08-30', '2025-06-25');

-- Insert Inspection Requests
INSERT INTO InspectionRequests (RequestNumber, ApplicationID, RFRID, NCRCID, Status, Priority, RequestedStartDate, RequestedEndDate, ScheduledDate, ScheduledStartTime, ScheduledEndTime, EstimatedDuration, DistanceFromRFR, WhySelected) VALUES
('REQ-2025-001', 2, 1, 1, 'pending_response', 'high', '2025-07-28', '2025-07-30', NULL, NULL, NULL, '4-6 hours', '12 miles', 'Selected for bakery expertise and proximity to Brooklyn location'),
('REQ-2025-002', 5, 1, 2, 'scheduled', 'medium', '2025-07-25', '2025-07-25', '2025-07-25', '10:00:00', '14:00:00', '4 hours', '18 miles', 'Available within requested timeframe and familiar with distribution facilities'),
('REQ-2025-003', 7, 1, 2, 'pending_response', 'medium', '2025-08-01', '2025-08-05', NULL, NULL, NULL, '2 days', '2,800 miles', 'Available for travel assignments and experienced with snack food facilities'),
('REQ-2025-004', 9, 1, 3, 'pending_response', 'urgent', '2025-07-29', '2025-07-31', NULL, NULL, NULL, '6 hours', '24 miles', 'Urgent request - local RFR needed for emergency re-inspection'),
('REQ-2025-005', 3, 1, 1, 'completed', 'high', '2025-07-18', '2025-07-18', '2025-07-18', '09:00:00', '14:00:00', '5 hours', '8 miles', 'Bakery specialist for artisan bread certification'),
('REQ-2025-006', 4, 1, 2, 'completed', 'medium', '2025-07-15', '2025-07-15', '2025-07-15', '08:00:00', '13:00:00', '5 hours', '22 miles', 'Dairy processing specialist'),
('REQ-2025-007', 1, NULL, 1, 'pending_response', 'medium', '2025-08-10', '2025-08-15', NULL, NULL, NULL, '2 days', 'TBD', 'Pharmaceutical facility requires specialized inspection');

-- Insert Contracts
INSERT INTO Contracts (ContractId, ApplicationId, ContractTypeId, EffectiveDate, ExpirationDate, ContractDuration, Status, AnnualFee, Currency, PaymentTerms, InvoicingSchedule, AdditionalRequirements, CreatedBy, ModifiedBy) VALUES
('CONTRACT-2025-001', 2, 'new_company', '2025-08-01', '2026-08-01', 12, 'rc_approved', 12500.00, 'USD', 'Net 30', 'Annual', 'All ingredients must maintain OU certification throughout contract period', 'contracts@ou.org', 'contracts@ou.org'),
('CONTRACT-2025-002', 3, 'new_company', '2025-07-15', '2026-07-15', 12, 'completed', 8500.00, 'USD', 'Net 30', 'Annual', 'Artisan bakery requirements must be maintained', 'contracts@ou.org', 'contracts@ou.org'),
('CONTRACT-2025-003', 4, 'renewal', '2025-08-01', '2026-08-01', 12, 'completed', 15000.00, 'USD', 'Net 30', 'Annual', 'Dairy processing renewal with expanded product line approval', 'contracts@ou.org', 'contracts@ou.org');

-- Insert Contract Ingredients
INSERT INTO ContractIngredients (ContractId, IngredientId, ScheduleType, IncludeInContract, Notes) VALUES
('CONTRACT-2025-001', 1, 'A', 1, 'Group 1 - No symbol required'),
('CONTRACT-2025-001', 7, 'A', 1, 'Group 1 - No symbol required'),
('CONTRACT-2025-001', 8, 'A', 1, 'Group 2 - Inspection verified'),
('CONTRACT-2025-002', 1, 'A', 1, 'Group 1 - No symbol required'),
('CONTRACT-2025-002', 6, 'A', 1, 'Group 1 - No symbol required'),
('CONTRACT-2025-003', 1, 'A', 1, 'Dairy facility approved flour'),
('CONTRACT-2025-003', 7, 'A', 1, 'Organic sugar approved');

-- Insert Contract Approvals
INSERT INTO ContractApprovals (ContractId, ApprovalType, Status, ApprovedBy, ApprovedDate, Notes) VALUES
('CONTRACT-2025-001', 'rc_approval', 'approved', 'Rabbi Klein', '2025-07-20', 'Brooklyn Bread Co. approved for certification'),
('CONTRACT-2025-001', 'legal_approval', 'not_required', NULL, NULL, 'Legal review not required for new company certification'),
('CONTRACT-2025-002', 'rc_approval', 'approved', 'Rabbi Stone', '2025-07-12', 'Artisan bakery approved'),
('CONTRACT-2025-002', 'legal_approval', 'not_required', NULL, NULL, 'Standard certification'),
('CONTRACT-2025-003', 'rc_approval', 'approved', 'Rabbi Goldstein', '2025-07-10', 'Dairy renewal approved'),
('CONTRACT-2025-003', 'legal_approval', 'not_required', NULL, NULL, 'Renewal contract');

-- Insert DocuSign Envelopes
INSERT INTO DocuSignEnvelopes (EnvelopeId, ContractId, Status, SentDate, CompletedDate, DocumentUrl) VALUES
('ENV-ABC123-DEF456', 'CONTRACT-2025-001', 'pending_signature', '2025-07-21', NULL, 'https://docusign.com/envelope/ABC123'),
('ENV-XYZ789-GHI012', 'CONTRACT-2025-002', 'completed', '2025-07-13', '2025-07-14', 'https://docusign.com/envelope/XYZ789'),
('ENV-MNO345-PQR678', 'CONTRACT-2025-003', 'completed', '2025-07-11', '2025-07-12', 'https://docusign.com/envelope/MNO345');

-- Insert DocuSign Signers
INSERT INTO DocuSignSigners (EnvelopeId, SignerRole, SignerName, SignerEmail, Status, SignedDate) VALUES
('ENV-ABC123-DEF456', 'company_representative', 'John Baker', 'john@brooklynbread.com', 'pending', NULL),
('ENV-ABC123-DEF456', 'ou_representative', 'Rabbi Stareshefsky', 'rabbi.stareshefsky@ou.org', 'completed', '2025-07-21'),
('ENV-XYZ789-GHI012', 'company_representative', 'David Miller', 'david@artisanbaking.com', 'completed', '2025-07-14'),
('ENV-XYZ789-GHI012', 'ou_representative', 'Rabbi Stareshefsky', 'rabbi.stareshefsky@ou.org', 'completed', '2025-07-13'),
('ENV-MNO345-PQR678', 'company_representative', 'Lisa Anderson', 'lisa@freshvalley.com', 'completed', '2025-07-12'),
('ENV-MNO345-PQR678', 'ou_representative', 'Rabbi Stareshefsky', 'rabbi.stareshefsky@ou.org', 'completed', '2025-07-11');

-- Insert RFR Availability
INSERT INTO RFRAvailability (RFRID, AvailabilityType, Location, Address, StartDate, EndDate, Notes) VALUES
(1, 'available', 'NYC Metro Area', 'Manhattan, Brooklyn, Queens', '2025-07-20', '2025-08-15', 'Available for local inspections'),
(1, 'unavailable', 'Vacation', 'Personal Time', '2025-08-16', '2025-08-30', 'Annual vacation'),
(2, 'available', 'NJ/NY Area', 'Newark, Jersey City, Manhattan', '2025-07-15', '2025-09-15', 'Regular availability'),
(3, 'available', 'Brooklyn/Long Island', 'Brooklyn, Nassau County', '2025-07-01', '2025-12-31', 'Year-round availability'),
(3, 'unavailable', 'Training', 'OU Headquarters', '2025-09-10', '2025-09-12', 'Mandatory training session');

-- Insert RFR Preferred Days
INSERT INTO RFRPreferredDays (RFRID, DayOfWeek, IsPreferred) VALUES
(1, 'Monday', 1), (1, 'Tuesday', 1), (1, 'Wednesday', 1), (1, 'Thursday', 1), (1, 'Friday', 0), (1, 'Saturday', 0), (1, 'Sunday', 0),
(2, 'Monday', 1), (2, 'Tuesday', 1), (2, 'Wednesday', 1), (2, 'Thursday', 1), (2, 'Friday', 1), (2, 'Saturday', 0), (2, 'Sunday', 0),
(3, 'Monday', 1), (3, 'Tuesday', 1), (3, 'Wednesday', 1), (3, 'Thursday', 1), (3, 'Friday', 1), (3, 'Saturday', 1), (3, 'Sunday', 0);

-- Insert Application Activity
INSERT INTO ApplicationActivity (ApplicationId, Action, Details, ActivityType, Status, UserId, UserDisplayName, CreatedAt) VALUES
(1, 'Ingredient Added', 'Natural Vanilla Extract (Premium Flavor Co)', 'ingredient', 'approved', 1, 'J. Mitchell', '2025-07-18 14:30:00'),
(1, 'Ingredient Added', 'Organic Quinoa Flour (Andean Grains Ltd)', 'ingredient', 'pending', 2, 'G. Magder', '2025-07-18 13:15:00'),
(1, 'Supplier Sync', 'Coconut Oil (Refined) auto-added from supplier portal', 'ingredient', 'approved', 4, 'Auto-Sync', '2025-07-18 11:45:00'),
(1, 'Facility Updated', 'Manufacturing process description revised', 'facility', 'approved', 1, 'J. Mitchell', '2025-07-18 09:20:00'),
(1, 'Initial Import', '3 ingredients imported from application submission', 'bulk', 'approved', 3, 'System Import', '2025-07-17 16:45:00'),
(1, 'Company Created', 'Happy Cow Mills Inc. added to Kashrus DB (KC-2025-4829)', 'company', 'approved', 3, 'System', '2025-07-17 16:30:00'),
(2, 'Contract Sent', 'Contract sent to Brooklyn Bread Co. via DocuSign', 'contract', 'approved', 3, 'System', '2025-07-21 10:00:00'),
(2, 'Inspection Completed', 'Facility inspection completed successfully', 'inspection', 'approved', 5, 'Rabbi Torres', '2025-07-15 14:00:00'),
(3, 'Contract Executed', 'Artisan Baking Company contract fully executed', 'contract', 'approved', 3, 'System', '2025-07-14 16:30:00');

-- Insert Messages
INSERT INTO Messages (RequestID, ApplicationId, SenderType, SenderID, SenderName, FromUser, ToUser, MessageText, MessageType, IsRead) VALUES
(1, 2, 'NCRC', 1, 'R. Klein', 'R. Klein', 'R. Stone', 'Brooklyn Bread Co. inspection scheduled for July 28th. Please confirm availability.', 'outgoing', 0),
(2, 5, 'RFR', 1, 'R. Stone', 'R. Stone', 'R. Goldstein', 'Distribution center inspection completed. Report submitted.', 'incoming', 1),
(3, 7, 'NCRC', 2, 'R. Goldstein', 'R. Goldstein', 'R. Stone', 'West Coast facility inspection requested. Travel required.', 'outgoing', 0),
(NULL, 1, 'USER', 1, 'J. Mitchell', 'J. Mitchell', 'Dispatcher', 'Application ready for initial review. All documentation complete.', 'outgoing', 1),
(NULL, 2, 'SYSTEM', 3, 'System', 'System', 'J. Baker', 'Contract has been sent for signature via DocuSign.', 'incoming', 0);

-- Insert Application Comments
INSERT INTO ApplicationComments (ApplicationId, Author, CommentText, CommentType, CreatedAt) VALUES
(1, 'J. Mitchell', 'Verified all ingredient certifications with suppliers. Coconut oil documentation updated.', 'internal', '2025-07-18 14:45:00'),
(1, 'G. Magder', 'Facility contact information confirmed. John Mitchell will be primary for all communications.', 'internal', '2025-07-18 13:20:00'),
(1, 'D. Herbsman', 'Pharmaceutical facility requires additional documentation for specialized ingredients.', 'internal', '2025-07-18 10:30:00'),
(2, 'Rabbi Torres', 'Brooklyn facility meets all kosher requirements. Pas Yisroel procedures in place.', 'internal', '2025-07-15 15:30:00'),
(2, 'D. Herbsman', 'All ingredients approved. Yoshon compliance verified.', 'internal', '2025-07-15 11:15:00'),
(3, 'Rabbi Stone', 'Artisan bakery inspection completed. Excellent facility and procedures.', 'internal', '2025-07-10 16:00:00');

-- Insert Tasks
INSERT INTO Tasks (Title, Plant, AssignedToId, AssignedById, StatusCode, PriorityCode, DaysActive, ApplicationCode, WorkflowStageCode, Description) VALUES
('Review Pharmaceutical Ingredients', 'Happy Cow Mills Production Facility', 3, 1, 'in_progress', 'high', 5, 'APP-2025-001', 'ingredients', 'Complete review of specialized pharmaceutical ingredients for Happy Cow Mills'),
('Schedule West Coast Inspection', 'West Coast Facility', 2, 1, 'pending', 'medium', 2, 'APP-2025-007', 'inspection', 'Coordinate travel and schedule for Sunshine Snacks inspection'),
('Contract Follow-up', 'Brooklyn Main Facility', 1, 1, 'pending', 'medium', 3, 'APP-2025-002', 'contract', 'Follow up on pending DocuSign contract for Brooklyn Bread Co.'),
('Emergency Re-inspection Prep', 'Processing Center', 4, 3, 'new', 'urgent', 0, 'APP-2025-009', 'inspection', 'Prepare for emergency re-inspection at Garden Fresh Foods'),
('Dairy Renewal Processing', 'Processing Facility', 2, 1, 'completed', 'medium', 10, 'APP-2025-004', 'certification', 'Process dairy facility renewal documentation');

-- Insert Task Messages
INSERT INTO TaskMessages (TaskId, SenderId, SenderName, MessageText, IsSystemMessage) VALUES
(1, 3, 'D. Herbsman', 'Started review of pharmaceutical ingredients. Need additional supplier documentation.', 0),
(1, 1, 'A. Gottesman', 'Supplier contacted for missing certifications. Expected by end of week.', 0),
(2, 2, 'R. Gorelik', 'Checking RFR availability for West Coast travel assignment.', 0),
(3, NULL, 'System', 'DocuSign reminder sent to Brooklyn Bread Co.', 1),
(4, 4, 'R. Epstein', 'Emergency inspection scheduled for July 29th. RFR assignment pending.', 0),
(5, NULL, 'System', 'Dairy renewal contract executed successfully.', 1);
