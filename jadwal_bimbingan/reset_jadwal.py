import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

# 2. Load file jadwal_bimbingan.json
with open("Json/jadwal_bimbingan.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. Reset isi tabel agar bersih dari sisa uji DML, lalu insert ulang
tables = r.table_list().run(conn)
if "jadwal_bimbingan" not in tables:
    r.table_create("jadwal_bimbingan", primary_key="id_jadwal_bimbingan").run(conn)
else:
    r.table("jadwal_bimbingan").delete().run(conn)

result = r.table("jadwal_bimbingan").insert(data, conflict="replace").run(conn)
print("Insertion result:", result)
print("Total:", r.table("jadwal_bimbingan").count().run(conn))

conn.close()