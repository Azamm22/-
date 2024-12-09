from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Секретный ключ для сессий

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('courier_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# Главная страница с формой для авторизации
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_applications'))
            elif user['role'] == 'courier':
                return redirect(url_for('dashboard'))
        else:
            return 'Неверный логин или пароль'

    return render_template('login.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, hashed_password, 'courier'))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('register.html')

# Страница курьера
@app.route('/dashboard')
def dashboard():
    if 'role' in session and session['role'] == 'courier':
        return f"Добро пожаловать, {session['username']}! Это страница курьера."
    return redirect(url_for('home'))

# Страница администратора
@app.route('/admin_applications', methods=['GET', 'POST'])
def admin_applications():
    if 'role' in session and session['role'] == 'admin':
        conn = get_db_connection()

        if request.method == 'POST':
            action = request.form['action']
            application_id = request.form['application_id']

            if action == 'accept':
                conn.execute('''UPDATE applications SET status = 'accepted' WHERE id = ?''', (application_id,))
                conn.execute('''UPDATE users SET is_active = 1 WHERE id = (SELECT user_id FROM applications WHERE id = ?)''', (application_id,))
            elif action == 'reject':
                reason = request.form['reason']
                conn.execute('''UPDATE applications SET status = 'rejected', reason = ? WHERE id = ?''', (reason, application_id))

            conn.commit()

        applications = conn.execute('SELECT * FROM applications').fetchall()
        conn.close()
        return render_template('admin_applications.html', applications=applications)
    return redirect(url_for('home'))

# Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Страница анкеты для курьера
@app.route('/application', methods=['GET', 'POST'])
def application():
    if 'role' in session and session['role'] == 'courier':
        user_id = session['user_id']

        conn = get_db_connection()
        application_exists = conn.execute(
            'SELECT * FROM applications WHERE user_id = ?', (user_id,)
        ).fetchone()

        if application_exists:
            if application_exists['status'] == 'pending':
                return "Ваша заявка на рассмотрении."
            elif application_exists['status'] == 'accepted':
                return redirect(url_for('dashboard'))
            elif application_exists['status'] == 'rejected':
                return f"Заявка отклонена. Причина: {application_exists['reason']}"

        if request.method == 'POST':
            full_name = request.form['full_name']
            contact_number = request.form['contact_number']
            city = request.form['city']
            transport_type = request.form['transport_type']

            conn.execute('''
                INSERT INTO applications (user_id, full_name, contact_number, city, transport_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, full_name, contact_number, city, transport_type))
            conn.commit()
            conn.close()

            return "Заявка отправлена на рассмотрение."

        conn.close()
        return render_template('application.html')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
