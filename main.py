import os
import csv
from datetime import datetime

FILENAME = "data.csv"
DIR = "/home/towoeshi/Projects/RPP/lab3"

FIELDNAMES = ["id", "date_start", "time_start",
              "date_end", "time_end", "task_name",
              "employee_name", "quality"]

GIT_STR = "Измеение для git"

class Record:

    def __init__(self, id, date_start, time_start, date_end, time_end,
                 task_name, employee_name, quality):
        self.id = id
        self.date_start = date_start
        self.time_start = time_start
        self.date_end = date_end
        self.time_end = time_end
        self.task_name = task_name
        self.employee_name = employee_name
        self.quality = quality

    # 4. Запись значений только через __setattr__ с простой валидацией
    def __setattr__(self, name, value):
        if name == "id":
            value = int(value)
        elif name == "quality":
            value = int(value)
            if value < 0 or value > 100:
                raise ValueError("Качество должно быть от 0 до 100")
        super().__setattr__(name, value)

    # 2. Перегрузка repr и str
    def __repr__(self):
        return (f"Record(id={self.id}, task='{self.task_name}', "
                f"employee='{self.employee_name}', quality={self.quality})")

    def __str__(self):
        return (f"[{self.id}] {self.task_name} | "
                f"{self.employee_name} | качество: {self.quality}%")

    def to_dict(self):
        return {
            "id": self.id,
            "date_start": self.date_start,
            "time_start": self.time_start,
            "date_end": self.date_end,
            "time_end": self.time_end,
            "task_name": self.task_name,
            "employee_name": self.employee_name,
            "quality": self.quality
        }

    # 6. Статический метод — считает длительность задачи в часах
    @staticmethod
    def get_duration(record):
        fmt = "%Y-%m-%d %H:%M"
        start = datetime.strptime(record.date_start + " " + record.time_start, fmt)
        end = datetime.strptime(record.date_end + " " + record.time_end, fmt)
        diff = end - start
        hours = round(diff.total_seconds() / 3600, 2)
        return hours

# 3. Наследование

class UrgentRecord(Record):

    def __init__(self, id, date_start, time_start, date_end, time_end,
                 task_name, employee_name, quality, priority):
        super().__init__(id, date_start, time_start, date_end, time_end,
                         task_name, employee_name, quality)
        self.priority = priority

    def __setattr__(self, name, value):
        if name == "priority":
            value = int(value)
            if value < 1 or value > 5:
                raise ValueError("Приоритет должен быть от 1 до 5")
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return (f"UrgentRecord(id={self.id}, task='{self.task_name}', "
                f"employee='{self.employee_name}', quality={self.quality}, "
                f"priority={self.priority})")

    def __str__(self):
        return f"[СРОЧНО! Приоритет {self.priority}] " + super().__str__()


# Класс коллекции задач

