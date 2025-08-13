-- =============================================
-- CREATE VIEWS FOR REPORTING AND API ACCESS
-- =============================================

-- Comprehensive Application Summary View
CREATE VIEW vw_ApplicationSummary AS
SELECT 
	a.ApplicationId,
	a.ApplicationNumber,
	a.ApplicationCode,
	c.CompanyName,
	c.KashrusCompanyId,
	f.FacilityName,
	f.NCRCPlantId,
	r.RegionName as Region,
	p.PriorityLabel as Priority,
	stat.StatusLabel as Status,
	a.ApplicationType,
	s.FullName as AssignedRC,
	a.SubmissionDate,
	a.ApplicationDate,
	a.PrimaryContactName,
	a.DaysInStage,
	a.IsOverdue,
	a.LastUpdate,
	a.NextAction,
	COUNT(DISTINCT ac.ContactId) AS ContactCount,
	COUNT(DISTINCT ap.ProductId) AS ProductCount,
	COUNT(DISTINCT ai.ApplicationIngredientId) AS IngredientCount,
	COUNT(DISTINCT CASE WHEN ai.Status = 'Recent' THEN ai.ApplicationIngredientId END) AS RecentIngredientCount,
	COUNT(DISTINCT af.FileId) AS FileCount,
	COUNT(DISTINCT ir.RequestID) AS InspectionRequestCount,
	ac_primary.ContactName as PrimaryContactName,
	ac_primary.Email as PrimaryContactEmail,
	ac_primary.Phone as PrimaryContactPhone,
	a.CreatedAt,
	a.UpdatedAt
FROM Applications a
INNER JOIN Companies c ON a.CompanyID = c.CompanyID
LEFT JOIN Facilities f ON a.FacilityID = f.FacilityID
LEFT JOIN Regions r ON a.RegionCode = r.RegionCode
LEFT JOIN Priorities p ON a.PriorityCode = p.PriorityCode
LEFT JOIN ApplicationStatuses stat ON a.StatusCode = stat.StatusCode
LEFT JOIN Staff s ON a.AssignedRCId = s.StaffId
LEFT JOIN ApplicationContacts ac ON a.ApplicationId = ac.ApplicationId
LEFT JOIN ApplicationContacts ac_primary ON a.ApplicationId = ac_primary.ApplicationId AND ac_primary.IsPrimary = 1
LEFT JOIN ApplicationProducts ap ON a.ApplicationId = ap.ApplicationId
LEFT JOIN ApplicationIngredients ai ON a.ApplicationId = ai.ApplicationId
LEFT JOIN ApplicationFiles af ON a.ApplicationId = af.ApplicationId
LEFT JOIN InspectionRequests ir ON a.ApplicationId = ir.ApplicationID
GROUP BY 
	a.ApplicationId, a.ApplicationNumber, a.ApplicationCode, c.CompanyName, c.KashrusCompanyId,
	f.FacilityName, f.NCRCPlantId, r.RegionName, p.PriorityLabel, stat.StatusLabel,
	a.ApplicationType, s.FullName, a.SubmissionDate, a.ApplicationDate, a.PrimaryContactName,
	a.DaysInStage, a.IsOverdue, a.LastUpdate, a.NextAction,
	ac_primary.ContactName, ac_primary.Email, ac_primary.Phone, a.CreatedAt, a.UpdatedAt;

-- ...existing CREATE VIEW statements and everything after...

-- All CREATE VIEW statements and everything after from NCRCDashbaord_ALL.sql
CREATE VIEW dbo.vw_ActiveRFRs AS
SELECT * FROM RFRs WHERE IsActive = 1;
GO

CREATE VIEW dbo.vw_ContractStatus AS
SELECT c.ContractId, c.Status, c.ExpirationDate, s.SupplierName
FROM Contracts c
JOIN Suppliers s ON c.SupplierId = s.SupplierId;
GO

-- ...additional CREATE VIEW statements...

-- End of views section
-- =============================================

USE OUKashrusSystem;
GO

-- All CREATE VIEW statements from NCRCDashbaord_ALL.sql
-- ...
-- (Paste all CREATE VIEW ... AS ... statements here, in order)
