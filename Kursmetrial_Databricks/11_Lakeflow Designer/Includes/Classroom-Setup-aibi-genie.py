# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common-Python

# COMMAND ----------

# DBTITLE 1,Create Catalog
## Set the user's default catalog (labuser_xxx)
_ = spark.sql(f'USE CATALOG {my_catalog}')

## Creates a SQL variable called my_catalog
_ = spark.sql(f'DECLARE OR REPLACE VARIABLE my_catalog STRING')
_ = spark.sql(f'SET VAR my_catalog = "{my_catalog}"')

# COMMAND ----------

# DBTITLE 1,Create Schema
########################################
## Create Schema 
########################################
my_schema = 'designer_meeting'
create_schemas(in_catalog = my_catalog, schemas_to_create = [my_schema])
_ = spark.sql(f'USE SCHEMA {my_schema}')

## Set SQL variable for schema
_ = spark.sql(f'DECLARE OR REPLACE VARIABLE my_schema STRING')
_ = spark.sql(f'SET VAR my_schema = "{my_schema}"')

# COMMAND ----------

# DBTITLE 1,Create Gold Tables If Not Exists

# ----------------------------------------------------------------------------------
# Seed definitions: one CREATE TABLE ... AS SELECT ... FROM VALUES per gold table.
# {fq} is replaced with the fully-qualified table name at runtime.
# NOTE: the apostrophe in a presenter name uses char(39) (not '' or backslash) so the
# literal is safe both as direct SQL and inside this Python string.
# ----------------------------------------------------------------------------------
GOLD_TABLES = {
    "gold_session_summary": """CREATE TABLE IF NOT EXISTS {fq} AS
    SELECT
        CAST(meeting_uuid AS STRING) AS meeting_uuid,
        CAST(session_name AS STRING) AS session_name,
        CAST(difficulty_level AS STRING) AS difficulty_level,
        CAST(event_date AS DATE) AS event_date,
        CAST(planned_duration_minutes AS BIGINT) AS planned_duration_minutes,
        CAST(presenter AS STRING) AS presenter,
        CAST(topic_category AS STRING) AS topic_category,
        CAST(total_attendees AS BIGINT) AS total_attendees,
        CAST(avg_duration_minutes AS DOUBLE) AS avg_duration_minutes
    FROM VALUES
        ('A0Fn+yCQQWaAjn1CKXeFHw==', 'Building RAG Applications on Databricks', 'Intermediate', '2025-11-03', 45, concat('James O', char(39), 'Brien'), 'AI/GenAI', 45, 35.0),
        ('zLoS4TxQSmKMLDrhT9bDRw==', 'CI/CD for Databricks Projects', 'Intermediate', '2025-11-03', 60, 'David Kim', 'DevOps', 17, 55.0),
        ('n72+ESyiS9C5YzGZzQexzg==', 'Databricks Asset Bundles 101', 'Intermediate', '2025-11-03', 60, 'Olivia Wang', 'DevOps', 51, 45.0),
        ('8xckvuCqTW6Ug0oQyJ94sg==', 'Databricks Asset Bundles 101', 'Advanced', '2025-11-03', 60, 'Tyler Brooks', 'DevOps', 49, 47.0),
        ('MUVmi3YYTNyigYwwrmD4VQ==', 'Databricks SQL Performance Tuning', 'Intermediate', '2025-11-03', 45, 'Raj Sundaram', 'Performance Optimization', 32, 35.0),
        ('wxbB1URtRnaPx6wUt/1S9g==', 'Databricks SQL Performance Tuning', 'Beginner', '2025-11-03', 45, 'Olivia Wang', 'Performance Optimization', 154, 36.0),
        ('pXs1rdaSQG2hQyQzEh8PVQ==', 'Databricks Workflows and Orchestration', 'Intermediate', '2025-11-03', 60, concat('James O', char(39), 'Brien'), 'AI/GenAI', 19, 49.0),
        ('qR7xKmN3T5WvYpLd8eZbJA==', 'Fine-Tuning LLMs on Databricks', 'Beginner', '2025-11-03', 45, 'Priya Patel', 'DevOps', NULL, NULL),
        ('6FfGZTDfRaOaV60bTjcEWw==', 'Introduction to Delta Sharing', 'Intermediate', '2025-11-03', 30, 'Priya Patel', 'Data Governance', 153, 24.0),
        ('ZtpDeZReStCXqBgXwqxcgA==', 'Lakebase Core Concepts', 'Advanced', '2025-11-03', 30, 'Priya Patel', 'Data Engineering', 11, 25.0),
        ('IYLmFeNeSBCG4nKRKOBecA==', 'MLflow Model Registry Best Practices', 'Beginner', '2025-11-03', 30, concat('James O', char(39), 'Brien'), 'Machine Learning', 46, 24.0),
        ('Kl3kufkDQYi4HZyd8cNgfw==', 'Photon Engine Performance Workshop', 'Beginner', '2025-11-03', 45, 'Tyler Brooks', 'Performance Optimization', 93, 35.0),
        ('/e3hcn3IRDO17ugBv3bXHg==', 'Serverless Compute Deep Dive', 'Intermediate', '2025-11-03', 60, 'Alex Martinez', 'DevOps', 52, 46.0),
        ('+S4Pk2aOT/iK4yZHYJhRcQ==', 'Serverless Compute Deep Dive', 'Intermediate', '2025-11-03', 90, 'Raj Sundaram', 'DevOps', 21, 76.0),
        ('4H8dS3ajRi+L0+dt4VkIoQ==', 'Unity Catalog Deep Dive', 'Beginner', '2025-11-03', 60, 'Tyler Brooks', 'Data Governance', 24, 46.0),
        ('b9DFS9uOQYSKCvjn47x8Gg==', 'Workspace Administration Fundamentals', 'Advanced', '2025-11-03', 30, 'Alex Martinez', 'Platform Administration', 34, 25.0),
        ('xtuXYkbSQaKDrDoCKO6ZRw==', 'Building Multi-Agent Systems', 'Beginner', '2025-11-04', 60, 'Nadia Kowalski', 'AI/GenAI', 57, 47.0),
        ('eRBoBDPXStuZ72F/YZKSyg==', 'Cluster Policies and Access Control', 'Intermediate', '2025-11-04', 45, 'Nadia Kowalski', 'Platform Administration', 152, 35.0),
        ('32kQUGAwSeCCSKJdM5FUtQ==', 'Cost Optimization Strategies', 'Intermediate', '2025-11-04', 60, 'Sarah Chen', 'Performance Optimization', 14, 48.0),
        ('wMRIAOYbSoaiTukN4hcxqA==', 'Data Engineering with Auto Loader', 'Intermediate', '2025-11-04', 45, concat('James O', char(39), 'Brien'), 'Data Engineering', 126, 35.0),
        ('VMdJ3ULURuG/+vCnYrKuOg==', 'Lakehouse Monitoring Deep Dive', 'Beginner', '2025-11-04', 45, 'Sarah Chen', 'Analytics', 20, 36.0),
        ('cdNHA8OmQtuI9L//LsrQfA==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-04', 90, 'Alex Martinez', 'Performance Optimization', 301, 71.0),
        ('n2LZtV8NReqBB/O5YgJSOg==', 'Databricks Workflows and Orchestration', 'Intermediate', '2025-11-05', 60, 'Rachel Thompson', 'Machine Learning', 304, 47.0),
        ('S3jXVdWJRVOTTw5cNkwBXw==', 'Delta Lake Optimization Techniques', 'Intermediate', '2025-11-05', 30, 'David Kim', 'Data Engineering', 58, 24.0),
        ('7gko3Uu0TQ6iJ8ykEAKqmQ==', 'Governance with Unity Catalog', 'Beginner', '2025-11-05', 30, 'Marcus Johnson', 'Data Governance', 99, 24.0),
        ('A4Q3s7NZSGqT5DdaMfuGcA==', 'Governance with Unity Catalog', 'Beginner', '2025-11-05', 45, 'Tyler Brooks', 'Data Governance', 51, 36.0),
        ('oHQd34I2SqW/xsOLH15dXQ==', 'Introduction to Mosaic AI Agents', 'Advanced', '2025-11-05', 45, 'Priya Patel', 'AI/GenAI', 192, 35.0),
        ('6uqID4Q6RNOs9BF+ysV86Q==', 'Lakehouse Monitoring Deep Dive', 'Advanced', '2025-11-05', 90, concat('James O', char(39), 'Brien'), 'Analytics', 12, 71.0),
        ('MbyD17xTQqKVZPQWAsdKXg==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-05', 60, concat('James O', char(39), 'Brien'), 'Performance Optimization', 45, 46.0),
        ('BpNYP8eZS8+aFDyqfj1xDg==', 'Vector Search Implementation Patterns', 'Intermediate', '2025-11-05', 60, 'Sarah Chen', 'Platform Administration', 29, 47.0),
        ('zs9B+IBwRMOuiuh7HQSuog==', 'Vector Search Implementation Patterns', 'Beginner', '2025-11-05', 90, 'Priya Patel', 'DevOps', 128, 69.0),
        ('129C862+SG2TFdctGI1CWQ==', 'Building RAG Applications on Databricks', 'Advanced', '2025-11-06', 90, 'Tyler Brooks', 'AI/GenAI', 68, 70.0),
        ('MlWvtJs5SxyEIXn6gH2zcQ==', 'Building RAG Applications on Databricks', 'Beginner', '2025-11-06', 60, 'Tyler Brooks', 'AI/GenAI', 30, 46.0),
        ('hAwu2ymxR7C4IJACg4Xhgw==', 'Cost Optimization Strategies', 'Beginner', '2025-11-06', 45, 'Elena Rodriguez', 'Performance Optimization', 51, 34.0),
        ('8IFbPCnKS4yi9udnquPAuw==', 'Real-time Analytics with DBSQL', 'Intermediate', '2025-11-06', 45, 'David Kim', 'Analytics', 83, 35.0),
        ('rJ2TuQnFQqyhaMK1otXElg==', 'Workspace Administration Fundamentals', 'Beginner', '2025-11-06', 30, 'Marcus Johnson', 'Platform Administration', 43, 23.0),
        ('462k7trSRNmLQYCTNYnlag==', 'CI/CD for Databricks Projects', 'Beginner', '2025-11-07', 45, 'David Kim', 'DevOps', 184, 36.0),
        ('v7VvlR9HQY+2sKCleislIQ==', 'Cost Optimization Strategies', 'Beginner', '2025-11-07', 30, 'Rachel Thompson', 'Performance Optimization', 48, 24.0),
        ('TO8imE/dS6SCOvT2nxHzzw==', 'Governance with Unity Catalog', 'Advanced', '2025-11-07', 60, 'Elena Rodriguez', 'Data Governance', 73, 47.0),
        ('4iUQF0z3Rs+SG6H6Ap0cdQ==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-07', 60, 'David Kim', 'Performance Optimization', 11, 44.0),
        ('rWM93eUNRvGqWtBYsJ8LMA==', 'Vector Search Implementation Patterns', 'Intermediate', '2025-11-07', 45, 'Alex Martinez', 'Data Engineering', 138, 35.0)
    AS t(meeting_uuid, session_name, difficulty_level, event_date, planned_duration_minutes, presenter, topic_category, total_attendees, avg_duration_minutes)
""",
    "gold_feedback_summary": """CREATE TABLE IF NOT EXISTS {fq} AS
    SELECT
        CAST(meeting_uuid AS STRING) AS meeting_uuid,
        CAST(session_name AS STRING) AS session_name,
        CAST(difficulty_level AS STRING) AS difficulty_level,
        CAST(event_date AS DATE) AS event_date,
        CAST(planned_duration_minutes AS BIGINT) AS planned_duration_minutes,
        CAST(presenter AS STRING) AS presenter,
        CAST(topic_category AS STRING) AS topic_category,
        CAST(avg_session_rating AS DOUBLE) AS avg_session_rating,
        CAST(avg_speaker_rating AS DOUBLE) AS avg_speaker_rating
    FROM VALUES
        ('A0Fn+yCQQWaAjn1CKXeFHw==', 'Building RAG Applications on Databricks', 'Intermediate', '2025-11-03', 45, concat('James O', char(39), 'Brien'), 'AI/GenAI', 3.5, 3.8),
        ('zLoS4TxQSmKMLDrhT9bDRw==', 'CI/CD for Databricks Projects', 'Intermediate', '2025-11-03', 60, 'David Kim', 'DevOps', 4.2, 4.5),
        ('n72+ESyiS9C5YzGZzQexzg==', 'Databricks Asset Bundles 101', 'Intermediate', '2025-11-03', 60, 'Olivia Wang', 'DevOps', 4.1, 4.5),
        ('8xckvuCqTW6Ug0oQyJ94sg==', 'Databricks Asset Bundles 101', 'Advanced', '2025-11-03', 60, 'Tyler Brooks', 'DevOps', 3.9, 4.2),
        ('MUVmi3YYTNyigYwwrmD4VQ==', 'Databricks SQL Performance Tuning', 'Intermediate', '2025-11-03', 45, 'Raj Sundaram', 'Performance Optimization', 4.3, 4.4),
        ('wxbB1URtRnaPx6wUt/1S9g==', 'Databricks SQL Performance Tuning', 'Beginner', '2025-11-03', 45, 'Olivia Wang', 'Performance Optimization', 4.2, 4.5),
        ('pXs1rdaSQG2hQyQzEh8PVQ==', 'Databricks Workflows and Orchestration', 'Intermediate', '2025-11-03', 60, concat('James O', char(39), 'Brien'), 'AI/GenAI', 3.6, 3.6),
        ('qR7xKmN3T5WvYpLd8eZbJA==', 'Fine-Tuning LLMs on Databricks', 'Beginner', '2025-11-03', 45, 'Priya Patel', 'DevOps', NULL, NULL),
        ('6FfGZTDfRaOaV60bTjcEWw==', 'Introduction to Delta Sharing', 'Intermediate', '2025-11-03', 30, 'Priya Patel', 'Data Governance', 4.6, 4.6),
        ('ZtpDeZReStCXqBgXwqxcgA==', 'Lakebase Core Concepts', 'Advanced', '2025-11-03', 30, 'Priya Patel', 'Data Engineering', 4.6, 4.4),
        ('IYLmFeNeSBCG4nKRKOBecA==', 'MLflow Model Registry Best Practices', 'Beginner', '2025-11-03', 30, concat('James O', char(39), 'Brien'), 'Machine Learning', 3.5, 3.7),
        ('Kl3kufkDQYi4HZyd8cNgfw==', 'Photon Engine Performance Workshop', 'Beginner', '2025-11-03', 45, 'Tyler Brooks', 'Performance Optimization', 3.8, 4.0),
        ('/e3hcn3IRDO17ugBv3bXHg==', 'Serverless Compute Deep Dive', 'Intermediate', '2025-11-03', 60, 'Alex Martinez', 'DevOps', 3.6, 4.3),
        ('+S4Pk2aOT/iK4yZHYJhRcQ==', 'Serverless Compute Deep Dive', 'Intermediate', '2025-11-03', 90, 'Raj Sundaram', 'DevOps', 4.1, 4.5),
        ('4H8dS3ajRi+L0+dt4VkIoQ==', 'Unity Catalog Deep Dive', 'Beginner', '2025-11-03', 60, 'Tyler Brooks', 'Data Governance', 3.7, 4.3),
        ('b9DFS9uOQYSKCvjn47x8Gg==', 'Workspace Administration Fundamentals', 'Advanced', '2025-11-03', 30, 'Alex Martinez', 'Platform Administration', 3.3, 3.9),
        ('xtuXYkbSQaKDrDoCKO6ZRw==', 'Building Multi-Agent Systems', 'Beginner', '2025-11-04', 60, 'Nadia Kowalski', 'AI/GenAI', 3.2, 3.6),
        ('eRBoBDPXStuZ72F/YZKSyg==', 'Cluster Policies and Access Control', 'Intermediate', '2025-11-04', 45, 'Nadia Kowalski', 'Platform Administration', 3.5, 3.6),
        ('32kQUGAwSeCCSKJdM5FUtQ==', 'Cost Optimization Strategies', 'Intermediate', '2025-11-04', 60, 'Sarah Chen', 'Performance Optimization', 4.9, 4.3),
        ('wMRIAOYbSoaiTukN4hcxqA==', 'Data Engineering with Auto Loader', 'Intermediate', '2025-11-04', 45, concat('James O', char(39), 'Brien'), 'Data Engineering', 3.4, 3.8),
        ('VMdJ3ULURuG/+vCnYrKuOg==', 'Lakehouse Monitoring Deep Dive', 'Beginner', '2025-11-04', 45, 'Sarah Chen', 'Analytics', 4.3, 4.8),
        ('cdNHA8OmQtuI9L//LsrQfA==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-04', 90, 'Alex Martinez', 'Performance Optimization', 3.8, 4.1),
        ('n2LZtV8NReqBB/O5YgJSOg==', 'Databricks Workflows and Orchestration', 'Intermediate', '2025-11-05', 60, 'Rachel Thompson', 'Machine Learning', 4.3, 4.5),
        ('S3jXVdWJRVOTTw5cNkwBXw==', 'Delta Lake Optimization Techniques', 'Intermediate', '2025-11-05', 30, 'David Kim', 'Data Engineering', 4.3, 4.4),
        ('7gko3Uu0TQ6iJ8ykEAKqmQ==', 'Governance with Unity Catalog', 'Beginner', '2025-11-05', 30, 'Marcus Johnson', 'Data Governance', 3.7, 4.2),
        ('A4Q3s7NZSGqT5DdaMfuGcA==', 'Governance with Unity Catalog', 'Beginner', '2025-11-05', 45, 'Tyler Brooks', 'Data Governance', 3.8, 3.7),
        ('oHQd34I2SqW/xsOLH15dXQ==', 'Introduction to Mosaic AI Agents', 'Advanced', '2025-11-05', 45, 'Priya Patel', 'AI/GenAI', 4.5, 4.5),
        ('6uqID4Q6RNOs9BF+ysV86Q==', 'Lakehouse Monitoring Deep Dive', 'Advanced', '2025-11-05', 90, concat('James O', char(39), 'Brien'), 'Analytics', 4.1, 3.9),
        ('MbyD17xTQqKVZPQWAsdKXg==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-05', 60, concat('James O', char(39), 'Brien'), 'Performance Optimization', 3.3, 3.6),
        ('BpNYP8eZS8+aFDyqfj1xDg==', 'Vector Search Implementation Patterns', 'Intermediate', '2025-11-05', 60, 'Sarah Chen', 'Platform Administration', 4.7, 4.7),
        ('zs9B+IBwRMOuiuh7HQSuog==', 'Vector Search Implementation Patterns', 'Beginner', '2025-11-05', 90, 'Priya Patel', 'DevOps', 4.5, 4.6),
        ('129C862+SG2TFdctGI1CWQ==', 'Building RAG Applications on Databricks', 'Advanced', '2025-11-06', 90, 'Tyler Brooks', 'AI/GenAI', 3.7, 4.1),
        ('MlWvtJs5SxyEIXn6gH2zcQ==', 'Building RAG Applications on Databricks', 'Beginner', '2025-11-06', 60, 'Tyler Brooks', 'AI/GenAI', 3.8, 4.3),
        ('hAwu2ymxR7C4IJACg4Xhgw==', 'Cost Optimization Strategies', 'Beginner', '2025-11-06', 45, 'Elena Rodriguez', 'Performance Optimization', 4.7, 4.7),
        ('8IFbPCnKS4yi9udnquPAuw==', 'Real-time Analytics with DBSQL', 'Intermediate', '2025-11-06', 45, 'David Kim', 'Analytics', 4.1, 4.7),
        ('rJ2TuQnFQqyhaMK1otXElg==', 'Workspace Administration Fundamentals', 'Beginner', '2025-11-06', 30, 'Marcus Johnson', 'Platform Administration', 4.0, 3.8),
        ('462k7trSRNmLQYCTNYnlag==', 'CI/CD for Databricks Projects', 'Beginner', '2025-11-07', 45, 'David Kim', 'DevOps', 4.3, 4.4),
        ('v7VvlR9HQY+2sKCleislIQ==', 'Cost Optimization Strategies', 'Beginner', '2025-11-07', 30, 'Rachel Thompson', 'Performance Optimization', 4.5, 4.5),
        ('TO8imE/dS6SCOvT2nxHzzw==', 'Governance with Unity Catalog', 'Advanced', '2025-11-07', 60, 'Elena Rodriguez', 'Data Governance', 4.5, 4.7),
        ('4iUQF0z3Rs+SG6H6Ap0cdQ==', 'Photon Engine Performance Workshop', 'Advanced', '2025-11-07', 60, 'David Kim', 'Performance Optimization', 4.2, 4.2),
        ('rWM93eUNRvGqWtBYsJ8LMA==', 'Vector Search Implementation Patterns', 'Intermediate', '2025-11-07', 45, 'Alex Martinez', 'Data Engineering', 3.8, 4.0)
    AS t(meeting_uuid, session_name, difficulty_level, event_date, planned_duration_minutes, presenter, topic_category, avg_session_rating, avg_speaker_rating)
""",
}

