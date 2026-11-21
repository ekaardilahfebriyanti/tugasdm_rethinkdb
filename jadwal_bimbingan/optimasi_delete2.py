import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

STATUS_TARGET = "selesai"
BATAS_TANGGAL = "2026-10-20"
INDEX_NAME = "status_tanggal_bimbingan"


def pastikan_index_bimbingan():
    tbl = r.db("kua_database").table("jadwal_bimbingan")
    if INDEX_NAME not in tbl.index_list().run(conn):
        tbl.index_create(
            INDEX_NAME,
            [r.row["status_bimbingan"], r.row["tanggal_bimbingan"]],
        ).run(conn)
        tbl.index_wait(INDEX_NAME).run(conn)


def ambil_target_hapus_opt():
    return list(
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .between(
            [STATUS_TARGET, r.minval],
            [STATUS_TARGET, BATAS_TANGGAL],
            index=INDEX_NAME,
            right_bound="open",
        )
        .run(conn)
    )


def delete_2_bimbingan_selesai_opt():
    return (
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .between(
            [STATUS_TARGET, r.minval],
            [STATUS_TARGET, BATAS_TANGGAL],
            index=INDEX_NAME,
            right_bound="open",
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
            delete_2_bimbingan_selesai_opt()
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
        pastikan_index_bimbingan()
        tbl_bimbingan = r.db("kua_database").table("jadwal_bimbingan")

        total_awal = tbl_bimbingan.count().run(conn)
        docs_target = ambil_target_hapus_opt()

        print("Total jadwal_bimbingan sebelum DELETE 2 (opt):", total_awal)
        print("Jumlah dokumen target DELETE 2 (opt):", len(docs_target))
        if docs_target:
            print("Contoh dokumen target:", docs_target[0])

        hasil_awal = delete_2_bimbingan_selesai_opt()
        print("Hasil DELETE 2 (opt):", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Total jadwal_bimbingan setelah DELETE 2 (opt):", tbl_bimbingan.count().run(conn))

        print("\n--- Stress Test DELETE 2 (Sesudah Optimasi) ---")
        run_stress_test(docs_target)

        restore_dokumen(docs_target)
        print("Total jadwal_bimbingan setelah restore kondisi awal:", tbl_bimbingan.count().run(conn))
    finally:
        conn.close()