from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

TARGET_BASELINE = {
    "penduduk": 215,
    "user": 15,
    "staff_administrasi": 6,
    "penghulu": 5,
    "penyuluh": 4,
    "pendaftaran_nikah": 100,
    "pemeriksaan_pendaftaran": 100,
    "jadwal_nikah": 98,
    "jadwal_bimbingan": 98,
    "akta_nikah": 77,
}

try:
    # 1. Hapus pendaftaran_nikah dengan id_pendaftaran > 100 (hapus 1 data -> jadi 100)
    res_daftar = (
        r.table("pendaftaran_nikah")
        .filter(lambda doc: doc["id_pendaftaran"] > 100)
        .delete()
        .run(conn)
    )
    print("Delete pendaftaran_nikah (id > 100):", res_daftar)

    # 2. Hapus jadwal_bimbingan dengan id_jadwal_bimbingan > 100 (hapus 2 data: 101, 102 -> jadi 98)
    res_bimbingan = (
        r.table("jadwal_bimbingan")
        .filter(lambda doc: doc["id_jadwal_bimbingan"] > 100)
        .delete()
        .run(conn)
    )
    print("Delete jadwal_bimbingan (id > 100):", res_bimbingan)

    # 3. Hapus NIK 3273070710880012, lalu cek selisih penduduk
    res_nik1 = r.table("penduduk").get("3273070710880012").delete().run(conn)
    print("Delete penduduk (3273070710880012):", res_nik1)

    sisa_lebih = r.table("penduduk").count().run(conn) - TARGET_BASELINE["penduduk"]
    if sisa_lebih > 0:
        # Tampilkan beberapa dokumen penduduk dengan NIK terbesar untuk dipastikan sebelum hapus sisanya
        kandidat = list(
            r.table("penduduk")
            .order_by(r.desc("nik"))
            .limit(sisa_lebih + 2)
            .pluck("nik", "nama_depan", "nama_belakang")
            .run(conn)
        )
        print(f"Masih lebih {sisa_lebih} di penduduk. Kandidat NIK terbesar:", kandidat)
        # Hapus tepat sebanyak sisa_lebih dokumen dengan NIK terbesar
        nik_terbesar = [d["nik"] for d in kandidat[:sisa_lebih]]
        res_nik_sisa = (
            r.table("penduduk")
            .filter(lambda doc: r.expr(nik_terbesar).contains(doc["nik"]))
            .delete()
            .run(conn)
        )
        print("Delete sisa penduduk berlebih:", res_nik_sisa)

    print("\n=== VERIFIKASI AKHIR BASELINE ===")
    for tabel, target in TARGET_BASELINE.items():
        aktual = r.table(tabel).count().run(conn)
        print(f"{tabel:<25} | Aktual: {aktual:<4} | Target: {target:<4} | {'OK' if aktual == target else 'CEK LAGI'}")

finally:
    conn.close()