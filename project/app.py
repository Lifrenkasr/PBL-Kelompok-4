from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://root:@localhost/akun_registrasi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = 'KUCINGDALAMSELIMUT'

db = SQLAlchemy(app)

class Users(db.Model):
   
    nama = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    nim_nip = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(30), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

# Rute untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'register' in request.form:  # Jika tombol register diklik
            return redirect(url_for('register'))  # Arahkan ke halaman registrasi
        username = request.form["username"]
        password = request.form["password"]

        # Periksa autentikasi Users (ganti dengan logika autentikasi sesuai kebutuhan)
        user = Users.query.filter_by(username=username).first()

        if user is None:
            flash("Login Gagal User Tidak Ditemukan", 'danger')
        elif password != Users.password:
            flash("Password Salah!", 'danger')
        else:
            session['username'] = True
            return redirect(url_for('dashboard'))
        # if user is None:
        #     session['username'] = True
        #     # Autentikasi berhasil, arahkan ke halaman dashboard setelah login
        #     return redirect(url_for('dashboard'))  # Ubah ke rute dashboard di sini
        # else:
        #     flash(f'Login gagal. Cek kembali username dan password.')
        #     print(f'Login gagal. Cek kembali username dan password.')
    return render_template('log.html')


# Rute untuk halaman registrasi
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

        user = Users.query.filter_by(username=username).first()

        if user:
            flash("User already exist", 'danger')
        elif password != konfirmasi_password:
            flash("Password didn't match", 'danger')
        else:
            new_user = Users(nama=nama, status=status, nim_nip=nim_nip, username=username, password=password)
            db.session.add(new_user)
            db.session.commit() 
            flash("Sign-Up Success!, you can log in now", 'success')
            return redirect(url_for('login'))

        # Periksa apakah password sesuai
        # if password == konfirmasi_password:
        #     # Koneksi ke MySQL
        #     cur = mysql.connection.cursor()
        #     cur.execute("INSERT INTO users (nama, status, nim_nip, username, password) VALUES (%s, %s, %s, %s, %s)",
        #                 (nama, status, nim_nip, username, password))
        #     mysql.connection.commit()
        #     cur.close()
        #     flash('Registrasi berhasil. Silakan login.')
        #     return redirect(url_for('login'))
        # else:
        #     flash('Password tidak sesuai.')
    return render_template('registrasi.html')

# Rute untuk halaman Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('Dashboard.html')

# Rute untuk halaman jadwal ruangan
@app.route('/jadwal_ruangan')
def jadwal_ruangan():
    return render_template('jadwal.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
