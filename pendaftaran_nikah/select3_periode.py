import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()

# 1. Koneksi ke RethinkDB
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

# 2. Jalankan query SELECT 3: Jumlah pendaftaran berdasarkan tahun dan bulan akad
def select_3_rekap_akad():
    cursor = (
        r.db("kua_database")
        .table("pendaftaran_nikah")
        .group(
            lambda doc: {
                "tahun": doc["tanggal_akad"].default("").split("-").nth(0),
                "bulan": doc["tanggal_akad"].default("").split("-").nth(1),
            }
        )
        .count()
        .run(conn)
    )
    # 3. Konversi hasil ke bentuk Python yang mudah dibaca/diukur
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
        hasil_awal = select_3_rekap_akad()
        print("Total grup:", len(hasil_awal))
        if isinstance(hasil_awal, dict):
            hasil_cetak = [{**dict(k), "jumlah": v} for k, v in hasil_awal.items()]
        else:
            hasil_cetak = hasil_awal
        print(json.dumps(hasil_cetak, indent=4, ensure_ascii=False))

        print("\n--- Stress Test SELECT 3 ---")
        run_stress_test(select_3_rekap_akad)
    finally:
        conn.close()