import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

def ambil_ids_akta():
    return (
        r.db("kua_database")
        .table("akta_nikah")
        .get_field("id_jadwal_nikah")
        .default(None)
        .filter(lambda val: val != None)
        .coerce_to("array")
    )

def ambil_target_hapus():
    ids_akta = ambil_ids_akta()
    return list(
        r.db("kua_database")
        .table("jadwal_nikah")
        .filter(
            lambda jadwal: (
                jadwal.has_fields("status_pernikahan", "id_jadwal_nikah")
                & (jadwal["status_pernikahan"] == "batal")
                & ids_akta.contains(jadwal["id_jadwal_nikah"]).not_()
            )
        )
        .run(conn)
    )

def delete_1_jadwal_nikah():
    ids_akta = ambil_ids_akta()
    return (
        r.db("kua_database")
        .table("jadwal_nikah")
        .filter(
            lambda jadwal: (
                jadwal.has_fields("status_pernikahan", "id_jadwal_nikah")
                & (jadwal["status_pernikahan"] == "batal")
                & ids_akta.contains(jadwal["id_jadwal_nikah"]).not_()
            )
        )
        .delete()
        .run(conn)
    )


def restore_dokumen(docs_asli):
    if not docs_asli:
        return
    r.db("kua_database").table("jadwal_nikah").insert(
        docs_asli, conflict="replace"
    ).run(conn)


def run_stress_test(docs_asli, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            restore_dokumen(docs_asli)
            t0 = time.perf_counter()
            delete_1_jadwal_nikah()
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
        tbl_jadwal = r.db("kua_database").table("jadwal_nikah")
        total_awal = tbl_jadwal.count().run(conn)
        docs_target = ambil_target_hapus()

        print("Total jadwal_nikah sebelum DELETE 1:", total_awal)
        print("Jumlah dokumen target DELETE 1:", len(docs_target))
        if docs_target:
            print("Contoh dokumen target:", docs_target[0])

        hasil_awal = delete_1_jadwal_nikah()
        print("Hasil DELETE 1:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Total jadwal_nikah setelah DELETE 1:", tbl_jadwal.count().run(conn))

        print("\n--- Stress Test DELETE 1 ---")
        run_stress_test(docs_target)

        # Kembalikan dokumen yang sempat dihapus agar kondisi baseline tetap terjaga
        restore_dokumen(docs_target)
        print("Total jadwal_nikah setelah restore kondisi awal:", tbl_jadwal.count().run(conn))
    finally:
        conn.close()