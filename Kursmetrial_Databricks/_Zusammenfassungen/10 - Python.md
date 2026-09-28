# Zusammenfassung – Introduction to Python for Data Science and Data Engineering

Alle Code-Beispiele aus den Modulen 01 bis 15, jeweils mit dem Ergebnis, das sie erzeugen.

Hinweise zum Lesen:

- Zellen werden wie im Notebook der Reihe nach ausgeführt. Variablen aus früheren Zellen gelten weiter.
- Im Notebook wird nur der Wert der **letzten Zeile** automatisch angezeigt. Alles andere braucht `print()`.
- Bei den Labs steht nur die Lösung. Die Vorlagen mit `<FILL_IN>` erzeugen kein Ergebnis.
- Syntaxmuster (z. B. `if bool: code_1`) sind kein lauffähiger Code. Sie stehen ohne Ergebnis da.
- Ausgaben, die vom Workspace abhängen (Benutzername, Catalogs), sind als Beispiel markiert.

---

## Modul 01 – Die Databricks-Umgebung

### Erste Python-Zelle

```python
print("I'm running Python!")
```

Ergebnis:

```text
I'm running Python!
```

### Markdown-Zelle mit `%md`

```markdown
%md
# Überschrift Eins
## Überschrift Zwei
Dies ist Text mit einem **fetten** Wort darin.
1. eins
2. zwei
- Äpfel
- Pfirsiche
| Name  | Alter | Rasse            |
|-------|-------|------------------|
| Buddy | 2     | Golden Retriever |
```

Ergebnis: Die Zelle wird nicht ausgeführt, sondern als formatierter Text gerendert. Man sieht echte Überschriften, fetten Text, nummerierte und ungeordnete Listen, einen Link und eine Tabelle.

---

## Modul 02 – Datentypen und Variablen

### Rechnen und Kommentare

```python
1+1
```

```text
2
```

```python
# Das ist unsere erste Zeile Python-Code!
1+1
```

```text
2
```

Der Kommentar nach `#` wird ignoriert.

### Integer

```python
2 * 3 + 5 - 1
```

```text
10
```

### Float und `type()`

```python
1.2 * 2.3 + 5.5
```

```text
8.26
```

```python
type(1.2)
```

```text
<class 'float'>
```

```python
type(1.)
```

```text
<class 'float'>
```

`1.` ist ein Float, weil der Punkt dabei ist.

### Genauigkeit: Integer vs. Float

```python
99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 + 1
```

```text
100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

Integer haben keine Obergrenze. Das Ergebnis ist exakt.

```python
.9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 + .0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
```

```text
1.0
```

Floats sind begrenzt genau. Das kleine Stück geht verloren, `.999…` ist schon `1.0`.

### Strings

```python
"Hello" + "123"
```

```text
'Hello123'
```

```python
"Hello" + " " + "123"
```

```text
'Hello 123'
```

`+` verkettet Strings. Ein Leerzeichen kommt nicht automatisch dazu.

```python
"Hello" + 123
```

```text
TypeError: can only concatenate str (not "int") to str
```

Im Kurs ist diese Zeile auskommentiert. Ohne `#` erzeugt sie diesen Fehler.

### Mehrzeiliger String

```python
print('''
This text can go on and on.
You can have as many lines as you need.
Perfect for large paragraphs, code, or anything that's just too long.
''')
```

```text

This text can go on and on.
You can have as many lines as you need.
Perfect for large paragraphs, code, or anything that's just too long.

```

Die Zeilenumbrüche am Anfang und Ende gehören mit zum String.

### Booleans

```python
True or False
```

```text
True
```

```python
True and False
```

```text
False
```

```python
not False
```

```text
True
```

### Variablen

```python
a = 3
b = 2
c = a*b

c
```

```text
6
```

```python
b = 4
c
```

```text
6
```

`c` bleibt `6`. Die Rechnung wurde bei der Zuweisung ausgeführt, nicht später neu.

### Schwache Typisierung

```python
b = "Hello World"
print(type(b))
b = 10
print(type(b))
```

```text
<class 'str'>
<class 'int'>
```

### Namenskonvention

```python
my_first_variable = 2
```

Kein Ergebnis. Es wird nur zugewiesen.

### Nur die letzte Zeile wird angezeigt

```python
a = 1
b = 2

a # Diese Zeile wird nicht ausgegeben, weil sie nicht die letzte Codezeile ist
b
```

```text
2
```

```python
print(a)
print(b)
```

```text
1
2
```

```python
print(10)
print("Hello world")
print(True)
```

```text
10
Hello world
True
```

### `.format()` und f-Strings

```python
a = 1
b = 2
print("The sum of {} + {} is {}".format(a, b, a + b))
```

```text
The sum of 1 + 2 is 3
```

```python
a = 1
b = 2
print(f"The sum of {a} + {b} is {a + b}")
```

```text
The sum of 1 + 2 is 3
```

### Spaltenausgabe mit f-Strings

```python
city1 = "San Francisco"
city2 = "Paris"
city3 = "Mumbai"

temperature1 = 58
temperature2 = 75
temperature3 = 81

humidity1 = .85
humidity2 = .5
humidity3 = .88 

print(f"{'City':15} {'Temperature':15} {'Humidity':15}")
print(f"{city1:15} {temperature1:11} {humidity1:12.2f}")
print(f"{city2:15} {temperature2:11} {humidity2:12.2f}")
print(f"{city3:15} {temperature3:11} {humidity3:12.2f}")
```

```text
City            Temperature     Humidity       
San Francisco            58         0.85
Paris                    75         0.50
Mumbai                   81         0.88
```

Strings stehen links, Zahlen rechts. `.2f` zeigt zwei Nachkommastellen.

### `sep` und `end`

```python
print(1,2,3)
print(4,5,6)
```

```text
1 2 3
4 5 6
```

```python
print(1,2,3, sep='--', end='. ') 
print("") 
print(4,5,6, sep='###', end='END') 
print("") 
print(1, 2, 3, sep='', end='$')
print("") 
print(4, 5, 6, sep='\t', end='Done')
```

```text
1--2--3. 
4###5###6END
123$
4	5	6Done
```

`sep` steht zwischen den Werten, `end` am Schluss. Das leere `print("")` sorgt jeweils für den Zeilenumbruch.

### Ternärer Operator

```python
is_tasty = True
food = "Delicious" if is_tasty else "Not Delicious"
print(food)
```

```text
Delicious
```

### Lab 02 – Lösungen

```python
name = "James"
num_chocolate = 10
chocolate_string = f"{name} would like to eat {num_chocolate} bars of chocolate"

print(chocolate_string)
```

```text
James would like to eat 10 bars of chocolate
```

```python
num_students = 16
num_days = 2
class_name = "introduction-to-python-for-data-science-and-data-engineering"
course_information = f"There are {num_students * num_days} student days in the {class_name}"

print(course_information)
```

```text
There are 32 student days in the introduction-to-python-for-data-science-and-data-engineering
```

Im f-String wird `16 * 2` direkt zu `32` gerechnet.

---

## Modul 03 – Kontrollfluss

### Syntax von `if`/`else`

```text
if bool:
    code_1
else:
    code_2
```

```python
if True:
    print("True")
else:
    print("False")
```

```text
True
```

### Widget als Eingabe

```python
dbutils.widgets.text("input", "1", "Enter a number from 1 - 10")  # Wir setzen 1 als Standardwert
input = dbutils.widgets.get("input")
```

Ergebnis: Oben im Notebook erscheint ein Textfeld „Enter a number from 1 - 10“ mit dem Wert `1`. Die Zelle selbst gibt nichts aus.

```python
input_as_number = int(input)
if input_as_number >= 1 and input_as_number <= 10:
    print("Valid Input")
else:
    print("Invalid Input")
    
dbutils.widgets.remove("input")
```

```text
Valid Input
```

Mit dem Standardwert `1`. Bei z. B. `15` im Widget käme `Invalid Input`. Danach ist das Widget entfernt.

### Vergleichsoperatoren

```python
print(1 == 1)
print(1.5 != 2.5)
print("abc" == "xyz")
print(True == True)
```

```text
True
True
False
True
```

```python
lunch_price = 20

if lunch_price <= 15:
    print("Buy it!")
else:
    print("Too expensive")
```

```text
Too expensive
```

### Verschachteltes `if`

```python
if lunch_price <= 15:
    print("Buy it!")
else:
    if lunch_price < 25:
        print("Is it really good?")
    else:
        print("This better be the best food of all time")
```

```text
Is it really good?
```

`lunch_price` ist noch `20`.

### `elif`

```text
if bool:
    code_1
elif bool:
    code_2
else:
    code_last
```

```python
lunch_price = 15

if lunch_price == 10:
    print("10 dollars exactly! Buy it!")
elif lunch_price <= 15:
    print("Buy it!")
elif lunch_price < 25:
    print("Is it really good?")
else:
    print("This better be the best food of all time")
```

```text
Buy it!
```

Nur der erste passende Zweig läuft.

### `pass`

```python
if True:
    pass
else:
    pass
```

Kein Ergebnis. `pass` tut nichts und dient als Platzhalter.

### Multi-Bedingungs-Programm (verschachtelt)

```python
dog_person = True
cat_person = True
age = 30

if age < 18:
    print("Ask your parents for permission!")
else:
    if dog_person and cat_person:
        print("Golden Retriever")
    else:
        if dog_person and not cat_person:
            print("Scottish Deerhound")
        else:
            if cat_person and not dog_person:
                print("You're barking up the wrong tree!")
            else:
                print("Are you sure a pet is right for you?")
```

```text
Golden Retriever
```

### Dasselbe flach mit `elif`

```python
dog_person = True
cat_person = True
age = 30

if age < 18:
    print("Ask your parents for permission!")
elif dog_person and cat_person:
    print("Golden Retriever")
elif dog_person and not cat_person:
    print("Scottish Deerhound")
elif cat_person and not dog_person:
    print("You're barking up the wrong tree!")
else:
    print("Are you sure a pet is right for you?")
```

```text
Golden Retriever
```

Gleiches Ergebnis, aber besser lesbar.

### Genie-Code-Prompts

```text
Create a Python program that recommends a dog breed based on `dog_person`, `cat_person`, and `age`.
Use if-statements and boolean logic. Add comments explaining each condition.
```

```text
Flatten the multi-conditional program in cell above that recommends a dog breed to use `elif` statements.
```

Ergebnis: Genie Code (der KI-Assistent) erzeugt daraus Code wie in den beiden Beispielen oben. Der genaue Text kann jedes Mal etwas anders sein.

### Lab 03 – Lösungen

```python
temperature = 72.0
sunny = False

if temperature >= 60.0 and sunny:
    print("ice cream")
elif temperature >= 60.0 and not sunny:
    print("dumplings")
else:
    print("hot tea")
```

```text
dumplings
```

```python
km_since_last_change = 15000
oil_change_light = True

if km_since_last_change >= 15000 and oil_change_light:
    print("Time for an oil change")
elif km_since_last_change >= 15000 and not oil_change_light:
    print("Wait for the light")
else:
    print("Wait longer")
```

```text
Time for an oil change
```

```python
12 % 7
```

```text
5
```

`%` liefert den Rest der Division.

```python
dbutils.widgets.text("year", "2022", "Enter Year Here")
```

Ergebnis: Ein Widget „Enter Year Here“ mit dem Wert `2022` erscheint oben im Notebook.

```python
year = int(dbutils.widgets.get("year"))

if year % 4 == 0:
    if year % 400 == 0 or year % 100 != 0:
        print(f"{year} is a leap year.")
    else:
        print(f"{year} is not a leap year.")
else:
    print(f"{year} is not a leap year.")
```

```text
2022 is not a leap year.
```

Mit `2024` im Widget käme `2024 is a leap year.`

```python
dbutils.widgets.remove("year")
```

Kein Ergebnis. Das Widget verschwindet.

---

## Modul 04 – Funktionen

### Syntax

```text
def function_name(parameters):
    function_code
```

```python
print(1)
```

```text
1
```

### Einfache Funktion

```python
def ten_dollars_to_euros():
    print(10.0 * 0.93)
```

Kein Ergebnis. Die Funktion wird nur definiert.

```python
ten_dollars_to_euros()
```

```text
9.3
```

```python
print("Python ran this line before the function body")

ten_dollars_to_euros()

print("Python ran this line after the function body")
```

