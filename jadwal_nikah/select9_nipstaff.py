import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

def select_9_jadwal_per_staff_admin():
    cursor = (
        r.db("kua_database")
        .table("jadwal_nikah")
        .group("nip_staff_admin")
        .count()
        .run(conn)
    )
    return dict(cursor) if isinstance(cursor, dict) else list(cursor)

def run_stress_test(fn, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        jumlah_data = 0

        for _ in range(n):
            t0 = time.perf_counter()
            hasil = fn()
            durations_ms.append((time.perf_counter() - t0) * 1000)
            jumlah_data = len(hasil) if hasattr(hasil, "__len__") else 1

        print(
            f"Iterasi {n:2d}x (grup={jumlah_data}) | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | "
            f"max={max(durations_ms):6.2f} ms | "
            f"total={sum(durations_ms):7.2f} ms"
        )

if __name__ == "__main__":
    try:
        hasil_awal = select_9_jadwal_per_staff_admin()
        print("Total grup:", len(hasil_awal))
        print(json.dumps(hasil_awal, indent=4, ensure_ascii=False))

        print("\n--- Stress Test SELECT 9 ---")
        run_stress_test(select_9_jadwal_per_staff_admin)
    finally:
        conn.close()