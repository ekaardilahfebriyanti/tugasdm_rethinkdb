import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# Load file jadwal_nikah.json
with open("Json/jadwal_nikah.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Buat tabel jadwal_nikah dengan id_jadwal_nikah sebagai primary key jika belum ada
tables = r.table_list().run(conn)
if "jadwal_nikah" not in tables:
    r.table_create("jadwal_nikah", primary_key="id_jadwal_nikah").run(conn)

# Insert dokumen ke tabel jadwal_nikah
result = r.table("jadwal_nikah").insert(data, conflict="replace").run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen
count = r.table("jadwal_nikah").count().run(conn)
print("Total:", count)

conn.close()