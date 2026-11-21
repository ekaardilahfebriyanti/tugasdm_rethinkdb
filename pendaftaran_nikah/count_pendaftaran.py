import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# 2. Jalankan query (gunakan tanda kutip pada key dictionary dan akhiri dengan .run(conn))
cursor = r.db("kua_database").table("pendaftaran_nikah").group(
        lambda doc: {
            "tahun": doc["tanggal_akad"].split("-").nth(0),
            "bulan": doc["tanggal_akad"].split("-").nth(1),
        }
    ).count().ungroup().run(conn)

# 3. Konversi cursor menjadi list dan cetak hasilnya
hasil = list(cursor)
print(json.dumps(hasil, indent=4))
print("Total data:", len(hasil))

conn.close()