import json
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

# Target jumlah dokumen sesuai Table IV-1 Sample Data
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
    print("=== 1. RINGKASAN JUMLAH DOKUMEN VS TARGET BASELINE ===")
    for tabel, target in TARGET_BASELINE.items():
        aktual = r.table(tabel).count().run(conn)
        selisih = aktual - target
        status = "AMAN" if selisih == 0 else f"LEBIH {selisih}" if selisih > 0 else f"KURANG {abs(selisih)}"
        print(f"{tabel:<25} | Aktual: {aktual:<4} | Target: {target:<4} | Status: {status}")

    print("\n=== 2. CEK DOKUMEN BERLEBIH (SISA DML / ID AKHIR) ===")

    # A. Cek 2 data penduduk dari INSERT 1
    nik_dml = ["3273070710880012", "3273016008890002"]
    penduduk_ekstra = list(
        r.table("penduduk")
        .filter(lambda doc: r.expr(nik_dml).contains(doc["nik"]))
        .pluck("nik", "nama_depan", "nama_belakang")
        .run(conn)
    )
    print("\n[penduduk] Kandidat hapus (INSERT 1):", json.dumps(penduduk_ekstra, ensure_ascii=False))

    # B. Cek pendaftaran_nikah dengan id_pendaftaran > 100
    pendaftaran_ekstra = list(
        r.table("pendaftaran_nikah")
        .filter(lambda doc: doc["id_pendaftaran"] > 100)
        .pluck("id_pendaftaran", "nik_suami", "nik_istri", "status_pendaftaran")
        .run(conn)
    )
    print("[pendaftaran_nikah] Kandidat hapus (id > 100):", json.dumps(pendaftaran_ekstra, ensure_ascii=False))

    # C. Cek pemeriksaan_pendaftaran dengan id_pendaftaran > 100
    pemeriksaan_ekstra = list(
        r.table("pemeriksaan_pendaftaran")
        .filter(lambda doc: doc["id_pendaftaran"] > 100)
        .pluck("id_pendaftaran", "status_pemeriksaan", "tanggal_pemeriksaan")
        .run(conn)
    )
    print("[pemeriksaan_pendaftaran] Kandidat hapus (id > 100):", json.dumps(pemeriksaan_ekstra, ensure_ascii=False))

    # D. Cek jadwal_bimbingan dengan id_jadwal_bimbingan > 100 atau 2 ID terakhir
    bimbingan_atas_100 = list(
        r.table("jadwal_bimbingan")
        .filter(lambda doc: doc["id_jadwal_bimbingan"] > 100)
        .pluck("id_jadwal_bimbingan", "tanggal_bimbingan", "status_bimbingan", "nip_penyuluh")
        .run(conn)
    )
    bimbingan_top5_id = list(
        r.table("jadwal_bimbingan")
        .order_by(r.desc("id_jadwal_bimbingan"))
        .limit(5)
        .pluck("id_jadwal_bimbingan", "tanggal_bimbingan", "status_bimbingan", "nip_penyuluh")
        .run(conn)
    )
    print("[jadwal_bimbingan] ID > 100:", json.dumps(bimbingan_atas_100, ensure_ascii=False))
    print("[jadwal_bimbingan] 5 ID terbesar saat ini:", json.dumps(bimbingan_top5_id, ensure_ascii=False))

    # E. Cek jadwal_nikah 5 ID terbesar (untuk memastikan aman di 98)
    jadwal_nikah_top5_id = list(
        r.table("jadwal_nikah")
        .order_by(r.desc("id_jadwal_nikah"))
        .limit(5)
        .pluck("id_jadwal_nikah", "status_pernikahan")
        .run(conn)
    )
    print("[jadwal_nikah] 5 ID terbesar saat ini:", json.dumps(jadwal_nikah_top5_id, ensure_ascii=False))

finally:
    conn.close()