from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime
from flask import send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
import os

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Ganti sesuai host MySQL Anda
app.config['MYSQL_USER'] = 'root'  # Ganti dengan username MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'akun_registrasi'  # Ganti dengan nama database MySQL Anda

# Inisialisasi ekstensi MySQL
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

# Rute untuk halamam login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('register'))
        username = request.form["username"]
        password = request.form["password"]

        # Periksa autentikasi pengguna
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Catat log access ke database
            log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action = "Login"
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO access_log (username, log_time, action) VALUES (%s, %s, %s)", (username, log_time, action))
            mysql.connection.commit()
            cur.close()

            session['username'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash(f'Login gagal. Cek kembali username dan password.')

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
        profile_picture = request.form['profile_picture']

        # Periksa apakah password sesuai
        if password == konfirmasi_password:
            # Koneksi ke MySQL
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (nama, status, nim_nip, username, password, profile_picture) VALUES (%s, %s, %s, %s, %s, %s)",
            (nama, status, nim_nip, username, password, profile_picture))
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
        
    if 'username' in session:
            # Koneksi ke database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM access_log ORDER BY log_time DESC LIMIT 1000")  # Ambil 10 log terakhir
        access_logs = cur.fetchall()
        cur.close()

        return render_template('dashboard.html', access_logs=access_logs, profile_picture=profile_picture)
    else:
        return redirect(url_for('login'))
    
# Rute untuk menampilkan daftar jadwal
@app.route('/jadwal', methods=['GET'])
def jadwal_list():
            if 'username' in session:
                    # Koneksi ke database
                cur = mysql.connection.cursor()
                cur.execute("SELECT profile_picture FROM users WHERE username = %s", (session['username'],))
                user_data = cur.fetchone()
                cur.close()

                profile_picture = user_data[0] if user_data and len(user_data) > 0 else 'default_profile.png'

                
                cur = mysql.connection.cursor()
                cur.execute("SELECT id, day, time, class FROM jadwal")
                jadwal_list = [Jadwal(id=row[0], day=row[1], time=row[2], class_name=row[3]) for row in cur.fetchall()]
                cur.close()
                
                return render_template('jadwal_list.html', jadwal_list=jadwal_list, profile_picture=profile_picture)
            else: 
                return redirect(url_for('login'))


@app.route('/jadwal/add', methods=['GET', 'POST'])
def add_jadwal():
            if 'username' in session:
                    # Koneksi ke database
                cur = mysql.connection.cursor()
                cur.execute("SELECT profile_picture FROM users WHERE username = %s", (session['username'],))
                user_data = cur.fetchone()
                cur.close()

                profile_picture = user_data[0] if user_data and len(user_data) > 0 else 'default_profile.png'

               
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

                return render_template('add_jadwal.html',add_jadwal=add_jadwal, profile_picture=profile_picture)
            else: 
                return redirect(url_for('login'))


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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/profile_picture/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Ambil data pengguna dari database dan teruskan ke templat
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
    user_data = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        # Ambil data dari formulir edit profil
        nama = request.form['nama']
        status = request.form['status']
        nim_nip = request.form['nim_nip']
        username = request.form['username']
        old_password = request.form['old_password']  # Tambah input untuk password lama
        new_password = request.form['password']
        
        # Verifikasi password lama sebelum mengubah
        if old_password != user_data[4]:  # Jika password lama tidak sesuai dengan yang ada di database
            flash('Password lama salah. Silakan coba lagi.')
            return redirect(url_for('edit_profile'))

        # Unggah gambar profil
        filename = user_data[6]  # Mengasumsikan jalur gambar profil berada pada kolom ke-7
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('File gambar tidak valid. Gunakan format: png, jpg, jpeg, atau gif.')

        # Koneksi ke database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET nama = %s, status = %s, nim_nip = %s, password = %s, profile_picture = %s, time = %s WHERE username = %s",
                    (nama, status, nim_nip, new_password, filename, datetime.now(), username))
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
    app.secret_key = 'your_secret_key'
app.run(debug=True, host="127.0.0.1", port=5000)