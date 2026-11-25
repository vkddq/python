from dataclasses import dataclass, field
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


@dataclass
class Item:
    name: str
    category: str
    quantity: int
    value: float
    condition: Condition
    location: str

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
        return [item for item in self.items if item.category == category]

    def total_inventory_value(self):
        return sum(item.total_value() for item in self.items)


def load(f):
    inventory = Inventory()
    with open(f, encoding="utf-8") as source:
        for line in source:
            fields = line.strip().split(";")
            inventory.add_item(
                Item(
                    fields[0], fields[1], int(fields[2]), float(fields[3]),
                    Condition(fields[4]), fields[5],
                )
            )
    return inventory


def zvit(f):
    inventory = load(f)
    print("Барахла:", len(inventory.items))
    for item in sorted(inventory.items, key=lambda item: item.location):
        print(item.location, "|", item.name, "|", item.quantity, "шт |", round(item.total_value(), 2))
    print("Разом:", round(inventory.total_inventory_value(), 2))


if __name__ == "__main__":
    zvit("barakhlo.csv")
