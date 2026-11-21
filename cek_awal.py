import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

def ukur_ms(fn, repeats=(1, 5, 10)):
    ringkasan = {}
    for n in repeats:
        durs = []
        for _ in range(n):
            t0 = time.perf_counter()
            fn()
            durs.append((time.perf_counter() - t0) * 1000)
        ringkasan[f"{n}x"] = round(statistics.mean(durs), 2)
    return ringkasan

def cek_kondisi_awal():
    print("=== CEK SAMPEL STRUKTUR & KUNCI RELASI ===")
    for tbl in ["penduduk", "pendaftaran_nikah", "pemeriksaan_pendaftaran", "jadwal_bimbingan", "jadwal_nikah", "akta_nikah"]:
        sampel = list(r.table(tbl).limit(1).run(conn))
        print(f"\n[{tbl}] keys:", list(sampel[0].keys()) if sampel else "KOSONG")

    print("\nCek NIP penyuluh & staff_admin yang ada:")
    print("penyuluh:", [d.get("nip") or d.get("nip_penyuluh") for d in r.table("penyuluh").run(conn)])
    print("staff_administrasi:", [d.get("nip") or d.get("nip_staff_admin") for d in r.table("staff_administrasi").run(conn)])

    batal_sample = list(
        r.table("pendaftaran_nikah")
        .filter(lambda d: d.has_fields("pembatalan_nikah"))
        .limit(2)
        .pluck("id_pendaftaran", "pembatalan_nikah")
        .run(conn)
    )
    print("Contoh pembatalan_nikah:", json.dumps(batal_sample, ensure_ascii=False))

if __name__ == "__main__":
    try:
        cek_kondisi_awal()
    finally:
        conn.close()