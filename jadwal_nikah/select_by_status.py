import json
from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

hasil = (
    r.db("kua_database")
    .table("akta_nikah")
    .group("tanggal_pengeluaran")
    .count()
    .ungroup()
    .order_by("group")
    .run(conn)
)

print(json.dumps(hasil, indent=4))

conn.close()