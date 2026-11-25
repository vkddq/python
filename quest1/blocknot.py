import csv
from dataclasses import dataclass, field, fields
from datetime import date
from enum import Enum


class Condition(Enum):
    NEW = "новий"
    USED = "уживаний"
    BROKEN = "зламаний"


NEW_MULTIPLIER = 1
USED_MULTIPLIER = 0.7
BROKEN_MULTIPLIER = 0.2

CONDITION_MULTIPLIERS = {
    Condition.NEW: NEW_MULTIPLIER,
    Condition.USED: USED_MULTIPLIER,
    Condition.BROKEN: BROKEN_MULTIPLIER,
}


@dataclass(order=True)
class Item:
    # Порядок порівняння: category, value. Решта полів не є ключами сортування.
    name: str = field(compare=False)
    category: str
    quantity: int = field(compare=False)
    value: float
    condition: Condition = field(compare=False)
    location: str = field(compare=False)
    added_on: date = field(default_factory=date.today, compare=False)

    def __eq__(self, other):
        # Різні речі з однаковою категорією і ціною не стають рівними.
        # Дата не впливає ані на рівність, ані на порядок.
        if not isinstance(other, Item):
            return NotImplemented
        return self._identity() == other._identity()

    def _identity(self):
        return (self.name, self.category, self.quantity, self.value,
                self.condition, self.location)

    def total_value(self):
        return self.quantity * self.value * CONDITION_MULTIPLIERS[self.condition]

    def __str__(self):
        return (
            f"[{self.category}] {self.name} ({self.quantity} шт.) - "
            f"{self.value} грн/шт, стан: {self.condition.value}"
        )


@dataclass
class Inventory:
    items: list[Item] = field(default_factory=list)

    def __post_init__(self):
        initial_items = list(self.items)
        self.items = []
        for item in initial_items:
            self.add_item(item)

    def add_item(self, item):
        if any(existing.name == item.name for existing in self.items):
            raise ValueError(f"Duplicate item name: {item.name}")
        self.items.append(item)

    def remove_item(self, name):
        for index, item in enumerate(self.items):
            if item.name == name:
                return self.items.pop(index)
        raise KeyError(name)

    def find_by_category(self, category):
        return self.filter_items(category=category)

    def total_inventory_value(self):
        return sum(item.total_value() for item in self.items)

    def filter_items(self, **criteria):
        """Точна відповідність усім полям; невідоме ім'я — помилка."""
        valid_fields = {f.name for f in fields(Item)}
        unknown = criteria.keys() - valid_fields
        if unknown:
            raise ValueError(f"Невідомі поля: {', '.join(sorted(unknown))}")
        return [item for item in self.items
                if all(getattr(item, name) == value for name, value in criteria.items())]

    def sorted_items(self):
        return sorted(self.items)

    def export_summary(self):
        """Кількість фізичних штук у кожній категорії."""
        summary = {}
        for item in self.items:
            summary[item.category] = summary.get(item.category, 0) + item.quantity
        return summary

    def save_to_csv(self, path):
        """Без заголовка: шість старих стовпців та ISO-дата."""
        with open(path, 'w', encoding='utf-8', newline='') as target:
            writer = csv.writer(target, delimiter=';')
            for item in self.items:
                writer.writerow([item.name, item.category, item.quantity, item.value,
                                 item.condition.value, item.location, item.added_on.isoformat()])

    @classmethod
    def load_from_csv(cls, path):
        inventory = cls()
        with open(path, encoding='utf-8', newline='') as source:
            for row in csv.reader(source, delimiter=';'):
                if len(row) not in (6, 7):
                    raise ValueError('CSV має містити 6 або 7 стовпців')
                inventory.add_item(Item(
                    name=row[0], category=row[1], quantity=int(row[2]),
                    value=float(row[3]), condition=Condition(row[4]), location=row[5],
                    added_on=date.fromisoformat(row[6]) if len(row) == 7 else date.today(),
                ))
        return inventory


def load(f):
    return Inventory.load_from_csv(f)


def zvit(f):
    inventory = load(f)
    print("Барахла:", len(inventory.items))
    for item in sorted(inventory.items, key=lambda item: item.location):
        print(item.location, "|", item.name, "|", item.quantity, "шт |", round(item.total_value(), 2))
    print("Разом:", round(inventory.total_inventory_value(), 2))


if __name__ == "__main__":
    zvit("barakhlo.csv")
