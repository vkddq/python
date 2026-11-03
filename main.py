from models import Antibiotic, Vitamin, Vaccine

def print_medicines_info(meds_list: list):
    for med in meds_list:
        print(med.info())

if __name__ == "__main__":
    pharmacy_inventory = [
        Antibiotic("Пеніцилін", 50, 12.5),
        Vitamin("Аскорбінка", 100, 5.0),
        Vaccine("Moderna", 20, 850.0)
    ]
    
    print_medicines_info(pharmacy_inventory)