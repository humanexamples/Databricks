## D. Einen bedingten If/Else-Task hinzufügen

In diesem Abschnitt fügen Sie Ihrem Job einen bedingten Task hinzu, der die Tabelle **loan_details_silver** auf Kreditnehmer mit hohem Risiko prüft. Der relevante Code befindet sich in [Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table]($./Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table).

Achten Sie genau auf die letzten Befehle, da sie den Ausgabe-Task-Wert setzen. Sobald die Anzahl der Kreditnehmer, die sowohl einen aktiven Kredit als auch eine Kreditkarte haben, 100 übersteigt, wird `risk_flag` auf **true** gesetzt.

### D1. Das Notebook prüfen: Auf Kreditnehmer mit hohem Risiko prüfen

1. Sehen Sie sich im Notebook [Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table]($./Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table) die `risk_flag`-Logik zur Identifizierung von Kreditnehmern mit hohem Risiko in der Tabelle **loan_details_silver** an.

  - Der Task **creating_loan_details_table** erstellt die Tabelle **loan_details_silver**.

  - Ihr Ziel ist es zu prüfen, ob diese Tabelle mehr als die zulässige Anzahl an Kreditnehmern mit hohem Risiko enthält.

  - Das Ergebnis dieser Prüfung (ein boolescher Wert) wird als `risk_flag` in der Task-Ausgabe gespeichert.

### D2. Einen bedingten If/Else-Task erstellen

1. Navigieren Sie zum erstellten Job, wechseln Sie zum Tab Tasks und fügen Sie einen neuen Task namens **checking_for_risky_borrowers** hinzu.

2. Setzen Sie den Task-Typ auf **If/Else condition**.

3. Legen Sie fest, dass dieser Task vom Task **creating_loan_details_table** abhängt.

4. Wählen Sie die Bedingung aus, indem Sie auf die Schaltfläche `{}` klicken, wählen Sie dann tasks.`creating_loan_details_table.values.my_value` und ersetzen Sie `my_value` durch `risk_flag`.

5. Legen Sie die Bedingung so fest, dass geprüft wird, ob dieser Wert `== true` ist: `tasks.creating_loan_details_table.values.risk_flag == true`

6. Klicken Sie auf **Save Task**.

![Lesson10_ifelse](./Includes/images/lab_elif/Lesson10_ifelse.png)

### D3. Die True-Bedingung behandeln

1. Wenn Kreditnehmer mit hohem Risiko gefunden werden (`risk_flag == true`), fügen Sie einen Notebook-Task namens **processing_high_risk_borrowers** hinzu.

2. Dieser Task sollte vom **True**-Zweig des Tasks **checking_for_risky_borrowers** abhängen.

3. Verwenden Sie für diese Bedingung das Notebook [Task Files/Lesson 10 Files/10.1 - Processing high risk borrowers]($./Task Files/Lesson 10 Files/10.1 - Processing high risk borrowers).

![Lesson10_if_task.png](./Includes/images/lab_elif/Lesson10_if_task.png)

### D4. Die False-Bedingung behandeln

1. Wenn die Anzahl der Kreditnehmer mit hohem Risiko unter dem Schwellenwert liegt (`risk_flag == false`), fügen Sie einen Notebook-Task namens **processing_low_risk_borrowers** hinzu.

2. Dieser Task sollte vom **False**-Zweig des Tasks **checking_for_risky_borrowers** abhängen.

3. Verwenden Sie für diese Bedingung das Notebook [Task Files/Lesson 10 Files/10.2 - Processing low risk borrowers]($./Task Files/Lesson 10 Files/10.2 - Processing low risk borrowers).

4. Dieses Setup stellt sicher, dass Ihr Job Kreditnehmer mit hohem und niedrigem Risiko getrennt verarbeitet.
![Lesson10_else_task](./Includes/images/lab_elif/Lesson10_else_task.png)
