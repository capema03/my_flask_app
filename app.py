from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)

# Kunci rahasia untuk Flask
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')  # Ganti dengan kunci rahasia yang lebih aman di produksi

# Konfigurasi lokasi database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi SQLAlchemy
db = SQLAlchemy(app)


# Definisi model tabel ContactMessage
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<ContactMessage {self.name}>'


# Fungsi validasi email
def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@gmail\.com\b$'
    return re.match(regex, email)


# Route utama untuk pengiriman pesan
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Validasi input
        if not name or not email or not message:
            flash('Harap isi semua bidang.', 'error')
            return redirect(url_for('index'))

        if not is_valid_email(email):
            flash('Harap masukkan alamat Gmail yang valid.', 'error')
            return redirect(url_for('index'))

        # Simpan pesan ke database
        new_message = ContactMessage(name=name, email=email, message=message)
        try:
            db.session.add(new_message)
            db.session.commit()
            flash('Pesan berhasil dikirim!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat mengirim pesan Anda.', 'error')
            print(f"Error: {e}")

        return redirect(url_for('index'))

    return render_template('index.html')


# Route untuk melihat semua pesan
@app.route('/messages')
def messages():
    all_messages = ContactMessage.query.all()
    return render_template('messages.html', messages=all_messages)


if __name__ == '__main__':
    # Buat tabel jika belum ada
    with app.app_context():
        db.create_all()
    app.run(debug=True)
