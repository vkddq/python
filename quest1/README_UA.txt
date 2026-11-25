Розбір старих завалів — файли для здачі

Потрібен Python 3.10 або новіший. Сама програма використовує лише стандартну
бібліотеку. Для тестів потрібен pytest, як у лекції тижня 7.
Початкову версію перевірено на Python 3.14.0.
Відкрийте термінал у цій папці (після розпакування архіву — у quest1).

Одноразове встановлення інструмента тестування:
    python -m pip install -r requirements-dev.txt

Повна перевірка старого коду, двох кроків і нової версії:
    python verify.py

Запуск старого формату звіту новою програмою:
    python blocknot.py

Тільки фінальні тести:
    python -m pytest -v

Для скріншота: покажіть команду, рядки PASSED та підсумок passed.
Додатковий скрін python verify.py покаже перевірки всіх версій.

Структура
original/blocknot.py — незмінний початковий код.
barakhlo.csv — незмінні вхідні дані.
golden/report.txt — реальний вивід старої програми.
tests/test_golden.py — незмінний тест тексту звіту.
tests/test_golden_pytest.py — новий еквівалент на pytest з тим самим еталоном.
pytest.ini — налаштування пошуку нових тестів; історичний тест запускає verify.py.
requirements-dev.txt — залежність для тестів.
stages/01_item.py — перший крок: Item, Enum, коефіцієнти.
stages/02_inventory.py — другий крок: Inventory, незалежне завантаження.
blocknot.py — завершений код з усіма новими можливостями.
tests/test_features.py — окремі перевірки поведінки й нових можливостей.
evidence — журнали справжніх запусків та початкові SHA256.
REPORT_UA.txt — запахи коду, рішення, межі та чесний опис роботи помічника.
DEFENSE_UA.txt — пояснення простими словами для захисту.
verify.py — відтворює перевірки, не перезаписує еталон чи тест.

Приклад використання в Python з цієї папки:
    from blocknot import Inventory, Condition
    stock = Inventory.load_from_csv('barakhlo.csv')
    print(stock.export_summary())
    for thing in stock.filter_items(condition=Condition.USED):
        print(thing)
    for thing in stock.sorted_items():
        print(thing)
    stock.save_to_csv('saved_inventory.csv')
    restored = Inventory.load_from_csv('saved_inventory.csv')

Summary для наданого CSV: інструменти 11 шт., електроніка 5 шт.,
металобрухт 13 шт. Сума з урахуванням стану — 1563.7.
Історична перевірка: 12 unittest-тестів пройшли до переходу на pytest.
Нові тести розділено за поведінкою та використано parametrize, тому їх більше.
Це не означає, що в програмі додано нові можливості.
Перевірки pytest ще не запускалися: тут немає встановленого pytest, а мережа
для його встановлення недоступна. Старі журнали не є доказом запуску pytest.
Після встановлення виконайте python verify.py та перевірте його підсумок.
Не запускайте стару програму двічі в одному процесі як нову модель:
її дефект накопичення навмисно збережено в original.