```text
Python ran this line before the function body
9.3
Python ran this line after the function body
```

### Parameter und Argumente

```python
def dollars_to_euros(dollar_amount):
    print(dollar_amount * 0.93)
```

```python
dollars_to_euros(5.0)
dollars_to_euros(10)
dollars_to_euros(20.0)
```

```text
4.65
9.3
18.6
```

### Mehrere Parameter

```python
def dollars_to_euros_with_rate(dollar_amount, conversion_rate):
    print(dollar_amount * conversion_rate)
```

```python
dollars_to_euros_with_rate(10.0, 0.93)
dollars_to_euros_with_rate(5.0, 1.0)
# dollars_to_euros_with_rate(5.0) # Wenn diese Zeile einkommentiert wird, tritt ein TypeError auf
```

```text
9.3
5.0
```

Ohne `#` käme: `TypeError: dollars_to_euros_with_rate() missing 1 required positional argument: 'conversion_rate'`.

### Benannter und gemischter Aufruf

```python
dollars_to_euros_with_rate(dollar_amount=10.0, conversion_rate=0.93)
dollars_to_euros_with_rate(conversion_rate=0.93, dollar_amount=10.0)
```

```text
9.3
9.3
```

Mit Namen ist die Reihenfolge egal.

```python
dollars_to_euros_with_rate(10.0, conversion_rate=0.93)
# dollars_to_euros_with_rate(10.0, dollar_amount=0.93) # Das würde einen TypeError auslösen
```

```text
9.3
```

Die auskommentierte Zeile gäbe: `TypeError: dollars_to_euros_with_rate() got multiple values for argument 'dollar_amount'`.

### Standardwerte

```text
def func(param, param=default_value):
    code
```

```python
def dollar_to_euro_with_default(dollar_amount, conversion_rate=0.93):
    print(dollar_amount * conversion_rate)
```

```python
dollar_to_euro_with_default(10.0)
dollar_to_euro_with_default(10.0, 0.5)
```

```text
9.3
5.0
```

### `print` vs. `return`

```python
a = dollar_to_euro_with_default(10.0)
print(a)
```

```text
9.3
None
```

Die Funktion druckt `9.3`, gibt aber nichts zurück. Deshalb ist `a` gleich `None`.

```python
def dollar_to_euro_with_default(dollar_amount, conversion_rate=0.93):
    return dollar_amount * conversion_rate
```

```python
a = dollar_to_euro_with_default(10.0)
print(a)
```

```text
9.3
```

Jetzt kommt der Wert per `return` zurück.

### Type Hints

```python
def dollar_to_euro_with_default(dollar_amount: float, conversion_rate: float = 0.93) -> float:
    return dollar_amount * conversion_rate
```

Kein Ergebnis. Type Hints sind nur Hinweise, Python prüft sie nicht.

### Kommentar

```python
# 10 Dollar mit dem Standard-Umrechnungskurs von 0,93 in Euro umrechnen
dollar_to_euro_with_default(dollar_amount=10.0, conversion_rate=0.93)
```

```text
9.3
```

### Docstring und `help()`

```python
def dollar_to_euro_with_default(dollar_amount: float, conversion_rate: float = 0.93) -> float:
    """
    Returns Dollar amount converted to Euros based on a conversion rate.
    
    Parameters:
        dollar_amount (float): Dollar amount to be converted to euros.
        conversion_rate (float): Dollar to Euro conversion rate. Default: 0.93.
    
    Returns:
        euro_amount (float): Euro equivalent of the dollar amount based on the conversion rate.
    """
    euro_amount = dollar_amount * conversion_rate
    return euro_amount
```

```python
help(dollar_to_euro_with_default)
```

```text
Help on function dollar_to_euro_with_default in module __main__:

dollar_to_euro_with_default(dollar_amount: float, conversion_rate: float = 0.93) -> float
    Returns Dollar amount converted to Euros based on a conversion rate.

    Parameters:
        dollar_amount (float): Dollar amount to be converted to euros.
        conversion_rate (float): Dollar to Euro conversion rate. Default: 0.93.

    Returns:
        euro_amount (float): Euro equivalent of the dollar amount based on the conversion rate.
```

### Scope

```python
def function():
    func_variable = 1
    return func_variable
```

```python
function()
# func_variable  # Wenn diese Zeile einkommentiert wird, tritt ein NameError auf – func_variable ist außerhalb des Gültigkeitsbereichs
```

```text
1
```

Ohne `#` käme: `NameError: name 'func_variable' is not defined`. Die Variable lebt nur in der Funktion.

### Eingebaute Funktionen

```python
print(max(1, 2))
print(len("abc"))
```

```text
2
3
```

```python
help(max)
```

```text
Help on built-in function max in module builtins:

max(...)
    max(iterable, *[, default=obj, key=func]) -> value
    max(arg1, arg2, *args, *[, key=func]) -> value

    With a single iterable argument, return its biggest item. The
    default keyword-only argument specifies an object to return if
    the provided iterable is empty.
    With two or more positional arguments, return the largest argument.
```

### Lambda

```python
add_ten = lambda a: a + 10

print(add_ten(5))   # 15
print(add_ten(22))  # 32
```

```text
15
32
```

```python
dollars_to_euros_lambda = lambda dollar_amount, conversion_rate=0.93: dollar_amount * conversion_rate

print(dollars_to_euros_lambda(10.0))        # Uses default rate: 9.3
print(dollars_to_euros_lambda(10.0, 0.5))   # Overrides rate: 5.0
```

```text
9.3
5.0
```

### Lambda als Sortierschlüssel

```python
rates = [
    {"currency": "GBP", "rate": 0.79},
    {"currency": "JPY", "rate": 149.50},
    {"currency": "EUR", "rate": 0.93},
]

sorted_rates = sorted(rates, key=lambda r: r["rate"])

for entry in sorted_rates:
    print(entry)
```

```text
{'currency': 'GBP', 'rate': 0.79}
{'currency': 'EUR', 'rate': 0.93}
{'currency': 'JPY', 'rate': 149.5}
```

Sortiert aufsteigend nach `rate`.

### Lab 04 – Lösungen

```python
def even_or_odd(num):
    if num % 2 == 0:
        return "even"
    else:
        return "odd"
```

```python
print(even_or_odd(15))
print(even_or_odd(20))
print(even_or_odd(27))
print(even_or_odd(100))
```

```text
odd
even
odd
even
```

```python
def fizz_buzz(num):
    if type(num) != int:
        return "Wrong type"
    elif num % 5 == 0 and num % 3 == 0:
        return "FizzBuzz"
    elif num % 5 == 0:
        return "Fizz"
    elif num % 3 == 0:
        return "Buzz"
    else:
        return num
```

```python
print(fizz_buzz(15))
print(fizz_buzz(20))
print(fizz_buzz(27))
print(fizz_buzz(100))
```

```text
FizzBuzz
Fizz
Buzz
Fizz
```

```python
def is_leap_year(year):
    if year % 4 == 0:
        if year % 400 == 0 or year % 100 != 0:
            print(f"{year} is a leap year.")
        else:
            print(f"{year} is not a leap year.")
    else:
        print(f"{year} is not a leap year.")
```

```python
is_leap_year(1901)
is_leap_year(1940)
is_leap_year(2000)
is_leap_year(2030)
```

```text
1901 is not a leap year.
1940 is a leap year.
2000 is a leap year.
2030 is not a leap year.
```

---

## Modul 05 – Collection-Typen und Methoden

### Methoden-Syntax

```text
object.method_name(arguments)
```

### String-Methoden

```python
greeting = "hello"
print(greeting.upper())
print(greeting)
```

```text
HELLO
hello
```

`upper()` gibt einen neuen String zurück. `greeting` bleibt unverändert.

```python
greeting
```

```text
'hello'
```

```python
help(greeting.capitalize)
```

```text
Help on built-in function capitalize:

capitalize() method of builtins.str instance
    Return a capitalized version of the string.

    More specifically, make the first character have upper case and the rest lower
    case.
```

```python
greeting.capitalize()
```

```text
'Hello'
```

### Listen erstellen

```text
[item1, item2, item3, ...]
```

```python
breakfast_list = ["pancakes", "eggs", "waffles"]
breakfast_list
```

```text
['pancakes', 'eggs', 'waffles']
```

```python
type(breakfast_list)
```

```text
<class 'list'>
```

```python
["hello", True, 1, 1.5]
```

```text
['hello', True, 1, 1.5]
```

Eine Liste darf gemischte Typen enthalten.

### Listen-Methoden

```python
breakfast_list.append("yogurt")
breakfast_list
```

```text
['pancakes', 'eggs', 'waffles', 'yogurt']
```

```python
["pancakes", "eggs"] + ["waffles", "yogurt"]
```

```text
['pancakes', 'eggs', 'waffles', 'yogurt']
```

```python
breakfast_list = ["pancakes", "eggs", "waffles"]
breakfast_list = breakfast_list + ["yogurt"]
breakfast_list
```

```text
['pancakes', 'eggs', 'waffles', 'yogurt']
```

```python
breakfast_list = ["pancakes", "eggs", "waffles"]
breakfast_list += ["yogurt"]
breakfast_list
```

```text
['pancakes', 'eggs', 'waffles', 'yogurt']
```

Drei Wege, ein Ergebnis.

```python
len(breakfast_list)
```

```text
4
```

### Indexierung

```text
list_name[index]
```

```python
breakfast_list[0]
```

```text
'pancakes'
```

```python
breakfast_list[-1]
```

```text
'yogurt'
```

### Slicing

```text
list_name[start:stop:step]
```

```python
breakfast_list[0:2]
```

```text
['pancakes', 'eggs']
```

Der `stop`-Index ist exklusiv.

```python
breakfast_list[0:4:2]
```

```text
['pancakes', 'waffles']
```

```python
breakfast_list[::2]
```

```text
['pancakes', 'waffles']
```

```python
print(breakfast_list[:2])
print(breakfast_list[1:])
```

```text
['pancakes', 'eggs']
['eggs', 'waffles', 'yogurt']
```

### Umdrehen, ändern, prüfen

```python
breakfast_list[::-1]
```

```text
['yogurt', 'waffles', 'eggs', 'pancakes']
```

```python
print(breakfast_list)
breakfast_list[0] = "sausage"
print(breakfast_list)
```

```text
['pancakes', 'eggs', 'waffles', 'yogurt']
['sausage', 'eggs', 'waffles', 'yogurt']
```

```python
"waffles" in breakfast_list
```

```text
True
```

### Dictionaries

```text
{key_1: value_1, key_2: value_2, ...}
```

```python
rates = [
    {"currency": "GBP", "rate": 0.79},
    {"currency": "JPY", "rate": 149.50},
    {"currency": "EUR", "rate": 0.93},
]
```

Kein Ergebnis. Das ist eine Liste von Dictionaries.

```python
breakfast_dict = {"pancakes": 1, "eggs": 2, "waffles": 3}
breakfast_dict
```

```text
{'pancakes': 1, 'eggs': 2, 'waffles': 3}
```

```python
breakfast_dict.get("waffles")
```

```text
3
```

```python
breakfast_dict["waffles"]
```

```text
3
```

Unterschied: Bei einem fehlenden Schlüssel gibt `get()` `None` zurück, `[]` wirft einen `KeyError`.

```python
breakfast_dict.keys()
```

```text
dict_keys(['pancakes', 'eggs', 'waffles'])
```

```python
breakfast_dict.items()
```

```text
dict_items([('pancakes', 1), ('eggs', 2), ('waffles', 3)])
```

### Dictionary ändern

```python
print(breakfast_dict)
breakfast_dict["waffles"] += 1
breakfast_dict["yogurt"] = 1
print(breakfast_dict)
```

```text
{'pancakes': 1, 'eggs': 2, 'waffles': 3}
{'pancakes': 1, 'eggs': 2, 'waffles': 4, 'yogurt': 1}
```

```python
print(breakfast_dict.keys())
print("bacon" in breakfast_dict.keys())
```

```text
dict_keys(['pancakes', 'eggs', 'waffles', 'yogurt'])
False
```

### Tupel

```text
(item1, item2, item3, ...)
```

```python
breakfast_tuple = ("pancakes", "eggs", "waffles")
breakfast_tuple
```

```text
('pancakes', 'eggs', 'waffles')
```

```python
breakfast_tuple[0]
```

