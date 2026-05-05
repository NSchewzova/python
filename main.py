import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

HISTORY_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("550x500")
        self.root.resizable(False, False)

        # Переменные для управления
        self.length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        # Загружаем историю
        self.history = self.load_history()

        # Создаём интерфейс
        self.create_widgets()
        self.update_history_display()

    # ------------- Работа с JSON -------------
    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    # ------------- Генерация пароля -------------
    def generate_password(self):
        # Проверяем, что выбран хотя бы один набор символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов!")
            return ""

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters  # верхний + нижний регистр
        if self.use_symbols.get():
            chars += string.punctuation

        length = self.length.get()
        # Валидация длины
        if length < 1:
            length = 1
        elif length > 100:
            length = 100
            messagebox.showwarning("Предупреждение", "Длина ограничена 100 символами.")

        password = ''.join(random.choice(chars) for _ in range(length))
        return password

    # ------------- Обработчики кнопок -------------
    def on_generate(self):
        pwd = self.generate_password()
        if not pwd:
            return
        # Очищаем поле и вставляем новый пароль
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, pwd)

        # Добавляем в историю
        self.history.append(pwd)
        self.save_history()
        self.update_history_display()

    def copy_to_clipboard(self):
        pwd = self.password_entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Нет сгенерированного пароля.")

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history.clear()
            self.save_history()
            self.update_history_display()

    # ------------- Обновление интерфейса -------------
    def update_history_display(self):
        # Очищаем таблицу
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        # Заполняем заново (последние 20 записей для наглядности)
        for idx, pwd in enumerate(reversed(self.history[-20:]), start=1):
            self.history_tree.insert("", tk.END, values=(idx, pwd))

    # ------------- Создание виджетов -------------
    def create_widgets(self):
        # --- Верхняя панель настройки ---
        frame_settings = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        frame_settings.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        tk.Label(frame_settings, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_slider = tk.Scale(frame_settings, from_=1, to=50, orient="horizontal",
                                      variable=self.length, length=200)
        self.length_slider.grid(row=0, column=1, padx=10, pady=5)
        self.length_label = tk.Label(frame_settings, textvariable=self.length)
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы
        tk.Checkbutton(frame_settings, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", pady=5)
        tk.Checkbutton(frame_settings, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w", pady=5)
        tk.Checkbutton(frame_settings, text="Спецсимволы (!@#$...)", variable=self.use_symbols).grid(row=1, column=2, sticky="w", pady=5)

        # --- Поле вывода пароля ---
        frame_output = tk.LabelFrame(self.root, text="Сгенерированный пароль", padx=10, pady=10)
        frame_output.pack(fill="x", padx=10, pady=5)

        self.password_entry = tk.Entry(frame_output, font=("Courier", 12), width=40)
        self.password_entry.pack(side="left", padx=5, fill="x", expand=True)

        tk.Button(frame_output, text="Копировать", command=self.copy_to_clipboard).pack(side="right", padx=5)

        # --- Кнопка генерации ---
        tk.Button(self.root, text="Сгенерировать пароль", command=self.on_generate,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # --- История ---
        frame_history = tk.LabelFrame(self.root, text="История паролей (последние 20)", padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("#", "Пароль")
        self.history_tree = ttk.Treeview(frame_history, columns=columns, show="headings", height=8)
        self.history_tree.heading("#", text="№")
        self.history_tree.heading("Пароль", text="Пароль")
        self.history_tree.column("#", width=40, anchor="center")
        self.history_tree.column("Пароль", width=350)
        self.history_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_history, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(frame_history, text="Очистить историю", command=self.clear_history,
                  bg="#f44336", fg="white").pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()