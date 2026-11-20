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
    r.db('kua_database').table('akta_nikah')
  .group('tanggal_pengeluaran')
  .count()
  .run(conn)
)

# 3. Konversi cursor menjadi list dan cetak hasilnya
hasil = list(cursor)
print(json.dumps(hasil, indent=4))
print("Total data:", len(hasil))

conn.close()