class TaskCollection:

    def __init__(self):
        self._records = []

    # 1. Итератор
    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self._records):
            raise StopIteration
        record = self._records[self._index]
        self._index += 1
        return record

    # 2. repr и str
    def __repr__(self):
        return f"TaskCollection(count={len(self._records)})"

    def __str__(self):
        result = f"Коллекция задач ({len(self._records)} записей):\n"
        for r in self._records:
            result += "  " + str(r) + "\n"
        return result

    # 5. Доступ по индексу
    def __getitem__(self, index):
        return self._records[index]

    def __len__(self):
        return len(self._records)

    def add(self, record):
        self._records.append(record)

    def remove_by_id(self, record_id):
        for i in range(len(self._records)):
            if self._records[i].id == record_id:
                self._records.pop(i)
                return True
        return False

    def get_next_id(self):
        if len(self._records) == 0:
            return 1
        max_id = self._records[0].id
        for r in self._records:
            if r.id > max_id:
                max_id = r.id
        return max_id + 1

    # 6. Статический метод — загрузка из CSV
    @staticmethod
    def load_from_csv(filename):
        collection = TaskCollection()
        if not os.path.exists(filename):
            print("Файл не найден.")
            return collection
        with open(filename, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = Record(
                    id=row["id"],
                    date_start=row["date_start"],
                    time_start=row["time_start"],
                    date_end=row["date_end"],
                    time_end=row["time_end"],
                    task_name=row["task_name"],
                    employee_name=row["employee_name"],
                    quality=row["quality"]
                )
                collection.add(record)
        print(f"Загружено записей: {len(collection)}")
        return collection

    def save_to_csv(self, filename):
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for r in self._records:
                writer.writerow(r.to_dict())
        print("Данные сохранены в файл.")

    # 7. Генератор — фильтрация по качеству
    def filter_by_quality(self, min_quality):
        for r in self._records:
            if r.quality >= min_quality:
                yield r

    # 7. Генератор — сортировка по строковому полю
    def sorted_by_string(self, field):
        sorted_list = sorted(self._records, key=lambda r: getattr(r, field))
        for r in sorted_list:
            yield r

    # 7. Генератор — сортировка по числовому полю
    def sorted_by_number(self, field):
        sorted_list = sorted(self._records, key=lambda r: int(getattr(r, field)))
        for r in sorted_list:
            yield r

    def print_table(self):
        if len(self._records) == 0:
            print("Нет данных для отображения.\n")
            return
        print(f"{'ID':<4} | {'Дата нач.':<12} | {'Вр.':<6} | {'Дата кон.':<12} | "
              f"{'Вр.':<6} | {'Задача':<35} | {'Исполнитель':<30} | {'Кач.':>5}")
        print("-" * 125)
        for r in self._records:
            marker = "[!]" if isinstance(r, UrgentRecord) else "   "
            print(f"{marker} {r.id:<4} | {r.date_start:<12} | {r.time_start:<6} | "
                  f"{r.date_end:<12} | {r.time_end:<6} | {r.task_name:<35} | "
                  f"{r.employee_name:<30} | {r.quality:>4}%")
        print(f"\nВсего записей: {len(self._records)}\n")



def get_default_data():
    collection = TaskCollection()
    collection.add(Record(1, "2025-11-01", "10:10", "2025-11-01", "16:30",
                          "Составление отчета", "Иванов Иван Иванович", 100))
    collection.add(Record(2, "2025-11-02", "09:00", "2025-11-02", "18:00",
                          "Разработка модуля авторизации", "Петров Петр Петрович", 95))
    collection.add(Record(3, "2025-11-03", "11:00", "2025-11-03", "12:30",
                          "Планерка отдела", "Сидорова Анна Сергеевна", 80))
    collection.add(Record(4, "2025-11-04", "14:00", "2025-11-04", "17:45",
                          "Тестирование интерфейса", "Иванов Иван Иванович", 90))
    collection.add(Record(5, "2025-11-05", "10:00", "2025-11-05", "15:00",
                          "Обновление документации", "Кузнецов Алексей Дмитриевич", 85))
    return collection

# очень важный комментарий
def main():
    print("feature two")
    collection = TaskCollection()
    print("feature one")
    while True:
        print("\nМеню программы")
        print("1. Просмотреть файлы директории")
        print("2. Загрузить данные из data.csv")
        print("3. Загрузить тестовые данные")
        print("4. Вывести все записи")
        print("5. Вывести данные, отсортированные по строковому полю (ФИО)")
        print("6. Вывести данные, отсортированные по числовому полю (ID)")
        print("7. Вывести данные по критерию (Качество >= значения)")
        print("8. Добавить запись и сохранить")
        print("9. Удалить запись по ID")
        print("10. Показать длительность задач")
        print("11. Показать repr и доступ по индексу")
        print("0. Выход")

        inp = input("\nВведите номер пункта: ").strip()

        if inp == "1":
            try:
                files = os.listdir(DIR)
                count = 0
                for f in files:
                    if os.path.isfile(os.path.join(DIR, f)):
                        count += 1
                print(f"Файлов в директории: {count}")
                print(f"Содержимое: {files}\n")
            except FileNotFoundError:
                print(f"Директория не найдена: {DIR}\n")

        elif inp == "2":
            collection = TaskCollection.load_from_csv(FILENAME)
            collection.print_table()

        elif inp == "3":
            collection = get_default_data()
            print("Тестовые данные загружены.")
            collection.print_table()

        elif inp == "4":
            collection.print_table()

        elif inp == "5":
            if len(collection) == 0:
                collection = get_default_data()
            print("\nОтсортировано по ФИО")
            result = TaskCollection()
            for r in collection.sorted_by_string("employee_name"):
                result.add(r)
            result.print_table()

        elif inp == "6":
            if len(collection) == 0:
                collection = get_default_data()
            print("\nОтсортировано по ID")
            result = TaskCollection()
            for r in collection.sorted_by_number("id"):
                result.add(r)
            result.print_table()

        elif inp == "7":
            if len(collection) == 0:
                collection = get_default_data()
            try:
                threshold = int(input("Минимальное качество (0-100): "))
                print(f"\nЗаписи с качеством >= {threshold}")
                result = TaskCollection()
                for r in collection.filter_by_quality(threshold):
                    result.add(r)
                result.print_table()
            except ValueError:
                print("Ошибка: введите целое число.\n")

        elif inp == "8":
            if len(collection) == 0:
                collection = get_default_data()
            print("\nДобавление новой записи")
            try:
                is_urgent = input("Срочная задача? (д/н): ").strip().lower()
                new_id = collection.get_next_id()
                date_start = input("Дата начала (ГГГГ-ММ-ДД): ").strip()
                time_start = input("Время начала (ЧЧ:ММ): ").strip()
                date_end = input("Дата конца (ГГГГ-ММ-ДД): ").strip()
                time_end = input("Время конца (ЧЧ:ММ): ").strip()
                task_name = input("Наименование задачи: ").strip()
                employee_name = input("ФИО исполнителя: ").strip()
                quality = input("Качество выполнения (0-100): ").strip()

                if is_urgent == "д":
                    priority = input("Приоритет (1-5): ").strip()
                    record = UrgentRecord(new_id, date_start, time_start,
                                         date_end, time_end, task_name,
                                         employee_name, quality, priority)
                else:
                    record = Record(new_id, date_start, time_start,
                                    date_end, time_end, task_name,
                                    employee_name, quality)

                collection.add(record)
                collection.save_to_csv(FILENAME)
                print(f"Добавлена запись: {record}\n")
            except ValueError as e:
                print(f"Ошибка: {e}\n")

        elif inp == "9":
            if len(collection) == 0:
                collection = get_default_data()
            try:
                del_id = int(input("Введите ID для удаления: "))
                if collection.remove_by_id(del_id):
                    print(f"Запись с id={del_id} удалена.")
                    collection.save_to_csv(FILENAME)
                else:
                    print(f"Запись с id={del_id} не найдена.")
            except ValueError:
                print("Ошибка: введите целое число.\n")

        elif inp == "10":
            if len(collection) == 0:
                collection = get_default_data()
            print("\nДлительность задач")
            for r in collection:
                hours = Record.get_duration(r)
                print(f"  {r.task_name:<35}: {hours} ч.")
            print()

        elif inp == "11":
            if len(collection) == 0:
                collection = get_default_data()
            print("\nrepr 7 записи (collection[0])")
            print(repr(collection[6]))
            print("\nВторая запись (collection[1])")
            print(collection[1])
            print(f"\nrepr коллекции")
            print(repr(collection))

        elif inp == "0":
            print("Программа завершена.")
            break

        else:
            print("Неверный ввод. Попробуйте снова.\n")


if __name__ == "__main__":
    main()