## F. Einen For-Each-Schleifen-Task hinzufügen

In diesem Abschnitt fügen Sie **customers_orders_report** einen nachgelagerten Task hinzu, der eine **For Each**-Schleife verwendet. Mit dieser Schleife kann der Job denselben Task mehrfach ausführen – einmal für jedes Element in einer angegebenen Liste oder Sammlung. Die Ausführung kann je nach Job-Konfiguration sequenziell oder parallel erfolgen. 

In unserem Fall möchten wir aus der Tabelle customers_orders_silver Bestell-Reports speziell für die Bundesstaaten **California, New York und Virginia** erstellen. Wir erstellen drei verschiedene Tabellen, um die staatenspezifischen Daten zu speichern. Wir verwenden dasselbe Code-Skript und übergeben den Namen des Bundesstaats mithilfe des **For Each**-Tasks dynamisch.

### F1. Die Notebooks erkunden

1. Sehen Sie sich das Notebook [Task Files/Lesson 09 Files/9.2 - Joining Customers and Orders Table]($./Task Files/Lesson 09 Files/9.2 - Joining Customers and Orders Table) an, das die Tabelle **customers_orders_silver** erstellt.

2. Das Notebook [Task Files/Lesson 09 Files/9.5 - For Each: Customer orders State]($./Task Files/Lesson 09 Files/9.5 - For Each: Customer orders State) wird in einer Schleife für jeden der oben genannten Bundesstaaten ausgeführt. Dieses Skript übernimmt den Wert des Bundesstaats dynamisch und führt sich für jeden Bundesstaat aus, wobei eine staatenspezifische Tabelle mit Daten aus customers_order_silver erstellt wird.

### F2. Einen For-Each-Iterator-Task erstellen (Teil 1 von 2)

Der „For Each“-Task umfasst zwei Schritte: Zuerst wird der Iterator definiert, dann das Skript angegeben, über das iteriert werden soll. Führen Sie nun die folgenden Schritte aus, um einen **For Each**-Iterator-Task hinzuzufügen, der über eine Reihe von **state**-Werten iteriert.

1. Wählen Sie im selben Job den Task **customers_orders_report**.

2. Wählen Sie **Add task** und den Task-Typ **For each**.

3. Benennen Sie den Task **customers_orders_state_wise_report_iterator**. 

4. Setzen Sie das Feld **Inputs** des Iterators auf `["CA", "NY", "VA"]`.  
  — Das sind die Bundesstaaten mit den meisten Kunden.

5. Lassen Sie die Einstellung **Concurrency** leer (empfohlen für Single-Node-Runs, um den Prozess nicht zu verlangsamen).

6. Setzen Sie das Feld **Depends on** für diesen Task auf **customers_orders_report**.

7. Stellen Sie sicher, dass **Run if dependencies** auf **All succeeded** gesetzt ist.

8. Klicken Sie auf **Add a task to loop over**.

#### For-Each-Iterator

![Lesson04_For_Each_Task_Iterator.png](./Includes/images/demo_advanced_tasks/Lesson09_For_Each_Task_Iterator.png)

### F3. Einen Task hinzufügen, über den iteriert wird (Teil 2 von 2)

Nachdem der **For Each**-Iterator eingerichtet ist, müssen wir einen Task angeben, über den iteriert wird. Führen Sie die folgenden Schritte aus, um diesen Task hinzuzufügen.

1. Der Iterator ist nun eingerichtet. Wählen Sie **Add a task to loop over**. 

2. Benennen Sie den Task, über den iteriert wird, **customers_orders_state_wise_report**.

3. Bestätigen Sie, dass der Task-**Type** **Notebook** und die **Source** **Workspace** ist.

4. Setzen Sie den Notebook-Pfad auf [Task Files/Lesson 09 Files/9.5 - For Each: Customer orders State]($./Task Files/Lesson 09 Files/9.5 - For Each: Customer orders State), das sich im Ordner **Task Files** befindet.

5. Setzen Sie **Compute** auf **serverless**.

6. Fügen Sie einen Schlüssel-Wert-Parameter hinzu:
   - Geben Sie als Schlüssel **state** ein. 
   - Klicken Sie für den Wert auf das Symbol **{}** und wählen Sie **input**.  
   - Dadurch wird jeder Bundesstaat-Code aus der Iterator-Schleife automatisch an das Notebook übergeben.

7. Klicken Sie auf **Create task**.

#### Iterator-Task
![Lesson04_iterator_task.pngg](./Includes/images/demo_advanced_tasks/Lesson09_iterator_task.png)
