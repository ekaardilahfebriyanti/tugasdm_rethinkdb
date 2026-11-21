import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

def select_10_jadwal_belum_akta():
    ids_akta = (
        r.db("kua_database")
        .table("akta_nikah")["id_jadwal_nikah"]
        .coerce_to("array")
    )
    cursor = (
        r.db("kua_database")
        .table("jadwal_nikah")
        .filter(lambda doc: ids_akta.contains(doc["id_jadwal_nikah"]).not_())
        .run(conn)
    )
    return list(cursor)

def run_stress_test(fn, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        jumlah_data = 0

        for _ in range(n):
            t0 = time.perf_counter()
            hasil = fn()
            durations_ms.append((time.perf_counter() - t0) * 1000)
            jumlah_data = len(hasil)

        print(
            f"Iterasi {n:2d}x (data={jumlah_data}) | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | "
            f"max={max(durations_ms):6.2f} ms | "
            f"total={sum(durations_ms):7.2f} ms"
        )

if __name__ == "__main__":
    try:
        hasil_awal = select_10_jadwal_belum_akta()
        print("Total data:", len(hasil_awal))
        if hasil_awal:
            print(json.dumps(hasil_awal[:2], indent=4, ensure_ascii=False))

        print("\n--- Stress Test SELECT 10 ---")
        run_stress_test(select_10_jadwal_belum_akta)
    finally:
        conn.close()