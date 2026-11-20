import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# Load file akta_nikah.json
with open("Json/akta_nikah.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Buat tabel akta_nikah dengan nomor_akta sebagai primary key jika belum ada
tables = r.table_list().run(conn)
if "akta_nikah" not in tables:
    r.table_create("akta_nikah", primary_key="nomor_akta").run(conn)

# Insert dokumen ke tabel akta_nikah
result = r.table("akta_nikah").insert(data, conflict="replace").run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen
count = r.table("akta_nikah").count().run(conn)
print("Total:", count)

conn.close()