```text
'pancakes'
```

```python
breakfast_tuple[1:3]
```

```text
('eggs', 'waffles')
```

```python
print("pancakes" in breakfast_tuple)
```

```text
True
```

Tupel kann man lesen, aber nicht ändern.

### Lab 05 – Lösungen

```python
dinner_list = ["potatoes", "peppers", "onions"]
print(dinner_list)
```

```text
['potatoes', 'peppers', 'onions']
```

```python
dinner_list[0] = "sweet potatoes"
print(dinner_list)
```

```text
['sweet potatoes', 'peppers', 'onions']
```

```python
dinner_list.append("rice")
print(dinner_list)
```

```text
['sweet potatoes', 'peppers', 'onions', 'rice']
```

```python
dinner_dict = {"sweet potatoes": 3, "peppers": 4, "onions": 1}
print(dinner_dict)
```

```text
{'sweet potatoes': 3, 'peppers': 4, 'onions': 1}
```

```python
dinner_dict["sweet potatoes"] = 2
dinner_dict["ice cream"] = 1
print(dinner_dict)
```

```text
{'sweet potatoes': 2, 'peppers': 4, 'onions': 1, 'ice cream': 1}
```

```python
ingredient_set_1 = {"carrots", "onions", "potatoes"}
ingredient_set_2 = {"broccoli", "carrots", "rice"}
ingredient_set_3 = {"sweet potatoes", "carrots", "corn"}
ingredient_intersection_set = ingredient_set_1 & ingredient_set_2 & ingredient_set_3
ingredient_intersection_set
```

```text
{'carrots'}
```

`&` bildet die Schnittmenge. Nur `carrots` ist in allen drei Sets.

---

## Modul 06 – Schleifen

### Syntax der for-Schleife

```text
for var_name in list:
    code_block
```

```python
for number in [0, 1, 2]:
    print(number)
```

```text
0
1
2
```

### `range()`

```python
for element in range(0, 10):
    print("Hello!")
```

```text
Hello!
Hello!
Hello!
Hello!
Hello!
Hello!
Hello!
Hello!
Hello!
Hello!
```

```python
for element in range(0, 10):
    print(element)
```

```text
0
1
2
3
4
5
6
7
8
9
```

`range(0, 10)` endet vor der `10`.

### Liste filtern

```python
numbers_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
final_list = []

for element in numbers_list:
    if element > 4:
        final_list.append(element)
        
final_list
```

```text
[5, 6, 7, 8, 9, 10]
```

### List Comprehension

```python
final_list_shortcut = [element for element in numbers_list if element > 4]
final_list_shortcut
```

```text
[5, 6, 7, 8, 9, 10]
```

```python
doubled_list = [2 * element for element in numbers_list if element > 4]
doubled_list
```

```text
[10, 12, 14, 16, 18, 20]
```

```python
[2 * element for element in numbers_list]
```

```text
[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
```

### `break` und `continue`

```python
for element in numbers_list:
    if element == 4:
        break
    print(element)
```

```text
1
2
3
```

`break` beendet die Schleife ganz.

```python
for element in numbers_list:
    if element == 4:
        continue
    print(element)
```

```text
1
2
3
5
6
7
8
9
10
```

`continue` überspringt nur die `4`.

### while-Schleife

```text
while boolean_expression:
    code_block
```

```python
count = 10

while count > 0:
    print(count)
    count = count - 1
```

```text
10
9
8
7
6
5
4
3
2
1
```

### Verschachtelte Schleifen

```python
for a in range(0,10):
    for b in range(0,10):
        for c in range(0,10):
            print(str(a) + str(b) + str(c))
```

```text
000
001
002
003
…
997
998
999
```

Insgesamt 1000 Zeilen, von `000` bis `999`. Die Mitte ist hier gekürzt.

### Lab 06 – Lösungen

Ziel-Ausgabe der Aufgabe:

```text
1. I will not let my dog eat my homework
2. I will not let my dog eat my homework
3. I will not let my dog eat my homework
...
50. I will not let my dog eat my homework
```

```python
def detention_helper(detention_message, num_lines):
    for i in range(num_lines):
        print(f"{i+1}. {detention_message}")
```

```python
detention_helper("I will not let my dog eat my homework", 50)
```

```text
1. I will not let my dog eat my homework
2. I will not let my dog eat my homework
3. I will not let my dog eat my homework
…
49. I will not let my dog eat my homework
50. I will not let my dog eat my homework
```

50 Zeilen, hier gekürzt. `i+1` sorgt dafür, dass die Zählung bei 1 beginnt.

```python
def detention_helper(detention_message, num_lines):
    i = 0
    while i < num_lines:
        i += 1
        print(f"{i}. {detention_message}")
```

```python
detention_helper("I will do my python homework", 25)
```

```text
1. I will do my python homework
2. I will do my python homework
3. I will do my python homework
…
24. I will do my python homework
25. I will do my python homework
```

25 Zeilen, hier gekürzt.

```python
city1 = "San Francisco"
temp1 = 58
humidity1 = 0.85

city2 = "Paris"
temp2 = 75
humidity2 = 0.50

city3 = "Mumbai"
temp3 = 81
humidity3 = 0.88

print(f"{'City':15} {'Temperature':15} {'Humidity':15}")
print(f"{city1:15} {temp1:11} {humidity1:12.2f}")
print(f"{city2:15} {temp2:11} {humidity2:12.2f}")
print(f"{city3:15} {temp3:11} {humidity3:12.2f}")
```

```text
City            Temperature     Humidity       
San Francisco            58         0.85
Paris                    75         0.50
Mumbai                   81         0.88
```

```python
city_list = ["San Francisco", "Paris", "Mumbai"]
temperature_list = [58, 75, 81]
humidity_list = [.85, .5, .88]

print(f"{'City':15} {'Temperature':15} {'Humidity':15}")
i = 0
while (i < len(city_list)):
    print(f"{city_list[i]:15} {temperature_list[i]:11} {humidity_list[i]:12.2f}")
    i = i + 1
```

```text
City            Temperature     Humidity       
San Francisco            58         0.85
Paris                    75         0.50
Mumbai                   81         0.88
```

Gleiche Ausgabe, aber mit Listen und Schleife statt neun Variablen.

Gewünschtes Verhalten von `item_count()`:

```python
item_count(['a', 'b', 'a'])
# Returns: {'a': 2, 'b': 1}
```

```python
def item_count(input_list):
    output_dict = {}
  
    for item in input_list:
        if item not in output_dict:
            output_dict[item] = 1
        else:
            output_dict[item] += 1
      
    return output_dict
```

```python
shopping_items = ['socks', 'shirt', 'pants', 'socks', 'shoes', 'suit', 'socks', 'shirt', 'shoes', 'shorts', 'pants', 'shorts', 'socks', 'shorts', 'shorts']

print(item_count(shopping_items))
```

```text
{'socks': 4, 'shirt': 2, 'pants': 2, 'shoes': 2, 'suit': 1, 'shorts': 4}
```

---

## Modul 07 – Fehler und Exceptions

### Syntaxfehler

```python
if print("Hello World")
```

```text
SyntaxError: expected ':'
```

Im Kurs ist die Zeile auskommentiert. Ein Syntaxfehler stoppt die Zelle, bevor irgendetwas läuft.

### Exception

```python
1 / 0
```

```text
ZeroDivisionError: division by zero
```

Auch diese Zeile ist im Kurs auskommentiert. Der Code ist gültig, scheitert aber beim Ausführen.

### `try`/`except`

```text
try:
    # Code, der eine Exception auslösen kann
except:
    # Code, der ausgeführt wird, wenn eine beliebige Exception auftritt
```

```python
try:
    1/0 # Throws an exception
except:
    print("Exception Handled")
```

```text
Exception Handled
```

### Bestimmten Exception-Typ abfangen

```text
try:
    # Code, der eine Exception auslösen kann
except ExceptionName:
    # Code, der nur ausgeführt wird, wenn ExceptionName ausgelöst wird
```

```python
try:
    1/0
except ZeroDivisionError:
    print("Exception Handled")
```

```text
Exception Handled
```

```python
try:
    print(undefined_variable)
except ZeroDivisionError:
    print("Exception Handled")
```

```text
NameError: name 'undefined_variable' is not defined
```

Im Kurs auskommentiert. Der `NameError` wird nicht abgefangen, weil nur `ZeroDivisionError` behandelt wird.

### Mehrere Typen

```text
except (ExceptionType1, ExceptionType2):
    # handles either exception
```

```python
try:
    1/0
    print(undefined_variable)
except (ZeroDivisionError, NameError):
    print("Exception Handled")
```

```text
Exception Handled
```

Schon `1/0` löst aus. Die zweite Zeile läuft gar nicht mehr.

### Fehlermeldung ausgeben

```python
try:
    #1/0 # Throws a ZeroDivisionError exception
    #print(undefined_variable) # Throws a NameError exception
except (ZeroDivisionError, NameError) as e: print(f"Exception Handled: {e}")
```

So wie im Kurs abgedruckt ergibt das `IndentationError: expected an indented block after 'try' statement`, weil beide Zeilen im `try` auskommentiert sind. Entfernt man das `#` vor einer Zeile, sieht man die Meldung:

```text
Exception Handled: division by zero
```

bzw. mit der zweiten Zeile:

```text
Exception Handled: name 'undefined_variable' is not defined
```

### `else`

```text
try:
    ...
except ExceptionType:
    # läuft, wenn eine Exception auftritt
else:
    # läuft nur, wenn KEINE Exception auftritt
```

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Cannot divide by zero!")
else:
    print(f"Division successful! Result: {result}")
```

```text
Division successful! Result: 5.0
```

### `finally`

```text
try:
    ...
except ExceptionType:
    ...
finally:
    # läuft IMMER, ob Exception oder nicht
```

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Cannot divide by zero!")
else:
    print(f"Division successful! Result: {result}")
finally:
    print("This always executes — use it for cleanup tasks.")
```

```text
Division successful! Result: 5.0
This always executes — use it for cleanup tasks.
```

### `assert`

```text
assert boolean_expression, optional_message
```

```python
assert 1 == 1
```

Kein Ergebnis. Die Bedingung ist wahr, also passiert nichts.

```python
assert 1 == 2, "That is not true"
```

```text
AssertionError: That is not true
```

Im Kurs auskommentiert.

---

## Modul 08 – Klassen

### Klasse definieren

```text
class ClassName():
    <code block>
```

```python
class Dog():
    pass
```

Kein Ergebnis.

### Instanziieren

```text
object_name = ClassName()
```

```python
my_dog = Dog()

type(my_dog)
```

```text
<class '__main__.Dog'>
```

### Funktionen sind Objekte

```text
my_variable = some_function   # assign the function (no parentheses)
my_variable()                 # über den neuen Namen aufrufen
```

```python
def greet(name):
    return f"Hello, {name}!"

say_hello = greet

print(say_hello("Rex"))
print(greet("Rex"))
print(type(say_hello))
```

```text
Hello, Rex!
Hello, Rex!
<class 'function'>
```

### Methoden

```text
object.method(args)
```

```text
class ClassName():

    def method_name(self, args):
        method code
```

```python
class UpdatedDog():
    
    def return_name(self, name):
        return f"name: {name}"
```

```python
my_updated_dog = UpdatedDog()

my_updated_dog.return_name("Rex")
```

```text
'name: Rex'
```

### `self`

```python
class DogWithSelf():
    
    def print_self(self):
        print(self)
        
dog_with_self = DogWithSelf()

print(dog_with_self)
dog_with_self.print_self()
```

```text
<__main__.DogWithSelf object at 0x7f3a1c2b5e10>
<__main__.DogWithSelf object at 0x7f3a1c2b5e10>
```

Beide Zeilen zeigen dieselbe Adresse. `self` ist also das Objekt selbst. Die Adresse ist bei jedem Lauf anders.

### `__init__` und Attribute

```text
class ClassName():

    def __init__(self, arg):
        self.arg = arg
```

```python
class DogWithAttributes():

    def __init__(self, name, color):
        print("This ran automatically!")
        self.name = name
        self.color = color

dog_with_attributes = DogWithAttributes("Rex", "Orange")
```

```text
This ran automatically!
```

`__init__` läuft automatisch beim Erzeugen des Objekts.

```python
dog_with_attributes.name
```

```text
'Rex'
```

