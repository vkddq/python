"""Сховище CSV. Інтерфейс вікна користується лише load та save."""
import csv
from dataclasses import asdict
import os
from pathlib import Path
import tempfile

from models import make_product, ValidationError

HEADERS = ['id', 'name', 'category', 'quantity', 'price', 'location', 'created_at']


class CSVRepository:
    def load(self, path):
        products = []
        try:
            with open(path, encoding='utf-8-sig', newline='') as source:
                reader = csv.DictReader(source, strict=True)
                if reader.fieldnames != HEADERS:
                    raise ValueError('Неправильні заголовки CSV. Потрібно: ' + ','.join(HEADERS))
                rows = list(reader)
            # Непорожні ID резервуємо до автоматичного створення нових.
            reserved_ids = {row['id'].strip() for row in rows if row.get('id')}
            used_ids = set()
            for number, row in enumerate(rows, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f'Рядок {number}: неправильна кількість стовпців.')
                conflicts = used_ids if row['id'].strip() else reserved_ids | used_ids
                try:
                    product = make_product(row, conflicts)
                except ValidationError as error:
                    raise ValueError(f'Рядок {number}: {error}') from error
                products.append(product)
                used_ids.add(product.id)
        except (csv.Error, UnicodeError) as error:
            raise ValueError(f'Не вдалося прочитати CSV: {error}') from error
        return products

    def save(self, path, products):
        # Запис у тимчасовий файл: помилка не зіпсує попереднє збереження.
        path = Path(path)
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', newline='',
                                             dir=path.parent, delete=False) as target:
                temporary_name = target.name
                writer = csv.DictWriter(target, fieldnames=HEADERS)
                writer.writeheader()
                writer.writerows(asdict(product) for product in products)
            os.replace(temporary_name, path)
        finally:
            if temporary_name is not None and Path(temporary_name).exists():
                Path(temporary_name).unlink()
