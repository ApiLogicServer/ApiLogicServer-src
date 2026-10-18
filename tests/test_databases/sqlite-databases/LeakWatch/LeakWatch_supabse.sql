-- ======================
-- MESSAGING: Channel
-- ======================
CREATE TABLE unified_messaging_channel (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  parent_id            text,
  has_subchannels      boolean,
  members              jsonb,
  is_active            boolean,
  is_private           boolean,
  web_url              text,
  raw                  jsonb
);
-- ======================
-- MESSAGING: Message
-- ======================
CREATE TABLE unified_messaging_message (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  channels             jsonb,
  parent_id            text,
  message_thread_identifier text,
  author_member        jsonb,
  destination_members  jsonb,
  hidden_members       jsonb,
  mentioned_members    jsonb,
  reactions            jsonb,
  subject              text,
  message              text,
  message_html         text,
  message_markdown     text,
  attachments          jsonb,
  web_url              text,
  reference            text,
  has_children         boolean,
  is_unread            boolean,
  buttons              jsonb,
  raw                  jsonb
);
-- ======================
-- CRM: Deal
-- ======================
CREATE TABLE unified_crm_deal (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  amount               numeric,
  currency             text,
  closed_at            timestamptz,
  closing_at           timestamptz,
  stages               jsonb,
  pipelines            jsonb,
  source               text,
  probability          numeric,
  tags                 text[],
  lost_reason          text,
  won_reason           text,
  user_id              text,
  contact_ids          text[],
  company_ids          text[],
  description          text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- CRM: Contact
-- ======================
CREATE TABLE unified_crm_contact (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  title                text,
  company              text,
  emails               jsonb,
  telephones           jsonb,
  deal_ids             text[],
  company_ids          text[],
  address              jsonb,
  user_id              text,
  link_urls            text[],
  metadata             jsonb,
  department           text,
  image_url            text,
  raw                  jsonb
);
-- ======================
-- CRM: Company
-- ======================
CREATE TABLE unified_crm_company (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  deal_ids             text[],
  contact_ids          text[],
  emails               jsonb,
  telephones           jsonb,
  websites             text[],
  address              jsonb,
  is_active            boolean,
  tags                 text[],
  description          text,
  industry             text,
  link_urls            text[],
  employees            numeric,
  timezone             text,
  user_id              text,
  metadata             jsonb,
  domains              text[],
  raw                  jsonb
);
-- ======================
-- CRM: Event
-- ======================
CREATE TABLE unified_crm_event (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  type                 text,
  note                 jsonb,
  meeting              jsonb,
  email                jsonb,
  call                 jsonb,
  task                 jsonb,
  marketing_email      jsonb,
  form                 jsonb,
  page_view            jsonb,
  deal_ids             text[],
  company_ids          text[],
  contact_ids          text[],
  lead_ids             text[],
  user_id              text,
  raw                  jsonb
);
-- ======================
-- CRM: Lead
-- ======================
CREATE TABLE unified_crm_lead (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  user_id              text,
  creator_user_id      text,
  contact_id           text,
  company_id           text,
  company_name         text,
  is_active            boolean,
  address              jsonb,
  emails               jsonb,
  telephones           jsonb,
  source               text,
  status               text,
  title                text,
  link_urls            text[],
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- CRM: Taxonomy
-- ======================
CREATE TABLE unified_crm_taxonomy (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  name                 text,
  label                text,
  type                 text,
  raw                  jsonb
);
-- ======================
-- CRM: Pipeline
-- ======================
CREATE TABLE unified_crm_pipeline (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  is_active            boolean,
  deal_probability     numeric,
  display_order        numeric,
  stages               jsonb,
  raw                  jsonb
);
-- ======================
-- MARTECH: List
-- ======================
CREATE TABLE unified_martech_list (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  start_at             timestamptz,
  end_at               timestamptz,
  user_id              text,
  is_active            boolean,
  address              jsonb,
  subject              text,
  sender_name          text,
  sender_email         text,
  language             text,
  sender_company       text,
  sender_phone         text,
  raw                  jsonb
);
-- ======================
-- MARTECH: Member
-- ======================
CREATE TABLE unified_martech_member (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  company              text,
  emails               jsonb,
  list_ids             text[],
  tags                 text[],
  status               text,
  raw                  jsonb
);
-- ======================
-- MARTECH: Campaign
-- ======================
CREATE TABLE unified_martech_campaign (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  status               text,
  list_ids             text[],
  subject_line         text,
  preview_text         text,
  from_name            text,
  from_email           text,
  reply_to_email       text,
  send_at              timestamptz,
  raw                  jsonb
);
-- ======================
-- MARTECH: Report
-- ======================
CREATE TABLE unified_martech_report (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  start_at             timestamptz,
  end_at               timestamptz,
  campaign_id          text,
  list_id              text,
  emails_sent          numeric,
  abuse_reports        numeric,
  unsubscribed         numeric,
  sent_at              timestamptz,
  hard_bounces         numeric,
  soft_bounces         numeric,
  syntax_errors        numeric,
  forwards_count       numeric,
  forwards_opens       numeric,
  opens_total          numeric,
  unique_opens         numeric,
  open_rate            numeric,
  last_open_at         timestamptz,
  clicks_total         numeric,
  unique_clicks        numeric,
  unique_subscriber_clicks numeric,
  click_rate           numeric,
  last_click_at        timestamptz,
  links                jsonb,
  human_opens_total    numeric,
  human_unique_opens   numeric,
  human_open_rate      numeric,
  raw                  jsonb
);
-- ======================
-- TICKETING: Ticket
-- ======================
CREATE TABLE unified_ticketing_ticket (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  customer_id          text,
  subject              text,
  description          text,
  status               text,
  closed_at            timestamptz,
  priority             text,
  category_id          text,
  source               text,
  source_ref           text,
  tags                 text[],
  user_id              text,
  url                  text,
  attachment_ids       text[],
  due_at               timestamptz,
  raw                  jsonb
);
-- ======================
-- TICKETING: Customer
-- ======================
CREATE TABLE unified_ticketing_customer (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  emails               jsonb,
  telephones           jsonb,
  tags                 text[],
  raw                  jsonb
);
-- ======================
-- TICKETING: Note
-- ======================
CREATE TABLE unified_ticketing_note (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  customer_id          text,
  description          text,
  ticket_id            text,
  user_id              text,
  raw                  jsonb
);
-- ======================
-- TICKETING: Category
-- ======================
CREATE TABLE unified_ticketing_category (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_active            boolean,
  parent_id            text,
  raw                  jsonb
);
-- ======================
-- UC: Call
-- ======================
CREATE TABLE unified_uc_call (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  contact_id           text,
  telephone            jsonb,
  start_at             timestamptz,
  end_at               timestamptz,
  user_id              text,
  contacts             jsonb,
  is_private           boolean,
  user_name            text,
  user_phone           text,
  type                 text,
  metadata             jsonb,
  raw                  jsonb,
  conversation_identifier text
);
-- ======================
-- UC: Contact
-- ======================
CREATE TABLE unified_uc_contact (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  title                text,
  company              text,
  emails               jsonb,
  telephones           jsonb,
  raw                  jsonb
);
-- ======================
-- UC: Comment
-- ======================
CREATE TABLE unified_uc_comment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           text,
  updated_at           text,
  content              text,
  user_id              text,
  call_id              text,
  raw                  jsonb
);
-- ======================
-- UC: Recording
-- ======================
CREATE TABLE unified_uc_recording (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  expires_at           timestamptz,
  call_id              text,
  web_url              text,
  contacts             jsonb,
  user_id              text,
  media                jsonb,
  user_name            text,
  user_phone           text,
  type                 text,
  conversation_identifier text,
  raw                  jsonb
);
-- ======================
-- UC: Scorecard
-- ======================
CREATE TABLE unified_uc_scorecard (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  call_id              text,
  scorecardtemplate_id text,
  name                 text,
  user_id              text,
  reviewer_user_id     text,
  reviewed_at          timestamptz,
  score                numeric,
  questions            jsonb,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- UC: Scorecardtemplate
-- ======================
CREATE TABLE unified_uc_scorecardtemplate (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_active            boolean,
  questions            jsonb,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ATS: Activity
-- ======================
CREATE TABLE unified_ats_activity (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  candidate_id         text,
  application_id       text,
  job_id               text,
  interview_id         text,
  document_ids         text[],
  title                text,
  description          text,
  is_private           boolean,
  user_ids             text[],
  type                 text,
  from                 jsonb,
  to                   jsonb,
  cc                   jsonb,
  bcc                  jsonb,
  sub_type             text,
  company_id           text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ATS: Candidate
-- ======================
CREATE TABLE unified_ats_candidate (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  emails               jsonb,
  title                text,
  telephones           jsonb,
  company_name         text,
  image_url            text,
  tags                 text[],
  address              jsonb,
  external_identifier  text,
  link_urls            text[],
  origin               text,
  company_id           text,
  sources              text[],
  date_of_birth        timestamptz,
  user_id              text,
  user_ids             text[],
  web_url              text,
  experiences          jsonb,
  education            jsonb,
  skills               text[],
  job_ids              text[],
  metadata             jsonb,
  summary              text,
  raw                  jsonb
);
-- ======================
-- ATS: Job
-- ======================
CREATE TABLE unified_ats_job (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  recruiter_ids        text[],
  hiring_manager_ids   text[],
  hiring_managers      jsonb,
  status               text,
  closed_at            timestamptz,
  addresses            jsonb,
  compensation         jsonb,
  employment_type      text,
  remote               boolean,
  language_locale      text,
  public_job_urls      text[],
  number_of_openings   numeric,
  company_id           text,
  questions            jsonb,
  postings             jsonb,
  groups               jsonb,
  openings             jsonb,
  minimum_experience_years numeric,
  minimum_degree       text,
  skills               text[],
  metadata             jsonb,
  user_id              text,
  industry             text,
  summary              text,
  raw                  jsonb
);
-- ======================
-- ATS: Interview
-- ======================
CREATE TABLE unified_ats_interview (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  candidate_id         text,
  job_id               text,
  application_id       text,
  user_ids             text[],
  status               text,
  start_at             timestamptz,
  end_at               timestamptz,
  location             text,
  meeting_url          text,
  external_event_xref  text,
  raw                  jsonb
);
-- ======================
-- ATS: Document
-- ======================
CREATE TABLE unified_ats_document (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  document_url         text,
  document_data        text,
  filename             text,
  type                 text,
  candidate_id         text,
  application_id       text,
  job_id               text,
  user_id              text,
  raw                  jsonb
);
-- ======================
-- ATS: Applicationstatus
-- ======================
CREATE TABLE unified_ats_applicationstatu (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  job_id               text,
  status               text,
  original_status      text,
  description          text,
  raw                  jsonb
);
-- ======================
-- ATS: Application
-- ======================
CREATE TABLE unified_ats_application (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  candidate_id         text,
  job_id               text,
  created_at           timestamptz,
  updated_at           timestamptz,
  applied_at           timestamptz,
  hired_at             timestamptz,
  rejected_at          timestamptz,
  rejected_reason      text,
  source               text,
  status               text,
  original_status      text,
  answers              jsonb,
  offers               jsonb,
  user_id              text,
  metadata             jsonb,
  original_substatus   text,
  summary              text,
  raw                  jsonb
);
-- ======================
-- ATS: Scorecard
-- ======================
CREATE TABLE unified_ats_scorecard (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  application_id       text,
  interviewer_id       text,
  interview_id         text,
  candidate_id         text,
  job_id               text,
  recommendation       text,
  comment              text,
  questions            jsonb,
  raw                  jsonb
);
-- ======================
-- ATS: Company
-- ======================
CREATE TABLE unified_ats_company (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  address              jsonb,
  website_url          text,
  phone                text,
  parent_id            text,
  recruiter_ids        text[],
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HRIS: Employee
-- ======================
CREATE TABLE unified_hris_employee (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  emails               jsonb,
  title                text,
  job_id               text,
  manager_id           text,
  employment_status    text,
  gender               text,
  telephones           jsonb,
  date_of_birth        timestamptz,
  employee_number      text,
  hired_at             timestamptz,
  terminated_at        timestamptz,
  termination_reason   text,
  marital_status       text,
  employment_type      text,
  address              jsonb,
  language_locale      text,
  currency             text,
  timezone             text,
  image_url            text,
  company_id           text,
  pronouns             text,
  employee_roles       text[],
  compensation         jsonb,
  salutation           text,
  bio                  text,
  ssn_sin              text,
  groups               jsonb,
  locations            jsonb,
  metadata             jsonb,
  storage_quota_allocated numeric,
  storage_quota_used   numeric,
  storage_quota_available numeric,
  relationships        jsonb,
  has_mfa              boolean,
  timeoff_days_total   numeric,
  timeoff_days_used    numeric,
  flsa_status          text,
  pay_frequency        text,
  raw                  jsonb
);
-- ======================
-- HRIS: Company
-- ======================
CREATE TABLE unified_hris_company (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  legal_name           text,
  address              jsonb,
  raw                  jsonb
);
-- ======================
-- HRIS: Location
-- ======================
CREATE TABLE unified_hris_location (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  address              jsonb,
  parent_id            text,
  external_identifier  text,
  telephones           jsonb,
  timezone             text,
  currency             text,
  language_locale      text,
  is_active            boolean,
  is_hq                boolean,
  company_id           text,
  raw                  jsonb
);
-- ======================
-- HRIS: Group
-- ======================
CREATE TABLE unified_hris_group (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  parent_id            text,
  type                 text,
  user_ids             text[],
  manager_ids          text[],
  is_active            boolean,
  company_id           text,
  pay_frequency        text,
  next_paid_at         timestamptz,
  raw                  jsonb
);
-- ======================
-- HRIS: Job
-- ======================
CREATE TABLE unified_hris_job (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  code                 text,
  is_active            boolean,
  employment_type      text,
  company_id           text,
  groups               jsonb,
  locations            jsonb,
  parent_id            text,
  users                jsonb,
  compensation         jsonb,
  raw                  jsonb
);
-- ======================
-- HRIS: Timeoff
-- ======================
CREATE TABLE unified_hris_timeoff (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  company_id           text,
  start_at             timestamptz,
  end_at               timestamptz,
  is_paid              boolean,
  status               text,
  approver_user_id     text,
  approved_at          timestamptz,
  comments             text,
  reason               text,
  original_type        text,
  type                 text,
  duration             numeric,
  duration_type        text,
  raw                  jsonb
);
-- ======================
-- HRIS: Payslip
-- ======================
CREATE TABLE unified_hris_payslip (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  company_id           text,
  payment_reference    text,
  payment_type         text,
  paid_at              timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  currency             text,
  gross_amount         numeric,
  net_amount           numeric,
  details              jsonb,
  deduction            jsonb,
  payroll_id           text,
  group_id             text,
  type                 text,
  hours                numeric,
  employee_tax_amount  numeric,
  employer_tax_amount  numeric,
  deduction_amount     numeric,
  employer_contribution_amount numeric,
  gross_ytd_amount     numeric,
  net_ytd_amount       numeric,
  raw                  jsonb
);
-- ======================
-- HRIS: Payroll
-- ======================
CREATE TABLE unified_hris_payroll (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  company_id           text,
  group_id             text,
  status               text,
  type                 text,
  start_at             timestamptz,
  end_at               timestamptz,
  paid_at              timestamptz,
  approved_at          timestamptz,
  currency             text,
  gross_amount         numeric,
  net_amount           numeric,
  employee_tax_amount  numeric,
  employer_tax_amount  numeric,
  deduction_amount     numeric,
  employer_contribution_amount numeric,
  total_cost_amount    numeric,
  user_ids             text[],
  payslip_ids          text[],
  raw                  jsonb
);
-- ======================
-- HRIS: Paycode
-- ======================
CREATE TABLE unified_hris_paycode (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  company_id           text,
  name                 text,
  code                 text,
  description          text,
  type                 text,
  detail_type          text,
  is_pre_tax           boolean,
  is_employer          boolean,
  is_active            boolean,
  raw                  jsonb
);
-- ======================
-- HRIS: Earning
-- ======================
CREATE TABLE unified_hris_earning (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  company_id           text,
  paycode_id           text,
  amount               numeric,
  currency             text,
  hours                numeric,
  rate_amount          numeric,
  frequency            text,
  start_at             timestamptz,
  end_at               timestamptz,
  status               text,
  payroll_id           text,
  payslip_id           text,
  notes                text,
  raw                  jsonb
);
-- ======================
-- HRIS: Device
-- ======================
CREATE TABLE unified_hris_device (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  asset_tag            text,
  version              text,
  manufacturer         text,
  model                text,
  os                   text,
  os_version           text,
  user_ids             text[],
  admin_user_ids       text[],
  location_id          text,
  has_antivirus        boolean,
  has_password_manager boolean,
  has_firewall         boolean,
  has_hd_encrypted     boolean,
  has_screenlock       boolean,
  is_missing           boolean,
  raw                  jsonb
);
-- ======================
-- HRIS: Timeshift
-- ======================
CREATE TABLE unified_hris_timeshift (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  employee_user_id     text,
  start_at             timestamptz,
  end_at               timestamptz,
  location_id          text,
  company_id           text,
  group_id             text,
  compensation         jsonb,
  approver_user_id     text,
  approved_at          timestamptz,
  hours                numeric,
  is_approved          boolean,
  raw                  jsonb
);
-- ======================
-- HRIS: Attendance
-- ======================
CREATE TABLE unified_hris_attendance (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  employee_user_id     text,
  start_at             timestamptz,
  end_at               timestamptz,
  timeshift_id         text,
  location_id          text,
  company_id           text,
  group_id             text,
  timezone             text,
  address              jsonb,
  hours                numeric,
  currency             text,
  status               text,
  breaks               jsonb,
  declared_tips_amount numeric,
  non_cash_tips_amount numeric,
  job_name             text,
  hourly_rate          numeric,
  approver_user_id     text,
  approved_at          timestamptz,
  raw                  jsonb
);
-- ======================
-- HRIS: Benefit
-- ======================
CREATE TABLE unified_hris_benefit (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  company_id           text,
  type                 text,
  tax                  text,
  frequency            text,
  is_active            boolean,
  employer_contribution_type text,
  employer_contribution_amount numeric,
  employer_contribution_max_amount numeric,
  coverage_level       text,
  currency             text,
  raw                  jsonb
);
-- ======================
-- HRIS: Deduction
-- ======================
CREATE TABLE unified_hris_deduction (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  company_id           text,
  benefit_id           text,
  amount               numeric,
  type                 text,
  coverage_level       text,
  frequency            text,
  start_at             timestamptz,
  end_at               timestamptz,
  is_active            boolean,
  notes                text,
  employer_amount      numeric,
  employer_type        text,
  max_amount           numeric,
  paycode_id           text,
  garnishment_type     text,
  raw                  jsonb
);
-- ======================
-- HRIS: Bankaccount
-- ======================
CREATE TABLE unified_hris_bankaccount (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  company_id           text,
  account_type         text,
  bank_name            text,
  routing_number       text,
  account_number       text,
  account_number_last4 text,
  name                 text,
  is_primary           boolean,
  iban                 text,
  bic                  text,
  country_code         text,
  currency             text,
  split_type           text,
  split_amount         numeric,
  priority             numeric,
  raw                  jsonb
);
-- ======================
-- HRIS: Taxonomy
-- ======================
CREATE TABLE unified_hris_taxonomy (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  type                 text,
  name                 text,
  description          text,
  domain               text,
  category             text,
  subcategory          text,
  parent_id            text,
  alternative_names    text[],
  url                  text,
  role_ids             text[],
  is_active            boolean,
  raw                  jsonb
);
-- ======================
-- HRIS: Document
-- ======================
CREATE TABLE unified_hris_document (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  document_url         text,
  document_data        text,
  filename             text,
  type                 text,
  user_id              text,
  company_id           text,
  raw                  jsonb
);
-- ======================
-- VERIFICATION: Package
-- ======================
CREATE TABLE unified_verification_package (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  aliases              text[],
  tags                 text[],
  description          text,
  parameters           jsonb,
  average_processing_times jsonb,
  has_redirect_url     boolean,
  has_target_url       boolean,
  needs_ip_address     boolean,
  cost_amount          numeric,
  currency             text,
  max_score            numeric,
  info_url             text,
  valid_regions        text[],
  raw                  jsonb
);
-- ======================
-- VERIFICATION: Request
-- ======================
CREATE TABLE unified_verification_request (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  package_id           text,
  parameters           jsonb,
  target_url           text,
  candidate_id         text,
  profile_ip_address   text,
  profile_name         text,
  profile_date_of_birth text,
  profile_addresses    jsonb,
  profile_gender       text,
  profile_emails       text[],
  profile_telephones   text[],
  profile_national_identifier text,
  response_completed_at timestamptz,
  response_expires_at  timestamptz,
  response_issued_at   timestamptz,
  response_status      text,
  response_score       numeric,
  response_redirect_url text,
  response_download_urls text[],
  response_details     jsonb,
  response_source      text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Account
-- ======================
CREATE TABLE unified_accounting_account (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  type                 text,
  status               text,
  balance              numeric,
  currency             text,
  customer_defined_code text,
  is_payable           boolean,
  parent_id            text,
  taxonomy             jsonb,
  organization_id      text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Journal
-- ======================
CREATE TABLE unified_accounting_journal (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  reference            text,
  tax_amount           numeric,
  currency             text,
  lineitems            jsonb,
  taxrate_id           text,
  description          text,
  posted_at            timestamptz,
  source               text,
  organization_id      text,
  category_ids         text[],
  project_id           text,
  attachments          jsonb,
  total_amount         numeric,
  exchange_rate        numeric,
  status               text,
  is_inclusive_of_tax  boolean,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Transaction
-- ======================
CREATE TABLE unified_accounting_transaction (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  memo                 text,
  total_amount         numeric,
  tax_amount           numeric,
  account_id           text,
  reference            text,
  sub_total_amount     numeric,
  split_account_id     text,
  payment_method       text,
  payment_terms        text,
  customer_message     text,
  type                 text,
  lineitems            jsonb,
  currency             text,
  contacts             jsonb,
  organization_id      text,
  category_ids         text[],
  project_id           text,
  transaction_at       timestamptz,
  exchange_rate        numeric,
  status               text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Contact
-- ======================
CREATE TABLE unified_accounting_contact (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  emails               jsonb,
  telephones           jsonb,
  currency             text,
  billing_address      jsonb,
  shipping_address     jsonb,
  is_active            boolean,
  tax_exemption        text,
  tax_number           text,
  is_customer          boolean,
  is_supplier          boolean,
  portal_url           text,
  payment_methods      jsonb,
  company_name         text,
  identification       text,
  associated_contacts  jsonb,
  organization_id      text,
  payment_terms        text,
  paymentterm_id       text,
  balance_amount       numeric,
  website              text,
  notes                text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Invoice
-- ======================
CREATE TABLE unified_accounting_invoice (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  due_at               timestamptz,
  paid_at              timestamptz,
  refunded_at          timestamptz,
  cancelled_at         timestamptz,
  posted_at            timestamptz,
  total_amount         numeric,
  paid_amount          numeric,
  refund_amount        numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  balance_amount       numeric,
  invoice_number       text,
  reference            text,
  contact_id           text,
  currency             text,
  notes                text,
  extended_notes       jsonb,
  refund_reason        text,
  term                 text,
  payment_terms        text,
  paymentterm_id       text,
  lineitems            jsonb,
  status               text,
  url                  text,
  payment_collection_method text,
  type                 text,
  attachments          jsonb,
  send                 boolean,
  organization_id      text,
  payments             jsonb,
  category_ids         text[],
  project_id           text,
  metadata             jsonb,
  sub_total_amount     numeric,
  exchange_rate        numeric,
  is_inclusive_of_tax  boolean,
  salesorder_ids       text[],
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Bill
-- ======================
CREATE TABLE unified_accounting_bill (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  bill_number          text,
  created_at           timestamptz,
  updated_at           timestamptz,
  due_at               timestamptz,
  paid_at              timestamptz,
  refunded_at          timestamptz,
  cancelled_at         timestamptz,
  posted_at            timestamptz,
  total_amount         numeric,
  paid_amount          numeric,
  refund_amount        numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  balance_amount       numeric,
  contact_id           text,
  currency             text,
  notes                text,
  extended_notes       jsonb,
  refund_reason        text,
  lineitems            jsonb,
  status               text,
  url                  text,
  payment_collection_method text,
  attachments          jsonb,
  send                 boolean,
  organization_id      text,
  term                 text,
  payment_terms        text,
  paymentterm_id       text,
  payments             jsonb,
  category_ids         text[],
  project_id           text,
  metadata             jsonb,
  sub_total_amount     numeric,
  exchange_rate        numeric,
  purchaseorder_ids    text[],
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Creditmemo
-- ======================
CREATE TABLE unified_accounting_creditmemo (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  due_at               timestamptz,
  paid_at              timestamptz,
  refunded_at          timestamptz,
  cancelled_at         timestamptz,
  posted_at            timestamptz,
  total_amount         numeric,
  paid_amount          numeric,
  refund_amount        numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  balance_amount       numeric,
  creditmemo_number    text,
  contact_id           text,
  invoice_id           text,
  currency             text,
  notes                text,
  refund_reason        text,
  lineitems            jsonb,
  status               text,
  url                  text,
  payment_collection_method text,
  attachments          jsonb,
  send                 boolean,
  organization_id      text,
  apply_amount         numeric,
  applications         jsonb,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Vendorcredit
-- ======================
CREATE TABLE unified_accounting_vendorcredit (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  due_at               timestamptz,
  posted_at            timestamptz,
  total_amount         numeric,
  balance_amount       numeric,
  account_id           text,
  currency             text,
  contact_id           text,
  bill_id              text,
  notes                text,
  lineitems            jsonb,
  status               text,
  organization_id      text,
  apply_amount         numeric,
  applications         jsonb,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Taxrate
-- ======================
CREATE TABLE unified_accounting_taxrate (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  rate                 numeric,
  is_active            boolean,
  organization_id      text,
  metadata             jsonb,
  effective_rate       numeric,
  total_rate           numeric,
  components           jsonb,
  type                 text,
  is_compound          boolean,
  country              text,
  region               text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Paymentterm
-- ======================
CREATE TABLE unified_accounting_paymentterm (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  type                 text,
  category             text,
  is_active            boolean,
  due_days             numeric,
  discount_days        numeric,
  discount_percent     numeric,
  day_of_month_due     numeric,
  discount_day_of_month numeric,
  due_next_month_days  numeric,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Organization
-- ======================
CREATE TABLE unified_accounting_organization (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  legal_name           text,
  currency             text,
  address              jsonb,
  tax_number           text,
  timezone             text,
  website              text,
  parent_id            text,
  fiscal_year_end_month numeric,
  organization_code    text,
  type                 text,
  is_elimination       boolean,
  books_close_at       timestamptz,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Order
-- ======================
CREATE TABLE unified_accounting_order (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  posted_at            timestamptz,
  contact_id           text,
  account_id           text,
  type                 text,
  currency             text,
  total_amount         numeric,
  shipping_address     jsonb,
  billing_address      jsonb,
  status               text,
  lineitems            jsonb,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Purchaseorder
-- ======================
CREATE TABLE unified_accounting_purchaseorder (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  posted_at            timestamptz,
  contact_id           text,
  account_id           text,
  currency             text,
  total_amount         numeric,
  shipping_address     jsonb,
  billing_address      jsonb,
  status               text,
  lineitems            jsonb,
  organization_id      text,
  category_ids         text[],
  metadata             jsonb,
  attachments          jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Salesorder
-- ======================
CREATE TABLE unified_accounting_salesorder (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  posted_at            timestamptz,
  contact_id           text,
  account_id           text,
  currency             text,
  total_amount         numeric,
  shipping_address     jsonb,
  billing_address      jsonb,
  status               text,
  lineitems            jsonb,
  sales_channel        text,
  organization_id      text,
  fees                 jsonb,
  category_ids         text[],
  metadata             jsonb,
  order_number         text,
  location_id          text,
  employee_user_id     text,
  device_id            text,
  fulfillment_type     text,
  guest_count          numeric,
  subtotal_amount      numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  tip_amount           numeric,
  service_charge_amount numeric,
  refunded_amount      numeric,
  closed_at            timestamptz,
  subscription_id      text,
  payments             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Salesreceipt
-- ======================
CREATE TABLE unified_accounting_salesreceipt (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb,
  receipt_number       text,
  reference            text,
  contact_id           text,
  account_id           text,
  posted_at            timestamptz,
  currency             text,
  exchange_rate        numeric,
  sub_total_amount     numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  total_amount         numeric,
  is_inclusive_of_tax  boolean,
  payment_method       text,
  notes                text,
  lineitems            jsonb,
  billing_address      jsonb,
  shipping_address     jsonb,
  category_ids         text[],
  project_id           text,
  attachments          jsonb,
  status               text
);
-- ======================
-- ACCOUNTING: Balancesheet
-- ======================
CREATE TABLE unified_accounting_balancesheet (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  name                 text,
  currency             text,
  net_assets_amount    numeric,
  assets               jsonb,
  liabilities          jsonb,
  equity               jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Trialbalance
-- ======================
CREATE TABLE unified_accounting_trialbalance (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  name                 text,
  currency             text,
  end_at               timestamptz,
  total_debit_amount   numeric,
  total_credit_amount  numeric,
  sub_items            jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Profitloss
-- ======================
CREATE TABLE unified_accounting_profitlos (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  category_ids         text[],
  start_at             timestamptz,
  end_at               timestamptz,
  name                 text,
  currency             text,
  income_total_amount  numeric,
  net_income_amount    numeric,
  expenses_total_amount numeric,
  cost_of_goods_sold_total_amount numeric,
  income_sections      jsonb,
  expenses_sections    jsonb,
  cost_of_goods_sold_sections jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Cashflow
-- ======================
CREATE TABLE unified_accounting_cashflow (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  category_ids         text[],
  contact_id           text,
  name                 text,
  currency             text,
  cash_beginning_amount numeric,
  cash_ending_amount   numeric,
  net_change_in_cash_amount numeric,
  operating_sections   jsonb,
  investing_sections   jsonb,
  financing_sections   jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Category
-- ======================
CREATE TABLE unified_accounting_category (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_active            boolean,
  parent_id            text,
  type                 text,
  code                 text,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Expense
-- ======================
CREATE TABLE unified_accounting_expense (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  contact_id           text,
  account_id           text,
  name                 text,
  payment_method       text,
  posted_at            timestamptz,
  total_amount         numeric,
  currency             text,
  tax_amount           numeric,
  reimbursed_amount    numeric,
  reimbursed_at        timestamptz,
  approved_at          timestamptz,
  approver_user_id     text,
  lineitems            jsonb,
  attachments          jsonb,
  organization_id      text,
  users                jsonb,
  approver_users       jsonb,
  status               text,
  external_number      text,
  category_ids         text[],
  project_id           text,
  metadata             jsonb,
  taxrate_id           text,
  exchange_rate        numeric,
  type                 text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Expensereport
-- ======================
CREATE TABLE unified_accounting_expensereport (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  user_id              text,
  approver_user_id     text,
  approver_users       jsonb,
  status               text,
  total_amount         numeric,
  currency             text,
  tax_amount           numeric,
  reimbursed_amount    numeric,
  reimbursed_at        timestamptz,
  approved_at          timestamptz,
  posted_at            timestamptz,
  external_number      text,
  lineitems            jsonb,
  attachments          jsonb,
  category_ids         text[],
  project_id           text,
  users                jsonb,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Purchasereceipt
-- ======================
CREATE TABLE unified_accounting_purchasereceipt (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb,
  receipt_number       text,
  contact_id           text,
  purchaseorder_id     text,
  posted_at            timestamptz,
  status               text,
  currency             text,
  total_amount         numeric,
  notes                text,
  lineitems            jsonb,
  attachments          jsonb
);
-- ======================
-- ACCOUNTING: Quote
-- ======================
CREATE TABLE unified_accounting_quote (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  quote_number         text,
  reference            text,
  title                text,
  summary              text,
  payment_terms        text,
  customer_message     text,
  memo                 text,
  contact_id           text,
  contacts             jsonb,
  issued_at            timestamptz,
  expires_at           timestamptz,
  sent_at              timestamptz,
  accepted_at          timestamptz,
  declined_at          timestamptz,
  status               text,
  currency             text,
  currency_rate        numeric,
  sub_total_amount     numeric,
  tax_amount           numeric,
  discount_amount      numeric,
  total_amount         numeric,
  tax_mode             text,
  lineitems            jsonb,
  invoice_id           text,
  project_id           text,
  group_id             text,
  category_ids         text[],
  url                  text,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Agedreceivable
-- ======================
CREATE TABLE unified_accounting_agedreceivable (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  currency             text,
  start_at             timestamptz,
  end_at               timestamptz,
  total_current_amount numeric,
  total_overdue_amount numeric,
  total_amount         numeric,
  periods              jsonb,
  organization_id      text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Agedpayable
-- ======================
CREATE TABLE unified_accounting_agedpayable (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  currency             text,
  start_at             timestamptz,
  end_at               timestamptz,
  total_current_amount numeric,
  total_overdue_amount numeric,
  total_amount         numeric,
  periods              jsonb,
  organization_id      text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Project
-- ======================
CREATE TABLE unified_accounting_project (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  code                 text,
  description          text,
  status               text,
  is_active            boolean,
  is_billable          boolean,
  contact_id           text,
  parent_id            text,
  manager_user_id      text,
  started_at           timestamptz,
  due_at               timestamptz,
  ended_at             timestamptz,
  currency             text,
  estimate_amount      numeric,
  estimated_cost_amount numeric,
  actual_cost_amount   numeric,
  invoiced_amount      numeric,
  to_be_invoiced_amount numeric,
  expense_amount       numeric,
  deposit_amount       numeric,
  deposit_applied_amount numeric,
  credit_note_amount   numeric,
  minutes_logged       numeric,
  minutes_to_be_invoiced numeric,
  percent_complete     numeric,
  billing_type         text,
  category_ids         text[],
  location_id          text,
  organization_id      text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Bankfeedaccount
-- ======================
CREATE TABLE unified_accounting_bankfeedaccount (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  organization_id      text,
  name                 text,
  bank_name            text,
  account_number       text,
  account_number_last4 text,
  routing_number       text,
  account_type         text,
  account_id           text,
  currency             text,
  balance              numeric,
  feed_start_at        timestamptz,
  status               text,
  raw                  jsonb
);
-- ======================
-- ACCOUNTING: Bankfeedtransaction
-- ======================
CREATE TABLE unified_accounting_bankfeedtransaction (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  organization_id      text,
  bankfeedaccount_id   text,
  transaction_at       timestamptz,
  posted_at            timestamptz,
  amount               numeric,
  type                 text,
  bank_category        text,
  description          text,
  merchant_name        text,
  is_pending           boolean,
  reference            text,
  currency             text,
  contact_id           text,
  account_id           text,
  category_ids         text[],
  raw                  jsonb
);
-- ======================
-- STORAGE: File
-- ======================
CREATE TABLE unified_storage_file (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  parent_id            text,
  user_id              text,
  size                 numeric,
  type                 text,
  mime_type            text,
  permissions          jsonb,
  download_url         text,
  hash                 text,
  data                 text,
  version              text,
  web_url              text,
  references           jsonb,
  tags                 text[],
  raw                  jsonb
);
-- ======================
-- COMMERCE: Item
-- ======================
CREATE TABLE unified_commerce_item (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  public_name          text,
  slug                 text,
  description          text,
  global_code          text,
  public_description   text,
  is_active            boolean,
  is_taxable           boolean,
  vendor_name          text,
  type                 text,
  is_visible           boolean,
  is_featured          boolean,
  weight               numeric,
  weight_unit          text,
  requires_shipping    boolean,
  prices               jsonb,
  inventory_id         text,
  total_stock          numeric,
  tags                 text[],
  media                jsonb,
  account_id           text,
  metadata             jsonb,
  collections          jsonb,
  taxrate_id           text,
  location_id          text,
  duration             numeric,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Collection
-- ======================
CREATE TABLE unified_commerce_collection (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  public_name          text,
  description          text,
  public_description   text,
  media                jsonb,
  is_visible           boolean,
  is_active            boolean,
  is_featured          boolean,
  tags                 text[],
  type                 text,
  parent_id            text,
  metadata             jsonb,
  item_metadata        jsonb,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Inventory
-- ======================
CREATE TABLE unified_commerce_inventory (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  updated_at           timestamptz,
  item_id              text,
  item_variant_id      text,
  item_option_id       text,
  location_id          text,
  available            numeric,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Location
-- ======================
CREATE TABLE unified_commerce_location (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  address              jsonb,
  description          text,
  is_active            boolean,
  language_locale      text,
  parent_id            text,
  currency             text,
  location_type        text,
  telephones           jsonb,
  rating               numeric,
  review_count         numeric,
  price_level          text,
  latitude             numeric,
  longitude            numeric,
  image_url            text,
  web_url              text,
  media                jsonb,
  raw                  jsonb,
  categories           text[]
);
-- ======================
-- COMMERCE: Review
-- ======================
CREATE TABLE unified_commerce_review (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  item_id              text,
  item_variant_id      text,
  location_id          text,
  rating               numeric,
  title                text,
  content              text,
  author_name          text,
  author_email         text,
  author_avatar_url    text,
  author_location      text,
  verified_purchase    boolean,
  helpful_votes        numeric,
  unhelpful_votes      numeric,
  media                jsonb,
  status               text,
  is_verified          boolean,
  is_featured          boolean,
  is_public            boolean,
  comments             jsonb,
  metadata             jsonb,
  url                  text,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Reservation
-- ======================
CREATE TABLE unified_commerce_reservation (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  location_id          text,
  start_at             timestamptz,
  end_at               timestamptz,
  size                 numeric,
  status               text,
  guest_name           text,
  guest_phone          text,
  guest_email          text,
  notes                text,
  item_id              text,
  item_name            text,
  staff_user_id        text,
  staff_name           text,
  created_at           timestamptz,
  updated_at           timestamptz,
  url                  text,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Availability
-- ======================
CREATE TABLE unified_commerce_availability (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  location_id          text,
  start_at             timestamptz,
  end_at               timestamptz,
  size                 numeric,
  item_id              text,
  staff_user_id        text,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Saleschannel
-- ======================
CREATE TABLE unified_commerce_saleschannel (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  slug                 text,
  description          text,
  is_active            boolean,
  collections          jsonb,
  raw                  jsonb
);
-- ======================
-- COMMERCE: Itemvariant
-- ======================
CREATE TABLE unified_commerce_itemvariant (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  public_name          text,
  description          text,
  public_description   text,
  sku                  text,
  is_active            boolean,
  is_visible           boolean,
  is_featured          boolean,
  media                jsonb,
  available_at         timestamptz,
  tags                 text[],
  width                numeric,
  height               numeric,
  length               numeric,
  weight               numeric,
  size_unit            text,
  weight_unit          text,
  total_stock          numeric,
  prices               jsonb,
  options              jsonb,
  inventory_id         text,
  requires_shipping    boolean,
  metadata             jsonb,
  items                jsonb,
  raw                  jsonb
);
-- ======================
-- PAYMENT: Payment
-- ======================
CREATE TABLE unified_payment_payment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  total_amount         numeric,
  contact_id           text,
  payment_method       text,
  type                 text,
  currency             text,
  notes                text,
  invoice_id           text,
  bill_id              text,
  link_id              text,
  account_id           text,
  reference            text,
  organization_id      text,
  allocations          jsonb,
  status               text,
  salesorder_id        text,
  tender_type          text,
  tip_amount           numeric,
  fee_amount           numeric,
  location_id          text,
  device_id            text,
  card_brand           text,
  card_last4           text,
  paid_at              timestamptz,
  exchange_rate        numeric,
  category_ids         text[],
  net_amount           numeric,
  raw                  jsonb
);
-- ======================
-- PAYMENT: Link
-- ======================
CREATE TABLE unified_payment_link (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  is_active            boolean,
  lineitems            jsonb,
  currency             text,
  amount               numeric,
  payment_id           text,
  contact_id           text,
  url                  text,
  description          text,
  is_chargeable_now    boolean,
  success_url          text,
  raw                  jsonb
);
-- ======================
-- PAYMENT: Refund
-- ======================
CREATE TABLE unified_payment_refund (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  total_amount         numeric,
  payment_id           text,
  currency             text,
  notes                text,
  status               text,
  reference            text,
  refunded_at          timestamptz,
  reason               text,
  tender_type          text,
  raw                  jsonb
);
-- ======================
-- PAYMENT: Payout
-- ======================
CREATE TABLE unified_payment_payout (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           text,
  updated_at           text,
  total_amount         numeric,
  currency             text,
  notes                text,
  status               text,
  arrival_at           timestamptz,
  fee_amount           numeric,
  net_amount           numeric,
  account_id           text,
  lineitems            jsonb,
  raw                  jsonb
);
-- ======================
-- PAYMENT: Subscription
-- ======================
CREATE TABLE unified_payment_subscription (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  description          text,
  contact_id           text,
  invoice_id           text,
  current_period_end_at timestamptz,
  current_period_start_at timestamptz,
  canceled_at          timestamptz,
  currency             text,
  total_amount         numeric,
  start_at             timestamptz,
  end_at               timestamptz,
  status               text,
  month                numeric,
  interval_unit        text,
  day_of_month         numeric,
  day_of_week          numeric,
  interval             numeric,
  lineitems            jsonb,
  raw                  jsonb
);
-- ======================
-- GENAI: Model
-- ======================
CREATE TABLE unified_genai_model (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  name                 text,
  description          text,
  max_tokens           numeric,
  web_url              text,
  has_temperature      boolean,
  has_questions        boolean,
  has_vision           boolean,
  raw                  jsonb
);
-- ======================
-- GENAI: Task
-- ======================
CREATE TABLE unified_genai_task (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  instructions         text,
  status               text,
  model_id             text,
  user_id              text,
  repo_url             text,
  source_branch_identifier text,
  target_branch_identifier text,
  pullrequest_url      text,
  web_url              text,
  messages             jsonb,
  summary              text,
  error                text,
  files_changed        numeric,
  lines_added          numeric,
  lines_deleted        numeric,
  tokens_used          numeric,
  started_at           timestamptz,
  completed_at         timestamptz,
  agent_id             text,
  organization_id      text,
  raw                  jsonb
);
-- ======================
-- GENAI: Agent
-- ======================
CREATE TABLE unified_genai_agent (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  instructions         text,
  model_id             text,
  is_active            boolean,
  raw                  jsonb
);
-- ======================
-- GENAI: Organization
-- ======================
CREATE TABLE unified_genai_organization (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_active            boolean,
  raw                  jsonb
);
-- ======================
-- GENAI: Skill
-- ======================
CREATE TABLE unified_genai_skill (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  version              text,
  raw                  jsonb
);
-- ======================
-- KMS: Space
-- ======================
CREATE TABLE unified_kms_space (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  parent_id            text,
  is_active            boolean,
  user_id              text,
  parent_page_id       text,
  raw                  jsonb
);
-- ======================
-- KMS: Page
-- ======================
CREATE TABLE unified_kms_page (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  title                text,
  type                 text,
  space_id             text,
  parent_id            text,
  is_active            boolean,
  user_id              text,
  download_url         text,
  metadata             jsonb,
  has_children         boolean,
  web_url              text,
  raw                  jsonb
);
-- ======================
-- KMS: Comment
-- ======================
CREATE TABLE unified_kms_comment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  type                 text,
  content_type         text,
  content              text,
  user_id              text,
  page_id              text,
  parent_id            text,
  raw                  jsonb
);
-- ======================
-- TASK: Project
-- ======================
CREATE TABLE unified_task_project (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  parent_id            text,
  user_ids             text[],
  group_ids            text[],
  description          text,
  has_tasks            boolean,
  has_children         boolean,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- TASK: Task
-- ======================
CREATE TABLE unified_task_task (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  project_id           text,
  parent_id            text,
  completed_at         timestamptz,
  status               text,
  notes                text,
  due_at               timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  priority             text,
  assigned_user_ids    text[],
  creator_user_id      text,
  follower_user_ids    text[],
  group_ids            text[],
  tags                 text[],
  url                  text,
  attachment_ids       text[],
  metadata             jsonb,
  has_children         boolean,
  type                 text,
  time_spent           numeric,
  time_spent_unit      text,
  progress             numeric,
  story_points         numeric,
  raw                  jsonb
);
-- ======================
-- TASK: Comment
-- ======================
CREATE TABLE unified_task_comment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  text                 text,
  user_id              text,
  user_name            text,
  task_id              text,
  parent_id            text,
  has_children         boolean,
  raw                  jsonb
);
-- ======================
-- TASK: Change
-- ======================
CREATE TABLE unified_task_change (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  task_id              text,
  user_id              text,
  items                jsonb,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Calendar
-- ======================
CREATE TABLE unified_calendar_calendar (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  timezone             text,
  is_primary           boolean,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Event
-- ======================
CREATE TABLE unified_calendar_event (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           text,
  updated_at           text,
  calendar_id          text,
  subject              text,
  start_at             text,
  end_at               text,
  is_all_day           boolean,
  timezone             text,
  notes                text,
  location             text,
  is_free              boolean,
  is_private           boolean,
  status               text,
  organizer            jsonb,
  attendees            jsonb,
  recurring_event_id   text,
  recurrence           jsonb,
  web_url              text,
  has_conference       boolean,
  conference           jsonb,
  attachments          jsonb,
  send_notifications   boolean,
  matter_id            text,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Busy
-- ======================
CREATE TABLE unified_calendar_busy (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  start_at             timestamptz,
  end_at               timestamptz,
  timezone             text,
  description          text,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Link
-- ======================
CREATE TABLE unified_calendar_link (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           text,
  updated_at           text,
  name                 text,
  url                  text,
  duration             numeric,
  description          text,
  is_active            boolean,
  price_amount         numeric,
  price_currency       text,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Recording
-- ======================
CREATE TABLE unified_calendar_recording (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  expires_at           timestamptz,
  event_id             text,
  web_url              text,
  media                jsonb,
  raw                  jsonb
);
-- ======================
-- CALENDAR: Webinar
-- ======================
CREATE TABLE unified_calendar_webinar (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  calendar_id          text,
  subject              text,
  start_at             timestamptz,
  end_at               timestamptz,
  timezone             text,
  notes                text,
  status               text,
  organizer            jsonb,
  join_url             text,
  web_url              text,
  panelists            jsonb,
  registrants          jsonb,
  panelist_password    text,
  registrant_password  text,
  conference           jsonb,
  recurrence           jsonb,
  capacity             numeric,
  is_webcast           boolean,
  is_enabled           boolean,
  is_auto_approve      boolean,
  require_first_name   boolean,
  require_last_name    boolean,
  require_email        boolean,
  require_company      boolean,
  require_job_title    boolean,
  require_address      boolean,
  require_phone        boolean,
  has_qa               boolean,
  has_polls            boolean,
  has_recording        boolean,
  raw                  jsonb
);
-- ======================
-- ADS: Organization
-- ======================
CREATE TABLE unified_ads_organization (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  currency             text,
  timezone             text,
  parent_id            text,
  status               text,
  account_number       text,
  managers             jsonb,
  raw                  jsonb
);
-- ======================
-- ADS: Campaign
-- ======================
CREATE TABLE unified_ads_campaign (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  organization_id      text,
  status               text,
  effective_status     text,
  start_at             timestamptz,
  end_at               timestamptz,
  budget_amount        numeric,
  budget_period        text,
  budget_unit          text,
  total_spend_amount   numeric,
  targeting            jsonb,
  goal                 text,
  planned_spend_amount numeric,
  frequency_cap        jsonb,
  advertising_channel_type text,
  campaign_budget_identifier text,
  currency             text,
  category             text,
  has_eu_political_ads boolean,
  labels               text[],
  kpi                  jsonb,
  raw                  jsonb
);
-- ======================
-- ADS: Creative
-- ======================
CREATE TABLE unified_ads_creative (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  campaign_id          text,
  group_id             text,
  item_id              text,
  organization_id      text,
  status               text,
  creative_type        text,
  hosting_source       text,
  width                numeric,
  height               numeric,
  asset_urls           text[],
  link_url             text,
  url_tags             text,
  body                 text,
  title                text,
  cta                  text,
  third_party_tag      text,
  vast_tag_url         text,
  external_creative_reference text,
  external_placement_reference text,
  external_ad_reference text,
  promoted             jsonb,
  path1                text,
  path2                text,
  data                 text,
  labels               text[],
  raw                  jsonb
);
-- ======================
-- ADS: Asset
-- ======================
CREATE TABLE unified_ads_asset (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  organization_id      text,
  name                 text,
  type                 text,
  url                  text,
  content              text,
  mime_type            text,
  width                numeric,
  height               numeric,
  file_size            numeric,
  raw                  jsonb
);
-- ======================
-- ADS: Insertionorder
-- ======================
CREATE TABLE unified_ads_insertionorder (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  organization_id      text,
  campaign_id          text,
  status               text,
  pacing               jsonb,
  frequency_cap        jsonb,
  kpi                  jsonb,
  budget_unit          text,
  budget_segments      jsonb,
  bid_strategy         jsonb,
  reference            text,
  raw                  jsonb
);
-- ======================
-- ADS: Group
-- ======================
CREATE TABLE unified_ads_group (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  parent_id            text,
  campaign_id          text,
  organization_id      text,
  insertionorder_id    text,
  status               text,
  effective_status     text,
  targeting            jsonb,
  bid_amount           numeric,
  bid_strategy         jsonb,
  budget_amount        numeric,
  budget_period        text,
  budget_allocation_type text,
  start_at             timestamptz,
  end_at               timestamptz,
  budget_unit          text,
  budget_max_amount    numeric,
  type                 text,
  has_eu_political_ads boolean,
  pacing               jsonb,
  frequency_cap        jsonb,
  creative_ids         text[],
  optimization_goal    text,
  billing_event        text,
  currency             text,
  promoted             jsonb,
  language_locale      text,
  creative_selection   text,
  raw                  jsonb
);
-- ======================
-- ADS: Ad
-- ======================
CREATE TABLE unified_ads_ad (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  campaign_id          text,
  group_id             text,
  organization_id      text,
  status               text,
  ad_type              text,
  advertiser_name      text,
  creative_ids         text[],
  creative_asset_url   text,
  ad_copy              text,
  headline             text,
  description          text,
  cta                  text,
  final_url            text,
  display_url          text,
  path1                text,
  path2                text,
  promoted             jsonb,
  logo_creative_id     text,
  raw                  jsonb
);
-- ======================
-- ADS: Report
-- ======================
CREATE TABLE unified_ads_report (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  currency             text,
  metrics              jsonb,
  start_at             timestamptz,
  end_at               timestamptz,
  organization_id      text,
  raw                  jsonb
);
-- ======================
-- ADS: Target
-- ======================
CREATE TABLE unified_ads_target (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  name                 text,
  type                 text,
  is_active            boolean,
  parent_id            text,
  audience_count_min   numeric,
  audience_count_max   numeric,
  raw                  jsonb
);
-- ======================
-- ADS: Promoted
-- ======================
CREATE TABLE unified_ads_promoted (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  name                 text,
  type                 text,
  raw                  jsonb
);
-- ======================
-- LMS: Course
-- ======================
CREATE TABLE unified_lms_course (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_private           boolean,
  is_active            boolean,
  price_amount         numeric,
  languages            text[],
  categories           text[],
  currency             text,
  media                jsonb,
  instructors          jsonb,
  students             jsonb,
  content_ids          text[],
  skills               text[],
  duration_minutes     numeric,
  provider_name        text,
  published_at         timestamptz,
  time_estimate_minutes numeric,
  raw                  jsonb
);
-- ======================
-- LMS: Class
-- ======================
CREATE TABLE unified_lms_clas (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  media                jsonb,
  course_id            text,
  languages            text[],
  instructors          jsonb,
  students             jsonb,
  raw                  jsonb
);
-- ======================
-- LMS: Student
-- ======================
CREATE TABLE unified_lms_student (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  emails               jsonb,
  telephones           jsonb,
  address              jsonb,
  image_url            text,
  raw                  jsonb
);
-- ======================
-- LMS: Instructor
-- ======================
CREATE TABLE unified_lms_instructor (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  emails               jsonb,
  title                text,
  telephones           jsonb,
  image_url            text,
  raw                  jsonb
);
-- ======================
-- LMS: Content
-- ======================
CREATE TABLE unified_lms_content (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  external_reference   text,
  course_ids           text[],
  name                 text,
  description          text,
  languages            text[],
  media                jsonb,
  is_active            boolean,
  duration_minutes     numeric,
  categories           text[],
  subjects             jsonb,
  skills               text[],
  tags                 text[],
  difficulty           text,
  sort_order           numeric,
  provider_name        text,
  short_description    text,
  localizations        jsonb,
  collection_ids       text[],
  instructors          jsonb,
  published_at         timestamptz,
  raw                  jsonb
);
-- ======================
-- LMS: Collection
-- ======================
CREATE TABLE unified_lms_collection (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  media                jsonb,
  is_active            boolean,
  parent_id            text,
  raw                  jsonb
);
-- ======================
-- LMS: Activity
-- ======================
CREATE TABLE unified_lms_activity (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  content_id           text,
  course_id            text,
  student_id           text,
  duration_minutes     numeric,
  assigned_grade       text,
  is_completed         boolean,
  progress_percentage  numeric,
  started_at           timestamptz,
  completed_at         timestamptz,
  raw                  jsonb
);
-- ======================
-- REPO: Organization
-- ======================
CREATE TABLE unified_repo_organization (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  avatar_url           text,
  web_url              text,
  user_ids             text[],
  raw                  jsonb
);
-- ======================
-- REPO: Repository
-- ======================
CREATE TABLE unified_repo_repository (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  owner                text,
  is_private           boolean,
  web_url              text,
  org_id               text,
  raw                  jsonb
);
-- ======================
-- REPO: Branch
-- ======================
CREATE TABLE unified_repo_branch (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  repo_id              text,
  raw                  jsonb
);
-- ======================
-- REPO: Commit
-- ======================
CREATE TABLE unified_repo_commit (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  repo_id              text,
  message              text,
  branch_id            text,
  pullrequest_ids      text[],
  lines_added          numeric,
  lines_deleted        numeric,
  lines_changed        numeric,
  raw                  jsonb
);
-- ======================
-- REPO: Pullrequest
-- ======================
CREATE TABLE unified_repo_pullrequest (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_ids             text[],
  repo_id              text,
  title                text,
  notes                text,
  target_branch_id     text,
  source_branch_id     text,
  status               text,
  labels               text[],
  closed_at            timestamptz,
  commit_ids           text[],
  raw                  jsonb
);
-- ======================
-- METADATA: Metadata
-- ======================
CREATE TABLE unified_metadata_metadata (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  slug                 text,
  format               text,
  original_format      text,
  options              text[],
  object_type          text,
  objects              jsonb,
  is_required          boolean,
  raw                  jsonb
);
-- ======================
-- FORMS: Form
-- ======================
CREATE TABLE unified_forms_form (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  fields               jsonb,
  is_active            boolean,
  published_url        text,
  response_count       numeric,
  has_multiple_submissions boolean,
  has_progress_bar     boolean,
  has_shuffle_questions boolean,
  confirmation_message text,
  confirmation_redirect_url text,
  raw                  jsonb
);
-- ======================
-- FORMS: Submission
-- ======================
CREATE TABLE unified_forms_submission (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  form_id              text,
  respondent_email     text,
  respondent_name      text,
  answers              jsonb,
  raw                  jsonb
);
-- ======================
-- DATASTORE: Database
-- ======================
CREATE TABLE unified_datastore_database (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  web_url              text,
  is_active            boolean,
  password             text,
  region               text,
  raw                  jsonb
);
-- ======================
-- DATASTORE: Table
-- ======================
CREATE TABLE unified_datastore_table (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  database_id          text,
  fields               jsonb,
  relationships        jsonb,
  web_url              text,
  parent_id            text,
  raw                  jsonb
);
-- ======================
-- DATASTORE: Record
-- ======================
CREATE TABLE unified_datastore_record (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  database_id          text,
  table_id             text,
  fields               jsonb,
  row_number           numeric,
  raw                  jsonb
);
-- ======================
-- SHIPPING: Shipment
-- ======================
CREATE TABLE unified_shipping_shipment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  order_id             text,
  organization_id      text,
  from_address         jsonb,
  to_address           jsonb,
  packages             jsonb,
  carrier_id           text,
  service_code         text,
  status               text,
  rate_id              text,
  label_id             text,
  tracking_id          text,
  shipped_at           timestamptz,
  rate_amount          numeric,
  rate_currency        text,
  rate_service_name    text,
  rate_estimated_days  numeric,
  rate_estimated_delivery_at timestamptz,
  is_rate_guaranteed   boolean,
  return_address       jsonb,
  return_authorization_number text,
  warehouse_location_id text,
  warehouse_location_name text,
  customs              jsonb,
  is_international     boolean,
  insurance            jsonb,
  special_instructions text[],
  is_signature_required boolean,
  is_adult_signature_required boolean,
  reference_number     text,
  is_return            boolean,
  original_shipment_id text,
  return_reason        text,
  return_type          text,
  carrier_name         text,
  tracking_url         text,
  lineitems            jsonb,
  raw                  jsonb
);
-- ======================
-- SHIPPING: Label
-- ======================
CREATE TABLE unified_shipping_label (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  shipment_id          text,
  tracking_number      text,
  label_url            text,
  label_format         text,
  status               text,
  is_voided            boolean,
  label_cost           numeric,
  label_cost_currency  text,
  rate_id              text,
  service_code         text,
  raw                  jsonb
);
-- ======================
-- SHIPPING: Tracking
-- ======================
CREATE TABLE unified_shipping_tracking (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  shipment_id          text,
  tracking_number      text,
  status               text,
  events               jsonb,
  estimated_delivery   timestamptz,
  actual_delivery_at   timestamptz,
  status_description   text,
  carrier_id           text,
  carrier_status_code  text,
  carrier_status_description text,
  raw                  jsonb
);
-- ======================
-- SHIPPING: Carrier
-- ======================
CREATE TABLE unified_shipping_carrier (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  code                 text,
  is_active            boolean,
  logo_url             text,
  website_url          text,
  raw                  jsonb
);
-- ======================
-- SIGNING: Document
-- ======================
CREATE TABLE unified_signing_document (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  status               text,
  sent_at              timestamptz,
  completed_at         timestamptz,
  expires_at           timestamptz,
  template_id          text,
  download_url         text,
  creator_id           text,
  raw                  jsonb
);
-- ======================
-- SIGNING: Signatory
-- ======================
CREATE TABLE unified_signing_signatory (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  document_id          text,
  name                 text,
  email                text,
  role                 text,
  status               text,
  order                numeric,
  signed_at            timestamptz,
  decline_reason       text,
  raw                  jsonb
);
-- ======================
-- SIGNING: Template
-- ======================
CREATE TABLE unified_signing_template (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  is_active            boolean,
  creator_id           text,
  raw                  jsonb
);
-- ======================
-- CLUBS: Group
-- ======================
CREATE TABLE unified_clubs_group (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  sport_type           text,
  group_type           text,
  address              jsonb,
  member_count         numeric,
  following_count      numeric,
  post_count           numeric,
  is_private           boolean,
  is_verified          boolean,
  is_featured          boolean,
  is_admin             boolean,
  is_owner             boolean,
  membership_status    text,
  url                  text,
  profile_image_url    text,
  cover_image_url      text,
  activity_types       text[],
  raw                  jsonb
);
-- ======================
-- CLUBS: Member
-- ======================
CREATE TABLE unified_clubs_member (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  group_id             text,
  is_admin             boolean,
  is_owner             boolean,
  membership_status    text,
  raw                  jsonb
);
-- ======================
-- CLUBS: Activity
-- ======================
CREATE TABLE unified_clubs_activity (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  group_id             text,
  name                 text,
  description          text,
  type                 text,
  athlete_id           text,
  athlete_name         text,
  distance             numeric,
  moving_time          numeric,
  elapsed_time         numeric,
  total_elevation_gain numeric,
  elevation_high       numeric,
  elevation_low        numeric,
  start_at             timestamptz,
  timezone             text,
  achievement_count    numeric,
  kudos_count          numeric,
  comment_count        numeric,
  athlete_count        numeric,
  photo_count          numeric,
  average_speed        numeric,
  max_speed            numeric,
  average_cadence      numeric,
  average_heartrate    numeric,
  max_heartrate        numeric,
  average_watts        numeric,
  max_watts            numeric,
  weighted_average_watts numeric,
  kilojoules           numeric,
  calories             numeric,
  has_heartrate        boolean,
  is_trainer           boolean,
  is_commute           boolean,
  is_manual            boolean,
  is_private           boolean,
  map_polyline         text,
  map_summary_polyline text,
  workout_type         numeric,
  suffer_score         numeric,
  pr_count             numeric,
  raw                  jsonb
);
-- ======================
-- CLUBS: Event
-- ======================
CREATE TABLE unified_clubs_event (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  group_id             text,
  name                 text,
  description          text,
  type                 text,
  status               text,
  start_at             timestamptz,
  end_at               timestamptz,
  timezone             text,
  duration_minutes     numeric,
  location_id          text,
  location_name        text,
  opponent_id          text,
  opponent_name        text,
  home_team_name       text,
  away_team_name       text,
  home_score           numeric,
  away_score           numeric,
  score_for            numeric,
  score_against        numeric,
  is_home              boolean,
  url                  text,
  raw                  jsonb
);
-- ======================
-- CLUBS: Location
-- ======================
CREATE TABLE unified_clubs_location (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  group_id             text,
  name                 text,
  address              jsonb,
  latitude             numeric,
  longitude            numeric,
  telephone            text,
  url                  text,
  raw                  jsonb
);
-- ======================
-- ANALYTICS: Property
-- ======================
CREATE TABLE unified_analytics_property (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  timezone             text,
  currency             text,
  industry             text,
  parent_id            text,
  raw                  jsonb
);
-- ======================
-- ANALYTICS: Event
-- ======================
CREATE TABLE unified_analytics_event (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  event_type           text,
  visitor_id           text,
  property_id          text,
  session_id           text,
  page_url             text,
  page_title           text,
  page_referrer        text,
  device               text,
  browser              text,
  os                   text,
  country              text,
  country_code         text,
  region               text,
  city                 text,
  metadata             jsonb,
  value                numeric,
  currency             text,
  utm_source           text,
  utm_medium           text,
  utm_campaign         text,
  utm_term             text,
  utm_content          text,
  raw                  jsonb
);
-- ======================
-- ANALYTICS: Session
-- ======================
CREATE TABLE unified_analytics_session (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  property_id          text,
  visitor_id           text,
  start_at             timestamptz,
  end_at               timestamptz,
  duration_seconds     numeric,
  landing_page         text,
  exit_page            text,
  page_views           numeric,
  events_count         numeric,
  source               text,
  medium               text,
  campaign             text,
  device               text,
  browser              text,
  os                   text,
  country              text,
  city                 text,
  is_bounce            boolean,
  is_conversion        boolean,
  raw                  jsonb
);
-- ======================
-- ANALYTICS: Visitor
-- ======================
CREATE TABLE unified_analytics_visitor (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  property_id          text,
  email                text,
  name                 text,
  age                  numeric,
  gender               text,
  country              text,
  country_code         text,
  city                 text,
  language             text,
  timezone             text,
  first_seen_at        timestamptz,
  last_seen_at         timestamptz,
  total_sessions       numeric,
  total_page_views     numeric,
  total_events         numeric,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- ANALYTICS: Report
-- ======================
CREATE TABLE unified_analytics_report (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  property_id          text,
  start_at             timestamptz,
  end_at               timestamptz,
  metrics              jsonb,
  raw                  jsonb
);
-- ======================
-- CDP: Profile
-- ======================
CREATE TABLE unified_cdp_profile (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  email                text,
  telephone            text,
  gender               text,
  birthdate            text,
  title                text,
  company              text,
  address              jsonb,
  identifiers          jsonb,
  metadata             jsonb,
  segments             jsonb,
  is_anonymous         boolean,
  consent              jsonb,
  source_id            text,
  raw                  jsonb
);
-- ======================
-- CDP: Segment
-- ======================
CREATE TABLE unified_cdp_segment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  slug                 text,
  description          text,
  definition           text,
  type                 text,
  compute_mode         text,
  size                 numeric,
  is_active            boolean,
  source_id            text,
  raw                  jsonb
);
-- ======================
-- CDP: Event
-- ======================
CREATE TABLE unified_cdp_event (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  name                 text,
  type                 text,
  occurred_at          timestamptz,
  profile_id           text,
  identifiers          jsonb,
  metadata             jsonb,
  source               text,
  source_id            text,
  raw                  jsonb
);
-- ======================
-- CDP: Source
-- ======================
CREATE TABLE unified_cdp_source (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  slug                 text,
  type                 text,
  direction            text,
  is_enabled           boolean,
  raw                  jsonb
);
-- ======================
-- CDP: Destination
-- ======================
CREATE TABLE unified_cdp_destination (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  slug                 text,
  type                 text,
  direction            text,
  is_enabled           boolean,
  raw                  jsonb
);
-- ======================
-- CDP: Activation
-- ======================
CREATE TABLE unified_cdp_activation (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  segment_id           text,
  destination_id       text,
  source_id            text,
  schedule             text,
  status               text,
  last_run_at          timestamptz,
  is_enabled           boolean,
  raw                  jsonb
);
-- ======================
-- PERFORMANCE: Cycle
-- ======================
CREATE TABLE unified_performance_cycle (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  type                 text,
  status               text,
  start_at             timestamptz,
  end_at               timestamptz,
  due_at               timestamptz,
  raw                  jsonb
);
-- ======================
-- PERFORMANCE: Review
-- ======================
CREATE TABLE unified_performance_review (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  reviewer_user_id     text,
  cycle_id             text,
  template_identifier  text,
  type                 text,
  status               text,
  rating               numeric,
  rating_maximum       numeric,
  rating_description   text,
  comment              text,
  questions            jsonb,
  is_acknowledged      boolean,
  submitted_at         timestamptz,
  completed_at         timestamptz,
  raw                  jsonb
);
-- ======================
-- PERFORMANCE: Goal
-- ======================
CREATE TABLE unified_performance_goal (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  user_ids             text[],
  company_id           text,
  parent_id            text,
  cycle_id             text,
  type                 text,
  status               text,
  progress             numeric,
  weight               numeric,
  start_at             timestamptz,
  due_at               timestamptz,
  completed_at         timestamptz,
  milestones           jsonb,
  raw                  jsonb
);
-- ======================
-- PERFORMANCE: Feedback
-- ======================
CREATE TABLE unified_performance_feedback (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  user_id              text,
  author_user_id       text,
  type                 text,
  message              text,
  tags                 text[],
  is_visible           boolean,
  raw                  jsonb
);
-- ======================
-- SOCIAL: Post
-- ======================
CREATE TABLE unified_social_post (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  profile_id           text,
  parent_post_id       text,
  title                text,
  body                 text,
  status               text,
  type                 text,
  media                jsonb,
  url                  text,
  language             text,
  scheduled_at         timestamptz,
  call_to_action       jsonb,
  metrics              jsonb,
  raw                  jsonb
);
-- ======================
-- SOCIAL: Profile
-- ======================
CREATE TABLE unified_social_profile (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  username             text,
  parent_id            text,
  description          text,
  url                  text,
  website_url          text,
  avatar_url           text,
  phone                text,
  location             text,
  address              jsonb,
  category             text,
  is_verified          boolean,
  is_private           boolean,
  metrics              jsonb,
  raw                  jsonb
);
-- ======================
-- SOCIAL: Review
-- ======================
CREATE TABLE unified_social_review (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  profile_id           text,
  rating               numeric,
  title                text,
  content              text,
  author_name          text,
  author_avatar_url    text,
  author_location      text,
  reply                jsonb,
  url                  text,
  raw                  jsonb
);
-- ======================
-- SOCIAL: Insight
-- ======================
CREATE TABLE unified_social_insight (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  profile_id           text,
  post_id              text,
  date                 timestamptz,
  period               text,
  metric               text,
  value                numeric,
  raw                  jsonb
);
-- ======================
-- LEGAL: Matter
-- ======================
CREATE TABLE unified_legal_matter (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  number               text,
  description          text,
  status               text,
  billing_method       text,
  practicearea_id      text,
  stage                text,
  contact_ids          text[],
  company_ids          text[],
  parties              jsonb,
  user_id              text,
  originating_user_id  text,
  user_ids             text[],
  client_reference     text,
  currency             text,
  is_billable          boolean,
  opened_at            timestamptz,
  closed_at            timestamptz,
  pending_at           timestamptz,
  statute_of_limitations_at timestamptz,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- LEGAL: Practicearea
-- ======================
CREATE TABLE unified_legal_practicearea (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  code                 text,
  is_active            boolean,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- LEGAL: Timeentry
-- ======================
CREATE TABLE unified_legal_timeentry (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  matter_id            text,
  user_id              text,
  description          text,
  worked_at            timestamptz,
  minutes              numeric,
  billable_minutes     numeric,
  rate_amount          numeric,
  total_amount         numeric,
  currency             text,
  is_billable          boolean,
  is_billed            boolean,
  invoice_id           text,
  activity_code        text,
  task_code            text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- LEGAL: Expense
-- ======================
CREATE TABLE unified_legal_expense (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  matter_id            text,
  user_id              text,
  description          text,
  incurred_at          timestamptz,
  quantity             numeric,
  price_amount         numeric,
  total_amount         numeric,
  currency             text,
  type                 text,
  category             text,
  is_billable          boolean,
  is_billed            boolean,
  invoice_id           text,
  expense_code         text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Instance
-- ======================
CREATE TABLE unified_compute_instance (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  status               text,
  status_reason        text,
  allowed_actions      text[],
  market               text,
  region_id            text,
  template_id          text,
  image                text,
  source_snapshot_id   text,
  parent_instance_id   text,
  gputype_id           text,
  gpu_model            text,
  gpu_count            numeric,
  sku                  text,
  cpu_count            numeric,
  memory_mb            numeric,
  disk_mb              numeric,
  architecture         text,
  price_amount         numeric,
  price_unit           text,
  currency             text,
  volume_ids           text[],
  endpoints            jsonb,
  ssh                  jsonb,
  has_internet_access  boolean,
  timeout_seconds      numeric,
  expires_at           timestamptz,
  on_expire            text,
  idle_timeout_seconds numeric,
  on_idle              text,
  project_identifier   text,
  service_id           text,
  env                  jsonb,
  started_at           timestamptz,
  terminated_at        timestamptz,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Template
-- ======================
CREATE TABLE unified_compute_template (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  aliases              text[],
  image                text,
  dockerfile           text,
  start_command        text,
  status               text,
  gpu_model            text,
  gpu_count            numeric,
  cpu_count            numeric,
  memory_mb            numeric,
  disk_mb              numeric,
  ports                jsonb,
  env                  jsonb,
  is_public            boolean,
  last_used_at         timestamptz,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Gputype
-- ======================
CREATE TABLE unified_compute_gputype (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  gpu_model            text,
  gpu_manufacturer     text,
  sku                  text,
  gpu_count            numeric,
  gpu_memory_mb        numeric,
  cpu_count            numeric,
  memory_mb            numeric,
  disk_mb              numeric,
  architecture         text,
  prices               jsonb,
  availability         jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Region
-- ======================
CREATE TABLE unified_compute_region (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  location             text,
  country              text,
  gpu_models           text[],
  raw                  jsonb
);
-- ======================
-- COMPUTE: Volume
-- ======================
CREATE TABLE unified_compute_volume (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  status               text,
  size_mb              numeric,
  used_mb              numeric,
  region_id            text,
  availability_zone    text,
  instance_ids         text[],
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Snapshot
-- ======================
CREATE TABLE unified_compute_snapshot (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  instance_id          text,
  volume_id            text,
  type                 text,
  status               text,
  size_mb              numeric,
  expires_at           timestamptz,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Usage
-- ======================
CREATE TABLE unified_compute_usage (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  instance_id          text,
  category             text,
  quantity             numeric,
  unit                 text,
  cost_amount          numeric,
  currency             text,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Key
-- ======================
CREATE TABLE unified_compute_key (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  public_key           text,
  private_key          text,
  fingerprint          text,
  registry_url         text,
  username             text,
  secret               text,
  instance_id          text,
  expires_at           timestamptz,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Service
-- ======================
CREATE TABLE unified_compute_service (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  type                 text,
  status               text,
  runtime              text,
  region_id            text,
  gputype_id           text,
  sku                  text,
  instance_count       numeric,
  min_instance_count   numeric,
  max_instance_count   numeric,
  repo_url             text,
  branch               text,
  image                text,
  build_command        text,
  start_command        text,
  url                  text,
  project_identifier   text,
  env                  jsonb,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Deployment
-- ======================
CREATE TABLE unified_compute_deployment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  service_id           text,
  status               text,
  trigger              text,
  environment          text,
  commit_identifier    text,
  commit_message       text,
  branch               text,
  image                text,
  url                  text,
  started_at           timestamptz,
  finished_at          timestamptz,
  error                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Domain
-- ======================
CREATE TABLE unified_compute_domain (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  service_id           text,
  name                 text,
  status               text,
  is_primary           boolean,
  redirect_url         text,
  raw                  jsonb
);
-- ======================
-- COMPUTE: Envvar
-- ======================
CREATE TABLE unified_compute_envvar (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  service_id           text,
  name                 text,
  value                text,
  environments         text[],
  is_secret            boolean,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Patient
-- ======================
CREATE TABLE unified_healthcare_patient (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  gender               text,
  birthdate            text,
  is_deceased          boolean,
  deceased_at          timestamptz,
  emails               jsonb,
  telephones           jsonb,
  address              jsonb,
  language             text,
  identifiers          jsonb,
  practitioner_ids     text[],
  is_active            boolean,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Practitioner
-- ======================
CREATE TABLE unified_healthcare_practitioner (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  first_name           text,
  last_name            text,
  title                text,
  gender               text,
  emails               jsonb,
  telephones           jsonb,
  address              jsonb,
  image_url            text,
  identifiers          jsonb,
  specialties          jsonb,
  qualifications       jsonb,
  languages            text[],
  location_ids         text[],
  is_active            boolean,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Location
-- ======================
CREATE TABLE unified_healthcare_location (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  name                 text,
  description          text,
  parent_id            text,
  organization_name    text,
  address              jsonb,
  telephones           jsonb,
  emails               jsonb,
  latitude             numeric,
  longitude            numeric,
  identifiers          jsonb,
  is_active            boolean,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Appointment
-- ======================
CREATE TABLE unified_healthcare_appointment (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  practitioner_ids     text[],
  location_id          text,
  slot_ids             text[],
  status               text,
  start_at             timestamptz,
  end_at               timestamptz,
  description          text,
  service_types        jsonb,
  reasons              jsonb,
  cancellation_reason  text,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Slot
-- ======================
CREATE TABLE unified_healthcare_slot (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  practitioner_id      text,
  location_id          text,
  status               text,
  start_at             timestamptz,
  end_at               timestamptz,
  service_types        jsonb,
  is_overbooked        boolean,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Encounter
-- ======================
CREATE TABLE unified_healthcare_encounter (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  practitioner_ids     text[],
  location_id          text,
  appointment_id       text,
  condition_ids        text[],
  status               text,
  type                 text,
  reasons              jsonb,
  start_at             timestamptz,
  end_at               timestamptz,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Condition
-- ======================
CREATE TABLE unified_healthcare_condition (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  encounter_id         text,
  practitioner_id      text,
  name                 text,
  codes                jsonb,
  status               text,
  type                 text,
  onset_at             timestamptz,
  resolved_at          timestamptz,
  recorded_at          timestamptz,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Allergy
-- ======================
CREATE TABLE unified_healthcare_allergy (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  encounter_id         text,
  practitioner_id      text,
  name                 text,
  codes                jsonb,
  status               text,
  type                 text,
  criticality          text,
  reactions            jsonb,
  onset_at             timestamptz,
  recorded_at          timestamptz,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Medication
-- ======================
CREATE TABLE unified_healthcare_medication (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  encounter_id         text,
  practitioner_id      text,
  name                 text,
  codes                jsonb,
  status               text,
  dosage               text,
  refill_count         numeric,
  authored_at          timestamptz,
  start_at             timestamptz,
  end_at               timestamptz,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Observation
-- ======================
CREATE TABLE unified_healthcare_observation (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  encounter_id         text,
  practitioner_id      text,
  name                 text,
  codes                jsonb,
  status               text,
  type                 text,
  value_number         numeric,
  value_unit           text,
  value_text           text,
  interpretation       text,
  reference_range      jsonb,
  components           jsonb,
  observed_at          timestamptz,
  issued_at            timestamptz,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- HEALTHCARE: Immunization
-- ======================
CREATE TABLE unified_healthcare_immunization (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  created_at           timestamptz,
  updated_at           timestamptz,
  patient_id           text,
  encounter_id         text,
  practitioner_id      text,
  location_id          text,
  name                 text,
  codes                jsonb,
  status               text,
  administered_at      timestamptz,
  lot_number           text,
  expires_at           timestamptz,
  notes                text,
  metadata             jsonb,
  raw                  jsonb
);
-- ======================
-- SCIM: Users
-- ======================
CREATE TABLE unified_scim_user (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  schemas              text[],
  externalId           text,
  userType             text,
  userName             text,
  meta                 jsonb,
  name                 jsonb,
  displayName          text,
  nickName             text,
  profileUrl           text,
  title                text,
  preferredLanguage    text,
  locale               text,
  timezone             text,
  active               boolean,
  password             text,
  phoneNumbers         jsonb,
  emails               jsonb,
  ims                  jsonb,
  photos               jsonb,
  addresses            jsonb,
  groups               jsonb,
  entitlements         jsonb,
  roles                jsonb,
  x509Certificates     jsonb,
  urn:ietf:params:scim:schemas:extension:enterprise:2.0:User jsonb,
  urn:ietf:params:scim:schemas:extension:lattice:attributes:1.0:User jsonb,
  urn:ietf:params:scim:schemas:extension:peakon:2.0:User jsonb
);
-- ======================
-- SCIM: Groups
-- ======================
CREATE TABLE unified_scim_group (
  unified_connection_id  text NOT NULL,
  unified_webhook_id     text NOT NULL,
  unified_external_xref  text,
  unified_integration_type text NOT NULL,
  unified_raw_id         text,
  unified_id             text NOT NULL,
  id                   text,
  externalId           text,
  displayName          text,
  groupType            text,
  members              jsonb,
  meta                 jsonb,
  schemas              text[]
);
