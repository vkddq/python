import argparse
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description='Аналіз постачань препаратів')
    parser.add_argument('csv', help='шлях до CSV з постачаннями')
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    print('Перші рядки:')
    print(df.head(3).to_string(index=False))
    print('\nПропуски в даних:')
    print(df.isna().sum())

    # Як у лекції: пропущену кількість не замінюємо нулем.
    before = len(df)
    df = df.dropna(subset=['quantity']).copy()
    removed = before - len(df)
    if df.empty:
        parser.error('Немає записів з указаною кількістю.')
    if df[['supplier', 'category', 'price_per_unit']].isna().any().any():
        parser.error('Заповніть постачальника, категорію та ціну в усіх рядках.')

    prices = df['price_per_unit'].to_numpy()
    quantities = df['quantity'].to_numpy()
    mean_price = np.mean(prices)
    median_quantity = np.median(quantities)
    std_price = np.std(prices, ddof=0)

    df['total_price'] = df['quantity'] * df['price_per_unit']
    by_supplier = df.groupby('supplier')['total_price'].sum()
    top_supplier = by_supplier.idxmax()
    by_category = df.groupby('category')['quantity'].sum()
    low = df[df['quantity'] < 100]
    top_three = df.sort_values('total_price', ascending=False).head(3)

    # Перевірки результату з презентації.
    assert (df['quantity'] >= 0).all()
    assert (df['price_per_unit'] >= 0).all()
    assert np.isfinite(prices).all()
    assert np.isfinite(quantities).all()
    assert by_category.sum() == df['quantity'].sum()
    assert len(low) + (df['quantity'] >= 100).sum() == len(df)
    assert df['total_price'].notna().all()

    low.to_csv('low_supply.csv', index=False)
    with open('report.txt', 'w', encoding='utf-8') as file:
        file.write('АНАЛІТИКА ПОСТАЧАНЬ\n\n')
        file.write(f'Опрацьовано записів: {len(df)}\n')
        file.write(f'Відкинуто рядків із порожньою quantity: {removed}\n')
        file.write(f'Середня ціна: {mean_price:.2f}\n')
        file.write(f'Медіана кількості: {median_quantity:.2f}\n')
        file.write(f'Стандартне відхилення цін: {std_price:.2f} (NumPy, ddof=0)\n')
        file.write('Середня ціна — звичайне середнє цін усіх записів, без ваг quantity.\n')
        file.write(f'Постачальник з найбільшим прибутком: {top_supplier}\n')
        file.write(f'Його загальний прибуток: {by_supplier.max():.2f}\n')
        file.write('Прибуток за умовою = quantity * price_per_unit, без віднімання витрат.\n')
        file.write('\nСумарна кількість за категоріями:\n')
        file.write(by_category.to_string() + '\n')
        file.write(f'\nДефіцитні поставки: low_supply.csv, записів: {len(low)}\n')
        file.write('Умова фільтра: quantity < 100, строго.\n')
        file.write('\nТри найдорожчі поставки:\n')
        file.write(top_three.to_string(index=False) + '\n')
        file.write('\nГрафік: by_category.png\n')

    print('\nКількість за категоріями:')
    print(by_category)
    print('\nТри найдорожчі поставки:')
    print(top_three.to_string(index=False))
    print('\nСтворено low_supply.csv та report.txt. Інваріанти: OK.')

    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    plt.bar(by_category.index, by_category.values, color='steelblue')
    plt.title('Кількість препаратів за категоріями')
    plt.xlabel('Категорія')
    plt.ylabel('Кількість, шт.')
    plt.tight_layout()
    plt.savefig('by_category.png', dpi=150)
    plt.close()
    print('Створено by_category.png.')


if __name__ == '__main__':
    main()
