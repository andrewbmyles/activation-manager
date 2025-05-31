-- BigQuery Setup Script for Activation Manager
-- This script creates the necessary tables for persisting user data

-- Create dataset if not exists
-- Run in BigQuery Console: CREATE SCHEMA IF NOT EXISTS `your-project.activation_manager`;

-- 1. Audiences Table
CREATE TABLE IF NOT EXISTS `activation_manager.audiences` (
  audience_id STRING NOT NULL,
  user_id STRING NOT NULL,
  name STRING NOT NULL,
  description STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  status STRING NOT NULL DEFAULT 'draft',
  data_type STRING NOT NULL,
  original_query STRING,
  selected_variables ARRAY<STRING>,
  variable_details JSON,
  segments JSON,
  total_audience_size INT64,
  metadata JSON
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, status
OPTIONS(
  description="Stores user-created audience definitions with their variables and segments"
);

-- 2. Platforms Table
CREATE TABLE IF NOT EXISTS `activation_manager.platforms` (
  platform_id STRING NOT NULL,
  user_id STRING NOT NULL,
  platform_type STRING NOT NULL,
  name STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  status STRING NOT NULL DEFAULT 'active',
  credentials JSON,  -- Must be encrypted before storage
  settings JSON,
  last_sync TIMESTAMP,
  sync_status STRING
)
CLUSTER BY user_id, platform_type
OPTIONS(
  description="Stores platform configurations for distribution"
);

-- 3. Distributions Table
CREATE TABLE IF NOT EXISTS `activation_manager.distributions` (
  distribution_id STRING NOT NULL,
  user_id STRING NOT NULL,
  audience_id STRING NOT NULL,
  platform_id STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  scheduled_at TIMESTAMP,
  executed_at TIMESTAMP,
  status STRING NOT NULL DEFAULT 'scheduled',
  distribution_type STRING DEFAULT 'initial',
  segments_distributed ARRAY<STRING>,
  match_results JSON,
  error_details JSON,
  metadata JSON
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, audience_id, status
OPTIONS(
  description="Tracks audience distributions to platforms"
);

-- 4. Users Table (Optional)
CREATE TABLE IF NOT EXISTS `activation_manager.users` (
  user_id STRING NOT NULL,
  email STRING NOT NULL,
  organization STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  last_login TIMESTAMP,
  permissions ARRAY<STRING>,
  quota JSON
)
CLUSTER BY organization
OPTIONS(
  description="Basic user information for multi-tenancy"
);

-- Create views for common access patterns

-- Recent audiences view
CREATE OR REPLACE VIEW `activation_manager.v_recent_audiences` AS
SELECT 
  a.*,
  ARRAY_LENGTH(selected_variables) as variable_count,
  JSON_EXTRACT_SCALAR(metadata, '$.campaign_id') as campaign_id
FROM `activation_manager.audiences` a
WHERE status != 'archived'
ORDER BY created_at DESC;

-- Distribution summary view
CREATE OR REPLACE VIEW `activation_manager.v_distribution_summary` AS
SELECT 
  d.*,
  a.name as audience_name,
  p.name as platform_name,
  p.platform_type,
  JSON_EXTRACT_SCALAR(d.match_results, '$.match_rate') as match_rate
FROM `activation_manager.distributions` d
JOIN `activation_manager.audiences` a ON d.audience_id = a.audience_id
JOIN `activation_manager.platforms` p ON d.platform_id = p.platform_id
ORDER BY d.created_at DESC;

-- User activity view
CREATE OR REPLACE VIEW `activation_manager.v_user_activity` AS
SELECT 
  u.user_id,
  u.email,
  u.organization,
  COUNT(DISTINCT a.audience_id) as total_audiences,
  COUNT(DISTINCT p.platform_id) as total_platforms,
  COUNT(DISTINCT d.distribution_id) as total_distributions,
  MAX(a.created_at) as last_audience_created,
  MAX(d.created_at) as last_distribution
FROM `activation_manager.users` u
LEFT JOIN `activation_manager.audiences` a ON u.user_id = a.user_id
LEFT JOIN `activation_manager.platforms` p ON u.user_id = p.user_id
LEFT JOIN `activation_manager.distributions` d ON u.user_id = d.user_id
GROUP BY u.user_id, u.email, u.organization;

-- Create stored procedures for common operations

-- Procedure to archive old distributions
CREATE OR REPLACE PROCEDURE `activation_manager.sp_archive_old_distributions`(
  days_to_keep INT64
)
BEGIN
  UPDATE `activation_manager.distributions`
  SET status = 'archived',
      updated_at = CURRENT_TIMESTAMP()
  WHERE DATE_DIFF(CURRENT_DATE(), DATE(created_at), DAY) > days_to_keep
    AND status IN ('completed', 'failed');
END;

-- Procedure to get audience with full details
CREATE OR REPLACE PROCEDURE `activation_manager.sp_get_audience_details`(
  IN p_audience_id STRING,
  OUT audience_data JSON
)
BEGIN
  SET audience_data = (
    SELECT TO_JSON_STRING(t)
    FROM (
      SELECT 
        a.*,
        ARRAY(
          SELECT AS STRUCT d.*
          FROM `activation_manager.distributions` d
          WHERE d.audience_id = p_audience_id
          ORDER BY d.created_at DESC
          LIMIT 10
        ) as recent_distributions
      FROM `activation_manager.audiences` a
      WHERE a.audience_id = p_audience_id
    ) t
  );
END;