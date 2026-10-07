def check_medication(name, quantity, category, temperature):
    if not isinstance(quantity, int) or not isinstance(temperature, float):
        return "Помилка даних"
    

    if temperature < 5.0:
        t_status = "Надто холодно"
    elif temperature > 25.0:
        t_status = "Надто жарко"
    else:
        t_status = "Норма"
        
  
    match category:
        case "antibiotic":
            c_status = "Рецептурний препарат"
        case "vitamin":
            c_status = "Вільний продаж"
        case "vaccine":
            c_status = "Потребує спецзберігання"
        case _:
            c_status = "Невідома категорія"
            
    
    return f"{name}, {c_status}, {t_status}"



medications = [
    ("Аспірин", 100, "vitamin", 20.0),
    ("Пеніцилін", 50, "antibiotic", 3.0),
    ("Moderna", 20, "vaccine", 26.5),
    ("Бинт", 200, "other", 20.0),
    ("Помилка типу", "10", "vitamin", 20.0) 
]

for med in medications:
    print(check_medication(med[0], med[1], med[2], med[3]))