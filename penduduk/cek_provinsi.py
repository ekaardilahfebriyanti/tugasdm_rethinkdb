import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# 2. Filter dokumen yang tidak memiliki atribut 'provinsi' atau nilainya kosong/null
cursor = (
    r.db("kua_database")
    .table("penduduk")
    .filter(
        lambda doc: (doc.has_fields("provinsi").not_())
        | (doc["provinsi"].default("") == "")
    )
    .run(conn)
)

# 3. Cetak seluruh data yang ditemukan beserta jumlahnya
hasil = list(cursor)
print(json.dumps(hasil, indent=4))
print("Total data tanpa provinsi:", len(hasil))

conn.close()