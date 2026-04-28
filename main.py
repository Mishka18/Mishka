import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from pathlib import Path
from webbrowser import get

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - Планировщик тренировок")
        self.root.geometry("800x600")
        
        # Данные для хранения тренировок
        self.trainings = []
        self.filtered_trainings = []
        
        # Типы тренировок
        self.training_types = ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Другое"]
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных из JSON
        self.load_from_json()
        
        # Обновление таблицы
        self.update_table()
    
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.type_combo = ttk.Combobox(input_frame, values=self.training_types, width=15)
        self.type_combo.grid(row=0, column=3, padx=5)
        self.type_combo.set("Бег")
        
        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5)
        
        # Кнопка Добавить
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10)
        
        # Рамка для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все"] + self.training_types, width=15)
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")
        self.filter_type.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=3, padx=5)
        self.filter_date.bind('<KeyRelease>', self.apply_filter)
        
        # Кнопка сброса фильтра
        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_btn.grid(row=0, column=4, padx=10)
        
        # Таблица для отображения тренировок
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создание Treeview
        columns = ("Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Добавление scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Git Commit", command=self.git_commit).pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def validate_date(self, date_str):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get()
        training_type = self.type_combo.get()
        duration = self.duration_entry.get()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление тренировки
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        
        self.trainings.append(training)
        self.update_table()
        self.status_bar.config(text=f"Добавлена тренировка: {date} - {training_type} - {duration} мин")
        
        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
    
    def update_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Определение отображаемых данных
        if self.filtered_trainings:
            display_data = self.filtered_trainings
        else:
            display_data = self.trainings
        
        # Сортировка по дате
        display_data.sort(key=lambda x: x['date'])
        
        # Добавление данных в таблицу
        for training in display_data:
            self.tree.insert("", tk.END, values=(
                training['date'],
                training['type'],
                f"{training['duration']:.1f}"
            ))
    
    def apply_filter(self, event=None):
        """Применение фильтрации"""
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get()
        
        self.filtered_trainings = []
        
        for training in self.trainings:
            # Фильтр по типу
            if filter_type != "Все" and training['type'] != filter_type:
                continue
            
            # Фильтр по дате
            if filter_date and filter_date not in training['date']:
                continue
            
            self.filtered_trainings.append(training)
        
        self.update_table()
        self.status_bar.config(text=f"Найдено тренировок: {len(self.filtered_trainings)}")
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.filtered_trainings = []
        self.update_table()
        self.status_bar.config(text="Фильтр сброшен")
    
    def delete_selected(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            # Получение индекса удаляемого элемента
            item = selected[0]
            values = self.tree.item(item)['values']
            
            # Поиск и удаление тренировки
            for i, training in enumerate(self.trainings):
                if (training['date'] == values[0] and 
                    training['type'] == values[1] and 
                    str(training['duration']) == values[2]):
                    del self.trainings[i]
                    break
            
            # Очистка фильтрованных данных
            self.filtered_trainings = []
            self.update_table()
            self.status_bar.config(text="Тренировка удалена")
    
    def save_to_json(self):
        """Сохранение данных в JSON файл"""
        try:
            with open('trainings.json', 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            self.status_bar.config(text="Данные сохранены в trainings.json")
            messagebox.showinfo("Успех", "Данные успешно сохранены в trainings.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_json(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists('trainings.json'):
            self.status_bar.config(text="Файл trainings.json не найден")
            return
        
        try:
            with open('trainings.json', 'r', encoding='utf-8') as f:
                self.trainings = json.load(f)
            self.filtered_trainings = []
            self.update_table()
            self.status_bar.config(text=f"Загружено {len(self.trainings)} тренировок")
            messagebox.showinfo("Успех", f"Загружено {len(self.trainings)} тренировок")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def git_commit(self):
        """Сохранение изменений в Git"""
        try:
            repo_path = Path.cwd()
            repo = get.Repo(repo_path)
            
            # Добавление файлов
            repo.index.add(['trainings.json', 'training_planner.py'])
            
            # Создание коммита
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-commit: Обновление тренировок от {timestamp}"
            repo.index.commit(commit_message)
            
            self.status_bar.config(text=f"Git коммит создан: {commit_message}")
            messagebox.showinfo("Успех", f"Изменения сохранены в Git\n{commit_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Git операция не удалась: {e}")

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()