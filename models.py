from abc import ABC, abstractmethod

class Medicine(ABC):
    def __init__(self, name: str, quantity: int, price: float):
        if not isinstance(name, str):
            raise TypeError("Name має бути рядком")
        if not isinstance(quantity, int):
            raise TypeError("Quantity має бути цілим числом")
        if not isinstance(price, (int, float)):
            raise TypeError("Price має бути числом")
            
        self.name = name
        self.quantity = quantity
        self.price = float(price)

    @abstractmethod
    def requires_prescription(self) -> bool:
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        pass

    def total_price(self) -> float:
        return self.quantity * self.price

    @abstractmethod
    def info(self) -> str:
        pass


class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8–15°C, темне місце"

    def info(self) -> str:
        return f"Антибіотик '{self.name}' | Рецепт: {self.requires_prescription()} | Зберігання: {self.storage_requirements()} | Сума: {self.total_price():.2f}"


class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15–25°C, сухо"

    def info(self) -> str:
        return f"Вітаміни '{self.name}' | Рецепт: {self.requires_prescription()} | Зберігання: {self.storage_requirements()} | Сума: {self.total_price():.2f}"


class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2–8°C, холодильник"

    def total_price(self) -> float:
        base_price = super().total_price()
        return base_price * 1.10

    def info(self) -> str:
        return f"Вакцина '{self.name}' | Рецепт: {self.requires_prescription()} | Зберігання: {self.storage_requirements()} | Сума: {self.total_price():.2f}"