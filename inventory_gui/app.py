"""Запуск: python app.py. Вікно не читає й не записує CSV самостійно."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models import make_product, ValidationError

COLUMNS = {
    'id': 'ID', 'name': 'Назва', 'category': 'Категорія', 'quantity': 'Кількість',
    'price': 'Ціна, грн', 'location': 'Місце', 'created_at': 'Створено',
}


class InventoryApp:
    def __init__(self, root, repository):
        self.root = root
        self.repository = repository
        self.products = []
        self.current_path = None
        self.selected_id = None
        self.dirty = False
        self.sort_column = None
        self.sort_reverse = False
        root.title('Облік товарів')
        root.geometry('1120x600')
        root.minsize(900, 480)
        root.protocol('WM_DELETE_WINDOW', self.close)

        menu = tk.Menu(root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Відкрити…', command=self.open_file)
        file_menu.add_command(label='Зберегти', command=self.save)
        file_menu.add_command(label='Зберегти як…', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Вийти', command=self.close)
        menu.add_cascade(label='Файл', menu=file_menu)
        root.config(menu=menu)

        search_frame = ttk.Frame(root, padding=10)
        search_frame.pack(fill='x')
        ttk.Label(search_frame, text='Пошук за назвою або категорією:').pack(side='left')
        self.search = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search).pack(side='left', fill='x', expand=True, padx=10)
        self.search.trace_add('write', lambda *_: self.refresh())

        body = ttk.Frame(root, padding=(10, 0, 10, 10))
        body.pack(fill='both', expand=True)
        table_frame = ttk.Frame(body)
        table_frame.pack(side='left', fill='both', expand=True)
        self.tree = ttk.Treeview(table_frame, columns=list(COLUMNS), show='headings', selectmode='browse')
        for key, title in COLUMNS.items():
            self.tree.heading(key, text=title, command=lambda column=key: self.sort_by(column))
            self.tree.column(key, width=105, minwidth=65)
        self.tree.column('name', width=155)
        self.tree.column('created_at', width=155)
        vertical = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        horizontal = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        self.tree.bind('<<TreeviewSelect>>', self.select_product)

        form = ttk.LabelFrame(body, text='Картка товару', padding=12)
        form.pack(side='right', fill='y', padx=(12, 0))
        self.entries = {}
        for key in list(COLUMNS)[:-1]:
            label = COLUMNS[key] + (' (порожній — автоматично)' if key == 'id' else '')
            ttk.Label(form, text=label).pack(anchor='w')
            entry = tk.Entry(form, width=31)
            entry.pack(fill='x', pady=(2, 7))
            self.entries[key] = entry
        for title, command in [('Додати', self.add_product), ('Оновити', self.update_product),
                               ('Видалити', self.delete_product), ('Очистити форму', self.clear_form)]:
            ttk.Button(form, text=title, command=command).pack(fill='x', pady=3)

        self.status = tk.StringVar(value='Додайте товар або відкрийте файл через меню «Файл».')
        ttk.Label(root, textvariable=self.status, relief='sunken', anchor='w', padding=5).pack(fill='x')

    def refresh(self):
        query = self.search.get().strip().casefold()
        visible = [product for product in self.products
                   if query in product.name.casefold() or query in product.category.casefold()]
        if self.sort_column:
            column = self.sort_column
            def key(product):
                value = getattr(product, column)
                return value.casefold() if isinstance(value, str) else value
            visible.sort(key=key, reverse=self.sort_reverse)
        self.tree.delete(*self.tree.get_children())
        for product in visible:
            values = [getattr(product, column) for column in COLUMNS]
            values[4] = f'{product.price:.2f}'
            self.tree.insert('', 'end', iid=product.id, values=values)
        if self.selected_id and self.tree.exists(self.selected_id):
            self.tree.selection_set(self.selected_id)
        else:
            self.selected_id = None
        self.status.set(f'Показано {len(visible)} з {len(self.products)} товарів.'
                        + (' Є незбережені зміни.' if self.dirty else ''))

    def sort_by(self, column):
        self.sort_reverse = not self.sort_reverse if self.sort_column == column else False
        self.sort_column = column
        self.refresh()

    def select_product(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_id = selected[0]
        product = next(product for product in self.products if product.id == self.selected_id)
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(getattr(product, key)))
            entry.configure(background='white')

    def clear_form(self):
        self.selected_id = None
        self.tree.selection_remove(*self.tree.selection())
        for entry in self.entries.values():
            entry.delete(0, 'end')
            entry.configure(background='white')
        self.status.set('Форму очищено. ID можна залишити порожнім.')

    def read_form(self, original=None):
        data = {key: entry.get() for key, entry in self.entries.items()}
        ids = {product.id for product in self.products if original is None or product.id != original.id}
        for entry in self.entries.values():
            entry.configure(background='white')
        try:
            return make_product(data, ids, original.created_at if original else None)
        except ValidationError as error:
            for key in error.errors:
                if key in self.entries:
                    self.entries[key].configure(background='#ffd6d6')
            self.status.set(str(error))
            return None

    def add_product(self):
        product = self.read_form()
        if product is None:
            return
        self.products.append(product)
        self.dirty = True
        self.clear_form()
        self.refresh()
        self.status.set(f'Додано «{product.name}». Збережіть зміни через меню «Файл».')

    def update_product(self):
        if self.selected_id is None:
            self.status.set('Спочатку виберіть товар у таблиці.')
            return
        index = next(i for i, product in enumerate(self.products) if product.id == self.selected_id)
        updated = self.read_form(self.products[index])
        if updated is None:
            return
        self.products[index] = updated
        self.selected_id = updated.id
        self.dirty = True
        self.refresh()
        self.status.set('Товар оновлено. Збережіть зміни через меню «Файл».')

    def delete_product(self):
        if self.selected_id is None:
            self.status.set('Спочатку виберіть товар у таблиці.')
            return
        if not messagebox.askyesno('Видалення', 'Видалити вибраний товар?', parent=self.root):
            return
        self.products = [product for product in self.products if product.id != self.selected_id]
        self.dirty = True
        self.clear_form()
        self.refresh()
        self.status.set('Товар видалено. Збережіть зміни через меню «Файл».')

    def confirm_unsaved(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel('Незбережені зміни', 'Зберегти зміни?', parent=self.root)
        if answer is None:
            return False
        return self.save() if answer else True

    def open_file(self):
        if not self.confirm_unsaved():
            return
        path = filedialog.askopenfilename(parent=self.root, title='Відкрити дані',
                                          filetypes=[('CSV', '*.csv'), ('Усі файли', '*.*')])
        if path:
            self.load_path(path)

    def load_path(self, path):
        try:
            products = self.repository.load(path)
        except (OSError, ValueError) as error:
            self.show_error(error)
            return False
        self.products = products  
        self.current_path = path
        self.dirty = False
        self.clear_form()
        self.search.set('')
        self.refresh()
        self.status.set(f'Відкрито: {Path(path).name}. Товарів: {len(products)}.')
        return True

    def save(self):
        return self.save_path(self.current_path) if self.current_path else self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(parent=self.root, title='Зберегти дані',
                                           defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        return self.save_path(path) if path else False

    def save_path(self, path):
        try:
            self.repository.save(path, self.products)  
        except (OSError, ValueError) as error:
            self.show_error(error)
            return False
        self.current_path = path
        self.dirty = False
        self.status.set(f'Збережено: {Path(path).name}. Товарів: {len(self.products)}.')
        return True

    def show_error(self, error):
        self.status.set(str(error))
        messagebox.showerror('Помилка', str(error), parent=self.root)

    def close(self):
        if self.confirm_unsaved():
            self.root.destroy()


if __name__ == '__main__':
    from repository import CSVRepository
    root = tk.Tk()
    app = InventoryApp(root, CSVRepository())
    root.mainloop()
