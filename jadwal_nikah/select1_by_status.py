import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

# 2. Jalankan query (gunakan tanda kutip pada key dictionary dan akhiri dengan .run(conn))
def select_1_jadwal_selesai():
    cursor = (
        r.db("kua_database")
        .table("jadwal_nikah")
        .filter({"status_pernikahan": "selesai"})
        .run(conn)
    )
    # 3. Konversi cursor menjadi list dan kembalikan hasilnya
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
        hasil_awal = select_1_jadwal_selesai()
        print("Total data:", len(hasil_awal))
        if hasil_awal:
            print("Contoh 1 data awal:")
            print(json.dumps(hasil_awal[0], indent=4, ensure_ascii=False))

        print("\n--- Stress Test SELECT 1 ---")
        run_stress_test(select_1_jadwal_selesai)
    finally:
        conn.close()