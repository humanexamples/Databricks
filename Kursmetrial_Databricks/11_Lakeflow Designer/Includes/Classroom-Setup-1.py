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

# DBTITLE 1,Path to Source Data
try:
    data_folder_path = find_folder(folder_name = 'Includes/data') 
except:
    data_folder_path = find_folder(folder_name = 'data') 

# COMMAND ----------

# DBTITLE 1,Create Source Files Volume
_ = spark.sql(f'CREATE VOLUME IF NOT EXISTS {my_catalog}.{my_schema}.source_files')

volume_path = f'/Volumes/{my_catalog}/{my_schema}/source_files'

## Set SQL variable for volue_path
_ = spark.sql(f'DECLARE OR REPLACE VARIABLE volume_path STRING')
_ = spark.sql(f'SET VAR volume_path = "{volume_path}"')

# COMMAND ----------

# DBTITLE 1,Copy Files to Volume

############################
## feedback files to volume
############################
folder = 'feedback'
copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_folder_path}/{folder}',
    target_volume_path=f'{volume_path}/{folder}',
    n=1
)

# ############################
# ## participant_lookup files to volume
# ############################
# folder = 'participant_lookup'

# copy_workspace_files_to_volume(
#     src_workspace_folder=f'{data_folder_path}/{folder}',
#     target_volume_path=f'{volume_path}/{folder}',
#     n=1
# )


############################
## participants files to volume
############################
folder = 'participants'

copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_folder_path}/{folder}',
    target_volume_path=f'{volume_path}/{folder}',
    n=1
)


############################
## sessions files to volume
############################
folder = 'sessions'

copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_folder_path}/{folder}',
    target_volume_path=f'{volume_path}/{folder}',
    n=1
)


# COMMAND ----------

# DBTITLE 1,CREATE TABLES
################################
# PARTICIPANTS
################################
create_table_from_files(
    catalog=my_catalog,
    schema=my_schema,
    table="participants_bronze",
    volume_path=f"{volume_path}/participants",
    format="json",
    options={"multiLine": "true"},
)

################################
# FEEDBACK
################################
create_table_from_files(
    catalog=my_catalog,
    schema=my_schema,
    table="feedback_bronze",
    volume_path=f"{volume_path}/feedback",
    format="json",
    options={"multiLine": "true", "schema": "meeting_uuid STRING, responses STRING"},
)


################################
# sessions
################################
create_table_from_files(
    catalog=my_catalog,
    schema=my_schema,
    table="sessions_bronze",
    volume_path=f"{volume_path}/sessions",
    format="json",
    options={"multiLine": "true"},
)

# COMMAND ----------

display_config_values(
  [
    ("Your Catalog", my_catalog),
    ("Your Schema", my_schema)
  ]
)

compute_validation(recommend_dbr_classic_version=None, recommended_serverless_version=5)