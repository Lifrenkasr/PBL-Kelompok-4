from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from flask import abort
import os
# import requests  # Import library untuk berkomunikasi dengan ESP32


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

#Configure MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/project_pbl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    nim_nip = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=False, default='default_profile.png')
    role = db.Column(db.String(255), nullable=False, default='user')  # 'user' atau 'admin'

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    log_time = db.Column(db.DateTime, nullable=False)
    action = db.Column(db.String(255), nullable=False)

class Jadwal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)
    class_name = db.Column(db.String(255), nullable=False)
    
# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = user.username
            session['role'] = user.role  # Tetapkan peran dalam sesi
            log_time = datetime.now()
            action = "Login"
            access_log = AccessLog(username=username, log_time=log_time, action=action)
            db.session.add(access_log)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash(f'Login failed. Check your username and password.')
    return render_template('log.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        status = request.form['status']
        nim_nip = request.form['nim_nip']
        username = request.form['username']
        password = request.form['password']
        konfirmasi_password = request.form['konfirmasi_password']
        profile_picture = request.form['profile_picture']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Choose a different one.')
            return redirect(url_for('register'))

        if password == konfirmasi_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(nama=nama, status=status, nim_nip=nim_nip, username=username, password=hashed_password, profile_picture=profile_picture)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.')

    return render_template('registrasi.html')

# Rute Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

        if user:
            profile_picture = user.profile_picture or 'default_profile.png'
            role = session.get('role', 'user')  # Tetapkan 'user' secara default jika peran tidak diatur

            access_logs = AccessLog.query.order_by(AccessLog.log_time.desc()).limit(1000).all()
            print(access_logs)  # Cek apakah data berhasil diambil

            if role == 'user':
                # Pengguna hanya dapat mengakses view room schedule dan door access
                return render_template('user_dashboard.html', access_logs=access_logs, profile_picture=profile_picture)
            elif role == 'admin':
                # Admin dapat mengakses fitur lebih banyak
                return render_template('Dashboard.html', access_logs=access_logs, profile_picture=profile_picture)
    
    return redirect(url_for('login'))

# Rute untuk menampilkan daftar jadwal
@app.route('/jadwal', methods=['GET'])
def jadwal_list():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

        if user:
            profile_picture = user.profile_picture or 'default_profile.png'

            jadwal_list = Jadwal.query.all()

            return render_template('jadwal_list.html', jadwal_list=jadwal_list, profile_picture=profile_picture)
        else:
            return redirect(url_for('login'))
    
@app.route('/jadwal/add', methods=['GET', 'POST'])
def add_jadwal():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

        if user:
            profile_picture = user.profile_picture or 'default_profile.png'

            if request.method == 'POST':
                day = request.form['day']
                time = request.form['time']
                class_name = request.form['class']

                new_jadwal = Jadwal(day=day, time=time, class_name=class_name)
                db.session.add(new_jadwal)
                db.session.commit()

                flash('Jadwal berhasil ditambahkan.')
                return redirect(url_for('jadwal_list'))

            return render_template('add_jadwal.html', add_jadwal=add_jadwal, profile_picture=profile_picture)
        else:
            return redirect(url_for('login'))


@app.route('/jadwal/edit/<int:jadwal_id>', methods=['GET', 'POST'])
def edit_jadwal(jadwal_id):
    user = User.query.filter_by(username=session['username']).first()

    if user:
        profile_picture = user.profile_picture or 'default_profile.png'

        jadwal = Jadwal.query.get(jadwal_id)

        if jadwal:
            if request.method == 'POST':
                day = request.form['day']
                time = request.form['time']
                class_name = request.form['class']

                jadwal.day = day
                jadwal.time = time
                jadwal.class_name = class_name

                db.session.commit()

                flash('Jadwal berhasil diubah.')
                return redirect(url_for('jadwal_list'))

            return render_template('edit_jadwal.html', jadwal=jadwal, profile_picture=profile_picture)
        else:
            flash('Jadwal tidak ditemukan.')
            return redirect(url_for('jadwal_list'))
    else:
        return redirect(url_for('login'))

@app.route('/jadwal/delete/<int:jadwal_id>')
def delete_jadwal(jadwal_id):
    user = User.query.filter_by(username=session['username']).first()

    if user:
        jadwal = Jadwal.query.get(jadwal_id)

        if jadwal:
            db.session.delete(jadwal)
            db.session.commit()

            flash('Jadwal berhasil dihapus.')
            return redirect(url_for('jadwal_list'))
        else:
            flash('Jadwal tidak ditemukan.')
            return redirect(url_for('jadwal_list'))
    else:
        return redirect(url_for('login'))
    
@app.route('/view_jadwal', methods=['GET'])
def view_jadwal():
        user = User.query.filter_by(username=session['username']).first()

        if user:
            profile_picture = user.profile_picture or 'default_profile.png'

            jadwal_list = Jadwal.query.all()

            return render_template('view_jadwal.html', jadwal_list=jadwal_list, profile_picture=profile_picture)
        else:
            return redirect(url_for('login'))
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Rute untuk menyajikan file gambar profil
@app.route('/profile_picture/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Edit Profile route
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

        if user:
            if request.method == 'POST':
                old_password = request.form.get('old_password')

                if old_password and not bcrypt.check_password_hash(user.password, old_password):
                    flash('Old password is incorrect. Please try again.', 'old_password_error')
                    return redirect(url_for('edit_profile'))

                # Hapus foto profil lama jika ada
                if user.profile_picture and user.profile_picture != 'default_profile.png':
                    old_profile_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                    if os.path.exists(old_profile_path):
                        os.remove(old_profile_path)

                # Pengaturan foto profil baru
                if 'profile_picture' in request.files:
                    file = request.files['profile_picture']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)

                        # Ensure the target directory exists
                        target_folder = os.path.join(app.config['UPLOAD_FOLDER'])
                        os.makedirs(target_folder, exist_ok=True)

                        full_path = os.path.join(target_folder, filename)
                        file.save(full_path)
                        user.profile_picture = filename
                    else:
                        flash('Invalid image file. Use formats: png, jpg, jpeg, or gif.')

                user.nama = request.form['nama']
                user.status = request.form['status']
                user.nim_nip = request.form['nim_nip']

                new_password = request.form.get('password')
                if new_password:
                    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    user.password = hashed_password

                user.time = datetime.now()

                db.session.commit()

                flash('Profile updated successfully.')
                return redirect(url_for('dashboard'))

            return render_template('edit_profile.html', user_data=user, profile_picture=user.profile_picture or 'default_profile.png')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Rute untuk logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)  # Hapus informasi peran dari sesi
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Buat tabel-tabel dalam database jika belum ada
    app.run(debug=True, host="127.0.0.1", port=5000)