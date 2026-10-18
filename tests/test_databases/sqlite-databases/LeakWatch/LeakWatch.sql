-- SQLite DDL converted from LeakWatch_supabse.sql (Supabase/PostgreSQL)
-- Type mapping: text -> TEXT; timestamptz -> TEXT (ISO-8601); boolean -> BOOLEAN;
-- numeric -> NUMERIC; jsonb and text[] -> TEXT (JSON-encoded).
-- Added: PRIMARY KEY on unified_id (source DDL declared none).

-- ======================
-- MESSAGING: Channel
-- ======================
CREATE TABLE unified_messaging_channel (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  parent_id TEXT,
  has_subchannels BOOLEAN,
  members TEXT,
  is_active BOOLEAN,
  is_private BOOLEAN,
  web_url TEXT,
  raw TEXT
);
-- ======================
-- MESSAGING: Message
-- ======================
CREATE TABLE unified_messaging_message (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  channels TEXT,
  parent_id TEXT,
  message_thread_identifier TEXT,
  author_member TEXT,
  destination_members TEXT,
  hidden_members TEXT,
  mentioned_members TEXT,
  reactions TEXT,
  subject TEXT,
  message TEXT,
  message_html TEXT,
  message_markdown TEXT,
  attachments TEXT,
  web_url TEXT,
  reference TEXT,
  has_children BOOLEAN,
  is_unread BOOLEAN,
  buttons TEXT,
  raw TEXT
);
-- ======================
-- CRM: Deal
-- ======================
CREATE TABLE unified_crm_deal (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  amount NUMERIC,
  currency TEXT,
  closed_at TEXT,
  closing_at TEXT,
  stages TEXT,
  pipelines TEXT,
  source TEXT,
  probability NUMERIC,
  tags TEXT,
  lost_reason TEXT,
  won_reason TEXT,
  user_id TEXT,
  contact_ids TEXT,
  company_ids TEXT,
  description TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- CRM: Contact
-- ======================
CREATE TABLE unified_crm_contact (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  title TEXT,
  company TEXT,
  emails TEXT,
  telephones TEXT,
  deal_ids TEXT,
  company_ids TEXT,
  address TEXT,
  user_id TEXT,
  link_urls TEXT,
  metadata TEXT,
  department TEXT,
  image_url TEXT,
  raw TEXT
);
-- ======================
-- CRM: Company
-- ======================
CREATE TABLE unified_crm_company (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  deal_ids TEXT,
  contact_ids TEXT,
  emails TEXT,
  telephones TEXT,
  websites TEXT,
  address TEXT,
  is_active BOOLEAN,
  tags TEXT,
  description TEXT,
  industry TEXT,
  link_urls TEXT,
  employees NUMERIC,
  timezone TEXT,
  user_id TEXT,
  metadata TEXT,
  domains TEXT,
  raw TEXT
);
-- ======================
-- CRM: Event
-- ======================
CREATE TABLE unified_crm_event (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  type TEXT,
  note TEXT,
  meeting TEXT,
  email TEXT,
  call TEXT,
  task TEXT,
  marketing_email TEXT,
  form TEXT,
  page_view TEXT,
  deal_ids TEXT,
  company_ids TEXT,
  contact_ids TEXT,
  lead_ids TEXT,
  user_id TEXT,
  raw TEXT
);
-- ======================
-- CRM: Lead
-- ======================
CREATE TABLE unified_crm_lead (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  user_id TEXT,
  creator_user_id TEXT,
  contact_id TEXT,
  company_id TEXT,
  company_name TEXT,
  is_active BOOLEAN,
  address TEXT,
  emails TEXT,
  telephones TEXT,
  source TEXT,
  status TEXT,
  title TEXT,
  link_urls TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- CRM: Taxonomy
-- ======================
CREATE TABLE unified_crm_taxonomy (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  name TEXT,
  label TEXT,
  type TEXT,
  raw TEXT
);
-- ======================
-- CRM: Pipeline
-- ======================
CREATE TABLE unified_crm_pipeline (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  is_active BOOLEAN,
  deal_probability NUMERIC,
  display_order NUMERIC,
  stages TEXT,
  raw TEXT
);
-- ======================
-- MARTECH: List
-- ======================
CREATE TABLE unified_martech_list (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  start_at TEXT,
  end_at TEXT,
  user_id TEXT,
  is_active BOOLEAN,
  address TEXT,
  subject TEXT,
  sender_name TEXT,
  sender_email TEXT,
  language TEXT,
  sender_company TEXT,
  sender_phone TEXT,
  raw TEXT
);
-- ======================
-- MARTECH: Member
-- ======================
CREATE TABLE unified_martech_member (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  company TEXT,
  emails TEXT,
  list_ids TEXT,
  tags TEXT,
  status TEXT,
  raw TEXT
);
-- ======================
-- MARTECH: Campaign
-- ======================
CREATE TABLE unified_martech_campaign (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  status TEXT,
  list_ids TEXT,
  subject_line TEXT,
  preview_text TEXT,
  from_name TEXT,
  from_email TEXT,
  reply_to_email TEXT,
  send_at TEXT,
  raw TEXT
);
-- ======================
-- MARTECH: Report
-- ======================
CREATE TABLE unified_martech_report (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  start_at TEXT,
  end_at TEXT,
  campaign_id TEXT,
  list_id TEXT,
  emails_sent NUMERIC,
  abuse_reports NUMERIC,
  unsubscribed NUMERIC,
  sent_at TEXT,
  hard_bounces NUMERIC,
  soft_bounces NUMERIC,
  syntax_errors NUMERIC,
  forwards_count NUMERIC,
  forwards_opens NUMERIC,
  opens_total NUMERIC,
  unique_opens NUMERIC,
  open_rate NUMERIC,
  last_open_at TEXT,
  clicks_total NUMERIC,
  unique_clicks NUMERIC,
  unique_subscriber_clicks NUMERIC,
  click_rate NUMERIC,
  last_click_at TEXT,
  links TEXT,
  human_opens_total NUMERIC,
  human_unique_opens NUMERIC,
  human_open_rate NUMERIC,
  raw TEXT
);
-- ======================
-- TICKETING: Ticket
-- ======================
CREATE TABLE unified_ticketing_ticket (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  customer_id TEXT,
  subject TEXT,
  description TEXT,
  status TEXT,
  closed_at TEXT,
  priority TEXT,
  category_id TEXT,
  source TEXT,
  source_ref TEXT,
  tags TEXT,
  user_id TEXT,
  url TEXT,
  attachment_ids TEXT,
  due_at TEXT,
  raw TEXT
);
-- ======================
-- TICKETING: Customer
-- ======================
CREATE TABLE unified_ticketing_customer (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  emails TEXT,
  telephones TEXT,
  tags TEXT,
  raw TEXT
);
-- ======================
-- TICKETING: Note
-- ======================
CREATE TABLE unified_ticketing_note (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  customer_id TEXT,
  description TEXT,
  ticket_id TEXT,
  user_id TEXT,
  raw TEXT
);
-- ======================
-- TICKETING: Category
-- ======================
CREATE TABLE unified_ticketing_category (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_active BOOLEAN,
  parent_id TEXT,
  raw TEXT
);
-- ======================
-- UC: Call
-- ======================
CREATE TABLE unified_uc_call (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  contact_id TEXT,
  telephone TEXT,
  start_at TEXT,
  end_at TEXT,
  user_id TEXT,
  contacts TEXT,
  is_private BOOLEAN,
  user_name TEXT,
  user_phone TEXT,
  type TEXT,
  metadata TEXT,
  raw TEXT,
  conversation_identifier TEXT
);
-- ======================
-- UC: Contact
-- ======================
CREATE TABLE unified_uc_contact (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  title TEXT,
  company TEXT,
  emails TEXT,
  telephones TEXT,
  raw TEXT
);
-- ======================
-- UC: Comment
-- ======================
CREATE TABLE unified_uc_comment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  content TEXT,
  user_id TEXT,
  call_id TEXT,
  raw TEXT
);
-- ======================
-- UC: Recording
-- ======================
CREATE TABLE unified_uc_recording (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  end_at TEXT,
  expires_at TEXT,
  call_id TEXT,
  web_url TEXT,
  contacts TEXT,
  user_id TEXT,
  media TEXT,
  user_name TEXT,
  user_phone TEXT,
  type TEXT,
  conversation_identifier TEXT,
  raw TEXT
);
-- ======================
-- UC: Scorecard
-- ======================
CREATE TABLE unified_uc_scorecard (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  call_id TEXT,
  scorecardtemplate_id TEXT,
  name TEXT,
  user_id TEXT,
  reviewer_user_id TEXT,
  reviewed_at TEXT,
  score NUMERIC,
  questions TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- UC: Scorecardtemplate
-- ======================
CREATE TABLE unified_uc_scorecardtemplate (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_active BOOLEAN,
  questions TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ATS: Activity
-- ======================
CREATE TABLE unified_ats_activity (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  candidate_id TEXT,
  application_id TEXT,
  job_id TEXT,
  interview_id TEXT,
  document_ids TEXT,
  title TEXT,
  description TEXT,
  is_private BOOLEAN,
  user_ids TEXT,
  type TEXT,
  "from" TEXT,
  "to" TEXT,
  cc TEXT,
  bcc TEXT,
  sub_type TEXT,
  company_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ATS: Candidate
-- ======================
CREATE TABLE unified_ats_candidate (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  emails TEXT,
  title TEXT,
  telephones TEXT,
  company_name TEXT,
  image_url TEXT,
  tags TEXT,
  address TEXT,
  external_identifier TEXT,
  link_urls TEXT,
  origin TEXT,
  company_id TEXT,
  sources TEXT,
  date_of_birth TEXT,
  user_id TEXT,
  user_ids TEXT,
  web_url TEXT,
  experiences TEXT,
  education TEXT,
  skills TEXT,
  job_ids TEXT,
  metadata TEXT,
  summary TEXT,
  raw TEXT
);
-- ======================
-- ATS: Job
-- ======================
CREATE TABLE unified_ats_job (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  recruiter_ids TEXT,
  hiring_manager_ids TEXT,
  hiring_managers TEXT,
  status TEXT,
  closed_at TEXT,
  addresses TEXT,
  compensation TEXT,
  employment_type TEXT,
  remote BOOLEAN,
  language_locale TEXT,
  public_job_urls TEXT,
  number_of_openings NUMERIC,
  company_id TEXT,
  questions TEXT,
  postings TEXT,
  groups TEXT,
  openings TEXT,
  minimum_experience_years NUMERIC,
  minimum_degree TEXT,
  skills TEXT,
  metadata TEXT,
  user_id TEXT,
  industry TEXT,
  summary TEXT,
  raw TEXT
);
-- ======================
-- ATS: Interview
-- ======================
CREATE TABLE unified_ats_interview (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  candidate_id TEXT,
  job_id TEXT,
  application_id TEXT,
  user_ids TEXT,
  status TEXT,
  start_at TEXT,
  end_at TEXT,
  location TEXT,
  meeting_url TEXT,
  external_event_xref TEXT,
  raw TEXT
);
-- ======================
-- ATS: Document
-- ======================
CREATE TABLE unified_ats_document (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  document_url TEXT,
  document_data TEXT,
  filename TEXT,
  type TEXT,
  candidate_id TEXT,
  application_id TEXT,
  job_id TEXT,
  user_id TEXT,
  raw TEXT
);
-- ======================
-- ATS: Applicationstatus
-- ======================
CREATE TABLE unified_ats_applicationstatu (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  job_id TEXT,
  status TEXT,
  original_status TEXT,
  description TEXT,
  raw TEXT
);
-- ======================
-- ATS: Application
-- ======================
CREATE TABLE unified_ats_application (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  candidate_id TEXT,
  job_id TEXT,
  created_at TEXT,
  updated_at TEXT,
  applied_at TEXT,
  hired_at TEXT,
  rejected_at TEXT,
  rejected_reason TEXT,
  source TEXT,
  status TEXT,
  original_status TEXT,
  answers TEXT,
  offers TEXT,
  user_id TEXT,
  metadata TEXT,
  original_substatus TEXT,
  summary TEXT,
  raw TEXT
);
-- ======================
-- ATS: Scorecard
-- ======================
CREATE TABLE unified_ats_scorecard (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  application_id TEXT,
  interviewer_id TEXT,
  interview_id TEXT,
  candidate_id TEXT,
  job_id TEXT,
  recommendation TEXT,
  comment TEXT,
  questions TEXT,
  raw TEXT
);
-- ======================
-- ATS: Company
-- ======================
CREATE TABLE unified_ats_company (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  address TEXT,
  website_url TEXT,
  phone TEXT,
  parent_id TEXT,
  recruiter_ids TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Employee
-- ======================
CREATE TABLE unified_hris_employee (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  emails TEXT,
  title TEXT,
  job_id TEXT,
  manager_id TEXT,
  employment_status TEXT,
  gender TEXT,
  telephones TEXT,
  date_of_birth TEXT,
  employee_number TEXT,
  hired_at TEXT,
  terminated_at TEXT,
  termination_reason TEXT,
  marital_status TEXT,
  employment_type TEXT,
  address TEXT,
  language_locale TEXT,
  currency TEXT,
  timezone TEXT,
  image_url TEXT,
  company_id TEXT,
  pronouns TEXT,
  employee_roles TEXT,
  compensation TEXT,
  salutation TEXT,
  bio TEXT,
  ssn_sin TEXT,
  groups TEXT,
  locations TEXT,
  metadata TEXT,
  storage_quota_allocated NUMERIC,
  storage_quota_used NUMERIC,
  storage_quota_available NUMERIC,
  relationships TEXT,
  has_mfa BOOLEAN,
  timeoff_days_total NUMERIC,
  timeoff_days_used NUMERIC,
  flsa_status TEXT,
  pay_frequency TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Company
-- ======================
CREATE TABLE unified_hris_company (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  legal_name TEXT,
  address TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Location
-- ======================
CREATE TABLE unified_hris_location (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  address TEXT,
  parent_id TEXT,
  external_identifier TEXT,
  telephones TEXT,
  timezone TEXT,
  currency TEXT,
  language_locale TEXT,
  is_active BOOLEAN,
  is_hq BOOLEAN,
  company_id TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Group
-- ======================
CREATE TABLE unified_hris_group (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  parent_id TEXT,
  type TEXT,
  user_ids TEXT,
  manager_ids TEXT,
  is_active BOOLEAN,
  company_id TEXT,
  pay_frequency TEXT,
  next_paid_at TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Job
-- ======================
CREATE TABLE unified_hris_job (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  code TEXT,
  is_active BOOLEAN,
  employment_type TEXT,
  company_id TEXT,
  groups TEXT,
  locations TEXT,
  parent_id TEXT,
  users TEXT,
  compensation TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Timeoff
-- ======================
CREATE TABLE unified_hris_timeoff (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  company_id TEXT,
  start_at TEXT,
  end_at TEXT,
  is_paid BOOLEAN,
  status TEXT,
  approver_user_id TEXT,
  approved_at TEXT,
  comments TEXT,
  reason TEXT,
  original_type TEXT,
  type TEXT,
  duration NUMERIC,
  duration_type TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Payslip
-- ======================
CREATE TABLE unified_hris_payslip (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  company_id TEXT,
  payment_reference TEXT,
  payment_type TEXT,
  paid_at TEXT,
  start_at TEXT,
  end_at TEXT,
  currency TEXT,
  gross_amount NUMERIC,
  net_amount NUMERIC,
  details TEXT,
  deduction TEXT,
  payroll_id TEXT,
  group_id TEXT,
  type TEXT,
  hours NUMERIC,
  employee_tax_amount NUMERIC,
  employer_tax_amount NUMERIC,
  deduction_amount NUMERIC,
  employer_contribution_amount NUMERIC,
  gross_ytd_amount NUMERIC,
  net_ytd_amount NUMERIC,
  raw TEXT
);
-- ======================
-- HRIS: Payroll
-- ======================
CREATE TABLE unified_hris_payroll (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  company_id TEXT,
  group_id TEXT,
  status TEXT,
  type TEXT,
  start_at TEXT,
  end_at TEXT,
  paid_at TEXT,
  approved_at TEXT,
  currency TEXT,
  gross_amount NUMERIC,
  net_amount NUMERIC,
  employee_tax_amount NUMERIC,
  employer_tax_amount NUMERIC,
  deduction_amount NUMERIC,
  employer_contribution_amount NUMERIC,
  total_cost_amount NUMERIC,
  user_ids TEXT,
  payslip_ids TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Paycode
-- ======================
CREATE TABLE unified_hris_paycode (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  company_id TEXT,
  name TEXT,
  code TEXT,
  description TEXT,
  type TEXT,
  detail_type TEXT,
  is_pre_tax BOOLEAN,
  is_employer BOOLEAN,
  is_active BOOLEAN,
  raw TEXT
);
-- ======================
-- HRIS: Earning
-- ======================
CREATE TABLE unified_hris_earning (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  company_id TEXT,
  paycode_id TEXT,
  amount NUMERIC,
  currency TEXT,
  hours NUMERIC,
  rate_amount NUMERIC,
  frequency TEXT,
  start_at TEXT,
  end_at TEXT,
  status TEXT,
  payroll_id TEXT,
  payslip_id TEXT,
  notes TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Device
-- ======================
CREATE TABLE unified_hris_device (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  asset_tag TEXT,
  version TEXT,
  manufacturer TEXT,
  model TEXT,
  os TEXT,
  os_version TEXT,
  user_ids TEXT,
  admin_user_ids TEXT,
  location_id TEXT,
  has_antivirus BOOLEAN,
  has_password_manager BOOLEAN,
  has_firewall BOOLEAN,
  has_hd_encrypted BOOLEAN,
  has_screenlock BOOLEAN,
  is_missing BOOLEAN,
  raw TEXT
);
-- ======================
-- HRIS: Timeshift
-- ======================
CREATE TABLE unified_hris_timeshift (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  employee_user_id TEXT,
  start_at TEXT,
  end_at TEXT,
  location_id TEXT,
  company_id TEXT,
  group_id TEXT,
  compensation TEXT,
  approver_user_id TEXT,
  approved_at TEXT,
  hours NUMERIC,
  is_approved BOOLEAN,
  raw TEXT
);
-- ======================
-- HRIS: Attendance
-- ======================
CREATE TABLE unified_hris_attendance (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  employee_user_id TEXT,
  start_at TEXT,
  end_at TEXT,
  timeshift_id TEXT,
  location_id TEXT,
  company_id TEXT,
  group_id TEXT,
  timezone TEXT,
  address TEXT,
  hours NUMERIC,
  currency TEXT,
  status TEXT,
  breaks TEXT,
  declared_tips_amount NUMERIC,
  non_cash_tips_amount NUMERIC,
  job_name TEXT,
  hourly_rate NUMERIC,
  approver_user_id TEXT,
  approved_at TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Benefit
-- ======================
CREATE TABLE unified_hris_benefit (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  company_id TEXT,
  type TEXT,
  tax TEXT,
  frequency TEXT,
  is_active BOOLEAN,
  employer_contribution_type TEXT,
  employer_contribution_amount NUMERIC,
  employer_contribution_max_amount NUMERIC,
  coverage_level TEXT,
  currency TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Deduction
-- ======================
CREATE TABLE unified_hris_deduction (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  company_id TEXT,
  benefit_id TEXT,
  amount NUMERIC,
  type TEXT,
  coverage_level TEXT,
  frequency TEXT,
  start_at TEXT,
  end_at TEXT,
  is_active BOOLEAN,
  notes TEXT,
  employer_amount NUMERIC,
  employer_type TEXT,
  max_amount NUMERIC,
  paycode_id TEXT,
  garnishment_type TEXT,
  raw TEXT
);
-- ======================
-- HRIS: Bankaccount
-- ======================
CREATE TABLE unified_hris_bankaccount (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  company_id TEXT,
  account_type TEXT,
  bank_name TEXT,
  routing_number TEXT,
  account_number TEXT,
  account_number_last4 TEXT,
  name TEXT,
  is_primary BOOLEAN,
  iban TEXT,
  bic TEXT,
  country_code TEXT,
  currency TEXT,
  split_type TEXT,
  split_amount NUMERIC,
  priority NUMERIC,
  raw TEXT
);
-- ======================
-- HRIS: Taxonomy
-- ======================
CREATE TABLE unified_hris_taxonomy (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  type TEXT,
  name TEXT,
  description TEXT,
  domain TEXT,
  category TEXT,
  subcategory TEXT,
  parent_id TEXT,
  alternative_names TEXT,
  url TEXT,
  role_ids TEXT,
  is_active BOOLEAN,
  raw TEXT
);
-- ======================
-- HRIS: Document
-- ======================
CREATE TABLE unified_hris_document (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  document_url TEXT,
  document_data TEXT,
  filename TEXT,
  type TEXT,
  user_id TEXT,
  company_id TEXT,
  raw TEXT
);
-- ======================
-- VERIFICATION: Package
-- ======================
CREATE TABLE unified_verification_package (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  aliases TEXT,
  tags TEXT,
  description TEXT,
  parameters TEXT,
  average_processing_times TEXT,
  has_redirect_url BOOLEAN,
  has_target_url BOOLEAN,
  needs_ip_address BOOLEAN,
  cost_amount NUMERIC,
  currency TEXT,
  max_score NUMERIC,
  info_url TEXT,
  valid_regions TEXT,
  raw TEXT
);
-- ======================
-- VERIFICATION: Request
-- ======================
CREATE TABLE unified_verification_request (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  package_id TEXT,
  parameters TEXT,
  target_url TEXT,
  candidate_id TEXT,
  profile_ip_address TEXT,
  profile_name TEXT,
  profile_date_of_birth TEXT,
  profile_addresses TEXT,
  profile_gender TEXT,
  profile_emails TEXT,
  profile_telephones TEXT,
  profile_national_identifier TEXT,
  response_completed_at TEXT,
  response_expires_at TEXT,
  response_issued_at TEXT,
  response_status TEXT,
  response_score NUMERIC,
  response_redirect_url TEXT,
  response_download_urls TEXT,
  response_details TEXT,
  response_source TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Account
-- ======================
CREATE TABLE unified_accounting_account (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  type TEXT,
  status TEXT,
  balance NUMERIC,
  currency TEXT,
  customer_defined_code TEXT,
  is_payable BOOLEAN,
  parent_id TEXT,
  taxonomy TEXT,
  organization_id TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Journal
-- ======================
CREATE TABLE unified_accounting_journal (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  reference TEXT,
  tax_amount NUMERIC,
  currency TEXT,
  lineitems TEXT,
  taxrate_id TEXT,
  description TEXT,
  posted_at TEXT,
  source TEXT,
  organization_id TEXT,
  category_ids TEXT,
  project_id TEXT,
  attachments TEXT,
  total_amount NUMERIC,
  exchange_rate NUMERIC,
  status TEXT,
  is_inclusive_of_tax BOOLEAN,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Transaction
-- ======================
CREATE TABLE unified_accounting_transaction (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  memo TEXT,
  total_amount NUMERIC,
  tax_amount NUMERIC,
  account_id TEXT,
  reference TEXT,
  sub_total_amount NUMERIC,
  split_account_id TEXT,
  payment_method TEXT,
  payment_terms TEXT,
  customer_message TEXT,
  type TEXT,
  lineitems TEXT,
  currency TEXT,
  contacts TEXT,
  organization_id TEXT,
  category_ids TEXT,
  project_id TEXT,
  transaction_at TEXT,
  exchange_rate NUMERIC,
  status TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Contact
-- ======================
CREATE TABLE unified_accounting_contact (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  emails TEXT,
  telephones TEXT,
  currency TEXT,
  billing_address TEXT,
  shipping_address TEXT,
  is_active BOOLEAN,
  tax_exemption TEXT,
  tax_number TEXT,
  is_customer BOOLEAN,
  is_supplier BOOLEAN,
  portal_url TEXT,
  payment_methods TEXT,
  company_name TEXT,
  identification TEXT,
  associated_contacts TEXT,
  organization_id TEXT,
  payment_terms TEXT,
  paymentterm_id TEXT,
  balance_amount NUMERIC,
  website TEXT,
  notes TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Invoice
-- ======================
CREATE TABLE unified_accounting_invoice (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  due_at TEXT,
  paid_at TEXT,
  refunded_at TEXT,
  cancelled_at TEXT,
  posted_at TEXT,
  total_amount NUMERIC,
  paid_amount NUMERIC,
  refund_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  balance_amount NUMERIC,
  invoice_number TEXT,
  reference TEXT,
  contact_id TEXT,
  currency TEXT,
  notes TEXT,
  extended_notes TEXT,
  refund_reason TEXT,
  term TEXT,
  payment_terms TEXT,
  paymentterm_id TEXT,
  lineitems TEXT,
  status TEXT,
  url TEXT,
  payment_collection_method TEXT,
  type TEXT,
  attachments TEXT,
  send BOOLEAN,
  organization_id TEXT,
  payments TEXT,
  category_ids TEXT,
  project_id TEXT,
  metadata TEXT,
  sub_total_amount NUMERIC,
  exchange_rate NUMERIC,
  is_inclusive_of_tax BOOLEAN,
  salesorder_ids TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Bill
-- ======================
CREATE TABLE unified_accounting_bill (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  bill_number TEXT,
  created_at TEXT,
  updated_at TEXT,
  due_at TEXT,
  paid_at TEXT,
  refunded_at TEXT,
  cancelled_at TEXT,
  posted_at TEXT,
  total_amount NUMERIC,
  paid_amount NUMERIC,
  refund_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  balance_amount NUMERIC,
  contact_id TEXT,
  currency TEXT,
  notes TEXT,
  extended_notes TEXT,
  refund_reason TEXT,
  lineitems TEXT,
  status TEXT,
  url TEXT,
  payment_collection_method TEXT,
  attachments TEXT,
  send BOOLEAN,
  organization_id TEXT,
  term TEXT,
  payment_terms TEXT,
  paymentterm_id TEXT,
  payments TEXT,
  category_ids TEXT,
  project_id TEXT,
  metadata TEXT,
  sub_total_amount NUMERIC,
  exchange_rate NUMERIC,
  purchaseorder_ids TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Creditmemo
-- ======================
CREATE TABLE unified_accounting_creditmemo (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  due_at TEXT,
  paid_at TEXT,
  refunded_at TEXT,
  cancelled_at TEXT,
  posted_at TEXT,
  total_amount NUMERIC,
  paid_amount NUMERIC,
  refund_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  balance_amount NUMERIC,
  creditmemo_number TEXT,
  contact_id TEXT,
  invoice_id TEXT,
  currency TEXT,
  notes TEXT,
  refund_reason TEXT,
  lineitems TEXT,
  status TEXT,
  url TEXT,
  payment_collection_method TEXT,
  attachments TEXT,
  send BOOLEAN,
  organization_id TEXT,
  apply_amount NUMERIC,
  applications TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Vendorcredit
-- ======================
CREATE TABLE unified_accounting_vendorcredit (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  due_at TEXT,
  posted_at TEXT,
  total_amount NUMERIC,
  balance_amount NUMERIC,
  account_id TEXT,
  currency TEXT,
  contact_id TEXT,
  bill_id TEXT,
  notes TEXT,
  lineitems TEXT,
  status TEXT,
  organization_id TEXT,
  apply_amount NUMERIC,
  applications TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Taxrate
-- ======================
CREATE TABLE unified_accounting_taxrate (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  rate NUMERIC,
  is_active BOOLEAN,
  organization_id TEXT,
  metadata TEXT,
  effective_rate NUMERIC,
  total_rate NUMERIC,
  components TEXT,
  type TEXT,
  is_compound BOOLEAN,
  country TEXT,
  region TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Paymentterm
-- ======================
CREATE TABLE unified_accounting_paymentterm (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  type TEXT,
  category TEXT,
  is_active BOOLEAN,
  due_days NUMERIC,
  discount_days NUMERIC,
  discount_percent NUMERIC,
  day_of_month_due NUMERIC,
  discount_day_of_month NUMERIC,
  due_next_month_days NUMERIC,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Organization
-- ======================
CREATE TABLE unified_accounting_organization (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  legal_name TEXT,
  currency TEXT,
  address TEXT,
  tax_number TEXT,
  timezone TEXT,
  website TEXT,
  parent_id TEXT,
  fiscal_year_end_month NUMERIC,
  organization_code TEXT,
  type TEXT,
  is_elimination BOOLEAN,
  books_close_at TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Order
-- ======================
CREATE TABLE unified_accounting_order (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  posted_at TEXT,
  contact_id TEXT,
  account_id TEXT,
  type TEXT,
  currency TEXT,
  total_amount NUMERIC,
  shipping_address TEXT,
  billing_address TEXT,
  status TEXT,
  lineitems TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Purchaseorder
-- ======================
CREATE TABLE unified_accounting_purchaseorder (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  posted_at TEXT,
  contact_id TEXT,
  account_id TEXT,
  currency TEXT,
  total_amount NUMERIC,
  shipping_address TEXT,
  billing_address TEXT,
  status TEXT,
  lineitems TEXT,
  organization_id TEXT,
  category_ids TEXT,
  metadata TEXT,
  attachments TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Salesorder
-- ======================
CREATE TABLE unified_accounting_salesorder (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  posted_at TEXT,
  contact_id TEXT,
  account_id TEXT,
  currency TEXT,
  total_amount NUMERIC,
  shipping_address TEXT,
  billing_address TEXT,
  status TEXT,
  lineitems TEXT,
  sales_channel TEXT,
  organization_id TEXT,
  fees TEXT,
  category_ids TEXT,
  metadata TEXT,
  order_number TEXT,
  location_id TEXT,
  employee_user_id TEXT,
  device_id TEXT,
  fulfillment_type TEXT,
  guest_count NUMERIC,
  subtotal_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  tip_amount NUMERIC,
  service_charge_amount NUMERIC,
  refunded_amount NUMERIC,
  closed_at TEXT,
  subscription_id TEXT,
  payments TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Salesreceipt
-- ======================
CREATE TABLE unified_accounting_salesreceipt (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT,
  receipt_number TEXT,
  reference TEXT,
  contact_id TEXT,
  account_id TEXT,
  posted_at TEXT,
  currency TEXT,
  exchange_rate NUMERIC,
  sub_total_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  total_amount NUMERIC,
  is_inclusive_of_tax BOOLEAN,
  payment_method TEXT,
  notes TEXT,
  lineitems TEXT,
  billing_address TEXT,
  shipping_address TEXT,
  category_ids TEXT,
  project_id TEXT,
  attachments TEXT,
  status TEXT
);
-- ======================
-- ACCOUNTING: Balancesheet
-- ======================
CREATE TABLE unified_accounting_balancesheet (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  end_at TEXT,
  name TEXT,
  currency TEXT,
  net_assets_amount NUMERIC,
  assets TEXT,
  liabilities TEXT,
  equity TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Trialbalance
-- ======================
CREATE TABLE unified_accounting_trialbalance (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  name TEXT,
  currency TEXT,
  end_at TEXT,
  total_debit_amount NUMERIC,
  total_credit_amount NUMERIC,
  sub_items TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Profitloss
-- ======================
CREATE TABLE unified_accounting_profitlos (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  category_ids TEXT,
  start_at TEXT,
  end_at TEXT,
  name TEXT,
  currency TEXT,
  income_total_amount NUMERIC,
  net_income_amount NUMERIC,
  expenses_total_amount NUMERIC,
  cost_of_goods_sold_total_amount NUMERIC,
  income_sections TEXT,
  expenses_sections TEXT,
  cost_of_goods_sold_sections TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Cashflow
-- ======================
CREATE TABLE unified_accounting_cashflow (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  end_at TEXT,
  category_ids TEXT,
  contact_id TEXT,
  name TEXT,
  currency TEXT,
  cash_beginning_amount NUMERIC,
  cash_ending_amount NUMERIC,
  net_change_in_cash_amount NUMERIC,
  operating_sections TEXT,
  investing_sections TEXT,
  financing_sections TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Category
-- ======================
CREATE TABLE unified_accounting_category (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_active BOOLEAN,
  parent_id TEXT,
  type TEXT,
  code TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Expense
-- ======================
CREATE TABLE unified_accounting_expense (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  contact_id TEXT,
  account_id TEXT,
  name TEXT,
  payment_method TEXT,
  posted_at TEXT,
  total_amount NUMERIC,
  currency TEXT,
  tax_amount NUMERIC,
  reimbursed_amount NUMERIC,
  reimbursed_at TEXT,
  approved_at TEXT,
  approver_user_id TEXT,
  lineitems TEXT,
  attachments TEXT,
  organization_id TEXT,
  users TEXT,
  approver_users TEXT,
  status TEXT,
  external_number TEXT,
  category_ids TEXT,
  project_id TEXT,
  metadata TEXT,
  taxrate_id TEXT,
  exchange_rate NUMERIC,
  type TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Expensereport
-- ======================
CREATE TABLE unified_accounting_expensereport (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  user_id TEXT,
  approver_user_id TEXT,
  approver_users TEXT,
  status TEXT,
  total_amount NUMERIC,
  currency TEXT,
  tax_amount NUMERIC,
  reimbursed_amount NUMERIC,
  reimbursed_at TEXT,
  approved_at TEXT,
  posted_at TEXT,
  external_number TEXT,
  lineitems TEXT,
  attachments TEXT,
  category_ids TEXT,
  project_id TEXT,
  users TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Purchasereceipt
-- ======================
CREATE TABLE unified_accounting_purchasereceipt (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT,
  receipt_number TEXT,
  contact_id TEXT,
  purchaseorder_id TEXT,
  posted_at TEXT,
  status TEXT,
  currency TEXT,
  total_amount NUMERIC,
  notes TEXT,
  lineitems TEXT,
  attachments TEXT
);
-- ======================
-- ACCOUNTING: Quote
-- ======================
CREATE TABLE unified_accounting_quote (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  quote_number TEXT,
  reference TEXT,
  title TEXT,
  summary TEXT,
  payment_terms TEXT,
  customer_message TEXT,
  memo TEXT,
  contact_id TEXT,
  contacts TEXT,
  issued_at TEXT,
  expires_at TEXT,
  sent_at TEXT,
  accepted_at TEXT,
  declined_at TEXT,
  status TEXT,
  currency TEXT,
  currency_rate NUMERIC,
  sub_total_amount NUMERIC,
  tax_amount NUMERIC,
  discount_amount NUMERIC,
  total_amount NUMERIC,
  tax_mode TEXT,
  lineitems TEXT,
  invoice_id TEXT,
  project_id TEXT,
  group_id TEXT,
  category_ids TEXT,
  url TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Agedreceivable
-- ======================
CREATE TABLE unified_accounting_agedreceivable (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  currency TEXT,
  start_at TEXT,
  end_at TEXT,
  total_current_amount NUMERIC,
  total_overdue_amount NUMERIC,
  total_amount NUMERIC,
  periods TEXT,
  organization_id TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Agedpayable
-- ======================
CREATE TABLE unified_accounting_agedpayable (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  currency TEXT,
  start_at TEXT,
  end_at TEXT,
  total_current_amount NUMERIC,
  total_overdue_amount NUMERIC,
  total_amount NUMERIC,
  periods TEXT,
  organization_id TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Project
-- ======================
CREATE TABLE unified_accounting_project (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  code TEXT,
  description TEXT,
  status TEXT,
  is_active BOOLEAN,
  is_billable BOOLEAN,
  contact_id TEXT,
  parent_id TEXT,
  manager_user_id TEXT,
  started_at TEXT,
  due_at TEXT,
  ended_at TEXT,
  currency TEXT,
  estimate_amount NUMERIC,
  estimated_cost_amount NUMERIC,
  actual_cost_amount NUMERIC,
  invoiced_amount NUMERIC,
  to_be_invoiced_amount NUMERIC,
  expense_amount NUMERIC,
  deposit_amount NUMERIC,
  deposit_applied_amount NUMERIC,
  credit_note_amount NUMERIC,
  minutes_logged NUMERIC,
  minutes_to_be_invoiced NUMERIC,
  percent_complete NUMERIC,
  billing_type TEXT,
  category_ids TEXT,
  location_id TEXT,
  organization_id TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Bankfeedaccount
-- ======================
CREATE TABLE unified_accounting_bankfeedaccount (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  organization_id TEXT,
  name TEXT,
  bank_name TEXT,
  account_number TEXT,
  account_number_last4 TEXT,
  routing_number TEXT,
  account_type TEXT,
  account_id TEXT,
  currency TEXT,
  balance NUMERIC,
  feed_start_at TEXT,
  status TEXT,
  raw TEXT
);
-- ======================
-- ACCOUNTING: Bankfeedtransaction
-- ======================
CREATE TABLE unified_accounting_bankfeedtransaction (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  organization_id TEXT,
  bankfeedaccount_id TEXT,
  transaction_at TEXT,
  posted_at TEXT,
  amount NUMERIC,
  type TEXT,
  bank_category TEXT,
  description TEXT,
  merchant_name TEXT,
  is_pending BOOLEAN,
  reference TEXT,
  currency TEXT,
  contact_id TEXT,
  account_id TEXT,
  category_ids TEXT,
  raw TEXT
);
-- ======================
-- STORAGE: File
-- ======================
CREATE TABLE unified_storage_file (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  parent_id TEXT,
  user_id TEXT,
  size NUMERIC,
  type TEXT,
  mime_type TEXT,
  permissions TEXT,
  download_url TEXT,
  hash TEXT,
  data TEXT,
  version TEXT,
  web_url TEXT,
  "references" TEXT,
  tags TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Item
-- ======================
CREATE TABLE unified_commerce_item (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  public_name TEXT,
  slug TEXT,
  description TEXT,
  global_code TEXT,
  public_description TEXT,
  is_active BOOLEAN,
  is_taxable BOOLEAN,
  vendor_name TEXT,
  type TEXT,
  is_visible BOOLEAN,
  is_featured BOOLEAN,
  weight NUMERIC,
  weight_unit TEXT,
  requires_shipping BOOLEAN,
  prices TEXT,
  inventory_id TEXT,
  total_stock NUMERIC,
  tags TEXT,
  media TEXT,
  account_id TEXT,
  metadata TEXT,
  collections TEXT,
  taxrate_id TEXT,
  location_id TEXT,
  duration NUMERIC,
  raw TEXT
);
-- ======================
-- COMMERCE: Collection
-- ======================
CREATE TABLE unified_commerce_collection (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  public_name TEXT,
  description TEXT,
  public_description TEXT,
  media TEXT,
  is_visible BOOLEAN,
  is_active BOOLEAN,
  is_featured BOOLEAN,
  tags TEXT,
  type TEXT,
  parent_id TEXT,
  metadata TEXT,
  item_metadata TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Inventory
-- ======================
CREATE TABLE unified_commerce_inventory (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  updated_at TEXT,
  item_id TEXT,
  item_variant_id TEXT,
  item_option_id TEXT,
  location_id TEXT,
  available NUMERIC,
  raw TEXT
);
-- ======================
-- COMMERCE: Location
-- ======================
CREATE TABLE unified_commerce_location (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  address TEXT,
  description TEXT,
  is_active BOOLEAN,
  language_locale TEXT,
  parent_id TEXT,
  currency TEXT,
  location_type TEXT,
  telephones TEXT,
  rating NUMERIC,
  review_count NUMERIC,
  price_level TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  image_url TEXT,
  web_url TEXT,
  media TEXT,
  raw TEXT,
  categories TEXT
);
-- ======================
-- COMMERCE: Review
-- ======================
CREATE TABLE unified_commerce_review (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  item_id TEXT,
  item_variant_id TEXT,
  location_id TEXT,
  rating NUMERIC,
  title TEXT,
  content TEXT,
  author_name TEXT,
  author_email TEXT,
  author_avatar_url TEXT,
  author_location TEXT,
  verified_purchase BOOLEAN,
  helpful_votes NUMERIC,
  unhelpful_votes NUMERIC,
  media TEXT,
  status TEXT,
  is_verified BOOLEAN,
  is_featured BOOLEAN,
  is_public BOOLEAN,
  comments TEXT,
  metadata TEXT,
  url TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Reservation
-- ======================
CREATE TABLE unified_commerce_reservation (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  location_id TEXT,
  start_at TEXT,
  end_at TEXT,
  size NUMERIC,
  status TEXT,
  guest_name TEXT,
  guest_phone TEXT,
  guest_email TEXT,
  notes TEXT,
  item_id TEXT,
  item_name TEXT,
  staff_user_id TEXT,
  staff_name TEXT,
  created_at TEXT,
  updated_at TEXT,
  url TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Availability
-- ======================
CREATE TABLE unified_commerce_availability (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  location_id TEXT,
  start_at TEXT,
  end_at TEXT,
  size NUMERIC,
  item_id TEXT,
  staff_user_id TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Saleschannel
-- ======================
CREATE TABLE unified_commerce_saleschannel (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  slug TEXT,
  description TEXT,
  is_active BOOLEAN,
  collections TEXT,
  raw TEXT
);
-- ======================
-- COMMERCE: Itemvariant
-- ======================
CREATE TABLE unified_commerce_itemvariant (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  public_name TEXT,
  description TEXT,
  public_description TEXT,
  sku TEXT,
  is_active BOOLEAN,
  is_visible BOOLEAN,
  is_featured BOOLEAN,
  media TEXT,
  available_at TEXT,
  tags TEXT,
  width NUMERIC,
  height NUMERIC,
  length NUMERIC,
  weight NUMERIC,
  size_unit TEXT,
  weight_unit TEXT,
  total_stock NUMERIC,
  prices TEXT,
  options TEXT,
  inventory_id TEXT,
  requires_shipping BOOLEAN,
  metadata TEXT,
  items TEXT,
  raw TEXT
);
-- ======================
-- PAYMENT: Payment
-- ======================
CREATE TABLE unified_payment_payment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  total_amount NUMERIC,
  contact_id TEXT,
  payment_method TEXT,
  type TEXT,
  currency TEXT,
  notes TEXT,
  invoice_id TEXT,
  bill_id TEXT,
  link_id TEXT,
  account_id TEXT,
  reference TEXT,
  organization_id TEXT,
  allocations TEXT,
  status TEXT,
  salesorder_id TEXT,
  tender_type TEXT,
  tip_amount NUMERIC,
  fee_amount NUMERIC,
  location_id TEXT,
  device_id TEXT,
  card_brand TEXT,
  card_last4 TEXT,
  paid_at TEXT,
  exchange_rate NUMERIC,
  category_ids TEXT,
  net_amount NUMERIC,
  raw TEXT
);
-- ======================
-- PAYMENT: Link
-- ======================
CREATE TABLE unified_payment_link (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  is_active BOOLEAN,
  lineitems TEXT,
  currency TEXT,
  amount NUMERIC,
  payment_id TEXT,
  contact_id TEXT,
  url TEXT,
  description TEXT,
  is_chargeable_now BOOLEAN,
  success_url TEXT,
  raw TEXT
);
-- ======================
-- PAYMENT: Refund
-- ======================
CREATE TABLE unified_payment_refund (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  total_amount NUMERIC,
  payment_id TEXT,
  currency TEXT,
  notes TEXT,
  status TEXT,
  reference TEXT,
  refunded_at TEXT,
  reason TEXT,
  tender_type TEXT,
  raw TEXT
);
-- ======================
-- PAYMENT: Payout
-- ======================
CREATE TABLE unified_payment_payout (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  total_amount NUMERIC,
  currency TEXT,
  notes TEXT,
  status TEXT,
  arrival_at TEXT,
  fee_amount NUMERIC,
  net_amount NUMERIC,
  account_id TEXT,
  lineitems TEXT,
  raw TEXT
);
-- ======================
-- PAYMENT: Subscription
-- ======================
CREATE TABLE unified_payment_subscription (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  description TEXT,
  contact_id TEXT,
  invoice_id TEXT,
  current_period_end_at TEXT,
  current_period_start_at TEXT,
  canceled_at TEXT,
  currency TEXT,
  total_amount NUMERIC,
  start_at TEXT,
  end_at TEXT,
  status TEXT,
  month NUMERIC,
  interval_unit TEXT,
  day_of_month NUMERIC,
  day_of_week NUMERIC,
  interval NUMERIC,
  lineitems TEXT,
  raw TEXT
);
-- ======================
-- GENAI: Model
-- ======================
CREATE TABLE unified_genai_model (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  name TEXT,
  description TEXT,
  max_tokens NUMERIC,
  web_url TEXT,
  has_temperature BOOLEAN,
  has_questions BOOLEAN,
  has_vision BOOLEAN,
  raw TEXT
);
-- ======================
-- GENAI: Task
-- ======================
CREATE TABLE unified_genai_task (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  instructions TEXT,
  status TEXT,
  model_id TEXT,
  user_id TEXT,
  repo_url TEXT,
  source_branch_identifier TEXT,
  target_branch_identifier TEXT,
  pullrequest_url TEXT,
  web_url TEXT,
  messages TEXT,
  summary TEXT,
  error TEXT,
  files_changed NUMERIC,
  lines_added NUMERIC,
  lines_deleted NUMERIC,
  tokens_used NUMERIC,
  started_at TEXT,
  completed_at TEXT,
  agent_id TEXT,
  organization_id TEXT,
  raw TEXT
);
-- ======================
-- GENAI: Agent
-- ======================
CREATE TABLE unified_genai_agent (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  instructions TEXT,
  model_id TEXT,
  is_active BOOLEAN,
  raw TEXT
);
-- ======================
-- GENAI: Organization
-- ======================
CREATE TABLE unified_genai_organization (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_active BOOLEAN,
  raw TEXT
);
-- ======================
-- GENAI: Skill
-- ======================
CREATE TABLE unified_genai_skill (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  version TEXT,
  raw TEXT
);
-- ======================
-- KMS: Space
-- ======================
CREATE TABLE unified_kms_space (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  parent_id TEXT,
  is_active BOOLEAN,
  user_id TEXT,
  parent_page_id TEXT,
  raw TEXT
);
-- ======================
-- KMS: Page
-- ======================
CREATE TABLE unified_kms_page (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  title TEXT,
  type TEXT,
  space_id TEXT,
  parent_id TEXT,
  is_active BOOLEAN,
  user_id TEXT,
  download_url TEXT,
  metadata TEXT,
  has_children BOOLEAN,
  web_url TEXT,
  raw TEXT
);
-- ======================
-- KMS: Comment
-- ======================
CREATE TABLE unified_kms_comment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  type TEXT,
  content_type TEXT,
  content TEXT,
  user_id TEXT,
  page_id TEXT,
  parent_id TEXT,
  raw TEXT
);
-- ======================
-- TASK: Project
-- ======================
CREATE TABLE unified_task_project (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  parent_id TEXT,
  user_ids TEXT,
  group_ids TEXT,
  description TEXT,
  has_tasks BOOLEAN,
  has_children BOOLEAN,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- TASK: Task
-- ======================
CREATE TABLE unified_task_task (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  project_id TEXT,
  parent_id TEXT,
  completed_at TEXT,
  status TEXT,
  notes TEXT,
  due_at TEXT,
  start_at TEXT,
  end_at TEXT,
  priority TEXT,
  assigned_user_ids TEXT,
  creator_user_id TEXT,
  follower_user_ids TEXT,
  group_ids TEXT,
  tags TEXT,
  url TEXT,
  attachment_ids TEXT,
  metadata TEXT,
  has_children BOOLEAN,
  type TEXT,
  time_spent NUMERIC,
  time_spent_unit TEXT,
  progress NUMERIC,
  story_points NUMERIC,
  raw TEXT
);
-- ======================
-- TASK: Comment
-- ======================
CREATE TABLE unified_task_comment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  text TEXT,
  user_id TEXT,
  user_name TEXT,
  task_id TEXT,
  parent_id TEXT,
  has_children BOOLEAN,
  raw TEXT
);
-- ======================
-- TASK: Change
-- ======================
CREATE TABLE unified_task_change (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  task_id TEXT,
  user_id TEXT,
  items TEXT,
  raw TEXT
);
-- ======================
-- CALENDAR: Calendar
-- ======================
CREATE TABLE unified_calendar_calendar (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  timezone TEXT,
  is_primary BOOLEAN,
  raw TEXT
);
-- ======================
-- CALENDAR: Event
-- ======================
CREATE TABLE unified_calendar_event (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  calendar_id TEXT,
  subject TEXT,
  start_at TEXT,
  end_at TEXT,
  is_all_day BOOLEAN,
  timezone TEXT,
  notes TEXT,
  location TEXT,
  is_free BOOLEAN,
  is_private BOOLEAN,
  status TEXT,
  organizer TEXT,
  attendees TEXT,
  recurring_event_id TEXT,
  recurrence TEXT,
  web_url TEXT,
  has_conference BOOLEAN,
  conference TEXT,
  attachments TEXT,
  send_notifications BOOLEAN,
  matter_id TEXT,
  raw TEXT
);
-- ======================
-- CALENDAR: Busy
-- ======================
CREATE TABLE unified_calendar_busy (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  start_at TEXT,
  end_at TEXT,
  timezone TEXT,
  description TEXT,
  raw TEXT
);
-- ======================
-- CALENDAR: Link
-- ======================
CREATE TABLE unified_calendar_link (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  url TEXT,
  duration NUMERIC,
  description TEXT,
  is_active BOOLEAN,
  price_amount NUMERIC,
  price_currency TEXT,
  raw TEXT
);
-- ======================
-- CALENDAR: Recording
-- ======================
CREATE TABLE unified_calendar_recording (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  end_at TEXT,
  expires_at TEXT,
  event_id TEXT,
  web_url TEXT,
  media TEXT,
  raw TEXT
);
-- ======================
-- CALENDAR: Webinar
-- ======================
CREATE TABLE unified_calendar_webinar (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  calendar_id TEXT,
  subject TEXT,
  start_at TEXT,
  end_at TEXT,
  timezone TEXT,
  notes TEXT,
  status TEXT,
  organizer TEXT,
  join_url TEXT,
  web_url TEXT,
  panelists TEXT,
  registrants TEXT,
  panelist_password TEXT,
  registrant_password TEXT,
  conference TEXT,
  recurrence TEXT,
  capacity NUMERIC,
  is_webcast BOOLEAN,
  is_enabled BOOLEAN,
  is_auto_approve BOOLEAN,
  require_first_name BOOLEAN,
  require_last_name BOOLEAN,
  require_email BOOLEAN,
  require_company BOOLEAN,
  require_job_title BOOLEAN,
  require_address BOOLEAN,
  require_phone BOOLEAN,
  has_qa BOOLEAN,
  has_polls BOOLEAN,
  has_recording BOOLEAN,
  raw TEXT
);
-- ======================
-- ADS: Organization
-- ======================
CREATE TABLE unified_ads_organization (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  currency TEXT,
  timezone TEXT,
  parent_id TEXT,
  status TEXT,
  account_number TEXT,
  managers TEXT,
  raw TEXT
);
-- ======================
-- ADS: Campaign
-- ======================
CREATE TABLE unified_ads_campaign (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  organization_id TEXT,
  status TEXT,
  effective_status TEXT,
  start_at TEXT,
  end_at TEXT,
  budget_amount NUMERIC,
  budget_period TEXT,
  budget_unit TEXT,
  total_spend_amount NUMERIC,
  targeting TEXT,
  goal TEXT,
  planned_spend_amount NUMERIC,
  frequency_cap TEXT,
  advertising_channel_type TEXT,
  campaign_budget_identifier TEXT,
  currency TEXT,
  category TEXT,
  has_eu_political_ads BOOLEAN,
  labels TEXT,
  kpi TEXT,
  raw TEXT
);
-- ======================
-- ADS: Creative
-- ======================
CREATE TABLE unified_ads_creative (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  campaign_id TEXT,
  group_id TEXT,
  item_id TEXT,
  organization_id TEXT,
  status TEXT,
  creative_type TEXT,
  hosting_source TEXT,
  width NUMERIC,
  height NUMERIC,
  asset_urls TEXT,
  link_url TEXT,
  url_tags TEXT,
  body TEXT,
  title TEXT,
  cta TEXT,
  third_party_tag TEXT,
  vast_tag_url TEXT,
  external_creative_reference TEXT,
  external_placement_reference TEXT,
  external_ad_reference TEXT,
  promoted TEXT,
  path1 TEXT,
  path2 TEXT,
  data TEXT,
  labels TEXT,
  raw TEXT
);
-- ======================
-- ADS: Asset
-- ======================
CREATE TABLE unified_ads_asset (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  organization_id TEXT,
  name TEXT,
  type TEXT,
  url TEXT,
  content TEXT,
  mime_type TEXT,
  width NUMERIC,
  height NUMERIC,
  file_size NUMERIC,
  raw TEXT
);
-- ======================
-- ADS: Insertionorder
-- ======================
CREATE TABLE unified_ads_insertionorder (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  organization_id TEXT,
  campaign_id TEXT,
  status TEXT,
  pacing TEXT,
  frequency_cap TEXT,
  kpi TEXT,
  budget_unit TEXT,
  budget_segments TEXT,
  bid_strategy TEXT,
  reference TEXT,
  raw TEXT
);
-- ======================
-- ADS: Group
-- ======================
CREATE TABLE unified_ads_group (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  parent_id TEXT,
  campaign_id TEXT,
  organization_id TEXT,
  insertionorder_id TEXT,
  status TEXT,
  effective_status TEXT,
  targeting TEXT,
  bid_amount NUMERIC,
  bid_strategy TEXT,
  budget_amount NUMERIC,
  budget_period TEXT,
  budget_allocation_type TEXT,
  start_at TEXT,
  end_at TEXT,
  budget_unit TEXT,
  budget_max_amount NUMERIC,
  type TEXT,
  has_eu_political_ads BOOLEAN,
  pacing TEXT,
  frequency_cap TEXT,
  creative_ids TEXT,
  optimization_goal TEXT,
  billing_event TEXT,
  currency TEXT,
  promoted TEXT,
  language_locale TEXT,
  creative_selection TEXT,
  raw TEXT
);
-- ======================
-- ADS: Ad
-- ======================
CREATE TABLE unified_ads_ad (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  campaign_id TEXT,
  group_id TEXT,
  organization_id TEXT,
  status TEXT,
  ad_type TEXT,
  advertiser_name TEXT,
  creative_ids TEXT,
  creative_asset_url TEXT,
  ad_copy TEXT,
  headline TEXT,
  description TEXT,
  cta TEXT,
  final_url TEXT,
  display_url TEXT,
  path1 TEXT,
  path2 TEXT,
  promoted TEXT,
  logo_creative_id TEXT,
  raw TEXT
);
-- ======================
-- ADS: Report
-- ======================
CREATE TABLE unified_ads_report (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  currency TEXT,
  metrics TEXT,
  start_at TEXT,
  end_at TEXT,
  organization_id TEXT,
  raw TEXT
);
-- ======================
-- ADS: Target
-- ======================
CREATE TABLE unified_ads_target (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  name TEXT,
  type TEXT,
  is_active BOOLEAN,
  parent_id TEXT,
  audience_count_min NUMERIC,
  audience_count_max NUMERIC,
  raw TEXT
);
-- ======================
-- ADS: Promoted
-- ======================
CREATE TABLE unified_ads_promoted (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  name TEXT,
  type TEXT,
  raw TEXT
);
-- ======================
-- LMS: Course
-- ======================
CREATE TABLE unified_lms_course (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_private BOOLEAN,
  is_active BOOLEAN,
  price_amount NUMERIC,
  languages TEXT,
  categories TEXT,
  currency TEXT,
  media TEXT,
  instructors TEXT,
  students TEXT,
  content_ids TEXT,
  skills TEXT,
  duration_minutes NUMERIC,
  provider_name TEXT,
  published_at TEXT,
  time_estimate_minutes NUMERIC,
  raw TEXT
);
-- ======================
-- LMS: Class
-- ======================
CREATE TABLE unified_lms_clas (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  media TEXT,
  course_id TEXT,
  languages TEXT,
  instructors TEXT,
  students TEXT,
  raw TEXT
);
-- ======================
-- LMS: Student
-- ======================
CREATE TABLE unified_lms_student (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  emails TEXT,
  telephones TEXT,
  address TEXT,
  image_url TEXT,
  raw TEXT
);
-- ======================
-- LMS: Instructor
-- ======================
CREATE TABLE unified_lms_instructor (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  emails TEXT,
  title TEXT,
  telephones TEXT,
  image_url TEXT,
  raw TEXT
);
-- ======================
-- LMS: Content
-- ======================
CREATE TABLE unified_lms_content (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  external_reference TEXT,
  course_ids TEXT,
  name TEXT,
  description TEXT,
  languages TEXT,
  media TEXT,
  is_active BOOLEAN,
  duration_minutes NUMERIC,
  categories TEXT,
  subjects TEXT,
  skills TEXT,
  tags TEXT,
  difficulty TEXT,
  sort_order NUMERIC,
  provider_name TEXT,
  short_description TEXT,
  localizations TEXT,
  collection_ids TEXT,
  instructors TEXT,
  published_at TEXT,
  raw TEXT
);
-- ======================
-- LMS: Collection
-- ======================
CREATE TABLE unified_lms_collection (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  media TEXT,
  is_active BOOLEAN,
  parent_id TEXT,
  raw TEXT
);
-- ======================
-- LMS: Activity
-- ======================
CREATE TABLE unified_lms_activity (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  content_id TEXT,
  course_id TEXT,
  student_id TEXT,
  duration_minutes NUMERIC,
  assigned_grade TEXT,
  is_completed BOOLEAN,
  progress_percentage NUMERIC,
  started_at TEXT,
  completed_at TEXT,
  raw TEXT
);
-- ======================
-- REPO: Organization
-- ======================
CREATE TABLE unified_repo_organization (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  avatar_url TEXT,
  web_url TEXT,
  user_ids TEXT,
  raw TEXT
);
-- ======================
-- REPO: Repository
-- ======================
CREATE TABLE unified_repo_repository (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  owner TEXT,
  is_private BOOLEAN,
  web_url TEXT,
  org_id TEXT,
  raw TEXT
);
-- ======================
-- REPO: Branch
-- ======================
CREATE TABLE unified_repo_branch (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  repo_id TEXT,
  raw TEXT
);
-- ======================
-- REPO: Commit
-- ======================
CREATE TABLE unified_repo_commit (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  repo_id TEXT,
  message TEXT,
  branch_id TEXT,
  pullrequest_ids TEXT,
  lines_added NUMERIC,
  lines_deleted NUMERIC,
  lines_changed NUMERIC,
  raw TEXT
);
-- ======================
-- REPO: Pullrequest
-- ======================
CREATE TABLE unified_repo_pullrequest (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_ids TEXT,
  repo_id TEXT,
  title TEXT,
  notes TEXT,
  target_branch_id TEXT,
  source_branch_id TEXT,
  status TEXT,
  labels TEXT,
  closed_at TEXT,
  commit_ids TEXT,
  raw TEXT
);
-- ======================
-- METADATA: Metadata
-- ======================
CREATE TABLE unified_metadata_metadata (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  slug TEXT,
  format TEXT,
  original_format TEXT,
  options TEXT,
  object_type TEXT,
  objects TEXT,
  is_required BOOLEAN,
  raw TEXT
);
-- ======================
-- FORMS: Form
-- ======================
CREATE TABLE unified_forms_form (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  fields TEXT,
  is_active BOOLEAN,
  published_url TEXT,
  response_count NUMERIC,
  has_multiple_submissions BOOLEAN,
  has_progress_bar BOOLEAN,
  has_shuffle_questions BOOLEAN,
  confirmation_message TEXT,
  confirmation_redirect_url TEXT,
  raw TEXT
);
-- ======================
-- FORMS: Submission
-- ======================
CREATE TABLE unified_forms_submission (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  form_id TEXT,
  respondent_email TEXT,
  respondent_name TEXT,
  answers TEXT,
  raw TEXT
);
-- ======================
-- DATASTORE: Database
-- ======================
CREATE TABLE unified_datastore_database (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  web_url TEXT,
  is_active BOOLEAN,
  password TEXT,
  region TEXT,
  raw TEXT
);
-- ======================
-- DATASTORE: Table
-- ======================
CREATE TABLE unified_datastore_table (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  database_id TEXT,
  fields TEXT,
  relationships TEXT,
  web_url TEXT,
  parent_id TEXT,
  raw TEXT
);
-- ======================
-- DATASTORE: Record
-- ======================
CREATE TABLE unified_datastore_record (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  database_id TEXT,
  table_id TEXT,
  fields TEXT,
  row_number NUMERIC,
  raw TEXT
);
-- ======================
-- SHIPPING: Shipment
-- ======================
CREATE TABLE unified_shipping_shipment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  order_id TEXT,
  organization_id TEXT,
  from_address TEXT,
  to_address TEXT,
  packages TEXT,
  carrier_id TEXT,
  service_code TEXT,
  status TEXT,
  rate_id TEXT,
  label_id TEXT,
  tracking_id TEXT,
  shipped_at TEXT,
  rate_amount NUMERIC,
  rate_currency TEXT,
  rate_service_name TEXT,
  rate_estimated_days NUMERIC,
  rate_estimated_delivery_at TEXT,
  is_rate_guaranteed BOOLEAN,
  return_address TEXT,
  return_authorization_number TEXT,
  warehouse_location_id TEXT,
  warehouse_location_name TEXT,
  customs TEXT,
  is_international BOOLEAN,
  insurance TEXT,
  special_instructions TEXT,
  is_signature_required BOOLEAN,
  is_adult_signature_required BOOLEAN,
  reference_number TEXT,
  is_return BOOLEAN,
  original_shipment_id TEXT,
  return_reason TEXT,
  return_type TEXT,
  carrier_name TEXT,
  tracking_url TEXT,
  lineitems TEXT,
  raw TEXT
);
-- ======================
-- SHIPPING: Label
-- ======================
CREATE TABLE unified_shipping_label (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  shipment_id TEXT,
  tracking_number TEXT,
  label_url TEXT,
  label_format TEXT,
  status TEXT,
  is_voided BOOLEAN,
  label_cost NUMERIC,
  label_cost_currency TEXT,
  rate_id TEXT,
  service_code TEXT,
  raw TEXT
);
-- ======================
-- SHIPPING: Tracking
-- ======================
CREATE TABLE unified_shipping_tracking (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  shipment_id TEXT,
  tracking_number TEXT,
  status TEXT,
  events TEXT,
  estimated_delivery TEXT,
  actual_delivery_at TEXT,
  status_description TEXT,
  carrier_id TEXT,
  carrier_status_code TEXT,
  carrier_status_description TEXT,
  raw TEXT
);
-- ======================
-- SHIPPING: Carrier
-- ======================
CREATE TABLE unified_shipping_carrier (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  code TEXT,
  is_active BOOLEAN,
  logo_url TEXT,
  website_url TEXT,
  raw TEXT
);
-- ======================
-- SIGNING: Document
-- ======================
CREATE TABLE unified_signing_document (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  status TEXT,
  sent_at TEXT,
  completed_at TEXT,
  expires_at TEXT,
  template_id TEXT,
  download_url TEXT,
  creator_id TEXT,
  raw TEXT
);
-- ======================
-- SIGNING: Signatory
-- ======================
CREATE TABLE unified_signing_signatory (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  document_id TEXT,
  name TEXT,
  email TEXT,
  role TEXT,
  status TEXT,
  "order" NUMERIC,
  signed_at TEXT,
  decline_reason TEXT,
  raw TEXT
);
-- ======================
-- SIGNING: Template
-- ======================
CREATE TABLE unified_signing_template (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  is_active BOOLEAN,
  creator_id TEXT,
  raw TEXT
);
-- ======================
-- CLUBS: Group
-- ======================
CREATE TABLE unified_clubs_group (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  sport_type TEXT,
  group_type TEXT,
  address TEXT,
  member_count NUMERIC,
  following_count NUMERIC,
  post_count NUMERIC,
  is_private BOOLEAN,
  is_verified BOOLEAN,
  is_featured BOOLEAN,
  is_admin BOOLEAN,
  is_owner BOOLEAN,
  membership_status TEXT,
  url TEXT,
  profile_image_url TEXT,
  cover_image_url TEXT,
  activity_types TEXT,
  raw TEXT
);
-- ======================
-- CLUBS: Member
-- ======================
CREATE TABLE unified_clubs_member (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  group_id TEXT,
  is_admin BOOLEAN,
  is_owner BOOLEAN,
  membership_status TEXT,
  raw TEXT
);
-- ======================
-- CLUBS: Activity
-- ======================
CREATE TABLE unified_clubs_activity (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  group_id TEXT,
  name TEXT,
  description TEXT,
  type TEXT,
  athlete_id TEXT,
  athlete_name TEXT,
  distance NUMERIC,
  moving_time NUMERIC,
  elapsed_time NUMERIC,
  total_elevation_gain NUMERIC,
  elevation_high NUMERIC,
  elevation_low NUMERIC,
  start_at TEXT,
  timezone TEXT,
  achievement_count NUMERIC,
  kudos_count NUMERIC,
  comment_count NUMERIC,
  athlete_count NUMERIC,
  photo_count NUMERIC,
  average_speed NUMERIC,
  max_speed NUMERIC,
  average_cadence NUMERIC,
  average_heartrate NUMERIC,
  max_heartrate NUMERIC,
  average_watts NUMERIC,
  max_watts NUMERIC,
  weighted_average_watts NUMERIC,
  kilojoules NUMERIC,
  calories NUMERIC,
  has_heartrate BOOLEAN,
  is_trainer BOOLEAN,
  is_commute BOOLEAN,
  is_manual BOOLEAN,
  is_private BOOLEAN,
  map_polyline TEXT,
  map_summary_polyline TEXT,
  workout_type NUMERIC,
  suffer_score NUMERIC,
  pr_count NUMERIC,
  raw TEXT
);
-- ======================
-- CLUBS: Event
-- ======================
CREATE TABLE unified_clubs_event (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  group_id TEXT,
  name TEXT,
  description TEXT,
  type TEXT,
  status TEXT,
  start_at TEXT,
  end_at TEXT,
  timezone TEXT,
  duration_minutes NUMERIC,
  location_id TEXT,
  location_name TEXT,
  opponent_id TEXT,
  opponent_name TEXT,
  home_team_name TEXT,
  away_team_name TEXT,
  home_score NUMERIC,
  away_score NUMERIC,
  score_for NUMERIC,
  score_against NUMERIC,
  is_home BOOLEAN,
  url TEXT,
  raw TEXT
);
-- ======================
-- CLUBS: Location
-- ======================
CREATE TABLE unified_clubs_location (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  group_id TEXT,
  name TEXT,
  address TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  telephone TEXT,
  url TEXT,
  raw TEXT
);
-- ======================
-- ANALYTICS: Property
-- ======================
CREATE TABLE unified_analytics_property (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  timezone TEXT,
  currency TEXT,
  industry TEXT,
  parent_id TEXT,
  raw TEXT
);
-- ======================
-- ANALYTICS: Event
-- ======================
CREATE TABLE unified_analytics_event (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  event_type TEXT,
  visitor_id TEXT,
  property_id TEXT,
  session_id TEXT,
  page_url TEXT,
  page_title TEXT,
  page_referrer TEXT,
  device TEXT,
  browser TEXT,
  os TEXT,
  country TEXT,
  country_code TEXT,
  region TEXT,
  city TEXT,
  metadata TEXT,
  value NUMERIC,
  currency TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  raw TEXT
);
-- ======================
-- ANALYTICS: Session
-- ======================
CREATE TABLE unified_analytics_session (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  property_id TEXT,
  visitor_id TEXT,
  start_at TEXT,
  end_at TEXT,
  duration_seconds NUMERIC,
  landing_page TEXT,
  exit_page TEXT,
  page_views NUMERIC,
  events_count NUMERIC,
  source TEXT,
  medium TEXT,
  campaign TEXT,
  device TEXT,
  browser TEXT,
  os TEXT,
  country TEXT,
  city TEXT,
  is_bounce BOOLEAN,
  is_conversion BOOLEAN,
  raw TEXT
);
-- ======================
-- ANALYTICS: Visitor
-- ======================
CREATE TABLE unified_analytics_visitor (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  property_id TEXT,
  email TEXT,
  name TEXT,
  age NUMERIC,
  gender TEXT,
  country TEXT,
  country_code TEXT,
  city TEXT,
  language TEXT,
  timezone TEXT,
  first_seen_at TEXT,
  last_seen_at TEXT,
  total_sessions NUMERIC,
  total_page_views NUMERIC,
  total_events NUMERIC,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- ANALYTICS: Report
-- ======================
CREATE TABLE unified_analytics_report (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  property_id TEXT,
  start_at TEXT,
  end_at TEXT,
  metrics TEXT,
  raw TEXT
);
-- ======================
-- CDP: Profile
-- ======================
CREATE TABLE unified_cdp_profile (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  telephone TEXT,
  gender TEXT,
  birthdate TEXT,
  title TEXT,
  company TEXT,
  address TEXT,
  identifiers TEXT,
  metadata TEXT,
  segments TEXT,
  is_anonymous BOOLEAN,
  consent TEXT,
  source_id TEXT,
  raw TEXT
);
-- ======================
-- CDP: Segment
-- ======================
CREATE TABLE unified_cdp_segment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  slug TEXT,
  description TEXT,
  definition TEXT,
  type TEXT,
  compute_mode TEXT,
  size NUMERIC,
  is_active BOOLEAN,
  source_id TEXT,
  raw TEXT
);
-- ======================
-- CDP: Event
-- ======================
CREATE TABLE unified_cdp_event (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  name TEXT,
  type TEXT,
  occurred_at TEXT,
  profile_id TEXT,
  identifiers TEXT,
  metadata TEXT,
  source TEXT,
  source_id TEXT,
  raw TEXT
);
-- ======================
-- CDP: Source
-- ======================
CREATE TABLE unified_cdp_source (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  slug TEXT,
  type TEXT,
  direction TEXT,
  is_enabled BOOLEAN,
  raw TEXT
);
-- ======================
-- CDP: Destination
-- ======================
CREATE TABLE unified_cdp_destination (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  slug TEXT,
  type TEXT,
  direction TEXT,
  is_enabled BOOLEAN,
  raw TEXT
);
-- ======================
-- CDP: Activation
-- ======================
CREATE TABLE unified_cdp_activation (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  segment_id TEXT,
  destination_id TEXT,
  source_id TEXT,
  schedule TEXT,
  status TEXT,
  last_run_at TEXT,
  is_enabled BOOLEAN,
  raw TEXT
);
-- ======================
-- PERFORMANCE: Cycle
-- ======================
CREATE TABLE unified_performance_cycle (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  type TEXT,
  status TEXT,
  start_at TEXT,
  end_at TEXT,
  due_at TEXT,
  raw TEXT
);
-- ======================
-- PERFORMANCE: Review
-- ======================
CREATE TABLE unified_performance_review (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  reviewer_user_id TEXT,
  cycle_id TEXT,
  template_identifier TEXT,
  type TEXT,
  status TEXT,
  rating NUMERIC,
  rating_maximum NUMERIC,
  rating_description TEXT,
  comment TEXT,
  questions TEXT,
  is_acknowledged BOOLEAN,
  submitted_at TEXT,
  completed_at TEXT,
  raw TEXT
);
-- ======================
-- PERFORMANCE: Goal
-- ======================
CREATE TABLE unified_performance_goal (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  user_ids TEXT,
  company_id TEXT,
  parent_id TEXT,
  cycle_id TEXT,
  type TEXT,
  status TEXT,
  progress NUMERIC,
  weight NUMERIC,
  start_at TEXT,
  due_at TEXT,
  completed_at TEXT,
  milestones TEXT,
  raw TEXT
);
-- ======================
-- PERFORMANCE: Feedback
-- ======================
CREATE TABLE unified_performance_feedback (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  user_id TEXT,
  author_user_id TEXT,
  type TEXT,
  message TEXT,
  tags TEXT,
  is_visible BOOLEAN,
  raw TEXT
);
-- ======================
-- SOCIAL: Post
-- ======================
CREATE TABLE unified_social_post (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  profile_id TEXT,
  parent_post_id TEXT,
  title TEXT,
  body TEXT,
  status TEXT,
  type TEXT,
  media TEXT,
  url TEXT,
  language TEXT,
  scheduled_at TEXT,
  call_to_action TEXT,
  metrics TEXT,
  raw TEXT
);
-- ======================
-- SOCIAL: Profile
-- ======================
CREATE TABLE unified_social_profile (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  username TEXT,
  parent_id TEXT,
  description TEXT,
  url TEXT,
  website_url TEXT,
  avatar_url TEXT,
  phone TEXT,
  location TEXT,
  address TEXT,
  category TEXT,
  is_verified BOOLEAN,
  is_private BOOLEAN,
  metrics TEXT,
  raw TEXT
);
-- ======================
-- SOCIAL: Review
-- ======================
CREATE TABLE unified_social_review (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  profile_id TEXT,
  rating NUMERIC,
  title TEXT,
  content TEXT,
  author_name TEXT,
  author_avatar_url TEXT,
  author_location TEXT,
  reply TEXT,
  url TEXT,
  raw TEXT
);
-- ======================
-- SOCIAL: Insight
-- ======================
CREATE TABLE unified_social_insight (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  profile_id TEXT,
  post_id TEXT,
  date TEXT,
  period TEXT,
  metric TEXT,
  value NUMERIC,
  raw TEXT
);
-- ======================
-- LEGAL: Matter
-- ======================
CREATE TABLE unified_legal_matter (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  number TEXT,
  description TEXT,
  status TEXT,
  billing_method TEXT,
  practicearea_id TEXT,
  stage TEXT,
  contact_ids TEXT,
  company_ids TEXT,
  parties TEXT,
  user_id TEXT,
  originating_user_id TEXT,
  user_ids TEXT,
  client_reference TEXT,
  currency TEXT,
  is_billable BOOLEAN,
  opened_at TEXT,
  closed_at TEXT,
  pending_at TEXT,
  statute_of_limitations_at TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- LEGAL: Practicearea
-- ======================
CREATE TABLE unified_legal_practicearea (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  code TEXT,
  is_active BOOLEAN,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- LEGAL: Timeentry
-- ======================
CREATE TABLE unified_legal_timeentry (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  matter_id TEXT,
  user_id TEXT,
  description TEXT,
  worked_at TEXT,
  minutes NUMERIC,
  billable_minutes NUMERIC,
  rate_amount NUMERIC,
  total_amount NUMERIC,
  currency TEXT,
  is_billable BOOLEAN,
  is_billed BOOLEAN,
  invoice_id TEXT,
  activity_code TEXT,
  task_code TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- LEGAL: Expense
-- ======================
CREATE TABLE unified_legal_expense (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  matter_id TEXT,
  user_id TEXT,
  description TEXT,
  incurred_at TEXT,
  quantity NUMERIC,
  price_amount NUMERIC,
  total_amount NUMERIC,
  currency TEXT,
  type TEXT,
  category TEXT,
  is_billable BOOLEAN,
  is_billed BOOLEAN,
  invoice_id TEXT,
  expense_code TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Instance
-- ======================
CREATE TABLE unified_compute_instance (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  status TEXT,
  status_reason TEXT,
  allowed_actions TEXT,
  market TEXT,
  region_id TEXT,
  template_id TEXT,
  image TEXT,
  source_snapshot_id TEXT,
  parent_instance_id TEXT,
  gputype_id TEXT,
  gpu_model TEXT,
  gpu_count NUMERIC,
  sku TEXT,
  cpu_count NUMERIC,
  memory_mb NUMERIC,
  disk_mb NUMERIC,
  architecture TEXT,
  price_amount NUMERIC,
  price_unit TEXT,
  currency TEXT,
  volume_ids TEXT,
  endpoints TEXT,
  ssh TEXT,
  has_internet_access BOOLEAN,
  timeout_seconds NUMERIC,
  expires_at TEXT,
  on_expire TEXT,
  idle_timeout_seconds NUMERIC,
  on_idle TEXT,
  project_identifier TEXT,
  service_id TEXT,
  env TEXT,
  started_at TEXT,
  terminated_at TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Template
-- ======================
CREATE TABLE unified_compute_template (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  aliases TEXT,
  image TEXT,
  dockerfile TEXT,
  start_command TEXT,
  status TEXT,
  gpu_model TEXT,
  gpu_count NUMERIC,
  cpu_count NUMERIC,
  memory_mb NUMERIC,
  disk_mb NUMERIC,
  ports TEXT,
  env TEXT,
  is_public BOOLEAN,
  last_used_at TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Gputype
-- ======================
CREATE TABLE unified_compute_gputype (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  gpu_model TEXT,
  gpu_manufacturer TEXT,
  sku TEXT,
  gpu_count NUMERIC,
  gpu_memory_mb NUMERIC,
  cpu_count NUMERIC,
  memory_mb NUMERIC,
  disk_mb NUMERIC,
  architecture TEXT,
  prices TEXT,
  availability TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Region
-- ======================
CREATE TABLE unified_compute_region (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  location TEXT,
  country TEXT,
  gpu_models TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Volume
-- ======================
CREATE TABLE unified_compute_volume (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  status TEXT,
  size_mb NUMERIC,
  used_mb NUMERIC,
  region_id TEXT,
  availability_zone TEXT,
  instance_ids TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Snapshot
-- ======================
CREATE TABLE unified_compute_snapshot (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  instance_id TEXT,
  volume_id TEXT,
  type TEXT,
  status TEXT,
  size_mb NUMERIC,
  expires_at TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Usage
-- ======================
CREATE TABLE unified_compute_usage (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  start_at TEXT,
  end_at TEXT,
  instance_id TEXT,
  category TEXT,
  quantity NUMERIC,
  unit TEXT,
  cost_amount NUMERIC,
  currency TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Key
-- ======================
CREATE TABLE unified_compute_key (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  public_key TEXT,
  private_key TEXT,
  fingerprint TEXT,
  registry_url TEXT,
  username TEXT,
  secret TEXT,
  instance_id TEXT,
  expires_at TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Service
-- ======================
CREATE TABLE unified_compute_service (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  type TEXT,
  status TEXT,
  runtime TEXT,
  region_id TEXT,
  gputype_id TEXT,
  sku TEXT,
  instance_count NUMERIC,
  min_instance_count NUMERIC,
  max_instance_count NUMERIC,
  repo_url TEXT,
  branch TEXT,
  image TEXT,
  build_command TEXT,
  start_command TEXT,
  url TEXT,
  project_identifier TEXT,
  env TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Deployment
-- ======================
CREATE TABLE unified_compute_deployment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  service_id TEXT,
  status TEXT,
  trigger TEXT,
  environment TEXT,
  commit_identifier TEXT,
  commit_message TEXT,
  branch TEXT,
  image TEXT,
  url TEXT,
  started_at TEXT,
  finished_at TEXT,
  error TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Domain
-- ======================
CREATE TABLE unified_compute_domain (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  service_id TEXT,
  name TEXT,
  status TEXT,
  is_primary BOOLEAN,
  redirect_url TEXT,
  raw TEXT
);
-- ======================
-- COMPUTE: Envvar
-- ======================
CREATE TABLE unified_compute_envvar (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  service_id TEXT,
  name TEXT,
  value TEXT,
  environments TEXT,
  is_secret BOOLEAN,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Patient
-- ======================
CREATE TABLE unified_healthcare_patient (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  gender TEXT,
  birthdate TEXT,
  is_deceased BOOLEAN,
  deceased_at TEXT,
  emails TEXT,
  telephones TEXT,
  address TEXT,
  language TEXT,
  identifiers TEXT,
  practitioner_ids TEXT,
  is_active BOOLEAN,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Practitioner
-- ======================
CREATE TABLE unified_healthcare_practitioner (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  first_name TEXT,
  last_name TEXT,
  title TEXT,
  gender TEXT,
  emails TEXT,
  telephones TEXT,
  address TEXT,
  image_url TEXT,
  identifiers TEXT,
  specialties TEXT,
  qualifications TEXT,
  languages TEXT,
  location_ids TEXT,
  is_active BOOLEAN,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Location
-- ======================
CREATE TABLE unified_healthcare_location (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  name TEXT,
  description TEXT,
  parent_id TEXT,
  organization_name TEXT,
  address TEXT,
  telephones TEXT,
  emails TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  identifiers TEXT,
  is_active BOOLEAN,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Appointment
-- ======================
CREATE TABLE unified_healthcare_appointment (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  practitioner_ids TEXT,
  location_id TEXT,
  slot_ids TEXT,
  status TEXT,
  start_at TEXT,
  end_at TEXT,
  description TEXT,
  service_types TEXT,
  reasons TEXT,
  cancellation_reason TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Slot
-- ======================
CREATE TABLE unified_healthcare_slot (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  practitioner_id TEXT,
  location_id TEXT,
  status TEXT,
  start_at TEXT,
  end_at TEXT,
  service_types TEXT,
  is_overbooked BOOLEAN,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Encounter
-- ======================
CREATE TABLE unified_healthcare_encounter (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  practitioner_ids TEXT,
  location_id TEXT,
  appointment_id TEXT,
  condition_ids TEXT,
  status TEXT,
  type TEXT,
  reasons TEXT,
  start_at TEXT,
  end_at TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Condition
-- ======================
CREATE TABLE unified_healthcare_condition (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  encounter_id TEXT,
  practitioner_id TEXT,
  name TEXT,
  codes TEXT,
  status TEXT,
  type TEXT,
  onset_at TEXT,
  resolved_at TEXT,
  recorded_at TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Allergy
-- ======================
CREATE TABLE unified_healthcare_allergy (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  encounter_id TEXT,
  practitioner_id TEXT,
  name TEXT,
  codes TEXT,
  status TEXT,
  type TEXT,
  criticality TEXT,
  reactions TEXT,
  onset_at TEXT,
  recorded_at TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Medication
-- ======================
CREATE TABLE unified_healthcare_medication (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  encounter_id TEXT,
  practitioner_id TEXT,
  name TEXT,
  codes TEXT,
  status TEXT,
  dosage TEXT,
  refill_count NUMERIC,
  authored_at TEXT,
  start_at TEXT,
  end_at TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Observation
-- ======================
CREATE TABLE unified_healthcare_observation (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  encounter_id TEXT,
  practitioner_id TEXT,
  name TEXT,
  codes TEXT,
  status TEXT,
  type TEXT,
  value_number NUMERIC,
  value_unit TEXT,
  value_text TEXT,
  interpretation TEXT,
  reference_range TEXT,
  components TEXT,
  observed_at TEXT,
  issued_at TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- HEALTHCARE: Immunization
-- ======================
CREATE TABLE unified_healthcare_immunization (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  created_at TEXT,
  updated_at TEXT,
  patient_id TEXT,
  encounter_id TEXT,
  practitioner_id TEXT,
  location_id TEXT,
  name TEXT,
  codes TEXT,
  status TEXT,
  administered_at TEXT,
  lot_number TEXT,
  expires_at TEXT,
  notes TEXT,
  metadata TEXT,
  raw TEXT
);
-- ======================
-- SCIM: Users
-- ======================
CREATE TABLE unified_scim_user (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  schemas TEXT,
  "externalId" TEXT,
  "userType" TEXT,
  "userName" TEXT,
  meta TEXT,
  name TEXT,
  "displayName" TEXT,
  "nickName" TEXT,
  "profileUrl" TEXT,
  title TEXT,
  "preferredLanguage" TEXT,
  locale TEXT,
  timezone TEXT,
  active BOOLEAN,
  password TEXT,
  "phoneNumbers" TEXT,
  emails TEXT,
  ims TEXT,
  photos TEXT,
  addresses TEXT,
  groups TEXT,
  entitlements TEXT,
  roles TEXT,
  "x509Certificates" TEXT,
  "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User" TEXT,
  "urn:ietf:params:scim:schemas:extension:lattice:attributes:1.0:User" TEXT,
  "urn:ietf:params:scim:schemas:extension:peakon:2.0:User" TEXT
);
-- ======================
-- SCIM: Groups
-- ======================
CREATE TABLE unified_scim_group (
  unified_connection_id TEXT NOT NULL,
  unified_webhook_id TEXT NOT NULL,
  unified_external_xref TEXT,
  unified_integration_type TEXT NOT NULL,
  unified_raw_id TEXT,
  unified_id TEXT NOT NULL PRIMARY KEY,
  id TEXT,
  "externalId" TEXT,
  "displayName" TEXT,
  "groupType" TEXT,
  members TEXT,
  meta TEXT,
  schemas TEXT
);
