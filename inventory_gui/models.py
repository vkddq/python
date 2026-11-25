"""Модель товару та спільна перевірка форми й завантажених даних."""
from dataclasses import dataclass
from datetime import datetime
import math
from uuid import uuid4


@dataclass
class Product:
    id: str
    name: str
    category: str
    quantity: int
    price: float
    location: str
    created_at: str


class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('; '.join(errors.values()))


def make_product(data, existing_ids, created_at=None):
    """Створює перевірений товар; errors містить імена некоректних полів."""
    errors = {}
    product_id = str(data.get('id', '')).strip()
    if not product_id:
        product_id = uuid4().hex[:12]
        while product_id in existing_ids:
            product_id = uuid4().hex[:12]
    if product_id in existing_ids:
        errors['id'] = 'Такий ID уже існує.'
    name = str(data.get('name', '')).strip()
    category = str(data.get('category', '')).strip()
    if not name:
        errors['name'] = 'Введіть назву товару.'
    if not category:
        errors['category'] = 'Введіть категорію.'
    try:
        quantity = int(str(data.get('quantity', '')).strip())
        if quantity < 0:
            raise ValueError
    except ValueError:
        errors['quantity'] = 'Кількість має бути цілим числом від 0.'
    try:
        price = float(str(data.get('price', '')).strip().replace(',', '.'))
        if not math.isfinite(price) or price < 0:
            raise ValueError
    except ValueError:
        errors['price'] = 'Ціна має бути скінченним числом від 0.'
    timestamp = created_at or str(data.get('created_at', '')).strip()
    if not timestamp:
        timestamp = datetime.now().isoformat(timespec='seconds')
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        errors['created_at'] = 'Некоректна дата створення.'
    if errors:
        raise ValidationError(errors)
    return Product(product_id, name, category, quantity, price,
                   str(data.get('location', '')).strip(), timestamp)
