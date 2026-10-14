def process_client(client_dict):
    match client_dict:
        case {"name": name, "amount": amount, "status": status}:
            if not isinstance(amount, (int, float)):
                return "Фальшиві дані"
            
            if amount < 100:
                amount_category = "Дрібнота"
            elif amount < 1000:
                amount_category = "Середнячок"
            else:
                amount_category = "Великий клієнт"
                
            match status:
                case "clean":
                    decision = "Працювати без питань"
                case "suspicious":
                    decision = "Перевірити документи"
                case "fraud":
                    decision = "У чорний список"
                case _:
                    decision = "Невідомий статус"
                    
            return f"{name}, {amount_category}, {decision}"
            
        case _:
            return "Фальшиві дані"


if __name__ == "__main__":
    clients = [
        {"name": "Олег", "amount": 50, "status": "clean"},
        {"name": "Анна", "amount": 500, "status": "suspicious"},
        {"name": "Іван", "amount": 1500, "status": "fraud"},
        {"name": "Бот", "amount": "100", "status": "clean"} # Фальшиві дані
    ]
    
    for client in clients:
        print(process_client(client))