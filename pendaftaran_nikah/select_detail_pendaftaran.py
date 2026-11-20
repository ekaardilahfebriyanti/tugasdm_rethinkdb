import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# 2. Jalankan query dengan sintaks Python (lambda, tanda kutip pada key, dan kurung siku)
cursor = (
    r.db("kua_database")
    .table("pendaftaran_nikah")
    .merge(
        lambda pendaftaran: {
            "identitas_suami": r.db("kua_database")
            .table("penduduk")
            .get(pendaftaran["nik_suami"]),
            "identitas_istri": r.db("kua_database")
            .table("penduduk")
            .get(pendaftaran["nik_istri"]),
        }
    )
    .run(conn)
)

# 3. Konversi cursor menjadi list dan cetak hasilnya
hasil = list(cursor)
print(json.dumps(hasil, indent=4))
print("Total data:", len(hasil))

conn.close()