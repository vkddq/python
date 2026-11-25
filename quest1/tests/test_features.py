"""Стиль тижня 7: assert, raises, approx, parametrize, fixtures."""
from dataclasses import fields, is_dataclass, replace
from datetime import date
from pathlib import Path

import pytest

from blocknot import Condition, Inventory, Item, load, zvit

ROOT = Path(__file__).resolve().parents[1]


def make_item(**changes):
    data = dict(name='Ключ', category='інструменти', quantity=3,
                value=15.0, condition=Condition.USED, location='гараж')
    data.update(changes)
    return Item(**data)


@pytest.fixture
def stock():
    """Кожен тест отримує свіжий склад."""
    return load(ROOT / 'barakhlo.csv')


def test_models_are_dataclasses():
    assert is_dataclass(Item)
    assert is_dataclass(Inventory)


def test_inventories_have_independent_lists():
    first, second = Inventory(), Inventory()
    first.add_item(make_item())
    assert second.items == []


@pytest.mark.parametrize('condition, expected', [
    (Condition.NEW, 45.0), (Condition.USED, 31.5), (Condition.BROKEN, 9.0),
])
def test_total_value_uses_condition_coefficient(condition, expected):
    thing = make_item(condition=condition)
    assert thing.total_value() == pytest.approx(expected)


def test_item_str_has_required_format():
    assert str(make_item()) == '[інструменти] Ключ (3 шт.) - 15.0 грн/шт, стан: уживаний'


def test_order_by_category_then_unit_value():
    items = [make_item(name='A', category='Б', value=1),
             make_item(name='B', category='А', value=20),
             make_item(name='C', category='А', value=2)]
    assert [thing.name for thing in sorted(items)] == ['C', 'B', 'A']


def test_equal_sort_keys_keep_original_order():
    items = [make_item(name='Z'), make_item(name='A')]
    assert [thing.name for thing in sorted(items)] == ['Z', 'A']


def test_different_names_are_not_equal():
    assert make_item(name='X') != make_item(name='Y')


def test_date_does_not_affect_equality_or_order():
    first = make_item(added_on=date(2020, 1, 1))
    second = replace(first, added_on=date(2030, 1, 1))
    assert first == second
    assert not first < second
    assert not second < first


def test_date_defaults_to_today_and_excludes_comparison():
    assert make_item().added_on == date.today()
    date_field = next(f for f in fields(Item) if f.name == 'added_on')
    assert date_field.compare is False


def test_add_item_adds_to_inventory():
    inventory = Inventory()
    thing = make_item()
    inventory.add_item(thing)
    assert inventory.items == [thing]


def test_add_item_rejects_duplicate_without_changing_inventory():
    inventory = Inventory([make_item()])
    with pytest.raises(ValueError):
        inventory.add_item(make_item(location='комора'))
    assert len(inventory.items) == 1
    assert inventory.items[0].location == 'гараж'


def test_constructor_rejects_duplicate_names():
    with pytest.raises(ValueError):
        Inventory([make_item(), make_item()])


def test_remove_item_returns_and_removes_item():
    inventory = Inventory([make_item()])
    removed = inventory.remove_item('Ключ')
    assert removed.name == 'Ключ'
    assert inventory.items == []


def test_remove_missing_item_raises_key_error():
    with pytest.raises(KeyError):
        Inventory().remove_item('немає')


def test_find_by_category(stock):
    result = stock.find_by_category('інструменти')
    assert [thing.name for thing in result] == ['Гаечний ключ', 'Плоскогубці', 'Викрутка']


def test_total_inventory_value(stock):
    assert stock.total_inventory_value() == pytest.approx(1563.7)


def test_repeat_report_gives_same_output(capsys):
    zvit(ROOT / 'barakhlo.csv')
    first = capsys.readouterr().out
    zvit(ROOT / 'barakhlo.csv')
    second = capsys.readouterr().out
    assert first == second


def test_load_returns_independent_inventories():
    first = load(ROOT / 'barakhlo.csv')
    second = load(ROOT / 'barakhlo.csv')
    first.remove_item('Викрутка')
    assert len(second.items) == 7


def test_filter_matches_all_given_fields(stock):
    result = stock.filter_items(category='інструменти', condition=Condition.NEW)
    assert [thing.name for thing in result] == ['Плоскогубці', 'Викрутка']


def test_filter_supports_quantity_price_and_location(stock):
    result = stock.filter_items(quantity=12, value=45.5, location='сарай')
    assert [thing.name for thing in result] == ['Мідний дріт']


def test_filter_without_criteria_returns_all_items(stock):
    assert stock.filter_items() == stock.items


def test_filter_without_matches_returns_empty_list(stock):
    assert stock.filter_items(name='немає') == []


def test_filter_supports_date():
    thing = make_item(added_on=date(2021, 2, 3))
    inventory = Inventory([thing])
    assert inventory.filter_items(added_on=date(2021, 2, 3)) == [thing]


def test_filter_rejects_unknown_field(stock):
    with pytest.raises(ValueError):
        stock.filter_items(typo=1)


def test_sorted_items_does_not_change_inventory(stock):
    original_names = [thing.name for thing in stock.items]
    result = stock.sorted_items()
    assert [(thing.category, thing.value) for thing in result] == sorted(
        (thing.category, thing.value) for thing in stock.items)
    assert [thing.name for thing in stock.items] == original_names


def test_csv_roundtrip_preserves_all_fields_including_date(tmp_path):
    special = make_item(name='  Ключ; "особливий"\nдругий рядок  ', added_on=date(2020, 2, 29))
    original = Inventory([special, make_item(name='Інший', condition=Condition.BROKEN)])
    path = tmp_path / 'stock.csv'
    original.save_to_csv(path)
    restored = Inventory.load_from_csv(path)
    assert len(restored.items) == len(original.items)
    for before, after in zip(original.items, restored.items):
        for item_field in fields(Item):
            assert getattr(before, item_field.name) == getattr(after, item_field.name)


def test_load_supports_original_six_column_csv(stock):
    assert len(stock.items) == 7
    assert stock.items[0].name == 'Гаечний ключ'


def test_summary_sums_physical_quantities(stock):
    assert stock.export_summary() == {'інструменти': 11, 'електроніка': 5, 'металобрухт': 13}


def test_empty_inventory_summary():
    assert Inventory().export_summary() == {}


def test_empty_csv_roundtrip(tmp_path):
    path = tmp_path / 'empty.csv'
    Inventory().save_to_csv(path)
    assert Inventory.load_from_csv(path).items == []


@pytest.mark.parametrize('text', [
    'лише;два', 'Річ;Категорія;1;2;невідомий;Тут',
    'Річ;Категорія;1;2;новий;Тут;не-дата',
])
def test_invalid_csv_record_raises_value_error(tmp_path, text):
    path = tmp_path / 'invalid.csv'
    path.write_text(text, encoding='utf-8')
    with pytest.raises(ValueError):
        Inventory.load_from_csv(path)