### Attribute in Methoden

```python
class DogWithAttributesAndMethod():
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
        
    def return_name(self):
        return self.name

    def return_color(self):
        return self.color
    
my_dog = DogWithAttributesAndMethod("Rex", "tan")

print(f"My dog's name is {my_dog.return_name()} and his coat color is {my_dog.return_color()}")
```

```text
My dog's name is Rex and his coat color is tan
```

### Attribute ändern

```python
class DogWithAttributesAndMethods():
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
        
    def return_name(self):
        return self.name
        
    def update_name(self, new_name):
        self.name = new_name
        
my_dog = DogWithAttributesAndMethods("Rex", "tan")
print(f"Here's my dog's name: {my_dog.return_name()}")

my_dog.update_name("Ruffles")
print(f"My dog's name after updating it, is: {my_dog.return_name()}")
```

```text
Here's my dog's name: Rex
My dog's name after updating it, is: Ruffles
```

### Mit anderen Instanzen arbeiten

```python
class DogFinal():
    
    def __init__(self, name_str, color_str):
        self.name = name_str
        self.color = color_str
        
    def return_name(self):
        return self.name
        
    def update_name(self, new_name):
        self.name = new_name
        
    def return_both_names(self, other_dog_object):
        return self.name + " and " + other_dog_object.name
        
dog_1 = DogFinal("Rex", "tan")
dog_2 = DogFinal("Ruffles", "black and tan")

dog_1.return_both_names(dog_2)
```

```text
'Rex and Ruffles'
```

### Vererbung

```text
class ChildClass(ParentClass):
    <code block>
```

```python
class Animal():
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

    def speak(self):
        return f"{self.name} says {self.sound}!"

class Dog(Animal):
    def __init__(self, name, color):
        super().__init__(name, sound="Woof")
        self.color = color

    def fetch(self):
        return f"{self.name} fetches the ball!"

class Cat(Animal):
    def __init__(self, name):
        super().__init__(name, sound="Meow")

my_dog = Dog("Rex", "tan")
my_cat = Cat("Whiskers")

print(my_dog.speak())
print(my_dog.fetch())
print(my_cat.speak())
print(type(my_dog))
```

```text
Rex says Woof!
Rex fetches the ball!
Whiskers says Meow!
<class '__main__.Dog'>
```

`speak()` kommt von `Animal`. `fetch()` gibt es nur bei `Dog`.

### Lab 08 – Lösungen

```python
class Simpson():
    
    def __init__(self, first_name, age, favorite_food):
        self.first_name = first_name
        self.age = age
        self.favorite_food = favorite_food
        
    def simpson_summary(self):
        return f"{self.first_name} Simpson is {self.age} years old and their favorite food is {self.favorite_food}"
        
    def older(self, other_simpson):
        return self.age > other_simpson.age
```

```python
homer = Simpson("Homer", 39, "Donuts")
bart = Simpson("Bart", 10, "Hamburgers")

print(homer.simpson_summary())
print(homer.older(bart))
print(bart.simpson_summary())
print(bart.older(homer))
```

```text
Homer Simpson is 39 years old and their favorite food is Donuts
True
Bart Simpson is 10 years old and their favorite food is Hamburgers
False
```

Hilfsfunktion für den größten gemeinsamen Teiler:

```python
def greatest_common_factor(a, b):
    gcf = 1
    if a < b:
        limit = a
    else:
        limit = b
    
    for index in range(2, limit + 1):
        if (a % index == 0) and (b % index == 0):
            gcf = index
        
    return gcf
```

Kein Ergebnis. Zum Beispiel gibt `greatest_common_factor(2, 4)` den Wert `2` zurück.

```python
class Fraction():
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def to_string(self):
        return f"{self.numerator} / {self.denominator}"

    def as_decimal(self):
        return self.numerator / self.denominator

    def least_common_denominator(self, other):
        a = self.denominator
        b = other.denominator
        lcd = a * b // greatest_common_factor(a, b)
        return lcd

    def reduce(self):
        gcf = greatest_common_factor(self.numerator, self.denominator)

        if self.denominator < 0:
            gcf *= -1

        self.numerator //= gcf
        self.denominator //= gcf
        return self

    def is_equal(self, other):
        return self.as_decimal() == other.as_decimal()

    def is_less_than(self, other):
        return self.as_decimal() < other.as_decimal()

    def scale(self, multiplier):
        self.numerator *= multiplier
        self.denominator *= multiplier
```

```python
one_half = Fraction(1, 2)
two_fourths = Fraction(2, 4)

print("one_half to_string:", one_half.to_string())
print("two_fourths to_string:", two_fourths.to_string())

print("one_half as_decimal:", one_half.as_decimal())
print("two_fourths as_decimal:", two_fourths.as_decimal())

print("one_half least common denominator with two_fourths:", one_half.least_common_denominator(two_fourths))
print("two_fourths least common denominator with one_half:", two_fourths.least_common_denominator(one_half))

reduced_1 = Fraction(one_half.numerator, one_half.denominator)
reduced_1.reduce()
print("one_half reduced:", reduced_1.to_string())

reduced_2 = Fraction(two_fourths.numerator, two_fourths.denominator)
reduced_2.reduce()
print("two_fourths reduced:", reduced_2.to_string())

print("one_half is equal to two_fourths:", one_half.is_equal(two_fourths))
print("two_fourths is equal to one_half:", two_fourths.is_equal(one_half))

print("one_half is less than two_fourths:", one_half.is_less_than(two_fourths))
print("two_fourths is less than one_half:", two_fourths.is_less_than(one_half))

scaled_1 = Fraction(one_half.numerator, one_half.denominator)
scaled_1.scale(2)
print("one_half scaled by 2:", scaled_1.to_string())

scaled_2 = Fraction(two_fourths.numerator, two_fourths.denominator)
scaled_2.scale(2)
print("two_fourths scaled by 2:", scaled_2.to_string())
```

```text
one_half to_string: 1 / 2
two_fourths to_string: 2 / 4
one_half as_decimal: 0.5
two_fourths as_decimal: 0.5
one_half least common denominator with two_fourths: 4
two_fourths least common denominator with one_half: 4
one_half reduced: 1 / 2
two_fourths reduced: 1 / 2
one_half is equal to two_fourths: True
two_fourths is equal to one_half: True
one_half is less than two_fourths: False
two_fourths is less than one_half: False
one_half scaled by 2: 2 / 4
two_fourths scaled by 2: 4 / 8
```

```python
class MixedNumber(Fraction):

    def __init__(self, whole, numerator, denominator):
        super().__init__(numerator, denominator)
        self.whole = whole

    def to_string(self):
        return f"{self.whole} {self.numerator} / {self.denominator}"

    def as_decimal(self):
        return self.whole + super().as_decimal()

    def to_improper(self):
        improper_numerator = self.whole * self.denominator + self.numerator
        return Fraction(improper_numerator, self.denominator)
```

```python
one_and_three_quarters = MixedNumber(1, 3, 4)
two_and_one_half = MixedNumber(2, 1, 2)

print("one_and_three_quarters:", one_and_three_quarters.to_string())
print("two_and_one_half:", two_and_one_half.to_string())

print("one_and_three_quarters as decimal:", one_and_three_quarters.as_decimal())
print("two_and_one_half as decimal:", two_and_one_half.as_decimal())

improper_one_and_three_quarters = one_and_three_quarters.to_improper()
print("one_and_three_quarters as improper:", improper_one_and_three_quarters.to_string())
improper_two_and_one_half = two_and_one_half.to_improper()
print("two_and_one_half as improper:", improper_two_and_one_half.to_string())

print("1 3/4 is less than 2 1/2:", one_and_three_quarters.is_less_than(two_and_one_half))
print("1 3/4 is equal to 2 1/2:", one_and_three_quarters.is_equal(two_and_one_half))
```

```text
one_and_three_quarters: 1 3 / 4
two_and_one_half: 2 1 / 2
one_and_three_quarters as decimal: 1.75
two_and_one_half as decimal: 2.5
one_and_three_quarters as improper: 7 / 4
two_and_one_half as improper: 5 / 2
1 3/4 is less than 2 1/2: True
1 3/4 is equal to 2 1/2: False
```

`is_less_than()` und `is_equal()` sind geerbt. Sie nutzen aber das überschriebene `as_decimal()` von `MixedNumber`.

---

## Modul 09 – Bibliotheken

### Anderes Notebook mit `%run` einbinden

```text
%run ../Includes/run_example
```

Ergebnis: Das Notebook `run_example` läuft komplett. Alles, was es definiert, ist danach hier verfügbar.

```python
greet("Bob")
```

Ergebnis: Der Begrüßungs-String, den `greet()` aus `run_example` zurückgibt, z. B. `'Hello, Bob!'`. Die Funktion wurde in diesem Notebook nie definiert.

### Bibliothek importieren

```python
import numpy
```

Kein Ergebnis. numpy ist auf Serverless schon installiert.

### `%pip`

```text
%pip install numpy
```

```text
Requirement already satisfied: numpy in /databricks/python3/lib/python3.12/site-packages (...)
```

Die Versionsnummer in der Klammer hängt von der Umgebung ab.

```text
%pip --help
```

Ergebnis: Die Hilfe von pip mit allen Befehlen (`install`, `uninstall`, `list`, `show` usw.) und Optionen.

### Drei Arten zu importieren

```python
import numpy

numpy.sqrt(4.0)
```

```text
np.float64(2.0)
```

```python
import numpy as np

np.sqrt(4.0)
```

```text
np.float64(2.0)
```

```python
from numpy import sqrt

sqrt(4.0)
```

```text
np.float64(2.0)
```

Gleiches Ergebnis. Nur der Aufruf ist anders: voller Name, Alias oder direkt die Funktion.

### Arrays erstellen

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
print("From list:", a)

b = np.array([[1, 2, 3], [4, 5, 6]])
print("2D array:\n", b)

print("Zeros:", np.zeros(4))
print("Ones:", np.ones(3))
print("Range:", np.arange(0, 10, 2))
```

```text
From list: [1 2 3 4 5]
2D array:
 [[1 2 3]
 [4 5 6]]
Zeros: [0. 0. 0. 0.]
Ones: [1. 1. 1.]
Range: [0 2 4 6 8]
```

### `dtype`

```python
int_array = np.array([1, 2, 3])
print("Integer array dtype:", int_array.dtype)

float_array = np.array([1.0, 2.0, 3.0])
print("Float array dtype:", float_array.dtype)

specified = np.array([1, 2, 3], dtype=np.float32)
print("Specified dtype:", specified.dtype, "| Values:", specified)
```

```text
Integer array dtype: int64
Float array dtype: float64
Specified dtype: float32 | Values: [1. 2. 3.]
```

### Indexierung, Slicing, Striding

```python
arr = np.array([10, 20, 30, 40, 50, 60, 70, 80])

print("First element:", arr[0])
print("Last element:", arr[-1])
print("Elements 1-3:", arr[1:4])
print("Every other element:", arr[::2])
print("Reversed:", arr[::-1])
```

```text
First element: 10
Last element: 80
Elements 1-3: [20 30 40]
Every other element: [10 30 50 70]
Reversed: [80 70 60 50 40 30 20 10]
```

### Aggregationen

```python
grades = np.array([75, 80, 85, 90, 95, 78, 82, 88, 91])

print("Sum of all elements:", grades.sum())
print("Mean of all elements:", grades.mean())
print("Max value:", grades.max())
print("Min value:", grades.min())
print("Standard deviation:", grades.std())
```

```text
Sum of all elements: 764
Mean of all elements: 84.88888888888889
Max value: 95
Min value: 75
Standard deviation: 6.261779023824609
```

### `help()` auf Bibliotheken

```python
help(np)
```

```text
Help on package numpy:

NAME
    numpy

DESCRIPTION
    NumPy
    =====

    Provides
      1. An array object of arbitrary homogeneous items
      2. Fast mathematical operations over arrays
      3. Linear Algebra, Fourier Transforms, Random Number Generation
…
```

Sehr lange Ausgabe, hier gekürzt. Sie listet alle Unterpakete und Funktionen.

```python
help(np.sqrt)
```

```text
Help on ufunc in module numpy:

sqrt = <ufunc 'sqrt'>
    sqrt(x, /, out=None, *, where=True, casting='same_kind', order='K', dtype=None, subok=True[, signature])

    Return the non-negative square-root of an array, element-wise.
