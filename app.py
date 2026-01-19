import psycopg2
import pandas as pd
from tabulate import tabulate
from sqlalchemy import create_engine

# Создаем движок SQLAlchemy
engine = create_engine('postgresql://misha:1986@localhost:5432/employees')


def fetch_employees(filter_by=None, filter_value=None, sort_by=None):
    conn = psycopg2.connect(
        dbname='employees', user='misha', password='1986', host='localhost', port='5432'
    )
    query = "SELECT id, full_name, position, hire_date, salary, manager_id FROM employees"
    params = ()
    if filter_by and filter_value:
        query += f" WHERE {filter_by} ILIKE %s"
        params = (f"%{filter_value}%",)
    if sort_by:
        query += f" ORDER BY {sort_by}"
    # Используйте движок вместо соединения
    df = pd.read_sql(query, engine, params=params)
    conn.close()
    return df

def main():
    while True:
        print("\nВыберите операцию:")
        print("1 - Посмотреть всех сотрудников")
        print("2 - Фильтровать по должности")
        print("3 - Фильтровать по имени")
        print("4 - Отсортировать по зарплате")
        print("5 - Выйти")
        choice = input("Ваш выбор: ")

        if choice == '1':
            df = fetch_employees()
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        elif choice == '2':
            position = input("Введите должность: ")
            df = fetch_employees('position', position)
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        elif choice == '3':
            name = input("Введите имя или часть имени: ")
            df = fetch_employees('full_name', name)
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        elif choice == '4':
            df = fetch_employees(sort_by='salary')
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        elif choice == '5':
            break
        else:
            print("Некорректный выбор.")

if __name__ == '__main__':
    main()