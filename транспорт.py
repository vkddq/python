from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: float) -> float:
        pass

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float:
        pass

    @abstractmethod
    def info(self) -> str:
        pass

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        return self.fuel_consumption(distance) * price_per_unit


class Car(Transport):
    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.07

    def info(self) -> str:
        return f"Автомобіль {self.name}"


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)
        if passengers > capacity:
            raise ValueError("Перевантажено!")
        self.passengers = passengers

    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.15

    def info(self) -> str:
        return f"Автобус {self.name} ({self.passengers}/{self.capacity} місць)"


class Bicycle(Transport):
    def __init__(self, name: str, speed: int, capacity: int):
        actual_speed = min(speed, 20)
        super().__init__(name, actual_speed, capacity)

    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return 0.0

    def info(self) -> str:
        return f"Велосипед {self.name} (швидкість обмежена: {self.speed} км/год)"


class ElectricCar(Car):
    def battery_usage(self, distance: float) -> float:
        return distance * 0.2

    def fuel_consumption(self, distance: float) -> float:
        return 0.0

    def info(self) -> str:
        return f"Електрокар {self.name}"


if __name__ == "__main__":
    fleet = [
        Car("Toyota", 110, 5),
        Bus("Ikarus", 70, 40, passengers=35),
        Bicycle("Kellys", 35, 1),
        ElectricCar("Tesla", 130, 4)
    ]

    distance_km = 100
    print(f"--- Розрахунок на {distance_km} км ---")
    
    for vehicle in fleet:
        print(f"[{vehicle.info()}]")
        print(f"Час у дорозі: {vehicle.move(distance_km):.2f} год")
        print(f"Витрати пального: {vehicle.fuel_consumption(distance_km):.2f} од.")
        print("-" * 30)