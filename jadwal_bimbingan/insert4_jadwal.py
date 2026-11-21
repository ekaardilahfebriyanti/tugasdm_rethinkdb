import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

ID_JADWAL_BIMBINGAN_BARU = 103

DATA_BIMBINGAN_BARU = {
    "id_jadwal_bimbingan": ID_JADWAL_BIMBINGAN_BARU,
    "nip_penyuluh": "198901062026101003",
    "nip_staff_admin": "198803162026102015",
    "ruangan": "Aula KUA",
    "status_bimbingan": "menunggu",
    "tanggal_bimbingan": "2026-11-25",
    "waktu_bimbingan": "09:00:00",
}

def insert_4_bimbingan():
    return (
        r.db("kua_database")
        .table("jadwal_bimbingan")
        .insert(DATA_BIMBINGAN_BARU)
        .run(conn)
    )

def bersihkan_bimbingan_uji():
    r.db("kua_database").table("jadwal_bimbingan").filter(
        {"id_jadwal_bimbingan": ID_JADWAL_BIMBINGAN_BARU}
    ).delete().run(conn)

def run_stress_test(repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            bersihkan_bimbingan_uji()
            t0 = time.perf_counter()
            insert_4_bimbingan()
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
        bersihkan_bimbingan_uji()
        hasil_awal = insert_4_bimbingan()
        print("Hasil INSERT 4:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print(
            "Total dokumen jadwal_bimbingan setelah INSERT 4:",
            r.db("kua_database").table("jadwal_bimbingan").count().run(conn),
        )

        print("\n--- Stress Test INSERT 4 ---")
        run_stress_test()

        # Pastikan dokumen id_jadwal_bimbingan=103 tetap tersimpan setelah stress test
        if not list(
            r.db("kua_database")
            .table("jadwal_bimbingan")
            .filter({"id_jadwal_bimbingan": ID_JADWAL_BIMBINGAN_BARU})
            .run(conn)
        ):
            insert_4_bimbingan()
        print(
            "Total dokumen akhir jadwal_bimbingan:",
            r.db("kua_database").table("jadwal_bimbingan").count().run(conn),
        )
    finally:
        conn.close()