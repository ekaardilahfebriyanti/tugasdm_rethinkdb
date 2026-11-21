import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# Load file jadwal_bimbingan.json
with open("Json/jadwal_bimbingan.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Buat tabel jadwal_bimbingan dengan id_jadwal_bimbingan sebagai primary key jika belum ada
tables = r.table_list().run(conn)
if "jadwal_bimbingan" not in tables:
    r.table_create("jadwal_bimbingan", primary_key="id_jadwal_bimbingan").run(conn)

# Insert hanya dokumen dengan id_jadwal_bimbingan yang belum ada (abaikan yang sudah ada)
result = r.table("jadwal_bimbingan").insert(
    data,
    conflict=lambda id, old_doc, new_doc: old_doc
).run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen
count = r.table("jadwal_bimbingan").count().run(conn)
print("Total:", count)

conn.close()