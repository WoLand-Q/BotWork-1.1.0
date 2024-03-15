import sqlite3
from datetime import datetime, date




connection = sqlite3.connect("db.db")
cursor = connection.cursor()

days_of_week = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]

shift_templates = {
    "Выходной": (None, None)
}


def set_schedule_template(employee_id, start_time, end_time, days):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    for day in days:
        # Проверяем, есть ли уже запись на этот день
        cursor.execute("SELECT id FROM schedules WHERE employee_id = ? AND work_day = ?", (employee_id, day))
        exists = cursor.fetchone()

        if exists:
            # Если запись есть - обновляем ее
            cursor.execute("UPDATE schedules SET start_time = ?, end_time = ? WHERE id = ?",
                           (start_time, end_time, exists[0]))
        else:
            # Если записи нет - создаем новую
            cursor.execute("INSERT INTO schedules (employee_id, work_day, start_time, end_time) VALUES (?, ?, ?, ?)",
                           (employee_id, day, start_time, end_time))

    connection.commit()
    connection.close()


def add_shift_template(name, start_time, end_time):
    shift_templates[name] = (start_time, end_time)

def get_employees_with_birthday_today():
    today = datetime.now().strftime('%d-%m')
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor()
    cursor.execute("SELECT name, username FROM employees WHERE strftime('%d-%m', birth_date) = ?", (today,))
    employees = cursor.fetchall()
    connection.close()
    return employees




def get_employee_birth_date(employee_name):
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor()

    # Запрос к БД для получения даты рождения сотрудника
    cursor.execute("SELECT birth_date FROM employees WHERE name = ?", (employee_name,))
    result = cursor.fetchone()

    connection.close()

    # Возвращаем дату рождения, если она есть, иначе None
    return result[0] if result else None



def update_employee_birth_date(employee_name, birth_date):
    connection = sqlite3.connect('db.db')  # Предполагается, что ваш файл БД называется db.db
    cursor = connection.cursor()

    # SQL-запрос для обновления даты рождения
    cursor.execute("UPDATE employees SET birth_date = ? WHERE name = ?", (birth_date, employee_name))

    connection.commit()
    connection.close()

def add_employee_to_db(name, position, birth_date):
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO employees (name, position, birth_date) VALUES (?, ?, ?)", (name, position, birth_date))
    connection.commit()
    connection.close()


def get_shift_templates():
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor()
    cursor.execute("SELECT start_time, end_time FROM shift_templates ORDER BY start_time")
    templates = cursor.fetchall()
    connection.close()
    return templates


def add_shift_template(start_time, end_time):
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO shift_templates (start_time, end_time) VALUES (?, ?)", (start_time, end_time))
    connection.commit()
    connection.close()




cursor.execute("""
CREATE TABLE IF NOT EXISTS user_bindings (
    user_id INTEGER PRIMARY KEY,
    employee_name TEXT NOT NULL,
    FOREIGN KEY (employee_name) REFERENCES employees (name)
)
""")

def get_employees_working_on_date(day):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    query = """
        SELECT e.id, e.name, s.start_time, s.end_time, ub.user_id, ub.username
        FROM schedules s
        JOIN employees e ON e.id = s.employee_id
        LEFT JOIN user_bindings ub ON e.name = ub.employee_name
        WHERE s.work_day = ?
        """

    cursor.execute(query, (day,))
    employees = cursor.fetchall()

    connection.close()

    result = [
        {
            'employee_id': row[0],
            'name': row[1],
            'start_time': row[2],
            'end_time': row[3],
            'telegram_id': row[4],
            'username': row[5]
        }
        for row in employees
    ]

    return result






def view_sales_plans():
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sales_plans")
    plans = cursor.fetchall()
    connection.close()
    return plans

# Выводим все записи из таблицы sales_plans
plans = view_sales_plans()
for plan in plans:
    print(plan)


def add_sales_plan_to_db(employee_id, day, sales_plan, tariff_plan):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Удаляем старый план для сотрудника на этот день
        cursor.execute("DELETE FROM sales_plans WHERE employee_id = ? AND day = ?", (employee_id, day))

        # Добавляем новый план
        cursor.execute("INSERT INTO sales_plans (employee_id, day, sales_plan, tariff_plan) VALUES (?, ?, ?, ?)",
                       (employee_id, day, sales_plan, tariff_plan))
        conn.commit()



#def date_to_day_of_week(date_str):
 #   if date_str in days_of_week:
  #      return date_str
   # days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    #date_object = datetime.strptime(date_str, "%Y-%m-%d")
    #day_index = date_object.weekday()
    #return days[day_index]

days_of_week_eng = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

def date_to_day_of_week(date_str):
    if date_str in days_of_week:
        return date_str
    elif date_str.upper() in days_of_week_eng:
        return days_of_week[days_of_week_eng.index(date_str.upper())]
    else:
        try:
            date_object = datetime.strptime(date_str, "%Y-%m-%d")
            day_index = date_object.weekday()
            return days_of_week[day_index]
        except ValueError:
            raise ValueError(f"Incorrect date format or day abbreviation: {date_str}")

