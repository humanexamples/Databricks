
## F. Ihren Job validieren

Prüfen Sie, ob die Tabelle **high_risk_borrowers_silver** in Ihrem Schema existiert.

Führen Sie außerdem den folgenden Befehl aus, um die Daten von **high_risk_borrowers_silver** zu überprüfen

```sql
%sql
SELECT count(*) FROM high_risk_borrowers_silver
```

Stellen Sie sicher, dass die Anzahl der Kreditnehmer mit hohem Risiko **143** beträgt; dies sollte der Gesamtzeilenzahl in der Tabelle **high_risk_borrowers_silver** entsprechen.
