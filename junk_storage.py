class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Назва має бути непорожнім рядком.')
        if '|' in name or '\n' in name or '\r' in name:
            raise ValueError('Назва не може містити | або перенос рядка.')
        if type(quantity) is not int:
            raise ValueError('Кількість має бути цілим числом.')
        if type(value) not in (int, float):
            raise ValueError('Ціна має бути числом.')
        value = float(value)
        if value != value or value in (float('inf'), -float('inf')):
            raise ValueError('Ціна має бути скінченним числом.')
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f'{self.name}: {self.quantity} шт., ціна {self.value}'


class StorageError(Exception):
    pass


class StorageBackend:
    def save(self, items):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class JunkStorage(StorageBackend):
    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def serialize(items: list[JunkItem], filename: str):
        lines = []
        for item in items:
            value = str(item.value).replace('.', ',')
            lines.append(f'{item.name}|{item.quantity}|{value}\n')
        with open(filename, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(line)

    @staticmethod
    def parse(filename: str) -> list[JunkItem]:
        items = []
        with open(filename, encoding='utf-8') as file:
            for number, line in enumerate(file, start=1):
                try:
                    name, quantity, value = line.rstrip('\r\n').split('|')
                    item = JunkItem(name, int(quantity), float(value.replace(',', '.')))
                except ValueError:
                    print(f'Попередження: рядок {number} пропущено: {line.strip()}')
                else:
                    items.append(item)
        return items

    def save(self, items):
        try:
            self.serialize(items, self.filename)
        except (OSError, UnicodeError) as error:
            raise StorageError('Не вдалося записати дані.') from error

    def load(self):
        try:
            return self.parse(self.filename)
        except FileNotFoundError:
            return []
        except (OSError, UnicodeError) as error:
            raise StorageError('Не вдалося прочитати дані.') from error


class JunkRepository:
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.items = storage.load()

    def add(self, item: JunkItem):
        if self.get(item.name) is not None:
            raise ValueError('Предмет із такою назвою вже є.')
        updated = self.items + [item]
        self.storage.save(updated)
        self.items = updated

    def get(self, name: str):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def find(self, text: str) -> list[JunkItem]:
        found = []
        for item in self.items:
            if text.lower() in item.name.lower():
                found.append(item)
        return found

    def list_all(self) -> list[JunkItem]:
        return self.items.copy()


def show_items(repository: JunkRepository):
    for item in repository.list_all():
        print(item)


if __name__ == '__main__':
    items = [
        JunkItem('Бляшанка', 5, 2.5),
        JunkItem('Стара плата', 3, 7.8),
        JunkItem('Купка дротів', 10, 1.2),
    ]
    storage = JunkStorage('junk.csv')
    try:
        storage.save(items)
        restored = storage.load()
        assert len(items) == len(restored)
        for original, loaded in zip(items, restored):
            assert original.name == loaded.name
            assert original.quantity == loaded.quantity
            assert original.value == loaded.value
        print('Запис і читання: значення збережено правильно.\n')
        repository = JunkRepository(storage)
        show_items(repository)
        print('\nДістати предмет:', repository.get('Стара плата'))
        print('Пошук за назвою:')
        for item in repository.find('дрот'):
            print(item)
        repository.add(JunkItem('Викрутка', 2, 15.0))
        print('\nПісля додавання:')
        show_items(repository)
    except (StorageError, ValueError) as error:
        print('Помилка:', error)
