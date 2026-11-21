from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Hapus tabel pemeriksaan_pendaftaran jika ada
if "pemeriksaan_pendaftaran" in r.table_list().run(conn):
    result = r.table_drop("pemeriksaan_pendaftaran").run(conn)
    print("Tabel berhasil dihapus:", result)
else:
    print("Tabel pemeriksaan_pendaftaran tidak ditemukan.")

conn.close()