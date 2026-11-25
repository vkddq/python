from dataclasses import dataclass
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


rich = []


def load(f):
    with open(f, encoding="utf-8") as source:
        for line in source:
            fields = line.strip().split(";")
            add(fields[0], fields[1], int(fields[2]), float(fields[3]), fields[4], fields[5])


def add(n, c, q, v, s, loc):
    rich.append(Item(n, c, q, v, Condition(s), loc))


def zvit(f):
    load(f)
    total = sum(item.total_value() for item in rich)
    print("Барахла:", len(rich))
    for item in sorted(rich, key=lambda item: item.location):
        print(item.location, "|", item.name, "|", item.quantity, "шт |", round(item.total_value(), 2))
    print("Разом:", round(total, 2))


if __name__ == "__main__":
    zvit("barakhlo.csv")