def get_sales_plan_for_employee(employee_id, date):
    work_day = date_to_day_of_week(date)
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """SELECT sales_plan
               FROM sales_plans
               WHERE employee_id = ? AND day = ?"""
    cursor.execute(query, (employee_id, work_day))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        return None


DATABASE_PATH = "db.db"

def get_db_connection():
    connection = sqlite3.connect("db.db")
    return connection

def get_tariff_plan_for_employee(employee_id, date_str):
    work_day = date_to_day_of_week(date_str)
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tariff_plan FROM sales_plans WHERE employee_id = ? AND day = ?", (employee_id, work_day))
        result = cursor.fetchone()
        print(f"[DEBUG] tariff_plan for employee_id={employee_id} on day={date_str} is {result[0] if result else None}")
        return result[0] if result else None




def unbind_telegram_user_from_employee(user_id: int):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    # Удаляем запись из таблицы user_bindings
    cursor.execute("DELETE FROM user_bindings WHERE user_id = ?", (user_id,))

    connection.commit()
    connection.close()

def delete_schedule_from_db(employee_id, day):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE employee_id = ? AND work_day = ?", (employee_id, day))
    conn.commit()
    conn.close()


def delete_employee_and_related_data(employee_name: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    # Получаем ID сотрудника по его имени
    cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
    employee_id = cursor.fetchone()

    # Если сотрудник с таким именем найден, удаляем все связанные записи
    if employee_id:
        employee_id = employee_id[0]

        # Удаляем запись из таблицы user_bindings
        cursor.execute("DELETE FROM user_bindings WHERE employee_name = ?", (employee_name,))

        # Удаляем связанные записи из таблицы schedules
        cursor.execute("DELETE FROM schedules WHERE employee_id = ?", (employee_id,))

        # Удаляем запись из таблицы employees
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))

        connection.commit()

    connection.close()


def get_employee_name_by_telegram_id(telegram_id: int) -> str:
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT employee_name FROM user_bindings WHERE user_id = ?", (telegram_id,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


