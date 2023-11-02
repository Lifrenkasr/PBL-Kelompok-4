from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Ganti sesuai host MySQL Anda
app.config['MYSQL_USER'] = 'root'  # Ganti dengan username MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'akun_registrasi'  # Ganti dengan nama database MySQL Anda

# Inisialisasi ekstensi MySQL
mysql = MySQL(app)


# Rute untuk halaman registrasi
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ambil data dari formulir login
        username = request.form['username']
        password = request.form['password']

        # Periksa autentikasi pengguna (ganti dengan logika autentikasi sesuai kebutuhan)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = user[3]
            # Autentikasi berhasil, tambahkan logika sesuai kebutuhan
            return redirect(url_for('dashboard'))
        else:
            flash(f'Login gagal. Cek kembali username dan password.')



    return render_template('log.html')


# Rute untuk halaman login
@app.route('/register', methods=['GET', 'POST'])
def register():
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
            # Koneksi ke MySQL
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (nama, status, nim_nip, username, password) VALUES (%s, %s, %s, %s, %s)",
                        (nama, status, nim_nip, username, password))
            mysql.connection.commit()
            cur.close()
            flash('Registrasi berhasil. Silakan login.')
            return redirect(url_for('login'))
        else:
            flash('Password tidak sesuai.')

    return render_template('registrasi.html')

#rute untuk halaman Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
