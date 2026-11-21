import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

NIK_UJI = ["3273070710880012", "3273016008890002"]

DATA_PENDUDUK_BARU = [
    {
        "nik": "3273070710880012",
        "nama_depan": "Ilham",
        "nama_belakang": "Fauzi",
        "tempat_lahir": "Bandung",
        "tanggal_lahir": "1998-05-15",
        "jenis_kelamin": "Laki-laki",
        "jalan": "Jl. Merdeka No. 10",
        "kelurahan": "Sukagalih",
        "kecamatan": "Sukajadi",
        "kabupaten_kota": "Bandung",
        "rt": "005",
        "rw": "001",
        "pekerjaan": "Programmer",
        "provinsi": "Jawa Barat",
        "golongan_darah": "A",
        "agama": "Islam",
        "status_perkawinan": "Belum Kawin",
    },
    {
        "nik": "3273016008890002",
        "nama_depan": "Siti",
        "nama_belakang": "Almira",
        "tempat_lahir": "Bandung",
        "tanggal_lahir": "1999-08-20",
        "jenis_kelamin": "Perempuan",
        "jalan": "Jl. Sukajadi No. 25",
        "kelurahan": "Sukagalih",
        "kecamatan": "Sukajadi",
        "kabupaten_kota": "Bandung",
        "rt": "010",
        "rw": "002",
        "pekerjaan": "Akuntan",
        "provinsi": "Jawa Barat",
        "golongan_darah": "A",
        "agama": "Islam",
        "status_perkawinan": "Belum Kawin",
    },
]

def insert_1_penduduk():
    return (
        r.db("kua_database")
        .table("penduduk")
        .insert(DATA_PENDUDUK_BARU)
        .run(conn)
    )

def bersihkan_nik_uji():
    r.db("kua_database").table("penduduk").get_all(*NIK_UJI).delete().run(conn)

def run_stress_test(repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            bersihkan_nik_uji()
            t0 = time.perf_counter()
            insert_1_penduduk()
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
        bersihkan_nik_uji()
        hasil_awal = insert_1_penduduk()
        print("Hasil INSERT 1:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Total dokumen penduduk setelah INSERT 1:", r.db("kua_database").table("penduduk").count().run(conn))

        print("\n--- Stress Test INSERT 1 ---")
        run_stress_test()
    finally:
        conn.close()