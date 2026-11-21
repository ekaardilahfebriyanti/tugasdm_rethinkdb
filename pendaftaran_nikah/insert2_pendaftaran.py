import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

ID_PENDAFTARAN_UJI = 101

DATA_PENDAFTARAN_BARU = {
    "id_pendaftaran": ID_PENDAFTARAN_UJI,
    "nik_suami": "3273070710880012",
    "nik_istri": "3273075208960196",
    "ayah": "Ahmad Santoso",
    "ibu": "Siti Aminah",
    "no_telepon": "081234567890",
    "jalur_pendaftaran": "online",
    "hari_akad": "Sabtu",
    "tanggal_akad": "2026-12-12",
    "jam_akad": "08:00:00",
    "tempat_akad": "KUA Kecamatan Sukajadi",
    "tanggal_isbat": None,
    "foto": "foto_3273011505980001_3273016008990002.png",
    "fotocopy_akta_kelahiran": "akta_3273011505980001_3273016008990002.png",
    "fotocopy_kk": "KK_3273011505980001_3273016008990002.png",
    "fotocopy_ktp": "KTP_3273011505980001.png",
    "n1_pengantar_nikah": "N1_3273011505980001_3273016008990002.pdf",
    "n2_permohonan_kehendak_nikah": "N2_3273011505980001_3273016008990002.pdf",
    "n3_permohonan_pencatatan_isbat": "N3_3273011505980001_3273016008990002.pdf",
    "n4_persetujuan_calon_pengantin": "N4_3273011505980001_3273016008990002.pdf",
    "n5_surat_izin_orang_tua": "N5_3273011505980001_3273016008990002.pdf",
    "n6_surat_keterangan_kematian": None,
    "n7_penolakan_kehendak_nikah_rujuk": None,
    "pembayaran_administrasi": 0,
    "pembayaran_akad": 0,
    "status_pendaftaran": "diterima",
}

def insert_2_pendaftaran():
    return (
        r.db("kua_database")
        .table("pendaftaran_nikah")
        .insert(DATA_PENDAFTARAN_BARU)
        .run(conn)
    )

def bersihkan_pendaftaran_uji():
    r.db("kua_database").table("pendaftaran_nikah").filter(
        {"id_pendaftaran": ID_PENDAFTARAN_UJI}
    ).delete().run(conn)

def run_stress_test(repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            bersihkan_pendaftaran_uji()
            t0 = time.perf_counter()
            insert_2_pendaftaran()
            durations_ms.append((time.perf_counter() - t0) * 1000)

        print(
            f"Iterasi {n:2d}x | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | "
            f"max={max(durations_ms):6.2f} ms | "
            f"total={sum(durations_ms):7.2f} ms"
        )


if __name__ == "__main__":
    try:
        bersihkan_pendaftaran_uji()
        hasil_awal = insert_2_pendaftaran()
        print("Hasil INSERT 2:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print(
            "Total dokumen pendaftaran_nikah setelah INSERT 2:",
            r.db("kua_database").table("pendaftaran_nikah").count().run(conn),
        )

        print("\n--- Stress Test INSERT 2 ---")
        run_stress_test()
    finally:
        conn.close()