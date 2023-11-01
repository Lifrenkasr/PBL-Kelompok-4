from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Ganti sesuai host MySQL Anda
app.config['MYSQL_USER'] = 'root'  # Ganti dengan username MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'akun_registrasi'  # Ganti dengan nama database MySQL Anda

# Inisialisasi ekstensi MySQL
mysql = MySQL(app)

# Halaman registrasi
@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