…
    Examples
    --------
    >>> import numpy as np
    >>> np.sqrt([1,4,9])
    array([ 1.,  2.,  3.])
```

Ebenfalls gekürzt.

---

## Modul 10 – pandas-Überblick

### Import

```python
import pandas as pd
```

Kein Ergebnis.

### DataFrame aus einer Liste

```python
data = [["John", 30, "Journalist"], ["Mary", 30, "Programmer"], ["Abe", 40, "Chef"]]

df = pd.DataFrame(data=data)
df
```

```text
      0   1           2
0  John  30  Journalist
1  Mary  30  Programmer
2   Abe  40        Chef
```

Ohne Spaltennamen heißen die Spalten `0`, `1`, `2`.

```python
cols = ["Name", "Age", "Job"]
df = pd.DataFrame(data=data, columns=cols)
df
```

```text
   Name  Age         Job
0  John   30  Journalist
1  Mary   30  Programmer
2   Abe   40        Chef
```

### DataFrame aus einem NumPy-Array

```python
import numpy as np

np_array = np.array([
    ["John", 30, "Journalist"],
    ["Mary", 30, "Programmer"],
    ["Abe", 40, "Chef"]
])

df2 = pd.DataFrame(data=np_array, columns=cols)
df2
```

```text
   Name Age         Job
0  John  30  Journalist
1  Mary  30  Programmer
2   Abe  40        Chef
```

```python
df2.dtypes
```

```text
Name    object
Age     object
Job     object
dtype: object
```

Ein NumPy-Array hat nur einen Typ. Deshalb wird `30` hier zum String, und `Age` ist `object`.

### Eine Spalte (Series) auswählen

```python
df["Age"]
```

```text
0    30
1    30
2    40
Name: Age, dtype: int64
```

```python
df.Age
```

```text
0    30
1    30
2    40
Name: Age, dtype: int64
```

```python
df2["Age"]
```

```text
0    30
1    30
2    40
Name: Age, dtype: object
```

Gleiche Werte, aber `object` statt `int64`.

### `dtypes`

```python
df.dtypes
```

```text
Name    object
Age      int64
Job     object
dtype: object
```

### Rechnen mit einer Series

```python
df["Age"] + df["Age"]
```

```text
0    60
1    60
2    80
Name: Age, dtype: int64
```

```python
df["Age"] * 3 - 1
```

```text
0     89
1     89
2    119
Name: Age, dtype: int64
```

### Einzelwert

```python
df["Age"][0]
```

```text
np.int64(30)
```

### Mehrere Spalten

```text
df[[col_1, col_2, col_3, ...]]
```

```python
df[["Name", "Age"]]
```

```text
   Name  Age
0  John   30
1  Mary   30
2   Abe   40
```

```python
df[["Name", "Job"]]
```

```text
   Name         Job
0  John  Journalist
1  Mary  Programmer
2   Abe        Chef
```

### `.iloc`

```text
df.iloc[row_selection, column_selection]
```

```python
df
```

```text
   Name  Age         Job
0  John   30  Journalist
1  Mary   30  Programmer
2   Abe   40        Chef
```

```python
df.iloc[:, [0, 2]]
```

```text
   Name         Job
0  John  Journalist
1  Mary  Programmer
2   Abe        Chef
```

```python
df.iloc[:1, :]
```

```text
   Name  Age         Job
0  John   30  Journalist
```

Mit Slice `:1` kommt ein DataFrame zurück.

```python
df.iloc[0, :]
```

```text
Name          John
Age             30
Job     Journalist
Name: 0, dtype: object
```

Mit einer einzelnen Zahl `0` kommt eine Series zurück.

### Unveränderlich per Standard

```python
df.drop("Age", axis=1)
```

```text
   Name         Job
0  John  Journalist
1  Mary  Programmer
2   Abe        Chef
```

```python
df
```

```text
   Name  Age         Job
0  John   30  Journalist
1  Mary   30  Programmer
2   Abe   40        Chef
```

`df` hat `Age` noch. `drop()` hat nur eine Kopie geliefert.

```python
df_no_age = df.drop("Age", axis=1)
df_no_age
```

```text
   Name         Job
0  John  Journalist
1  Mary  Programmer
2   Abe        Chef
```

### `inplace=True`

```python
df.drop("Age", axis=1, inplace=True)
```

Kein Ergebnis. Die Methode gibt `None` zurück.

```python
df
```

```text
   Name         Job
0  John  Journalist
1  Mary  Programmer
2   Abe        Chef
```

Jetzt ist `Age` in `df` selbst weg.

### Lab 10 – Lösungen

```python
import pandas as pd
```

```python
data = [["Buddy", 3, "Australian Shepherd"], ["Harley", 10, "Labrador"], ["Luna", 2, "Golden Retriever"], ["Bailey", 8, "Chihuahua"]]
column_names = ["Name", "Age", "Breed"]

df = pd.DataFrame(data=data, columns=column_names)
df
```

```text
     Name  Age                Breed
0   Buddy    3  Australian Shepherd
1  Harley   10             Labrador
2    Luna    2     Golden Retriever
3  Bailey    8            Chihuahua
```

```python
df.dtypes
```

```text
Name     object
Age       int64
Breed    object
dtype: object
```

```python
name_age_df = df[["Name", "Age"]]
name_age_df
```

```text
     Name  Age
0   Buddy    3
1  Harley   10
2    Luna    2
3  Bailey    8
```

```python
df["Human Age"] = df["Age"] * 7
df
```

```text
     Name  Age                Breed  Human Age
0   Buddy    3  Australian Shepherd         21
1  Harley   10             Labrador         70
2    Luna    2     Golden Retriever         14
3  Bailey    8            Chihuahua         56
```

```python
breed = df[df["Name"] == "Buddy"]["Breed"][0]
breed
```

```text
'Australian Shepherd'
```

---

## Modul 11 – Fortgeschrittenes pandas

### Klassenraum-Setup

```text
%run ../Includes/Classroom-Setup-11
```

Ergebnis: Das Setup legt das Objekt `DA` an und stellt die Datensätze im eigenen Volume bereit.

```python
print(f"Username:                           {DA.username}")
print(f"Default Catalog Name:               {DA.catalog_name}")
print(f"User Based Schema Name:             {DA.schema_name}")
```

Beispielausgabe (die Werte hängen vom eigenen Workspace ab):

```text
Username:                           labuser1234567@vocareum.com
Default Catalog Name:               dbacademy
User Based Schema Name:             labuser1234567
```

```python
spark.sql("SHOW CATALOGS").display()
```

Beispielausgabe als Tabelle mit einer Spalte `catalog`:

```text
catalog
dbacademy
samples
system
```

```python
spark.sql(f"USE CATALOG {DA.catalog_name}")
```

```text
DataFrame[]
```

`USE` liefert einen leeren DataFrame. Wichtig ist nur die Wirkung: `dbacademy` ist jetzt der aktuelle Catalog.

```python
spark.sql(f"SHOW SCHEMAS IN {DA.catalog_name}").display()
```

Beispielausgabe als Tabelle mit der Spalte `databaseName`:

```text
databaseName
default
information_schema
labuser1234567
```

```python
spark.sql(f"USE SCHEMA {DA.schema_name}")
```

```text
DataFrame[]
```

```python
spark.sql("""
SELECT
  current_catalog() AS `Current Catalog`,
  current_schema() AS `Current Schema`,
  CURRENT_USER() AS `Current User`
""").display()
```

Beispielausgabe als Tabelle mit einer Zeile:

```text
Current Catalog | Current Schema  | Current User
dbacademy       | labuser1234567  | labuser1234567@vocareum.com
```

### Airbnb-Daten laden

```python
import pandas as pd
```

Pfadmuster:

```text
/Volumes/<your_catalog>/<your_schema>/datasets/airbnb/sf-airbnb.csv
```

```python
file_path = f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv"
df = pd.read_csv(file_path)
```

Kein Ergebnis. `df` hat danach 7151 Zeilen und 106 Spalten.

### `head()` und `tail()`

```python
df.head(3)
```

```text
     id                    listing_url       scrape_id last_scraped  ... calculated_host_listings_count_entire_homes  \
0   958  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
1  5858  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
2  7918  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                

  calculated_host_listings_count_private_rooms calculated_host_listings_count_shared_rooms reviews_per_month  
0                              0                                            0                           1.54  
1                              0                                            0                           0.93  
2                              9                                            0                           0.15  

[3 rows x 106 columns]
```

In Databricks erscheint das als scrollbare Tabelle mit allen 106 Spalten.

```python
df.tail(3)
```

```text
            id                    listing_url       scrape_id last_scraped  ...  \
7148  32841126  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...   
7149  32842243  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...   
7150  32845190  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...   

     calculated_host_listings_count_entire_homes calculated_host_listings_count_private_rooms  \
7148                              8                                           0                 
7149                             86                                           1                 
7150                             86                                           1                 

     calculated_host_listings_count_shared_rooms reviews_per_month  
7148                              0                            NaN  
7149                              0                            NaN  
7150                              0                            NaN  

[3 rows x 106 columns]
```

### Spalten auflisten

```python
df.columns
```

```text
Index(['id', 'listing_url', 'scrape_id', 'last_scraped', 'name', 'summary', 'space', 'description',
       'experiences_offered', 'neighborhood_overview',
       ...
       'instant_bookable', 'is_business_travel_ready', 'cancellation_policy', 'require_guest_profile_picture',
       'require_guest_phone_verification', 'calculated_host_listings_count',
       'calculated_host_listings_count_entire_homes', 'calculated_host_listings_count_private_rooms',
       'calculated_host_listings_count_shared_rooms', 'reviews_per_month'],
      dtype='object', length=106)
```

```python
list(df.columns)
```

```text
['id', 'listing_url', 'scrape_id', 'last_scraped', 'name', 'summary', 'space', 'description', 'experiences_offered', 'neighborhood_overview', 'notes', 'transit', 'access', 'interaction', 'house_rules', 'thumbnail_url', 'medium_url', 'picture_url', 'xl_picture_url', 'host_id', 'host_url', 'host_name', 'host_since', 'host_location', 'host_about', 'host_response_time', 'host_response_rate', 'host_acceptance_rate', 'host_is_superhost', 'host_thumbnail_url', 'host_picture_url', 'host_neighbourhood', 'host_listings_count', 'host_total_listings_count', 'host_verifications', 'host_has_profile_pic', 'host_identity_verified', 'street', 'neighbourhood', 'neighbourhood_cleansed', 'neighbourhood_group_cleansed', 'city', 'state', 'zipcode', 'market', 'smart_location', 'country_code', 'country', 'latitude', 'longitude', 'is_location_exact', 'property_type', 'room_type', 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'bed_type', 'amenities', 'square_feet', 'price', 'weekly_price', 'monthly_price', 'security_deposit', 'cleaning_fee', 'guests_included', 'extra_people', 'minimum_nights', 'maximum_nights', 'minimum_minimum_nights', 'maximum_minimum_nights', 'minimum_maximum_nights', 'maximum_maximum_nights', 'minimum_nights_avg_ntm', 'maximum_nights_avg_ntm', 'calendar_updated', 'has_availability', 'availability_30', 'availability_60', 'availability_90', 'availability_365', 'calendar_last_scraped', 'number_of_reviews', 'number_of_reviews_ltm', 'first_review', 'last_review', 'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness', 'review_scores_checkin', 'review_scores_communication', 'review_scores_location', 'review_scores_value', 'requires_license', 'license', 'jurisdiction_names', 'instant_bookable', 'is_business_travel_ready', 'cancellation_policy', 'require_guest_profile_picture', 'require_guest_phone_verification', 'calculated_host_listings_count', 'calculated_host_listings_count_entire_homes', 'calculated_host_listings_count_private_rooms', 'calculated_host_listings_count_shared_rooms', 'reviews_per_month']
```

`list()` zeigt alle Namen ohne `...`.

### Datentypen

```python
df.dtypes
```

```text
id                                                int64
listing_url                                      object
scrape_id                                         int64
last_scraped                                     object
name                                             object
                                                 ...   
