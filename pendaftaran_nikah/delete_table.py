from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Hapus tabel pemeriksaan_pendaftaran jika ada
if "pendaftaran_nikah" in r.table_list().run(conn):
    result = r.table_drop("pendaftaran_nikah").run(conn)
    print("Tabel berhasil dihapus:", result)
else:
    print("Tabel pendaftaran_nikah tidak ditemukan.")

conn.close()