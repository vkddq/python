from functools import wraps
from math import isfinite


def get_amount(line):
    if not isinstance(line, str):
        return None
    parts = line.split()
    if len(parts) != 2 or parts[0] not in ('payment', 'refund', 'transfer'):
        return None
    try:
        amount = float(parts[1])
    except ValueError:
        return None
    if not isfinite(amount):
        return None
    return amount


def shadow(limit=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            generator = func(*args, **kwargs)
            total = 0
            warned = False
            while True:
                try:
                    line = next(generator)
                except StopIteration as result:
                    return result.value
                amount = get_amount(line)
                if amount is None:
                    continue
                total += amount
                print(line)
                if total > limit and not warned:
                    print('Тіньовий ліміт перевищено. Активую схему')
                    warned = True
                yield line
        return wrapper
    return decorator


def suspicious_counter(threshold=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            generator = func(*args, **kwargs)
            count = 0
            suspicious_total = 0
            while True:
                try:
                    line = next(generator)
                except StopIteration as result:
                    if count > 0:
                        print(f'Підозрілих операцій: {count}; їх сума: {suspicious_total:g}')
                    return result.value
                amount = get_amount(line)
                if amount is None:
                    continue
                if amount > threshold:
                    count += 1
                    suspicious_total += amount
                    print(f'Підозріла операція: сума {amount:g} перевищує {threshold:g}')
                yield line
        return wrapper
    return decorator


def transactions(lines):
    total = 0
    for line in lines:
        amount = get_amount(line)
        if amount is None:
            continue
        total += amount
        yield line
    return total


@suspicious_counter(threshold=250)
@shadow(limit=200)
def watched_transactions(lines):
    total = yield from transactions(lines)
    return total


if __name__ == '__main__':
    lines = ['payment 120', 'refund 50', 'transfer 300', 'wrong', 'payment error']
    generator = watched_transactions(lines)
    while True:
        try:
            next(generator)
        except StopIteration as result:
            print(f'Фінальна сума: {result.value:g}')
            break
