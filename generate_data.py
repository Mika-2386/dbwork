import random
from datetime import date, timedelta
from mimesis import Person
import psycopg2

# Настройки подключения
DB_NAME = 'employees'
DB_USER = 'misha'
DB_PASSWORD = '1986'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Иерархия должностей
positions = {
    'CEO': {'level': 1, 'count': 1},
    'Manager': {'level': 2, 'count': 10},
    'Team Lead': {'level': 3, 'count': 40},
    'Senior Developer': {'level': 4, 'count': 150},
    'Developer': {'level': 5, 'count': 50000}
}

# Инициируем генератор данных
generic = Person('ru')

# Подключение к базе
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()

# Очистка таблицы перед вставкой новых данных
cur.execute("TRUNCATE TABLE employees RESTART IDENTITY CASCADE;")
conn.commit()

# Создаём CEO
ceo_name = generic.full_name()
hire_date = date(2010, 1, 1) + timedelta(days=random.randint(0, 365*10))
salary = round(random.uniform(150000, 300000), 2)

cur.execute(
    "INSERT INTO employees (full_name, position, hire_date, salary, manager_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
    (ceo_name, 'CEO', hire_date, salary, None)
)
ceo_id = cur.fetchone()[0]

# Храним всех сотрудников для дальнейшей привязки
def create_subordinates(manager_id, position, count):
    subordinates = []
    for _ in range(count):
        name = generic.full_name()
        hire_date = date(2010, 1, 1) + timedelta(days=random.randint(0, 365*10))
        salary = round(random.uniform(50000, 150000), 2)
        cur.execute(
            "INSERT INTO employees (full_name, position, hire_date, salary, manager_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, position, hire_date, salary, manager_id)
        )
        new_id = cur.fetchone()[0]
        subordinates.append({'id': new_id, 'full_name': name, 'position': position, 'hire_date': hire_date, 'salary': salary, 'manager_id': manager_id})
    return subordinates

# Создаем менеджеров под CEO
manager_list = create_subordinates(ceo_id, 'Manager', positions['Manager']['count'])

# Создаем Team Lead под менеджерами
team_leads = []
for m in manager_list:
    team_leads.extend(create_subordinates(m['id'], 'Team Lead', 4))  # 4 Team Lead на менеджера

# Создаем Senior Developer под Team Lead
senior_devs = []
for tl in team_leads:
    senior_devs.extend(create_subordinates(tl['id'], 'Senior Developer', 30))  # 30 Senior Dev на Team Lead

# Создаем Developer под Senior Developer
for s in senior_devs:
    create_subordinates(s['id'], 'Developer', 50)  # 50 Developer на Senior Dev

# Подтверждение
conn.commit()
cur.close()
conn.close()
print("Данные успешно сгенерированы и вставлены.")