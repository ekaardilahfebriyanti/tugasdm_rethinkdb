from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host='172.28.224.1', port=28015, db='kua_database')

for nama_tabel in r.table_list().run(conn):
    print(f"\n--- TABEL: {nama_tabel.upper()} ---")
    for data in r.table(nama_tabel).run(conn):
        print(data)

conn.close()