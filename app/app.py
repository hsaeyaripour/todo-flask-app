from flask import Flask, render_template, request, redirect
import psycopg2
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # حتما اضافه کن برای session

def get_db_connection():
    conn = psycopg2.connect(
        host="db",
        database="todo",
        user="postgres",
        password="postgres"
    )
    return conn

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id_, username, password):
        self.id = id_
        self.username = username
        self.password = password

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def get_by_id(id_):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE id = %s", (id_,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(*row)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        return 'نام کاربری یا رمز عبور اشتباه است'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # اول چک می‌کنیم نام کاربری قبلاً ثبت نشده
        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            conn.close()
            return 'این نام کاربری قبلاً ثبت شده'
        
        # اگر نبود، ثبتش کن
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, task FROM tasks WHERE user_id = %s;', (current_user.id,))
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task = request.form['task']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (task, user_id) VALUES (%s, %s);', (task, current_user.id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s AND user_id = %s;', (id, current_user.id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)