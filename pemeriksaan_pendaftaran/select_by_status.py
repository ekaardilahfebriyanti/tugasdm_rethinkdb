import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# 2. Jalankan query (hasilnya langsung berupa dict)
hasil = (
    r.db('kua_database').table('pemeriksaan_pendaftaran')
  .group('status_pemeriksaan')
  .count()
  .run(conn)
)

# 3. Cetak hasil per status dan total keseluruhan
print(json.dumps(hasil, indent=4))
print("Total kategori status:", len(hasil))
print("Total seluruh jadwal:", sum(hasil.values()))

conn.close()