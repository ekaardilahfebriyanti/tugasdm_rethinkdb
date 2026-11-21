import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi langsung ke database kua_database yang sudah ada
conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Load file JSON
with open("Json/penduduk.json", "r", encoding="utf-8") as f:
    penduduk_list = json.load(f)

with open("Json/user.json", "r", encoding="utf-8") as f:
    user_list = json.load(f)

# Daftar 11 atribut penduduk yang akan di-embed
fields_penduduk = [
    "nik",
    "nama_depan",
    "nama_belakang",
    "tanggal_lahir",
    "jenis_kelamin",
    "jalan",
    "rt",
    "rw",
    "kelurahan",
    "kecamatan",
    "kabupaten_kota"
]

# Mapping data penduduk berdasarkan NIK
penduduk_by_nik = {
    p["nik"]: {key: p[key] for key in fields_penduduk}
    for p in penduduk_list
}

# Proses embed data penduduk ke dokumen user
user_embedded = []
for u in user_list:
    nik = u.get("penduduk", {}).get("nik") or u["username"].replace("user_", "")
    user_embedded.append({
        "username": u["username"],
        "password": u["password"],
        "penduduk": penduduk_by_nik.get(nik)
    })

# Buat tabel user dengan primary_key="username" jika belum ada
tables = r.table_list().run(conn)
if "user" not in tables:
    r.table_create("user", primary_key="username").run(conn)

# Insert dokumen ke tabel user
result = r.table("user").insert(user_embedded, conflict="replace").run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen
count = r.table("user").count().run(conn)
print("Total:", count)

conn.close()