# COMMAND ----------

# DBTITLE 1,Create Gold Tables
# ----------------------------------------------------------------------------------
# Ensure each gold table exists, with notes for the learner
# ----------------------------------------------------------------------------------
def ensure_gold_tables(catalog: str, schema: str) -> None:
    """Create each gold table only if it does not already exist, printing a note
    for the learner about what happened to each one."""
    line = "=" * 70

    print(line)
    print("  Gold table setup for Demo - Deliver Insights with AI/BI and Genie")
    print(line)
    print(f"  Catalog: {catalog}")
    print(f"  Schema:  {schema}")
    print(line)

    created, skipped = 0, 0
    for table_name, ddl_template in GOLD_TABLES.items():
        fq = f"{catalog}.{schema}.{table_name}"

        if spark.catalog.tableExists(fq):
            rows = spark.table(fq).count()
            skipped += 1
            print(f"  [SKIP]   {table_name}: already exists ({rows:,} rows). "
                  f"Leaving your table as-is.")
        else:
            print(f"  [CREATE] {table_name}: not found. Creating it for this demo...")
            spark.sql(ddl_template.format(fq=fq))
            rows = spark.table(fq).count()
            created += 1
            print(f"           {table_name}: created ({rows:,} rows).")

    print(line)
    if created == 0:
        print("  Both gold tables already existed. Nothing to create.")
    elif skipped == 0:
        print(f"  Created {created} gold table(s) from seed data.")
    else:
        print(f"  Created {created} gold table(s); {skipped} already existed.")
    print("  Gold layer is ready. You can proceed with the demonstration.")
    print(line)


ensure_gold_tables(my_catalog, my_schema)

# COMMAND ----------

display_config_values(
  [
    ("Your Catalog", my_catalog),
    ("Your Schema", my_schema)
  ]
)

compute_validation(recommend_dbr_classic_version=None, recommended_serverless_version=5)