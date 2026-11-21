from rethinkdb import RethinkDB

# 1. Inisialisasi dan koneksi ke server lokal
r = RethinkDB()
conn = r.connect(host='172.28.224.1', port=28015)

NAMA_DB = 'belajar_python_db'

# 2. Buat database (dicek dulu agar tidak error jika skrip dijalankan 2x)
if NAMA_DB not in r.db_list().run(conn):
    r.db_create(NAMA_DB).run(conn)
    print(f"Database '{NAMA_DB}' berhasil dibuat.")
else:
    print(f"Database '{NAMA_DB}' sudah ada.")

# Arahkan koneksi agar default ke database yang baru dibuat
conn.use(NAMA_DB)

# 3. Buat struktur tabel ('karyawan' dan 'proyek')
tabel_yang_dibutuhkan = ['karyawan', 'proyek']
tabel_saat_ini = r.table_list().run(conn)

for nama_tabel in tabel_yang_dibutuhkan:
    if nama_tabel not in tabel_saat_ini:
        r.table_create(nama_tabel).run(conn)
        print(f"Tabel '{nama_tabel}' berhasil dibuat.")

# 4. Siapkan struktur data JSON menggunakan Python List & Dictionary
data_karyawan = [
    {
        "id": "K001",
        "nama": "Budi Santoso",
        "divisi": "Engineering",
        "aktif": True,
        "skill": ["Python", "RethinkDB", "FastAPI"],
        "kontak": {
            "email": "budi@contoh.com",
            "kota": "Bandung"
        }
    },
    {
        "id": "K002",
        "nama": "Rina Wijaya",
        "divisi": "Data Science",
        "aktif": True,
        "skill": ["Python", "Pandas", "Machine Learning"],
        "kontak": {
            "email": "rina@contoh.com",
            "kota": "Jakarta"
        }
    }
]

data_proyek = [
    {
        "kode": "PRJ-01",
        "nama_proyek": "Sistem Analitik Real-Time",
        "pic_id": "K001",
        "budget": 25000000,
        "selesai": False,
        "milestones": [
            {"tahap": "Setup DB", "status": "done"},
            {"tahap": "Integrasi API", "status": "in_progress"}
        ]
    },
    {
        "kode": "PRJ-02",
        "nama_proyek": "Prediksi Penjualan Q4",
        "pic_id": "K002",
        "budget": 18000000,
        "selesai": True,
        "milestones": [
            {"tahap": "Cleaning Data", "status": "done"},
            {"tahap": "Training Model", "status": "done"}
        ]
    }
]

# 5. Insert data ke masing-masing tabel
# conflict="replace" berguna agar jika skrip dijalankan ulang, data dengan ID sama diperbarui tanpa error duplikat
res_karyawan = r.table('karyawan').insert(data_karyawan, conflict="replace").run(conn)
print("Status insert karyawan:", res_karyawan)

# Untuk tabel 'proyek', data akan otomatis mendapat UUID unik setiap kali insert dijalankan
res_proyek = r.table('proyek').insert(data_proyek).run(conn)
print("Status insert proyek:", res_proyek)

# 6. Verifikasi dengan membaca kembali data yang baru masuk
print("\n--- DATA KARYAWAN TERSIMPAN ---")
for item in r.table('karyawan').run(conn):
    print(f"[{item['id']}] {item['nama']} - Kota: {item['kontak']['kota']} | Skill: {', '.join(item['skill'])}")

# Tutup koneksi
conn.close()