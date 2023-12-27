from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'akun_registrasi'
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

class Jadwal:
    def __init__(self, id, day, time, class_name):
        self.id = id
        self.day = day
        self.time = time
        self.class_name = class_name

# Rute untuk halaman login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('register'))
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal. Cek kembali username dan password.')

    return render_template('log.html')

# Rute untuk halaman registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        status = request.form['status']
        nim_nip = request.form['nim_nip']
        username = request.form['username']
        password = request.form['password']
        konfirmasi_password = request.form['konfirmasi_password']

        if password == konfirmasi_password:
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
    if 'username' in session:
        # Koneksi ke database
        cur = mysql.connection.cursor()
        cur.execute("SELECT profile_picture FROM users WHERE username = %s", (session['username'],))
        user_data = cur.fetchone()
        cur.close()

        profile_picture = user_data[0] if user_data and len(user_data) > 0 else 'default_profile.png'


        return render_template('Dashboard.html', profile_picture=profile_picture)
    else:
        return redirect(url_for('login'))
    
# Rute untuk menampilkan daftar jadwal
# Rute untuk menampilkan daftar jadwal
@app.route('/jadwal', methods=['GET'])
def jadwal_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, day, time, class FROM jadwal")
    jadwal_list = [Jadwal(id=row[0], day=row[1], time=row[2], class_name=row[3]) for row in cur.fetchall()]
    cur.close()
    return render_template('jadwal_list.html', jadwal_list=jadwal_list)



@app.route('/jadwal/add', methods=['GET', 'POST'])
def add_jadwal():
    if request.method == 'POST':
        day = request.form['day']
        time = request.form['time']
        class_name = request.form['class']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jadwal (day, time, class) VALUES (%s, %s, %s)", (day, time, class_name))
        mysql.connection.commit()
        cur.close()
        flash('Jadwal berhasil ditambahkan.')
        return redirect(url_for('jadwal_list'))

    return render_template('add_jadwal.html')

@app.route('/jadwal/edit/<int:jadwal_id>', methods=['GET', 'POST'])
def edit_jadwal(jadwal_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jadwal WHERE id = %s", (jadwal_id,))
    jadwal_data = cur.fetchone()
    cur.close()

    if jadwal_data:
        jadwal = Jadwal(id=jadwal_data[0], day=jadwal_data[1], time=jadwal_data[2], class_name=jadwal_data[3])

        if request.method == 'POST':
            day = request.form['day']
            time = request.form['time']
            class_name = request.form['class']

            cur = mysql.connection.cursor()
            cur.execute("UPDATE jadwal SET day = %s, time = %s, class = %s WHERE id = %s",
                        (day, time, class_name, jadwal_id))
            mysql.connection.commit()
            cur.close()
            flash('Jadwal berhasil diubah.')
            return redirect(url_for('jadwal_list'))

        return render_template('edit_jadwal.html', jadwal=jadwal)

    else:
        flash('Jadwal tidak ditemukan.')
        return redirect(url_for('jadwal_list'))

@app.route('/jadwal/delete/<int:jadwal_id>')
def delete_jadwal(jadwal_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jadwal WHERE id = %s", (jadwal_id,))
    mysql.connection.commit()
    cur.close()
    flash('Jadwal berhasil dihapus.')
    return redirect(url_for('jadwal_list'))

    
# Fungsi bantu untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rute untuk mengakses file gambar profil
@app.route('/profile_picture/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rute untuk mengedit profil
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
    user_data = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        nama = request.form['nama']
        status = request.form['status']
        nim_nip = request.form['nim_nip']
        username = request.form['username']
        password = request.form['password']

        filename = user_data[6]
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('File gambar tidak valid. Gunakan format: png, jpg, jpeg, atau gif.')

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET nama = %s, status = %s, nim_nip = %s, password = %s, profile_picture = %s WHERE username = %s",
                    (nama, status, nim_nip, password, filename, username))
        mysql.connection.commit()
        cur.close()
        flash('Profil berhasil diubah.')
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', user_data=user_data)

# Rute untuk logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, host="127.0.0.1", port=5000)