calculated_host_listings_count                    int64
calculated_host_listings_count_entire_homes       int64
calculated_host_listings_count_private_rooms      int64
calculated_host_listings_count_shared_rooms       int64
reviews_per_month                               float64
Length: 106, dtype: object
```

```python
df[["first_review", "last_review"]].dtypes
```

```text
first_review    object
last_review     object
dtype: object
```

Die Datumsspalten sind nur Text (`object`).

### Datum parsen mit `pd.to_datetime()`

```python
df["first_review"]
```

```text
0       2009-07-23
1       2009-05-03
2       2009-08-31
3       2014-09-08
4       2009-09-25
           ...    
7146           NaN
7147           NaN
7148           NaN
7149           NaN
7150           NaN
Name: first_review, Length: 7151, dtype: object
```

```python
df["last_review"]
```

```text
0       2019-02-17
1       2017-08-06
2       2016-11-21
3       2018-09-12
4       2018-08-11
           ...    
7146           NaN
7147           NaN
7148           NaN
7149           NaN
7150           NaN
Name: last_review, Length: 7151, dtype: object
```

```python
df["first_review"] = pd.to_datetime(df["first_review"])
df["last_review"] = pd.to_datetime(df["last_review"])

df[["id", "first_review", "last_review"]].head(10)
```

```text
      id first_review last_review
0    958   2009-07-23  2019-02-17
1   5858   2009-05-03  2017-08-06
2   7918   2009-08-31  2016-11-21
3   8142   2014-09-08  2018-09-12
4   8339   2009-09-25  2018-08-11
5   8567   2009-08-14  2018-09-02
6   8739   2009-08-01  2019-02-27
7   9225   2009-10-26  2019-02-25
8  10251   2009-09-12  2019-02-18
9  10820   2009-10-22  2018-12-01
```

```python
df[["first_review", "last_review"]].dtypes
```

```text
first_review    datetime64[ns]
last_review     datetime64[ns]
dtype: object
```

Jetzt echte Datumswerte. Aus `NaN` wird dabei `NaT` (Not a Time).

### Datum formatieren mit `strftime()`

```python
df["first_review_fmt"] = df["first_review"].dt.strftime("%m-%d-%Y")
df["last_review_fmt"] = df["last_review"].dt.strftime("%m-%d-%Y")

df[["id", "first_review", "first_review_fmt", "last_review", "last_review_fmt"]].head(10)
```

```text
      id first_review first_review_fmt last_review last_review_fmt
0    958   2009-07-23       07-23-2009  2019-02-17      02-17-2019
1   5858   2009-05-03       05-03-2009  2017-08-06      08-06-2017
2   7918   2009-08-31       08-31-2009  2016-11-21      11-21-2016
3   8142   2014-09-08       09-08-2014  2018-09-12      09-12-2018
4   8339   2009-09-25       09-25-2009  2018-08-11      08-11-2018
5   8567   2009-08-14       08-14-2009  2018-09-02      09-02-2018
6   8739   2009-08-01       08-01-2009  2019-02-27      02-27-2019
7   9225   2009-10-26       10-26-2009  2019-02-25      02-25-2019
8  10251   2009-09-12       09-12-2009  2019-02-18      02-18-2019
9  10820   2009-10-22       10-22-2009  2018-12-01      12-01-2018
```

Die `_fmt`-Spalten sind wieder Strings im Format Monat-Tag-Jahr.

### Spalten umbenennen

```python
df = df.rename(columns={"old_name": "new_name"})
```

```python
df.rename(columns={"old_col_a": "new_col_a", "old_col_b": "new_col_b"})
```

Ergebnis: Der unveränderte DataFrame (`[7151 rows x 108 columns]`). Die Spalten `old_...` gibt es nicht. pandas ignoriert unbekannte Namen ohne Fehler.

```python
df = df.rename(columns={"neighbourhood": "neighborhood"})
df[["id", "neighborhood"]].head(10)
```

```text
      id           neighborhood
0    958        Duboce Triangle
1   5858         Bernal Heights
2   7918            Cole Valley
3   8142            Cole Valley
4   8339  Western Addition/NOPA
5   8567  Western Addition/NOPA
6   8739       Mission District
7   9225           Potrero Hill
8  10251       Mission District
9  10820           Lower Haight
```

### Boolean-Indexierung

```python
filtered_df = df[df["host_is_superhost"] == "t"]
filtered_df[["id", "host_is_superhost"]].head(10)
```

```text
       id host_is_superhost
0     958                 t
6    8739                 t
8   10251                 t
14  12522                 t
15  12584                 t
18  18231                 t
19  18904                 t
20  19040                 t
21  21334                 t
23  23611                 t
```

Der Index behält die ursprünglichen Zeilennummern.

```python
df["host_is_superhost"] == "t"
```

```text
0        True
1       False
2       False
3       False
4       False
        ...  
7146    False
7147     True
7148     True
7149    False
7150    False
Name: host_is_superhost, Length: 7151, dtype: bool
```

Die Bedingung allein ergibt eine Series aus `True`/`False`.

```python
df["host_is_superhost"] != "t"
```

```text
0       False
1        True
2        True
3        True
4        True
        ...  
7146     True
7147    False
7148    False
7149     True
7150     True
Name: host_is_superhost, Length: 7151, dtype: bool
```

### Bedingungen verknüpfen mit `&`

```python
filtered_df = df[(df["host_is_superhost"] == "t") & (df["number_of_reviews"] >= 150)]
filtered_df[["id", "host_is_superhost", "number_of_reviews"]].head(10)
```

```text
       id host_is_superhost  number_of_reviews
0     958                 t                180
6    8739                 t                647
8   10251                 t                320
14  12522                 t                390
19  18904                 t                363
20  19040                 t                227
23  23611                 t                234
24  23630                 t                353
26  24450                 t                218
27  24463                 t                272
```

Jede Bedingung braucht eigene Klammern.

### Aggregationen

```python
print(df["number_of_reviews"].mean())
print(df["number_of_reviews"].min())
print(df["number_of_reviews"].max())
```

```text
43.52915676129213
0
677
```

### `describe()`

```python
df["number_of_reviews"].describe()
```

```text
count    7151.000000
mean       43.529157
std        72.519229
min         0.000000
25%         1.000000
50%        11.000000
75%        54.000000
max       677.000000
Name: number_of_reviews, dtype: float64
```

```python
df[["number_of_reviews", "host_listings_count", "bedrooms"]].describe()
```

```text
       number_of_reviews  host_listings_count     bedrooms
count        7151.000000          7151.000000  7149.000000
mean           43.529157            52.569571     1.342565
std            72.519229           177.371652     0.932685
min             0.000000             0.000000     0.000000
25%             1.000000             1.000000     1.000000
50%            11.000000             2.000000     1.000000
75%            54.000000             8.000000     2.000000
max           677.000000          1199.000000    14.000000
```

`bedrooms` hat nur 7149 Werte. Zwei Zeilen sind leer.

```python
df[["number_of_reviews", "host_listings_count", "bedrooms"]].describe().round(2)
```

```text
       number_of_reviews  host_listings_count  bedrooms
count            7151.00              7151.00   7149.00
mean               43.53                52.57      1.34
std                72.52               177.37      0.93
min                 0.00                 0.00      0.00
25%                 1.00                 1.00      1.00
50%                11.00                 2.00      1.00
75%                54.00                 8.00      2.00
max               677.00              1199.00     14.00
```

### `groupby()`

```python
df.groupby(["neighborhood"])
```

```text
<pandas.core.groupby.generic.DataFrameGroupBy object at 0x7f3a1c2b5e10>
```

Ohne Aggregation gibt es nur ein Gruppen-Objekt, keine Zahlen.

```python
grouped_df = df.groupby(["neighborhood"])[["bedrooms"]].mean().head(10)
grouped_df
```

```text
                bedrooms
neighborhood            
Alamo Square    1.340000
Balboa Terrace  1.382979
Bayview         1.384615
Bernal Heights  1.493113
Chinatown       1.119403
Civic Center    0.833333
Cole Valley     1.513043
Cow Hollow      1.292308
Crocker Amazon  1.361702
Daly City       1.200000
```

### `reset_index()`

```python
grouped_df.columns
```

```text
Index(['bedrooms'], dtype='object')
```

`neighborhood` ist keine Spalte, sondern der Index.

```python
reset_df = grouped_df.reset_index()
reset_df
```

```text
     neighborhood  bedrooms
0    Alamo Square  1.340000
1  Balboa Terrace  1.382979
2         Bayview  1.384615
3  Bernal Heights  1.493113
4       Chinatown  1.119403
5    Civic Center  0.833333
6     Cole Valley  1.513043
7      Cow Hollow  1.292308
8  Crocker Amazon  1.361702
9       Daly City  1.200000
```

Jetzt ist `neighborhood` eine normale Spalte.

### Sortieren

```python
sorted_df = df.sort_values(["bedrooms"])
sorted_df[["id","bedrooms"]].head(10)
```

```text
            id  bedrooms
6966  32381497       0.0
6970  32384648       0.0
6978  32398307       0.0
47       41423       0.0
49       42403       0.0
56       45299       0.0
32       25662       0.0
41       39418       0.0
884    1979461       0.0
885    1984709       0.0
```

Alle zehn haben `0.0`. Die Reihenfolge innerhalb gleicher Werte ist nicht festgelegt.

```python
df["bedrooms"].sort_values()
```

```text
6966     0.0
6970     0.0
6978     0.0
47       0.0
49       0.0
        ... 
1928     7.0
2673     7.0
2543    14.0
286      NaN
6911     NaN
Name: bedrooms, Length: 7151, dtype: float64
```

`NaN` steht immer am Ende.

```python
df["bedrooms"].sort_values(ascending=False)
```

```text
2543    14.0
1928     7.0
2673     7.0
2029     6.0
2935     6.0
        ... 
7094     0.0
7099     0.0
7142     0.0
286      NaN
6911     NaN
Name: bedrooms, Length: 7151, dtype: float64
```

Auch absteigend bleibt `NaN` am Ende.

### Fehlende Werte

```python
nan_df = df[["security_deposit", "notes"]]
nan_df
```

```text
     security_deposit                          notes
0             $100.00  Due to the fact that we ha...
1                 NaN  All the furniture in the h...
2             $200.00  Please email your picture ...
3             $200.00  Please email your picture ...
4               $0.00  tax ID on file tax ID on file
...               ...                            ...
7146            $0.00                            NaN
7147          $400.00                            NaN
7148          $695.00  Please note that the unit ...
7149              NaN                            NaN
7150              NaN  - Signed lease required. -...

[7151 rows x 2 columns]
```

```python
nan_df.isna().sum()
```

```text
security_deposit    1469
notes               2744
dtype: int64
```

```python
nan_df.dropna()
```

```text
     security_deposit                          notes
0             $100.00  Due to the fact that we ha...
2             $200.00  Please email your picture ...
3             $200.00  Please email your picture ...
4               $0.00  tax ID on file tax ID on file
6               $0.00  We live in a dense, urban ...
...               ...                            ...
7136          $400.00  Incorrectly pinned on Airb...
7138        $2,000.00  Although the place is not ...
7139          $100.00  Short Term Rental Registra...
7144          $500.00  Please let us know if you ...
7148          $695.00  Please note that the unit ...

[3623 rows x 2 columns]
```

Jede Zeile mit mindestens einem `NaN` fällt weg. Es bleiben 3623 von 7151.

```python
nan_df.fillna("Missing")
```

```text
     security_deposit                          notes
0             $100.00  Due to the fact that we ha...
1             Missing  All the furniture in the h...
2             $200.00  Please email your picture ...
3             $200.00  Please email your picture ...
4               $0.00  tax ID on file tax ID on file
...               ...                            ...
7146            $0.00                        Missing
7147          $400.00                        Missing
7148          $695.00  Please note that the unit ...
7149          Missing                        Missing
7150          Missing  - Signed lease required. -...

[7151 rows x 2 columns]
```

```python
nan_df.fillna({"security_deposit": "$0.00", "notes": "Missing"}, inplace=False)
```

```text
     security_deposit                          notes
0             $100.00  Due to the fact that we ha...
1               $0.00  All the furniture in the h...
2             $200.00  Please email your picture ...
3             $200.00  Please email your picture ...
4               $0.00  tax ID on file tax ID on file
...               ...                            ...
7146            $0.00                        Missing
7147          $400.00                        Missing
7148          $695.00  Please note that the unit ...
7149            $0.00                        Missing
7150            $0.00  - Signed lease required. -...

