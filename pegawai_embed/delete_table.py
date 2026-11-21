from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Hapus tabel pemeriksaan_pendaftaran jika ada
if "penyuluh" in r.table_list().run(conn):
    result = r.table_drop("penyuluh").run(conn)
    print("Tabel berhasil dihapus:", result)
else:
    print("Tabel penyuluh tidak ditemukan.")

conn.close()