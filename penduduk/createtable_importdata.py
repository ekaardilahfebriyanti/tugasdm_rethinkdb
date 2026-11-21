import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Load file penduduk.json
with open("Json/penduduk.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Buat tabel penduduk dengan nik sebagai primary key jika belum ada
tables = r.table_list().run(conn)
if "penduduk" not in tables:
    r.table_create("penduduk", primary_key="nik").run(conn)

# Insert dokumen ke tabel penduduk
result = r.table("penduduk").insert(data, conflict="replace").run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen
count = r.table("penduduk").count().run(conn)
print("Total:", count)

conn.close()