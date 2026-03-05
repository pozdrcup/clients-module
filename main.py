# main.py - графический интерфейс (tkinter)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import db


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт клиентов")
        self.root.geometry("960x620")

        # стиль
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview", rowheight=28, font=("Arial", 11),
                         background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"),
                         background="#d5dbe3", foreground="#2c3e50")
        style.map("Treeview", background=[("selected", "#3a86a8")])

        style.configure("Add.TButton", font=("Arial", 11), padding=8)
        style.configure("Small.TButton", font=("Arial", 10), padding=5)

        bg = "#e8ecf1"
        self.bg = bg
        self.root.configure(bg=bg)

        try:
            db.init_db()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к БД:\n{e}")
            root.destroy()
            return

        self.create_widgets()
        self.load_clients()

    def create_widgets(self):
        bg = self.bg

        # кнопки
        btn_frame = tk.Frame(self.root, bg=bg)
        btn_frame.pack(fill=tk.X, padx=12, pady=(10, 4))

        buttons = [
            ("➕ Добавить", self.add_client_window),
            ("✏️ Редактировать", self.edit_client_window),
            ("🗑 Удалить", self.delete_client),
            ("📦 Новый заказ", self.add_order_window),
            ("📋 Заказы", self.show_orders_window),
            ("📊 Отчёт", self.show_report),
            ("💾 Скачать отчёт", self.export_report),
        ]
        for text, cmd in buttons:
            ttk.Button(btn_frame, text=text, command=cmd,
                       style="Add.TButton").pack(side=tk.LEFT, padx=3)

        # поиск
        search_frame = tk.Frame(self.root, bg=bg)
        search_frame.pack(fill=tk.X, padx=12, pady=4)

        tk.Label(search_frame, text="Поиск:", bg=bg,
                 font=("Arial", 11)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     width=25, font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_clients())

        ttk.Button(search_frame, text="Найти", style="Small.TButton",
                   command=self.search_clients).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Сброс", style="Small.TButton",
                   command=self.load_clients).pack(side=tk.LEFT, padx=2)

        tk.Frame(search_frame, width=20, bg=bg).pack(side=tk.LEFT)

        tk.Label(search_frame, text="Период с:", bg=bg,
                 font=("Arial", 11)).pack(side=tk.LEFT)
        self.date_from = tk.Entry(search_frame, width=12, font=("Arial", 11))
        self.date_from.pack(side=tk.LEFT, padx=3)
        tk.Label(search_frame, text="по:", bg=bg,
                 font=("Arial", 11)).pack(side=tk.LEFT)
        self.date_to = tk.Entry(search_frame, width=12, font=("Arial", 11))
        self.date_to.pack(side=tk.LEFT, padx=3)
        ttk.Button(search_frame, text="Отчёт по дате", style="Small.TButton",
                   command=self.report_by_date).pack(side=tk.LEFT, padx=4)

        # таблица
        table_frame = tk.Frame(self.root, bg=bg)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        columns = ("id", "fio", "phone", "email", "date", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns,
                                  show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("fio", text="ФИО")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("email", text="Email")
        self.tree.heading("date", text="Дата рег.")
        self.tree.heading("notes", text="Примечания")

        self.tree.column("id", width=45, anchor=tk.CENTER)
        self.tree.column("fio", width=190)
        self.tree.column("phone", width=125)
        self.tree.column("email", width=190)
        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("notes", width=210)

        self.tree.tag_configure("odd", background="#f0f3f7")
        self.tree.tag_configure("even", background="#ffffff")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # статусбар
        self.status = tk.Label(self.root, text="Готово", bd=1,
                                relief=tk.SUNKEN, anchor=tk.W,
                                font=("Arial", 10), bg="#dfe4ea", padx=8)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def load_clients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            clients = db.get_all_clients()
            for i, c in enumerate(clients):
                tag = "odd" if i % 2 else "even"
                self.tree.insert("", tk.END, tags=(tag,),
                    values=(c[0], c[1], c[2] or "", c[3] or "",
                            str(c[4]), c[5] or ""))
            self.status.config(text=f"Загружено клиентов: {len(clients)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def search_clients(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("Внимание", "Введите запрос для поиска")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            results = db.search_clients(keyword)
            for i, c in enumerate(results):
                tag = "odd" if i % 2 else "even"
                self.tree.insert("", tk.END, tags=(tag,),
                    values=(c[0], c[1], c[2] or "", c[3] or "",
                            str(c[4]), c[5] or ""))
            self.status.config(text=f"Найдено: {len(results)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def report_by_date(self):
        d1 = self.date_from.get().strip()
        d2 = self.date_to.get().strip()
        if not d1 or not d2:
            messagebox.showwarning("Внимание", "Укажите обе даты (ГГГГ-ММ-ДД)")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            results = db.report_by_date(d1, d2)
            for i, c in enumerate(results):
                tag = "odd" if i % 2 else "even"
                self.tree.insert("", tk.END, tags=(tag,),
                    values=(c[0], c[1], c[2] or "", c[3] or "",
                            str(c[4]), ""))
            self.status.config(text=f"Клиентов за период: {len(results)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента в таблице")
            return None
        values = self.tree.item(selected[0])["values"]
        return values[0]

    # --- экспорт отчёта ---
    def export_report(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить отчёт",
            defaultextension=".csv",
            filetypes=[("CSV файл", "*.csv"), ("Текстовый файл", "*.txt")],
            initialfile="отчёт_клиенты.csv"
        )
        if not path:
            return
        try:
            clients = db.get_all_clients()
            summary = db.report_summary()

            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")

                # сводка
                writer.writerow(["СВОДНЫЙ ОТЧЁТ"])
                writer.writerow(["Всего клиентов", summary["clients"]])
                writer.writerow(["Всего заказов", summary["orders"]])
                writer.writerow(["Общая сумма", f"{summary['total_sum']:.2f}"])
                writer.writerow([])

                # таблица клиентов
                writer.writerow(["ID", "ФИО", "Телефон", "Email",
                                 "Дата регистрации", "Примечания"])
                for c in clients:
                    writer.writerow([c[0], c[1], c[2] or "", c[3] or "",
                                     str(c[4]), c[5] or ""])

                # заказы по каждому клиенту
                writer.writerow([])
                writer.writerow(["ЗАКАЗЫ КЛИЕНТОВ"])
                for c in clients:
                    orders = db.get_client_orders(c[0])
                    if orders:
                        writer.writerow([])
                        writer.writerow([f"Клиент: {c[1]} (ID={c[0]})"])
                        writer.writerow(["ID заказа", "Описание", "Сумма",
                                         "Дата", "Статус"])
                        for o in orders:
                            writer.writerow([o[0], o[1], f"{o[2]:.2f}",
                                             str(o[3]), o[4]])

            messagebox.showinfo("Успех", f"Отчёт сохранён:\n{path}")
            self.status.config(text=f"Отчёт сохранён: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _make_form(self, title, fields, defaults=None, on_save=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.resizable(False, False)
        win.configure(bg="#f5f7fa")

        entries = {}
        for i, label in enumerate(fields):
            tk.Label(win, text=label, bg="#f5f7fa",
                     font=("Arial", 11)).grid(row=i, column=0,
                     padx=14, pady=8, sticky=tk.W)
            e = tk.Entry(win, width=30, font=("Arial", 11),
                         )
            if defaults and i < len(defaults):
                e.insert(0, str(defaults[i]))
            e.grid(row=i, column=1, padx=14, pady=8)
            entries[i] = e
        entries[0].focus()

        def do_save():
            if on_save:
                on_save(entries, win)

        ttk.Button(win, text="Сохранить", command=do_save,
                   style="Add.TButton").grid(
                   row=len(fields), column=0, columnspan=2, pady=16)
        return win

    # --- добавление клиента ---
    def add_client_window(self):
        def save(entries, win):
            name = entries[0].get().strip()
            if not name:
                messagebox.showwarning("Ошибка", "ФИО не может быть пустым")
                return
            try:
                cid = db.add_client(name, entries[1].get().strip(),
                                    entries[2].get().strip(),
                                    entries[3].get().strip())
                messagebox.showinfo("Успех", f"Клиент добавлен (ID: {cid})")
                win.destroy()
                self.load_clients()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        self._make_form("Добавить клиента",
                        ["ФИО:", "Телефон:", "Email:", "Примечания:"],
                        on_save=save)

    # --- редактирование ---
    def edit_client_window(self):
        cid = self.get_selected_id()
        if cid is None:
            return
        selected = self.tree.selection()
        vals = self.tree.item(selected[0])["values"]

        def save(entries, win):
            try:
                if db.update_client(cid, entries[0].get().strip(),
                                    entries[1].get().strip(),
                                    entries[2].get().strip(),
                                    entries[3].get().strip()):
                    messagebox.showinfo("Успех", "Данные обновлены")
                    win.destroy()
                    self.load_clients()
                else:
                    messagebox.showwarning("Ошибка", "Клиент не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        self._make_form(f"Редактировать клиента ID={cid}",
                        ["ФИО:", "Телефон:", "Email:", "Примечания:"],
                        defaults=[vals[1], vals[2], vals[3], vals[5]],
                        on_save=save)

    # --- удаление ---
    def delete_client(self):
        cid = self.get_selected_id()
        if cid is None:
            return
        if not messagebox.askyesno("Подтверждение",
                                    f"Удалить клиента ID={cid}?"):
            return
        try:
            if db.delete_client(cid):
                self.load_clients()
                self.status.config(text=f"Клиент ID={cid} удалён")
            else:
                messagebox.showwarning("Ошибка", "Клиент не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- добавление заказа ---
    def add_order_window(self):
        cid = self.get_selected_id()
        if cid is None:
            return

        def save(entries, win):
            d = entries[0].get().strip()
            if not d:
                messagebox.showwarning("Ошибка", "Описание пустое")
                return
            try:
                a = float(entries[1].get().strip())
            except ValueError:
                messagebox.showwarning("Ошибка", "Сумма должна быть числом")
                return
            try:
                oid = db.add_order(cid, d, a)
                messagebox.showinfo("Успех", f"Заказ добавлен (ID: {oid})")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        self._make_form(f"Новый заказ — клиент ID={cid}",
                        ["Описание:", "Сумма:"],
                        on_save=save)

    # --- заказы клиента ---
    def show_orders_window(self):
        cid = self.get_selected_id()
        if cid is None:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Заказы клиента ID={cid}")
        win.geometry("720x420")
        win.configure(bg="#f5f7fa")

        cols = ("id", "desc", "amount", "date", "status")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        tree.heading("id", text="ID")
        tree.heading("desc", text="Описание")
        tree.heading("amount", text="Сумма")
        tree.heading("date", text="Дата")
        tree.heading("status", text="Статус")
        tree.column("id", width=45, anchor=tk.CENTER)
        tree.column("desc", width=260)
        tree.column("amount", width=100, anchor=tk.E)
        tree.column("date", width=100, anchor=tk.CENTER)
        tree.column("status", width=110, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        def load_orders():
            for row in tree.get_children():
                tree.delete(row)
            try:
                orders = db.get_client_orders(cid)
                for o in orders:
                    tree.insert("", tk.END,
                        values=(o[0], o[1], f"{o[2]:.2f}", str(o[3]), o[4]))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        load_orders()

        status_frame = tk.Frame(win, bg="#f5f7fa")
        status_frame.pack(fill=tk.X, padx=12, pady=8)

        tk.Label(status_frame, text="Новый статус:", bg="#f5f7fa",
                 font=("Arial", 11)).pack(side=tk.LEFT)
        status_var = tk.StringVar(value="новый")
        combo = ttk.Combobox(status_frame, textvariable=status_var,
                             values=["новый", "в работе", "выполнен", "отменён"],
                             width=14, font=("Arial", 11), state="readonly")
        combo.pack(side=tk.LEFT, padx=6)

        def change_status():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Внимание", "Выберите заказ")
                return
            oid = tree.item(sel[0])["values"][0]
            try:
                if db.update_order_status(oid, status_var.get()):
                    load_orders()
                else:
                    messagebox.showwarning("Ошибка", "Заказ не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(status_frame, text="Применить", style="Small.TButton",
                   command=change_status).pack(side=tk.LEFT, padx=4)

    # --- сводный отчет ---
    def show_report(self):
        try:
            r = db.report_summary()
            msg = (f"Всего клиентов: {r['clients']}\n"
                   f"Всего заказов: {r['orders']}\n"
                   f"Общая сумма: {r['total_sum']:.2f} руб.")
            messagebox.showinfo("Сводный отчёт", msg)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
