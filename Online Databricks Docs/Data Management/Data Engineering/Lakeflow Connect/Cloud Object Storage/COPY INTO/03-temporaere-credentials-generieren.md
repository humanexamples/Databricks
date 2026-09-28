# Temporäre Zugangsdaten generieren

Diese Seite beschreibt, wie ein IAM-Benutzer im eigenen AWS-Konto angelegt wird, der nur die minimal nötigen Rechte zum Lesen von Daten aus einem Amazon-S3-Bucket besitzt.

## IAM-Policy erstellen

1. Die AWS-IAM-Konsole öffnen (z. B. unter https://console.aws.amazon.com/iam).
2. Auf **Policies** klicken.
3. Auf **Create Policy** klicken.
4. Den Tab **JSON** wählen.
5. Den vorhandenen JSON-Code durch folgenden Code ersetzen. `<s3-bucket>` durch den Namen des S3-Buckets ersetzen, `<folder>` durch den Namen des Ordners im Bucket.

```python
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyAccessToTrips",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::<s3-bucket>", "arn:aws:s3:::<s3-bucket>/<folder>/*"]
    }
  ]
}
```

6. Auf **Next: Tags** klicken.
7. Auf **Next: Review** klicken.
8. Einen Namen für die Policy vergeben und auf **Create policy** klicken.

## IAM-Benutzer erstellen

1. In der Seitenleiste **Users** auswählen.
2. Auf **Add users** klicken.
3. Einen Benutzernamen vergeben.
4. Die Option **Access key – Programmatic access** aktivieren und auf **Next: Permissions** klicken.
5. **Attach existing policies directly** auswählen.
6. Das Kontrollkästchen neben der zuvor erstellten Policy aktivieren und auf **Next: Tags** klicken.
7. Auf **Next: Review** klicken.
8. Auf **Create user** klicken.
9. Die angezeigten Werte **Access key ID** und **Secret access key** sicher speichern – sie werden für den nächsten Schritt (AWS-STS-Session-Token) benötigt.

## Named Profile erstellen

1. Auf dem lokalen Entwicklungsrechner mit der AWS CLI ein Named Profile mit den zuvor kopierten Zugangsdaten anlegen (siehe AWS-Dokumentation zu "Named profiles for the AWS CLI").
2. Die Zugangsdaten testen: Mit der AWS CLI folgenden Befehl ausführen, der den Inhalt des Datenordners anzeigt. `<s3-bucket>`, `<folder>` und `<named-profile>` entsprechend ersetzen.

```python
aws s3 ls s3://<s3-bucket>/<folder>/ --profile <named-profile>
```

3. Um das Session-Token zu erhalten, folgenden Befehl ausführen (`<named-profile>` durch den Namen des Named Profile ersetzen):

```python
aws sts get-session-token --profile <named-profile>
```

4. Die angezeigten Werte **AccessKeyId**, **SecretAccessKey** und **SessionToken** sicher speichern.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/generate-temporary-credentials  
**Stand:** 2026-08-07