[7151 rows x 2 columns]
```

Mit einem Dictionary bekommt jede Spalte einen eigenen Ersatzwert.

### CSV schreiben und lesen

```python
file_path = "/tmp/sf-airbnb_updated.csv"
df.to_csv(file_path, index=False)
```

Kein Ergebnis. Die Datei liegt danach unter `/tmp`.

```python
load_df = pd.read_csv(file_path)
load_df.head()
```

```text
     id                    listing_url       scrape_id last_scraped  ... calculated_host_listings_count_shared_rooms  \
0   958  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
1  5858  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
2  7918  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
3  8142  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
4  8339  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                

  reviews_per_month first_review_fmt last_review_fmt  
0              1.54       07-23-2009      02-17-2019  
1              0.93       05-03-2009      08-06-2017  
2              0.15       08-31-2009      11-21-2016  
3              0.15       09-08-2014      09-12-2018  
4              0.23       09-25-2009      08-11-2018  

[5 rows x 108 columns]
```

Jetzt 108 Spalten, weil die beiden `_fmt`-Spalten mitgespeichert wurden. Beim Einlesen sind die Datumsspalten wieder Text (`object`).

### Lab 11 – Lösungen (Kalifornien-Wohnungsdaten)

Setup wie in der Demo:

```text
%run ../Includes/Classroom-Setup-11
```

```python
print(f"Username:                           {DA.username}")
print(f"Default Catalog Name:               {DA.catalog_name}")
print(f"User Based Schema Name:             {DA.schema_name}")
```

Beispielausgabe:

```text
Username:                           labuser1234567@vocareum.com
Default Catalog Name:               dbacademy
User Based Schema Name:             labuser1234567
```

```python
spark.sql("""
SELECT
  current_catalog() AS `Current Catalog`,
  current_schema() AS `Current Schema`,
  CURRENT_USER() AS `Current User`
""").display()
```

Beispielausgabe: eine Tabellenzeile mit `dbacademy`, dem eigenen Schema und dem eigenen Benutzer.

```python
spark.sql(f"SHOW TABLES IN {DA.catalog_name}.{DA.schema_name}").display()
```

Ergebnis: Tabelle mit den Spalten `database`, `tableName` und `isTemporary`. Sie listet die Tabellen im eigenen Schema. Die CSV-Dateien liegen im Volume, nicht als Tabelle, und erscheinen hier nicht.

```python
import pandas as pd
```

```python
file_path = f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/cahousing/ca-housing.csv"
df = pd.read_csv(file_path)
```

Kein Ergebnis. `df` hat 20640 Zeilen und 9 Spalten.

```python
df.head()
df.tail()
df.info()
```

```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 20640 entries, 0 to 20639
Data columns (total 9 columns):
 #   Column      Non-Null Count  Dtype  
---  ------      --------------  -----  
 0   MedInc      20640 non-null  float64
 1   HouseAge    20640 non-null  float64
 2   AveRooms    20640 non-null  float64
 3   AveBedrms   20640 non-null  float64
 4   Population  20640 non-null  float64
 5   AveOccup    20640 non-null  float64
 6   Latitude    20640 non-null  float64
 7   Longitude   20640 non-null  float64
 8   label       20640 non-null  float64
dtypes: float64(9)
memory usage: 1.4 MB
```

Achtung: Nur `info()` erzeugt eine Ausgabe. `head()` und `tail()` stehen nicht in der letzten Zeile und werden ohne `display()` oder `print()` nicht angezeigt.

```python
df = df.rename(columns={
    "MedInc": "median_income",
    "HouseAge": "housing_median_age",
    "AveRooms": "avg_rooms",
    "AveBedrms": "avg_bedrooms",
    "AveOccup": "avg_occupancy",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "label": "median_house_value"
})
df.head()
```

```text
   median_income  housing_median_age  avg_rooms  avg_bedrooms  Population  avg_occupancy  latitude  longitude  median_house_value
0         8.3252                41.0   6.984127      1.023810       322.0       2.555556     37.88    -122.23               4.526
1         8.3014                21.0   6.238137      0.971880      2401.0       2.109842     37.86    -122.22               3.585
2         7.2574                52.0   8.288136      1.073446       496.0       2.802260     37.85    -122.24               3.521
3         5.6431                52.0   5.817352      1.073059       558.0       2.547945     37.85    -122.25               3.413
4         3.8462                52.0   6.281853      1.081081       565.0       2.181467     37.85    -122.25               3.422
```

`Population` wurde nicht umbenannt.

```python
older_housing_df = df[df["housing_median_age"] >= 40]
older_housing_df.head(10)
```

```text
    median_income  housing_median_age  avg_rooms  avg_bedrooms  Population  avg_occupancy  latitude  longitude  median_house_value
0          8.3252                41.0   6.984127      1.023810       322.0       2.555556     37.88    -122.23               4.526
2          7.2574                52.0   8.288136      1.073446       496.0       2.802260     37.85    -122.24               3.521
3          5.6431                52.0   5.817352      1.073059       558.0       2.547945     37.85    -122.25               3.413
4          3.8462                52.0   6.281853      1.081081       565.0       2.181467     37.85    -122.25               3.422
5          4.0368                52.0   4.761658      1.103627       413.0       2.139896     37.85    -122.25               2.697
6          3.6591                52.0   4.931907      0.951362      1094.0       2.128405     37.84    -122.25               2.992
7          3.1200                52.0   4.797527      1.061824      1157.0       1.788253     37.84    -122.25               2.414
8          2.0804                42.0   4.294118      1.117647      1206.0       2.026891     37.84    -122.26               2.267
9          3.6912                52.0   4.970588      0.990196      1551.0       2.172269     37.84    -122.25               2.611
10         3.2031                52.0   5.477612      1.079602       910.0       2.263682     37.85    -122.26               2.815
```

Zeile 1 fehlt, weil ihr Alter nur 21 ist.

```python
high_value_df = older_housing_df[(older_housing_df["median_income"] > 5) & (older_housing_df["median_house_value"] > 3.0)]
high_value_df.head(10)
```

```text
     median_income  housing_median_age  avg_rooms  avg_bedrooms  Population  avg_occupancy  latitude  longitude  median_house_value
0           8.3252                41.0   6.984127      1.023810       322.0       2.555556     37.88    -122.23               4.526
2           7.2574                52.0   8.288136      1.073446       496.0       2.802260     37.85    -122.24               3.521
3           5.6431                52.0   5.817352      1.073059       558.0       2.547945     37.85    -122.25               3.413
118         5.8596                50.0   6.742627      1.069705       970.0       2.600536     37.84    -122.23               3.276
119         5.2868                47.0   6.546392      0.936082      1098.0       2.263918     37.84    -122.23               3.476
120         5.9560                41.0   6.851064      1.079787       794.0       2.111702     37.83    -122.24               3.661
122         6.3434                52.0   6.947891      1.019851      1061.0       2.632754     37.85    -122.23               3.736
123         5.1773                52.0   6.358559      1.034234      1177.0       2.120721     37.84    -122.24               3.895
124         7.2354                52.0   7.117166      0.994550       901.0       2.455041     37.85    -122.24               3.911
128         7.5544                40.0   7.631498      1.030581      1616.0       2.470948     37.83    -122.21               4.115
```

```python
print(df["Population"].mean())
print(df["Population"].min())
print(df["Population"].max())
```

```text
1425.4767441860465
3.0
35682.0
```

```python
print(df[["median_income", "median_house_value"]].describe().round(2))

true_df = df[["median_income", "median_house_value"]].copy()
true_df["median_income"] = true_df["median_income"] * 10_000
true_df["median_house_value"] = true_df["median_house_value"] * 100_000
true_df.describe().round(0)
```

```text
       median_income  median_house_value
count       20640.00            20640.00
mean            3.87                2.07
std             1.90                1.15
min             0.50                0.15
25%             2.56                1.20
50%             3.53                1.80
75%             4.74                2.65
max            15.00                5.00
```

```text
       median_income  median_house_value
count        20640.0             20640.0
mean         38707.0            206856.0
std          18998.0            115396.0
min           4999.0             14999.0
25%          25634.0            119600.0
50%          35348.0            179700.0
75%          47432.0            264725.0
max         150001.0            500001.0
```

Die erste Tabelle kommt von `print()`, die zweite ist die letzte Zeile. Im Datensatz ist das Einkommen in 10.000 $ und der Hauswert in 100.000 $ angegeben. Nach dem Skalieren sieht man echte Dollarbeträge.

```python
df["age_category"] = pd.cut(df["housing_median_age"], bins=[0, 20, 40, 52], labels=["Young", "Mid", "Old"])

grouped_df = df.groupby(["age_category"], observed=True)[["median_house_value"]].mean().round(2).reset_index()
grouped_df
```

```text
  age_category  median_house_value
0        Young                1.93
1          Mid                2.07
2          Old                2.29
```

`pd.cut()` teilt das Alter in die Bereiche 0–20, 21–40 und 41–52 ein.

```python
sorted_df = grouped_df.sort_values("median_house_value", ascending=False)
sorted_df
```

```text
  age_category  median_house_value
2          Old                2.29
1          Mid                2.07
0        Young                1.93
```

Antwort auf die Lab-Frage: Die ältesten Wohnblöcke haben im Schnitt den höchsten Hauswert.

```python
print(df["avg_bedrooms"].isna().sum())

clean_df = df.fillna({"avg_bedrooms": df["avg_bedrooms"].median()})

print(clean_df["avg_bedrooms"].isna().sum())
```

```text
0
0
```

In diesem Datensatz fehlen keine Werte. Beide Zählungen sind `0`. Gäbe es Lücken, stünde oben deren Anzahl und unten `0`.

```python
final_df = (
    df[df["median_income"] > 3]
    .groupby(["age_category"])[["median_house_value"]]
    .mean().round(0)
    .sort_values("median_house_value", ascending=False)
    .reset_index()
)
final_df
```

```text
  age_category  median_house_value
0          Old                 3.0
1        Young                 2.0
2          Mid                 2.0
```

`round(0)` rundet auf ganze Einheiten (also 100.000 $). Dadurch sehen Young und Mid gleich aus. pandas zeigt zusätzlich eine `FutureWarning`, weil `observed` hier nicht gesetzt ist.

---

## Modul 12 – Datenvisualisierung

### Setup

```text
%run ../Includes/Classroom-Setup-12
```

```python
print(f"Username:                           {DA.username}")
print(f"Default Catalog Name:               {DA.catalog_name}")
print(f"User Based Schema Name:             {DA.schema_name}")
```

Beispielausgabe:

```text
Username:                           labuser1234567@vocareum.com
Default Catalog Name:               dbacademy
User Based Schema Name:             labuser1234567
```

```python
spark.sql("""
SELECT
  current_catalog() AS `Current Catalog`,
  current_schema() AS `Current Schema`,
  CURRENT_USER() AS `Current User`
""").display()
```

Beispielausgabe: eine Tabellenzeile mit Catalog, Schema und Benutzer.

```python
spark.sql(f"SHOW TABLES IN {DA.catalog_name}.{DA.schema_name}").display()
```

Ergebnis: Tabelle mit `database`, `tableName`, `isTemporary` für das eigene Schema.

### Daten laden

```python
import pandas as pd
```

```python
file_path = f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv"
df = pd.read_csv(file_path)
df.head(3)
```

```text
     id                    listing_url       scrape_id last_scraped  ... calculated_host_listings_count_entire_homes  \
0   958  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
1  5858  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
2  7918  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                

  calculated_host_listings_count_private_rooms calculated_host_listings_count_shared_rooms reviews_per_month  
0                              0                                            0                           1.54  
1                              0                                            0                           0.93  
2                              9                                            0                           0.15  

