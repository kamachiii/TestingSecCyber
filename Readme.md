# VulnLab - Keamanan Web
## Fitur
- Autentikasi pengguna (Login/Logout)
- Dashboard pengguna
- Sistem komentar di halaman profil
- Fitur transfer saldo antar pengguna
- Halaman admin dasar

## Prasyarat
- Python 3.x
- pip

## Cara Menjalankan
1. Buat dan aktifin Virtual Environment (rekomend)

```cmd
python -m venv venv
source venv/bin/activate
```

2. Install dependencies dari requirements.txt

```cmd
pip install -r requirements.txt
```

3. Jalankan aplikasi

```cmd
flask run
```

4. Buka `http://127.0.0.1:5000` di browser anda


## Akun Contoh
- Username: `alice` | Password: `password123` | Role: `user`
- Username: `bob` | Password: `mypassword` | Role: `user`
- Username: `admin` | Password: `adminpass` | Role: `admin`
