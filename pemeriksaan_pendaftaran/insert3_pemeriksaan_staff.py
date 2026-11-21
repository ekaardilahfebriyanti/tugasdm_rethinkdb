import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

ID_PENDAFTARAN_BARU = 102

DATA_PEMERIKSAAN_102 = {
    "id_pendaftaran": ID_PENDAFTARAN_BARU,
    "n8_pemeriksaan_nikah": "N8_3273011505980001_3273016008990002.pdf",
    "nip_staff_admin": "198811082026101004",
    "status_pemeriksaan": "diterima",
    "tanggal_pemeriksaan": "2026-11-22",
}

def insert_3_pemeriksaan_102():
    return (
        r.db("kua_database")
        .table("pemeriksaan_pendaftaran")
        .insert(DATA_PEMERIKSAAN_102)
        .run(conn)
    )

def bersihkan_102():
    r.db("kua_database").table("pemeriksaan_pendaftaran").filter(
        {"id_pendaftaran": ID_PENDAFTARAN_BARU}
    ).delete().run(conn)

def run_stress_test(repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            bersihkan_102()
            t0 = time.perf_counter()
            insert_3_pemeriksaan_102()
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
        bersihkan_102()
        hasil_awal = insert_3_pemeriksaan_102()
        print("Hasil INSERT 3 (id=102):", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print(
            "Total dokumen pemeriksaan_pendaftaran:",
            r.db("kua_database").table("pemeriksaan_pendaftaran").count().run(conn),
        )
        print(
            "Dokumen id_pendaftaran=101 (tetap original):",
            r.db("kua_database").table("pemeriksaan_pendaftaran").get(101).run(conn),
        )

        print("\n--- Stress Test INSERT 3 (id=102) ---")
        run_stress_test()

        # Pastikan setelah stress test id=102 tetap ada (total 101)
        if not list(
            r.db("kua_database")
            .table("pemeriksaan_pendaftaran")
            .filter({"id_pendaftaran": ID_PENDAFTARAN_BARU})
            .run(conn)
        ):
            insert_3_pemeriksaan_102()
        print(
            "Total dokumen akhir pemeriksaan_pendaftaran:",
            r.db("kua_database").table("pemeriksaan_pendaftaran").count().run(conn),
        )
    finally:
        conn.close()