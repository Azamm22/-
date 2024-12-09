import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('courier_management.db')
cursor = conn.cursor()

# Создание таблицы пользователей, если она ещё не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Создание таблицы заявок курьеров
cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        full_name TEXT,
        contact_number TEXT,
        city TEXT,
        transport_type TEXT,
        status TEXT DEFAULT 'pending',
        reason TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Подтверждаем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблицы users и applications были успешно созданы!")
