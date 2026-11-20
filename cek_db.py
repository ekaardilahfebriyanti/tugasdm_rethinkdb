from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="localhost",
    port=28015
)

if "kua_database" not in r.db_list().run(conn):
    result = r.db_create("kua_database").run(conn)
    print("Database kua_database berhasil dibuat:", result)
else:
    print("Database kua_database sudah ada.")

conn.close()