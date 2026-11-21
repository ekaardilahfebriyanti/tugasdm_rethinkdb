import json
from rethinkdb import RethinkDB

# 1. Koneksi langsung ke database 'belajar_python_db'
r = RethinkDB()
conn = r.connect(host='172.28.224.1', port=28015, db='belajar_python_db')

# 2. Menampilkan semua data dari tabel 'karyawan'
print("=== ISI TABEL KARYAWAN ===")
cursor_karyawan = r.table('karyawan').run(conn)
for dokumen in cursor_karyawan:
    # json.dumps dengan indent=2 membuat output tampil rapi seperti JSON asli
    print(json.dumps(dokumen, indent=2))

# 3. Menampilkan semua data dari tabel 'proyek'
print("\n=== ISI TABEL PROYEK ===")
cursor_proyek = r.table('proyek').run(conn)
for dokumen in cursor_proyek:
    print(json.dumps(dokumen, indent=2))

# Tutup koneksi
conn.close()