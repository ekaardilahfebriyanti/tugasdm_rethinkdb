import json
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# 2. Gabungkan nama dan alamat dengan penanganan field yang kosong/tidak ada
cursor = (
    r.db("kua_database")
    .table("penduduk")
    .map(
        lambda doc: {
            "nik": doc["nik"],
            "nama_lengkap": (
                doc["nama_depan"].default("")
                + r.branch(
                    doc["nama_belakang"].default("") != "",
                    " " + doc["nama_belakang"].default(""),
                    ""
                )
            ),
            "alamat": (
                doc["jalan"].default("")
                + ", RT " + doc["rt"].default("").coerce_to("string")
                + "/RW " + doc["rw"].default("").coerce_to("string")
                + ", Kel. " + doc["kelurahan"].default("")
                + ", Kec. " + doc["kecamatan"].default("")
                + ", " + doc["kabupaten_kota"].default("")
                + r.branch(
                    doc["provinsi"].default("") != "",
                    ", " + doc["provinsi"].default(""),
                    ""
                )
            )
        }
    )
    .run(conn)
)

# 3. Konversi cursor menjadi list dan cetak hasilnya
hasil = list(cursor)
print(json.dumps(hasil, indent=4))
print("Total data:", len(hasil))

conn.close()