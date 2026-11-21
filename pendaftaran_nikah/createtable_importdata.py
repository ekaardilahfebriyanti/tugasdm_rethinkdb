import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Load file pendaftaran_nikah.json dan pembatalan_nikah.json
with open("Json/pendaftaran_nikah.json", "r", encoding="utf-8") as f:
    pendaftaran_list = json.load(f)

with open("Json/pembatalan_nikah.json", "r", encoding="utf-8") as f:
    pembatalan_list = json.load(f)

# Petakan data pembatalan berdasarkan id_pendaftaran (tanpa mengulang field id_pendaftaran)
pembatalan_map = {}
for item in pembatalan_list:
    id_pend = item["id_pendaftaran"]
    pembatalan_map[id_pend] = {
        "id_pembatalan": item["id_pembatalan"],
        "alasan": item["alasan"],
        "status_pembatalan": item["status_pembatalan"],
        "tanggal_pembatalan": item["tanggal_pembatalan"],
        "nip_staff_admin": item["nip_staff_admin"]
    }

# Embed pembatalan_nikah ke dalam dokumen pendaftaran_nikah yang sesuai
for pendaftaran in pendaftaran_list:
    id_pend = pendaftaran["id_pendaftaran"]
    if id_pend in pembatalan_map:
        pendaftaran["pembatalan_nikah"] = pembatalan_map[id_pend]

# Buat tabel pendaftaran_nikah dengan id_pendaftaran sebagai primary key jika belum ada
tables = r.table_list().run(conn)
if "pendaftaran_nikah" not in tables:
    r.table_create("pendaftaran_nikah", primary_key="id_pendaftaran").run(conn)

# Insert dokumen ke tabel pendaftaran_nikah
result = r.table("pendaftaran_nikah").insert(pendaftaran_list, conflict="replace").run(conn)
print("Insertion result:", result)

# Tampilkan total dokumen dan jumlah dokumen yang memiliki pembatalan_nikah
total_count = r.table("pendaftaran_nikah").count().run(conn)
embedded_count = r.table("pendaftaran_nikah").has_fields("pembatalan_nikah").count().run(conn)
print("Total pendaftaran_nikah:", total_count)
print("Total dengan pembatalan_nikah (embedded):", embedded_count)

conn.close()