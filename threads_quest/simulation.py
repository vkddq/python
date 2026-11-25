"""Навчальна симуляція. Запуск: python simulation.py або з --unsafe."""
import random
import sys
import threading
import time


class Warehouse:
    def __init__(self, name, meds, price_per_unit):
        self.name = name
        self.meds = meds
        self.initial_meds = meds
        self.price_per_unit = price_per_unit
        self.lock = threading.Lock()

    def steal(self, amount, unsafe=False):
        """У безпечній версії Runner викликає цей метод усередині lock."""
        event = random.random()
        if event < 0.15:
            return 0, True  # Спіймали: цього разу нічого не взяв.
        if event < 0.35:
            amount = random.randint(0, amount)  # Частину вантажу не вдалося взяти.

        if self.meds <= 0:
            return 0, False
        taken = min(amount, self.meds)
        if unsafe:
            # Навмисна помилка: інший потік може змінити meds за цей час.
            time.sleep(0.001)
        self.meds -= taken
        return taken, False


class Runner(threading.Thread):
    def __init__(self, warehouse, name, use_lock=True):
        super().__init__(name=name)
        self.warehouse = warehouse
        self.use_lock = use_lock
        self.stolen = 0
        self.profit = 0
        self.caught = 0
        self.progress = 0

    def attempt(self, amount):
        taken, caught = self.warehouse.steal(amount, unsafe=not self.use_lock)
        self.stolen += taken
        self.profit += taken * self.warehouse.price_per_unit
        self.caught += int(caught)

    def run(self):
        for attempt_number in range(1, 11):
            amount = random.randint(10, 30)
            if self.use_lock:
                # Перевірка запасу, списання та розрахунок — одна критична секція.
                with self.warehouse.lock:
                    self.attempt(amount)
            else:
                self.attempt(amount)
            self.progress = attempt_number
            if attempt_number < 10:
                time.sleep(random.uniform(0.1, 0.5))


def show_progress(runners):
    bars = []
    for index, runner in enumerate(runners, start=1):
        bar = '#' * runner.progress + '-' * (10 - runner.progress)
        bars.append(f'B{index}[{bar}]{runner.progress}/10')
    print('\r' + ' '.join(bars), end='', flush=True)


def check_invariants(warehouses, runners):
    for warehouse in warehouses:
        stolen = sum(runner.stolen for runner in runners if runner.warehouse is warehouse)
        assert warehouse.meds >= 0, f'Інваріант 1: {warehouse.name}, залишок {warehouse.meds}'
        assert warehouse.initial_meds == warehouse.meds + stolen, (
            f'Інваріант 2: {warehouse.name}, було {warehouse.initial_meds}, '
            f'залишилось {warehouse.meds}, взяли {stolen}'
        )
    expected_profit = sum(
        (warehouse.initial_meds - warehouse.meds) * warehouse.price_per_unit
        for warehouse in warehouses
    )
    actual_profit = sum(runner.profit for runner in runners)
    assert actual_profit == expected_profit, (
        f'Інваріант 3: прибуток {actual_profit}, очікувалось {expected_profit}'
    )


def simulate(use_lock=True, display=True):
    warehouses = [Warehouse(f'Склад {index + 1}', random.randint(100, 300), 10)
                  for index in range(3)]
    # Два бігуни ділять перший склад, два — другий, один — третій.
    runners = [Runner(warehouses[index % 3], f'Бігун {index + 1}', use_lock)
               for index in range(5)]
    for runner in runners:
        runner.start()
    while display and any(runner.is_alive() for runner in runners):
        show_progress(runners)
        time.sleep(0.1)
    for runner in runners:
        runner.join()
    if display:
        show_progress(runners)
        print()
        for warehouse in warehouses:
            stolen = sum(runner.stolen for runner in runners if runner.warehouse is warehouse)
            print(f'{warehouse.name}: було {warehouse.initial_meds}, '
                  f'залишилось {warehouse.meds}, взяли {stolen}')
        for runner in runners:
            print(f'{runner.name}: взяв {runner.stolen}, прибуток {runner.profit} грн, '
                  f'спіймали {runner.caught} разів')
        print(f'Загальний прибуток: {sum(runner.profit for runner in runners)} грн')
    return warehouses, runners


def run_checks(use_lock, count=100):
    failures = 0
    first_failure = None
    for run_number in range(1, count + 1):
        warehouses, runners = simulate(use_lock, display=False)
        try:
            check_invariants(warehouses, runners)
        except AssertionError as error:
            failures += 1
            if first_failure is None:
                first_failure = run_number
            print(f'Прогін {run_number}: {error}', flush=True)
        else:
            print(f'Прогін {run_number}: OK', flush=True)
    print(f'Lock={use_lock}: перевірено {count}, порушень {failures}, '
          f'перший невдалий прогін: {first_failure}')
    return failures


def main():
    use_lock = '--unsafe' not in sys.argv
    if '--check' in sys.argv:
        failures = run_checks(use_lock)
        if use_lock and failures:
            raise SystemExit(1)
        return
    for run_number in range(1, 4):
        print(f'\nПрогін {run_number}. Lock: {"увімкнено" if use_lock else "ВИМКНЕНО"}')
        warehouses, runners = simulate(use_lock)
        try:
            check_invariants(warehouses, runners)
            print('Інваріанти: OK')
        except AssertionError as error:
            print(f'ПОМИЛКА на прогоні {run_number}: {error}')


if __name__ == '__main__':
    main()