[3 rows x 106 columns]
```

### `display()`

```python
display(df)
```

Ergebnis: Eine interaktive Tabelle mit allen 7151 Zeilen und 106 Spalten. Man kann sortieren, filtern und über `+` eine Visualisierung anlegen.

```python
display(df)
```

Ergebnis mit der Einstellung Bar, X = `neighbourhood`, Y = `bedrooms`, Aggregation Average: ein Balkendiagramm mit 55 Stadtteilen. Die höchsten Werte haben Sea Cliff (≈ 2,33), Japantown (2,0) und Forest Hill (≈ 1,73).

![Balkendiagramm: durchschnittliche Schlafzimmer pro Stadtteil](Zusammenfassung_Bilder/12-1_display_bar.png)

### Histogramm

```python
df["bedrooms"].hist()
```

![Histogramm bedrooms](Zusammenfassung_Bilder/12-1_hist_bedrooms.png)

Die meisten Unterkünfte haben 0 bis 2 Schlafzimmer. Standard sind 10 Bins.

```python
df["bedrooms"].hist(bins=20)
```

![Histogramm bedrooms mit 20 Bins](Zusammenfassung_Bilder/12-1_hist_bedrooms_20bins.png)

Mit 20 Bins ist die Verteilung feiner.

### Box-Plot

```python
df.boxplot(["bedrooms", "bathrooms"])
```

![Boxplot bedrooms und bathrooms](Zusammenfassung_Bilder/12-1_boxplot.png)

Die Boxen sind schmal: Die mittleren 50 % liegen bei 1 bis 2. Die Kreise sind Ausreißer, ganz oben je ein Wert mit 14.

### Seaborn

```python
import seaborn as sns
```

Kein Ergebnis.

```python
sns.scatterplot(data=df, x="bedrooms", y="bathrooms")
```

![Streudiagramm bedrooms vs. bathrooms](Zusammenfassung_Bilder/12-1_scatter.png)

```python
sns.regplot(data=df, x="bedrooms", y="bathrooms")
```

![Regressionsdiagramm bedrooms vs. bathrooms](Zusammenfassung_Bilder/12-1_regplot.png)

Die Linie steigt. Mehr Schlafzimmer gehen mit mehr Badezimmern einher.

### Pearson-Korrelation

Muster:

```python
from scipy import stats

r_value, p_value = stats.pearsonr(df["x_column"], df["y_column"])
```

Mit den Platzhaltern `x_column`/`y_column` kommt ein `KeyError`. Es geht nur um die Form des Aufrufs.

```python
from scipy import stats

clean_df = df[["bedrooms", "bathrooms"]].dropna()

r_value, p_value = stats.pearsonr(clean_df["bedrooms"], clean_df["bathrooms"])

print(f"Pearson correlation coefficient (r): {r_value:.4f}")
print(f"P-value: {p_value:.2e}")
print(f"\nInterpretation: {'Strong' if abs(r_value) >= 0.7 else 'Moderate' if abs(r_value) >= 0.4 else 'Weak'} {'positive' if r_value > 0 else 'negative'} linear relationship")
```

```text
Pearson correlation coefficient (r): 0.4121
P-value: 2.22e-290

Interpretation: Moderate positive linear relationship
```

`dropna()` ist nötig, weil `pearsonr` keine `NaN` verträgt.

### Lab 12 – Lösungen

Setup wie in der Demo (`%run ../Includes/Classroom-Setup-12`, `DA`-Ausgabe, `current_catalog()`, `SHOW TABLES`), mit denselben Ergebnissen.

```python
import pandas as pd
import seaborn as sns

sns.set(rc = {"figure.figsize": (15,8)})
```

Kein Ergebnis. Alle folgenden Seaborn-Plots werden 15 × 8 Zoll groß.

```python
file_path = f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/cahousing/ca-housing.csv"
df = pd.read_csv(file_path)
```

Kein Ergebnis.

```python
df = pd.read_csv(csv_path)
```

```text
NameError: name 'csv_path' is not defined
```

Diese Zelle ist ein Rest im Kurs-Notebook. Die Variable heißt `file_path`. Die Zelle kann man überspringen, `df` ist schon geladen.

```python
display(df)
```

Ergebnis mit der Einstellung Bar, X = `HouseAge`, Y = `Population`, Aggregation Sum:

![Balkendiagramm: Summe Population pro HouseAge](Zusammenfassung_Bilder/12-2_display_bar.png)

Der höchste Balken ist bei 52 Jahren (≈ 1,19 Mio.). 52 ist der Maximalwert im Datensatz, ältere Blöcke werden dort gesammelt.

```python
df["Population"].hist()
```

![Histogramm Population](Zusammenfassung_Bilder/12-2_hist_population.png)

Fast alles liegt im ersten Bin. Ein paar extreme Werte bis 35682 strecken die Achse.

```python
df["Population"].hist(bins=50)
```

![Histogramm Population mit 50 Bins](Zusammenfassung_Bilder/12-2_hist_population_50bins.png)

```python
df.boxplot(["AveRooms", "AveBedrms"])
```

![Boxplot AveRooms und AveBedrms](Zusammenfassung_Bilder/12-2_boxplot.png)

Beide Boxen sind flach. Es gibt starke Ausreißer nach oben.

```python
sns.scatterplot(
    data=df, 
    x="Longitude", 
    y="Latitude", 
    hue="MedInc", 
    palette="viridis")
```

![Streudiagramm Längen- und Breitengrad nach Einkommen](Zusammenfassung_Bilder/12-2_scatter_lat_lon.png)

Die Punkte bilden die Umrisse Kaliforniens. Hohe Einkommen (gelb/grün) liegen an der Küste um San Francisco und Los Angeles.

```python
sns.regplot(data=df, x="MedInc", y="label")
```

![Regressionsdiagramm MedInc vs. label](Zusammenfassung_Bilder/12-2_regplot.png)

Die Linie steigt deutlich. Die waagerechte Punktreihe oben bei 5.0 ist die Kappung des Hauswerts.

```python
from scipy import stats

r_value, p_value = stats.pearsonr(df["MedInc"], df["label"])

print(f"Pearson correlation coefficient (r): {r_value:.4f}")
print(f"P-value: {p_value:.2e}")

if r_value < 0:
    strength = "Negative"
elif 0.90 <= r_value <= 1.00:
    strength = "Very strong"
elif 0.70 <= r_value < 0.90:
    strength = "Strong"
elif 0.40 <= r_value < 0.70:
    strength = "Moderate"
elif 0.20 <= r_value < 0.40:
    strength = "Weak"
else:
    strength = "None or very weak"

print(f"Strength of relationship: {strength}")
```

```text
Pearson correlation coefficient (r): 0.6881
P-value: 0.00e+00
Strength of relationship: Moderate
```

Der p-Wert ist so klein, dass er als `0.00e+00` erscheint.

---

## Modul 13 – pandas mit Spark skalieren

### Setup

```text
%run ../Includes/Classroom-Setup-13
```

`DA`-Ausgabe, `current_catalog()` und `SHOW TABLES` liefern dasselbe wie in Modul 11 und 12.

### Lesen mit PySpark

```python
spark_df = spark.read.csv(f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv", header="true", inferSchema="true", multiLine="true", escape='"')
display(spark_df)
```

Ergebnis: Eine interaktive Tabelle mit 7151 Zeilen und 106 Spalten. Die Ausgabe zeigt auch das Schema mit den erkannten Typen. `multiLine` und `escape` sind nötig, weil Beschreibungen Zeilenumbrüche und Anführungszeichen enthalten.

### Lesen mit pandas

```python
import pandas as pd

pandas_df = pd.read_csv(f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv")
pandas_df.head()
```

```text
     id                    listing_url       scrape_id last_scraped  ... calculated_host_listings_count_entire_homes  \
0   958  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
1  5858  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              1                
2  7918  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
3  8142  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              0                
4  8339  https://www.airbnb.com/roo...  20190306152813   2019-03-06  ...                              2                

  calculated_host_listings_count_private_rooms calculated_host_listings_count_shared_rooms reviews_per_month  
0                              0                                            0                           1.54  
1                              0                                            0                           0.93  
2                              9                                            0                           0.15  
3                              9                                            0                           0.15  
4                              0                                            0                           0.23  

[5 rows x 106 columns]
```

### Lesen mit der pandas-API auf Spark

```python
import pyspark.pandas as ps

df = ps.read_csv(f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv", inferSchema=True, multiLine=True, escape='"')
df.head()
```

Ergebnis: Dieselben ersten 5 Zeilen wie bei pandas (`id` 958, 5858, 7918, 8142, 8339). Die Syntax ist pandas, die Arbeit macht aber Spark verteilt. Dazu kann eine Warnung zum Default-Index erscheinen.

### Index-Typ

```python
ps.set_option("compute.default_index_type", "distributed-sequence")

df_dist_sequence = ps.read_csv(f"/Volumes/{DA.catalog_name}/{DA.schema_name}/datasets/airbnb/sf-airbnb.csv", inferSchema="true", multiLine="true", escape='"')
df_dist_sequence.head()
```

Ergebnis: Wieder dieselben 5 Zeilen mit Index 0 bis 4. Der Index ist fortlaufend, wird aber verteilt berechnet.

### Konvertieren

```python
df = ps.DataFrame(spark_df)
display(df)
```

Ergebnis: Dieselbe Tabelle wie oben, jetzt als pandas-on-Spark-DataFrame.

```python
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pyspark.pandas")

df = spark_df.pandas_api()
display(df)
```

Ergebnis: Dieselbe Tabelle. `pandas_api()` ist der kürzere Weg. Die Index-Warnung ist unterdrückt.

```python
display(df.to_spark())
```

Ergebnis: Dieselben Daten, wieder als PySpark-DataFrame. Der pandas-Index geht dabei verloren.

### Value Counts

```python
display(spark_df.groupby("property_type").count().orderBy("count", ascending=False))
```

Ergebnis als Tabelle mit den Spalten `property_type` und `count` (26 Zeilen):

```text
property_type        count
Apartment             3013
House                 1990
Condominium            762
Guest suite            496
Boutique hotel         183
Townhouse              140
Serviced apartment     116
Hotel                  100
Loft                    93
Hostel                  87
Guesthouse              44
Bed and breakfast       29
Other                   22
Aparthotel              20
Bungalow                17
Villa                   10
Cottage                  8
Resort                   8
Cabin                    3
Tiny house               3
Boat                     2
Timeshare                1
In-law                   1
Treehouse                1
Castle                   1
Earth house              1
```

Bei gleicher Anzahl kann die Reihenfolge abweichen.

```python
df["property_type"].value_counts()
```

```text
Apartment             3013
House                 1990
Condominium            762
Guest suite            496
Boutique hotel         183
Townhouse              140
Serviced apartment     116
Hotel                  100
Loft                    93
Hostel                  87
Guesthouse              44
Bed and breakfast       29
Other                   22
Aparthotel              20
Bungalow                17
Villa                   10
Cottage                  8
Resort                   8
Cabin                    3
Tiny house               3
Boat                     2
Timeshare                1
In-law                   1
Treehouse                1
Castle                   1
Earth house              1
Name: count, dtype: int64
```

Gleiche Zahlen, aber in pandas-Syntax und als Series.

### Visualisierung

Muster, um das Zeilenlimit für Plots zu ändern:

```python
ps.set_option("plotting.max_rows", <new_value>)
```

```python
df["bedrooms"].hist(bins=20)
```

![Histogramm bedrooms mit 20 Bins](Zusammenfassung_Bilder/13-1_hist_bedrooms.png)

In Databricks erscheint das Histogramm interaktiv (plotly). Die Verteilung ist dieselbe wie in Modul 12.

### SQL auf einem pandas-on-Spark-DataFrame

```python
ps.sql("SELECT distinct(property_type) FROM {df}", df=df)
```

Ergebnis: Ein DataFrame mit einer Spalte `property_type` und 26 Zeilen, je eine pro Unterkunftstyp (Apartment, House, Condominium, Guest suite … Castle, Earth house). Die Reihenfolge ist nicht festgelegt.

---

## Modul 14 – Cloud Computing

```sql
%sql SHOW CATALOGS
```

Ergebnis: Tabelle mit der Spalte `catalog`. Sie listet alle Catalogs, auf die man Zugriff hat, z. B. `dbacademy`, `samples`, `system`.

```sql
%sql SHOW SCHEMAS IN samples
```

Ergebnis: Tabelle mit der Spalte `databaseName`. Sie listet die Beispiel-Schemas, darunter `nyctaxi` und `tpch`.

```sql
%sql SHOW TABLES IN samples.tpch
```

```text
database | tableName | isTemporary
tpch     | customer  | false
tpch     | lineitem  | false
tpch     | nation    | false
tpch     | orders    | false
tpch     | part      | false
tpch     | partsupp  | false
tpch     | region    | false
tpch     | supplier  | false
```

Das sind die acht Tabellen des TPC-H-Benchmarks.

---

## Modul 15 – Weitere Ressourcen

Dieses Modul enthält keinen Code.
