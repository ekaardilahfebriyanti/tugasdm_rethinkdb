import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

STATUS_TARGET = "selesai"
BATAS_TANGGAL = "2026-10-20"

def ambil_target_hapus():
    return list(
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .filter(
            lambda jadwal: (
                jadwal.has_fields("status_bimbingan", "tanggal_bimbingan")
                & (jadwal["status_bimbingan"] == STATUS_TARGET)
                & (jadwal["tanggal_bimbingan"] < BATAS_TANGGAL)
            )
        )
        .run(conn)
    )

def delete_2_bimbingan_selesai():
    return (
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .filter(
            lambda jadwal: (
                jadwal.has_fields("status_bimbingan", "tanggal_bimbingan")
                & (jadwal["status_bimbingan"] == STATUS_TARGET)
                & (jadwal["tanggal_bimbingan"] < BATAS_TANGGAL)
            )
        )
        .delete()
        .run(conn)
    )

def restore_dokumen(docs_asli):
    if not docs_asli:
        return
    r.db("kua_database").table("jadwal_bimbingan").insert(
        docs_asli, conflict="replace"
    ).run(conn)


def run_stress_test(docs_asli, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            restore_dokumen(docs_asli)
            t0 = time.perf_counter()
            delete_2_bimbingan_selesai()
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
        tbl_bimbingan = r.db("kua_database").table("jadwal_bimbingan")
        total_awal = tbl_bimbingan.count().run(conn)
        docs_target = ambil_target_hapus()

        print("Total jadwal_bimbingan sebelum DELETE 2:", total_awal)
        print("Jumlah dokumen target DELETE 2:", len(docs_target))
        if docs_target:
            print("Contoh dokumen target:", docs_target[0])

        hasil_awal = delete_2_bimbingan_selesai()
        print("Hasil DELETE 2:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Total jadwal_bimbingan setelah DELETE 2:", tbl_bimbingan.count().run(conn))

        print("\n--- Stress Test DELETE 2 ---")
        run_stress_test(docs_target)

        # Kembalikan dokumen yang sempat dihapus agar kondisi baseline tetap terjaga
        restore_dokumen(docs_target)
        print("Total jadwal_bimbingan setelah restore kondisi awal:", tbl_bimbingan.count().run(conn))
    finally:
        conn.close()