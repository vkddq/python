import pytest

from service_body_test import Order


@pytest.fixture
def order():
    return Order(1, [
        {'name': 'A', 'price': 100.0, 'quantity': 2},
        {'name': 'B', 'price': 80.0, 'quantity': 3},
        {'name': 'C', 'price': 10.0, 'quantity': 5},
    ])


@pytest.mark.parametrize('items, expected', [
    ([], 0),
    ([{'price': 12.5, 'quantity': 2}], 25.0),
    ([{'price': 10.0, 'quantity': 2}, {'price': 3.0, 'quantity': 4}], 32.0),
    ([{'price': 50.0, 'quantity': 0}], 0.0),
    ([{'price': 0.0, 'quantity': 10}], 0.0),
    ([{'price': 0.1, 'quantity': 3}, {'price': 0.2, 'quantity': 2}], 0.7),
])
def test_total_for_different_items(items, expected):
    assert Order(1, items).total() == pytest.approx(expected)


def test_total_does_not_change_items(order):
    before = [item.copy() for item in order.items]
    order.total()
    assert order.items == before


@pytest.mark.parametrize('prices, expected_index', [
    ([10.0], 0),
    ([10.0, 30.0, 20.0], 1),
    ([50.0, 20.0, 10.0], 0),
    ([10.0, 20.0, 50.0], 2),
    ([20.0, 20.0, 10.0], 0),
    ([0.0, 0.0], 0),
])
def test_most_expensive_returns_correct_item(prices, expected_index):
    items = []
    for price in prices:
        items.append({'price': price, 'quantity': 1})
    assert Order(1, items).most_expensive() is items[expected_index]


def test_most_expensive_uses_unit_price_not_item_total():
    items = [
        {'price': 5.0, 'quantity': 100},
        {'price': 10.0, 'quantity': 1},
    ]
    assert Order(1, items).most_expensive() is items[1]


def test_most_expensive_of_empty_order_raises_value_error():
    with pytest.raises(ValueError):
        Order(1, []).most_expensive()


@pytest.mark.parametrize('percent, expected_prices', [
    (0, [100.0, 80.0, 10.0]),
    (0.01, [99.99, 79.992, 9.999]),
    (10, [90.0, 72.0, 9.0]),
    (25, [75.0, 60.0, 7.5]),
    (50, [50.0, 40.0, 5.0]),
    (99.99, [0.01, 0.008, 0.001]),
    (100, [0.0, 0.0, 0.0]),
])
def test_discount_changes_price_of_every_item(order, percent, expected_prices):
    order.apply_discount(percent)
    prices = [item['price'] for item in order.items]
    assert prices == pytest.approx(expected_prices)


@pytest.mark.parametrize('percent', [-10, -0.01, 100.01, 150, float('nan'), float('inf'), -float('inf')])
def test_invalid_discount_raises_and_does_not_change_items(order, percent):
    before = [item.copy() for item in order.items]
    with pytest.raises(ValueError, match='Invalid discount'):
        order.apply_discount(percent)
    assert order.items == before


def test_discount_does_not_change_quantities_names_or_id(order):
    order.apply_discount(20)
    assert [item['quantity'] for item in order.items] == [2, 3, 5]
    assert [item['name'] for item in order.items] == ['A', 'B', 'C']
    assert order.id == 1


def test_total_after_discount(order):
    order.apply_discount(10)
    assert order.total() == pytest.approx(441.0)


def test_repeated_discounts_apply_to_current_prices(order):
    order.apply_discount(20)
    order.apply_discount(50)
    assert [item['price'] for item in order.items] == pytest.approx([40.0, 32.0, 4.0])


@pytest.mark.parametrize('percent', [0, 50, 100])
def test_valid_discount_on_empty_order(percent):
    empty = Order(1, [])
    empty.apply_discount(percent)
    assert empty.items == []
    assert empty.total() == 0


@pytest.mark.parametrize('percent', [-0.01, 100.01])
def test_invalid_discount_on_empty_order(percent):
    with pytest.raises(ValueError, match='Invalid discount'):
        Order(1, []).apply_discount(percent)


@pytest.mark.parametrize('order_id, count, expected', [
    (1, 0, '<Order 1: 0 items>'),
    (7, 1, '<Order 7: 1 items>'),
    ('A-12', 3, '<Order A-12: 3 items>'),
])
def test_repr_has_required_format(order_id, count, expected):
    items = []
    for number in range(count):
        items.append({'price': 10.0, 'quantity': 1})
    assert repr(Order(order_id, items)) == expected