def bind_telegram_id_to_employee(telegram_id: int, employee_name: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_bindings (user_id, employee_name) VALUES (?, ?)", (telegram_id, employee_name))
    connection.commit()
    connection.close()

def add_holiday(date: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO holidays (date) VALUES (?)", (date,))
    connection.commit()
    connection.close()

def is_holiday(date: str) -> bool:
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT date FROM holidays WHERE date = ?", (date,))
    result = cursor.fetchone()
    connection.close()
    return True if result else False


def bind_user_to_employee(user_id, employee_name, username):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    # Получим employee_id на основе employee_name
    cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
    result = cursor.fetchone()
    if result:
        employee_id = result[0]
    else:
        print(f"Binding '{employee_name}' to user with ID {user_id} and username {username}")
        print(f"Employee {employee_name} not found in the database.")
        return

    # Добавляем связь в таблицу user_bindings
    cursor.execute("""
        INSERT INTO user_bindings (user_id, employee_name, username, employee_id, telegram_id)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, employee_name, username, employee_id, user_id))

    # Обновляем данные в таблице employees
    cursor.execute("""
        UPDATE employees
        SET telegram_id = ?, username = ?
        WHERE name = ?
        """, (user_id, username, employee_name))

    conn.commit()
    conn.close()



def get_employee_name_by_user_id(user_id: int) -> str:
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT employee_name FROM user_bindings WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    work_day TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees (id)
)
""")


def clear_schedule_and_plans_for_employee(employee_id: int):
    # Удаляем все записи графика для данного сотрудника
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM schedules WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM sales_plans WHERE employee_id = ?", (employee_id,))

    conn.commit()
    conn.close()


# Создание таблицы сотрудников
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")
connection.commit()
connection.close()



def add_schedule_to_db(employee_id: int, day: str, start_time: str, end_time: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    # Проверка на существование записи

    cursor.execute("SELECT id FROM schedules WHERE employee_id = ? AND work_day = ?", (employee_id, day))
    if cursor.fetchone():

        if start_time is None and end_time is None:
            cursor.execute("DELETE FROM schedules WHERE employee_id = ? AND work_day = ?", (employee_id, day))
        else:
            cursor.execute("UPDATE schedules SET start_time = ?, end_time = ? WHERE employee_id = ? AND work_day = ?",
                           (start_time, end_time, employee_id, day))
    else:

        if start_time is not None and end_time is not None:
            cursor.execute("INSERT INTO schedules (employee_id, work_day, start_time, end_time) VALUES (?, ?, ?, ?)",
                           (employee_id, day, start_time, end_time))
    connection.commit()
    connection.close()
def get_employee_id_by_name(employee_name: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
    employee_id = cursor.fetchone()
    connection.close()
    return employee_id[0] if employee_id else None

def save_report(employee_id, date, proposals, sales):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports (employee_id, date, proposals, sales)
        VALUES (?, ?, ?, ?)
        """, (employee_id, date, proposals, sales))

    conn.commit()
    conn.close()


def get_schedule_from_db(employee_name: str):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("""
    SELECT work_day, start_time, end_time 
    FROM schedules 
    INNER JOIN employees ON schedules.employee_id = employees.id
    WHERE employees.name = ?
    """, (employee_name,))
    schedule = cursor.fetchall()
    connection.close()
    return schedule



def add_employee_to_db(name: str):
    try:
        connection = sqlite3.connect("db.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,))
        connection.commit()
        connection.close()
        print(f"Employee {name} added successfully!")  # Логирование
    except Exception as e:
        print(f"Error when adding {name} to the employees table: {e}")



def get_all_employees_from_db():
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM employees")
    employees = [row[0] for row in cursor.fetchall()]
    connection.close()
    print(f"Employees from DB: {employees}")
    return employees




def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('db.db')
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY,
        image_path TEXT NOT NULL,
        upload_date TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def save_report(employee_id, proposals, sales):
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO reports (employee_id, date, proposals, sales)
        VALUES (?, date('now'), ?, ?)
        """, (employee_id, proposals, sales))
        conn.commit()


def get_unreported_employees():
    """
    Получение списка сотрудников, не отправивших отчет.
    """
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    DAY_MAPPING = {
        "MON": "ПН",
        "TUE": "ВТ",
        "WED": "СР",
        "THU": "ЧТ",
        "FRI": "ПТ",
        "SAT": "СБ",
        "SUN": "ВС"
    }

    current_day = DAY_MAPPING[datetime.now().strftime('%a').upper()]
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(current_day)

    # Получение списка сотрудников, которые должны были подать отчет сегодня

    cursor.execute("""
        SELECT DISTINCT employees.id, employees.name, employees.username, employees.telegram_id
        FROM employees
        JOIN sales_plans ON employees.id = sales_plans.employee_id
        WHERE sales_plans.day = ?
        """, (current_day,))
    employees_to_report = cursor.fetchall()

    unreported_employees = []

    for employee in employees_to_report:
        cursor.execute("""
                SELECT * FROM reports WHERE employee_id = ? AND date = ?
                """, (employee[0], current_date))
        report = cursor.fetchone()
        if not report:
            unreported_employees.append(employee)
        print(f"Report for employee {employee[1]} on {current_date}:", report)

    print("Employees to report today:", employees_to_report)

    cursor.execute("""
            SELECT DISTINCT employees.id, employees.name, employees.username 
            FROM employees
            JOIN sales_plans ON employees.id = sales_plans.employee_id
            WHERE sales_plans.day = "ЧТ"
            """)
    results = cursor.fetchall()
    print(results)

    result = cursor.fetchall()
    conn.close()
    return unreported_employees






def get_working_employees_for_today():
    today = datetime.date.today().strftime('%a').upper()  # Получаем текущий день недели
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    cursor.execute("SELECT employee_id FROM schedules WHERE work_day = ?", (today,))
    employees = cursor.fetchall()

    conn.close()
    return [employee[0] for employee in employees]


def insert_image(file_id, upload_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schedule_images (file_id, upload_date) VALUES (?, ?)", (file_id, upload_date))
    conn.commit()
    conn.close()



def get_latest_image():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM schedule_images ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row



DATABASE = "db.db"


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            work_day TEXT NOT NULL,
            start_time INTEGER,
            end_time INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_plans (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            work_day TEXT NOT NULL,
            proposals_plan INTEGER,
            sales_plan INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        ''')

        # New reports table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            report_date DATE NOT NULL,
            proposals_made INTEGER,
            sales_made INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        ''')

def get_employee_id_by_telegram_id(telegram_id: int):
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()
    cursor.execute("SELECT employee_name FROM user_bindings WHERE user_id = ?", (telegram_id,))
    employee_name = cursor.fetchone()
    if employee_name:
        employee_name = employee_name[0]
        cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
        employee_id = cursor.fetchone()
        connection.close()
        return employee_id[0] if employee_id else None
    connection.close()
    return None


def add_report(employee_id, proposals, sales):
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        today_date = date.today()
        print(f"Inserting into DB: employee_id: {employee_id}, date: {today_date}, proposals_made: {proposals}, sales_made: {sales}")
        try:
            cursor.execute("""
                INSERT INTO reports (employee_id, date, proposals_made, sales_made)
                VALUES (?, ?, ?, ?)
            """, (employee_id, today_date, proposals, sales))
            conn.commit()
        except Exception as e:
            print("Error during insertion:", e)

def has_reported_today(employee_id):
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM reports WHERE employee_id = ? AND report_date = ?
        """, (employee_id, date.today()))
        return cursor.fetchone() is not None

