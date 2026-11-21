from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# Hapus tabel pemeriksaan_pendaftaran jika ada
if "penduduk" in r.table_list().run(conn):
    result = r.table_drop("penduduk").run(conn)
    print("Tabel berhasil dihapus:", result)
else:
    print("Tabel penduduk tidak ditemukan.")

conn.close()