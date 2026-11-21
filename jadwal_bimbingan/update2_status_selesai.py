import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

TARGET_ID = 103
STATUS_BARU = "selesai"

def ambil_dokumen_103():
    docs = list(
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .filter({"id_jadwal_bimbingan": TARGET_ID})
        .run(conn)
    )
    return docs[0] if docs else None

def update_2_status_bimbingan():
    return (
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .filter({"id_jadwal_bimbingan": TARGET_ID})
        .update({"status_bimbingan": STATUS_BARU})
        .run(conn)
    )

def set_status_bimbingan(nilai_status):
    r.db("kua_database").table("jadwal_bimbingan").filter(
        {"id_jadwal_bimbingan": TARGET_ID}
    ).update({"status_bimbingan": nilai_status}).run(conn)


def run_stress_test(status_awal, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            set_status_bimbingan(status_awal)
            t0 = time.perf_counter()
            update_2_status_bimbingan()
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
        doc_awal = ambil_dokumen_103()
        print("Dokumen 101 sebelum UPDATE 2:", doc_awal)
        status_awal = doc_awal.get("status_bimbingan", "menunggu") if doc_awal else "menunggu"

        hasil_awal = update_2_status_bimbingan()
        print("Hasil UPDATE 2:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Dokumen 101 setelah UPDATE 2:", ambil_dokumen_103())

        print("\n--- Stress Test UPDATE 2 ---")
        run_stress_test(status_awal)

        # Kembalikan ke status awal agar data baseline tetap terjaga
        set_status_bimbingan(status_awal)
        print("Dokumen 103 setelah dikembalikan ke kondisi awal:", ambil_dokumen_103())
    finally:
        conn.close()