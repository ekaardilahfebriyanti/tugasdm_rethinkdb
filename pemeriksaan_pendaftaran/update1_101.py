import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

TARGET_ID = 101
STATUS_BARU = "ditolak"
STATUS_ORIGINAL = "diterima"

def update_1_status_pemeriksaan():
    return (
        r.db("kua_database")
        .table("pemeriksaan_pendaftaran")
        .filter({"id_pendaftaran": TARGET_ID})
        .update({"status_pemeriksaan": STATUS_BARU})
        .run(conn)
    )

def reset_status_pemeriksaan():
    r.db("kua_database").table("pemeriksaan_pendaftaran").filter(
        {"id_pendaftaran": TARGET_ID}
    ).update({"status_pemeriksaan": STATUS_ORIGINAL}).run(conn)

def run_stress_test(repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            reset_status_pemeriksaan()
            t0 = time.perf_counter()
            update_1_status_pemeriksaan()
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
        reset_status_pemeriksaan()
        hasil_awal = update_1_status_pemeriksaan()
        print("Hasil UPDATE 1:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print(
            "Dokumen 101 saat terupdate:",
            list(
                r.db("kua_database")
                .table("pemeriksaan_pendaftaran")
                .filter({"id_pendaftaran": TARGET_ID})
                .run(conn)
            ),
        )

        print("\n--- Stress Test UPDATE 1 ---")
        run_stress_test()

        # Kembalikan ke status original agar data awal 101 tetap aman
        reset_status_pemeriksaan()
        print(
            "Dokumen 101 setelah dikembalikan ke original:",
            list(
                r.db("kua_database")
                .table("pemeriksaan_pendaftaran")
                .filter({"id_pendaftaran": TARGET_ID})
                .run(conn)
            ),
        )
    finally:
        conn.close()