import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")


def pastikan_index_akta():
    tbl_akta = r.db("kua_database").table("akta_nikah")
    if "id_jadwal_nikah" not in tbl_akta.index_list().run(conn):
        tbl_akta.index_create("id_jadwal_nikah").run(conn)
        tbl_akta.index_wait("id_jadwal_nikah").run(conn)


def select_10_opt():
    return list(
        r.db("kua_database")
        .table("jadwal_nikah")
        .filter(
            lambda jadwal: jadwal.has_fields("id_jadwal_nikah")
            & r.db("kua_database")
            .table("akta_nikah")
            .get_all(jadwal["id_jadwal_nikah"], index="id_jadwal_nikah")
            .is_empty()
        )
        .run(conn)
    )


def benchmark_repeats(fn, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            t0 = time.perf_counter()
            fn()
            durations_ms.append((time.perf_counter() - t0) * 1000)
        print(
            f"Iterasi {n:2d}x | total={sum(durations_ms):7.2f} ms | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | max={max(durations_ms):6.2f} ms"
        )


if __name__ == "__main__":
    try:
        pastikan_index_akta()
        hasil = select_10_opt()

        print(f"Jumlah data ({len(hasil)}):")
        print(json.dumps(hasil, indent=2, ensure_ascii=False, default=str))

        print("\n--- Stress Test Select 10 (Sesudah Optimasi) ---")
        benchmark_repeats(select_10_opt)
    finally:
        conn.close()