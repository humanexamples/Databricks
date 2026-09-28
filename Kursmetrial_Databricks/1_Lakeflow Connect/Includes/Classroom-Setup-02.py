# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA IDENTIFIER(DA.schema_name);

# COMMAND ----------

spark.sql('DROP TABLE IF EXISTS mydeltatable')
spark.sql('CREATE TABLE IF NOT EXISTS mydeltatable (id INT, name STRING)')
spark.sql('INSERT INTO mydeltatable (id, name) VALUES (1,"Peter")')
print('Created Delta table mydeltatable for the demonstration.')