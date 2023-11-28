from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Ganti sesuai host MySQL Anda
app.config['MYSQL_USER'] = 'root'  # Ganti dengan username MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'akun_registrasi'  # Ganti dengan nama database MySQL Anda

# Inisialisasi ekstensi MySQL
mysql = MySQL(app)


class User:
    def __init__(self, username, password, nama='', status='', nim_nip=''):
        self.username = username
        self.password = password
        self.nama = nama
        self.status = status
        self.nim_nip = nim_nip

    def save_to_db(self):
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (nama, status, nim_nip, username, password) VALUES (%s, %s, %s, %s, %s)",
            (self.nama, self.status, self.nim_nip, self.username, self.password)
        )
        mysql.connection.commit()
        cur.close()


class Login:
    def __init__(self, app):
        self.app = app
        self.app.add_url_rule('/', view_func=self.login, methods=['GET', 'POST'])

    def login(self):
        if request.method == 'POST':
            # Ambil data dari formulir login
            username = request.form['username']
            password = request.form['password']

            # Periksa autentikasi pengguna (ganti dengan logika autentikasi sesuai kebutuhan)
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user_data = cur.fetchone()
            cur.close()

            if user_data:
                user = User(*user_data[3:8])  # Assuming the columns in the database match the order of User constructor
                session['username'] = user.username
                # Autentikasi berhasil, tambahkan logika sesuai kebutuhan
                return redirect(url_for('dashboard'))
            else:
                flash('Login gagal. Cek kembali username dan password.')

        return render_template('log.html')


class Registration:
    def __init__(self, app):
        self.app = app
        self.app.add_url_rule('/register', view_func=self.register, methods=['GET', 'POST'])

    def register(self):
        if request.method == 'POST':
            # Ambil data dari formulir registrasi
            nama = request.form['nama']
            status = request.form['status']
            nim_nip = request.form['nim_nip']
            username = request.form['username']
            password = request.form['password']
            konfirmasi_password = request.form['konfirmasi_password']

            # Periksa apakah password sesuai
            if password == konfirmasi_password:
                # Buat objek User dan simpan ke database
                new_user = User(username, password, nama, status, nim_nip)
                new_user.save_to_db()
                flash('Registrasi berhasil. Silakan login.')
                return redirect(url_for('login'))
            else:
                flash('Password tidak sesuai.')

        return render_template('registrasi.html')


class Dashboard:
    def __init__(self, app):
        self.app = app
        self.app.add_url_rule('/dashboard', view_func=self.dashboard)

    def dashboard(self):
        return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    login_instance = Login(app)
    registration_instance = Registration(app)
    dashboard_instance = Dashboard(app)
    app.run(debug=True)
    
    #test