# Workspace bereitstellen und verwalten

Ressourcen ohne Admin-Rechte (Secrets, Notebooks, Jobs, Cluster, Instance Pools), Workspace-Sicherheit mit Admin-Rechten (Gruppen, Nutzer, Berechtigungen), Storage-Optionen sowie fortgeschrittene Konfiguration (IP-Access-Lists) mit dem Databricks-Terraform-Provider. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Provider-Grundkonfiguration](#provider-konfig)
2. [Standardfunktionalität (ohne Admin-Rechte)](#standard)
3. [Workspace-Sicherheit (Admin-Rechte erforderlich)](#sicherheit)
4. [Storage](#storage)
5. [Fortgeschrittene Konfiguration: IP-Access-Lists](#ip-access)
6. [Neuen Workspace erstellen](#neuer-workspace)

---

## <a id="provider-konfig">1. Provider-Grundkonfiguration</a>

```hcl
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
    }
  }
}

provider "databricks" {}

data "databricks_current_user" "me" {}
data "databricks_spark_version" "latest" {}
data "databricks_node_type" "smallest" {
  local_disk = true
}
```

Diese Data Sources initialisieren gängige Variablen für Nutzerkontext, Spark-Versionen und Node-Typen.

## <a id="standard">2. Standardfunktionalität (ohne Admin-Rechte)</a>

### Secret Management

```hcl
resource "databricks_secret_scope" "this" {
  name = "demo-${data.databricks_current_user.me.alphanumeric}"
}

resource "databricks_token" "pat" {
  comment          = "Created from ${abspath(path.module)}"
  lifetime_seconds = 3600
}

resource "databricks_secret" "token" {
  string_value = databricks_token.pat.token_value
  scope        = databricks_secret_scope.this.name
  key          = "token"
}
```

### Notebook-Erstellung

```hcl
resource "databricks_notebook" "this" {
  path     = "${data.databricks_current_user.me.home}/Terraform"
  language = "PYTHON"
  content_base64 = base64encode(<<-EOT
    token = dbutils.secrets.get('${databricks_secret_scope.this.name}', '${databricks_secret.token.key}')
    print(f'This should be redacted: {token}')
    EOT
  )
}
```

### Job-Konfiguration

```hcl
resource "databricks_job" "this" {
  name = "Terraform Demo (${data.databricks_current_user.me.alphanumeric})"
  task {
    task_key = "demo_task"
    new_cluster {
      num_workers   = 1
      spark_version = data.databricks_spark_version.latest.id
      node_type_id  = data.databricks_node_type.smallest.id
    }
    notebook_task {
      notebook_path = databricks_notebook.this.path
    }
  }
  email_notifications {}
}
```

### Cluster-Verwaltung

```hcl
resource "databricks_cluster" "this" {
  cluster_name = "Exploration (${data.databricks_current_user.me.alphanumeric})"
  spark_version           = data.databricks_spark_version.latest.id
  instance_pool_id        = databricks_instance_pool.smallest_nodes.id
  autotermination_minutes = 20
  autoscale {
    min_workers = 1
    max_workers = 10
  }
}
```

### Cluster-Policy

```hcl
resource "databricks_cluster_policy" "this" {
  name = "Minimal (${data.databricks_current_user.me.alphanumeric})"
  definition = jsonencode({
    "dbus_per_hour" : {
      "type" : "range",
      "maxValue" : 10
    },
    "autotermination_minutes" : {
      "type" : "fixed",
      "value" : 20,
      "hidden" : true
    }
  })
}
```

### Instance Pool

```hcl
resource "databricks_instance_pool" "smallest_nodes" {
  instance_pool_name = "Smallest Nodes (${data.databricks_current_user.me.alphanumeric})"
  min_idle_instances = 0
  max_capacity       = 30
  node_type_id       = data.databricks_node_type.smallest.id
  preloaded_spark_versions = [
    data.databricks_spark_version.latest.id
  ]
  idle_instance_autotermination_minutes = 20
}
```

### Outputs

```hcl
output "notebook_url" {
  value = databricks_notebook.this.url
}

output "job_url" {
  value = databricks_job.this.url
}
```

## <a id="sicherheit">3. Workspace-Sicherheit (Admin-Rechte erforderlich)</a>

### Secret ACL

```hcl
resource "databricks_secret_acl" "spectators" {
  principal  = databricks_group.spectators.display_name
  scope      = databricks_secret_scope.this.name
  permission = "READ"
}
```

### Gruppen- und Nutzerverwaltung

```hcl
resource "databricks_group" "spectators" {
  display_name = "Spectators (by ${data.databricks_current_user.me.alphanumeric})"
}

resource "databricks_user" "dummy" {
  user_name    = "dummy+${data.databricks_current_user.me.alphanumeric}@example.com"
  display_name = "Dummy ${data.databricks_current_user.me.alphanumeric}"
}

resource "databricks_group_member" "a" {
  group_id  = databricks_group.spectators.id
  member_id = databricks_user.dummy.id
}
```

### Berechtigungskonfiguration

**Notebook-Berechtigungen:**

```hcl
resource "databricks_permissions" "notebook" {
  notebook_path = databricks_notebook.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "CAN_RUN"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_READ"
  }
}
```

**Job-Berechtigungen:**

```hcl
resource "databricks_permissions" "job" {
  job_id = databricks_job.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "IS_OWNER"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_MANAGE_RUN"
  }
}
```

**Cluster-Berechtigungen:**

```hcl
resource "databricks_permissions" "cluster" {
  cluster_id = databricks_cluster.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "CAN_RESTART"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_ATTACH_TO"
  }
}
```

**Cluster-Policy-Berechtigungen:**

```hcl
resource "databricks_permissions" "policy" {
  cluster_policy_id = databricks_cluster_policy.this.id
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_USE"
  }
}
```

**Instance-Pool-Berechtigungen:**

```hcl
resource "databricks_permissions" "pool" {
  instance_pool_id = databricks_instance_pool.smallest_nodes.id
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_ATTACH_TO"
  }
}
```

## <a id="storage">4. Storage</a>

Mehrere Optionen für Storage-Management:

- **Datei-Management:** `databricks_dbfs_file` für JAR-, Wheel- und Egg-Bibliotheken.
- **Datei-Auflistung:** die Data Source `databricks_dbfs_file_paths` zur Aufzählung von DBFS-Einträgen.
- **Datei-Abruf:** die Data Source `databricks_dbfs_file` zum Lesen kleiner Dateiinhalte.
- **AWS-Integration:** `databricks_aws_s3_mount` zum Mounten von AWS-S3-Storage.

## <a id="ip-access">5. Fortgeschrittene Konfiguration: IP-Access-Lists</a>

```hcl
data "http" "my" {
  url = "https://ifconfig.me"
}

resource "databricks_workspace_conf" "this" {
  custom_config = {
    "enableIpAccessLists": "true"
  }
}

resource "databricks_ip_access_list" "only_me" {
  label = "only ${data.http.my.body} is allowed to access workspace"
  list_type = "ALLOW"
  ip_addresses = ["${data.http.my.body}/32"]
  depends_on = [databricks_workspace_conf.this]
}
```

Dieses Beispiel aktiviert IP-Access-Lists und konfiguriert eine Einschränkung, die nur einer bestimmten IP-Adresse Zugriff auf den Workspace erlaubt.

## <a id="neuer-workspace">6. Neuen Workspace erstellen</a>

Workspace-Automatisierung (Serverless- und Classic-Deployments) erfolgt primär über die Ressource `databricks_mws_workspaces`.
