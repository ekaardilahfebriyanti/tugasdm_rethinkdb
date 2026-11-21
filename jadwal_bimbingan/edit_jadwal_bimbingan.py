import json
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

hasil = (
    r.db("kua_database")
    .table("jadwal_bimbingan")
    .get(102)
    .update({"nip_penyuluh": "198901062026101003"})
    .run(conn)
)

print(json.dumps(hasil, indent=4))
conn.close()