import json, statistics, time
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(host="172.28.224.1", port=28015, db="kua_database")

ID_PEMBATALAN_TARGET = 1
STATUS_BARU = "disetujui"

def kondisi_pembatalan():
    return lambda doc: (
        doc.has_fields("pembatalan_nikah")
        & (doc["pembatalan_nikah"] != None)
        & (doc["pembatalan_nikah"]["id_pembatalan"] == ID_PEMBATALAN_TARGET)
    )

def ambil_dokumen_target():
    docs = list(
        r.db("kua_database")
        .table("pendaftaran_nikah")
        .filter(kondisi_pembatalan())
        .run(conn)
    )
    return docs[0] if docs else None

def update_3_status_pembatalan():
    return (
        r.db("kua_database")
        .table("pendaftaran_nikah")
        .filter(kondisi_pembatalan())
        .update(
            lambda doc: {
                "pembatalan_nikah": doc["pembatalan_nikah"].merge(
                    {"status_pembatalan": STATUS_BARU}
                )
            }
        )
        .run(conn)
    )


def set_status_pembatalan(nilai_status):
    r.db("kua_database").table("pendaftaran_nikah").filter(
        kondisi_pembatalan()
    ).update(
        lambda doc: {
            "pembatalan_nikah": doc["pembatalan_nikah"].merge(
                {"status_pembatalan": nilai_status}
            )
        }
    ).run(conn)


def run_stress_test(status_awal, repeats=(1, 5, 10)):
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            set_status_pembatalan(status_awal)
            t0 = time.perf_counter()
            update_3_status_pembatalan()
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
        doc_awal = ambil_dokumen_target()
        print("Dokumen sebelum UPDATE 3:", doc_awal)
        status_awal = (
            doc_awal.get("pembatalan_nikah", {}).get("status_pembatalan", "menunggu")
            if doc_awal
            else "menunggu"
        )

        hasil_awal = update_3_status_pembatalan()
        print("Hasil UPDATE 3:", json.dumps(hasil_awal, indent=2, ensure_ascii=False))
        print("Dokumen setelah UPDATE 3:", ambil_dokumen_target())

        print("\n--- Stress Test UPDATE 3 ---")
        run_stress_test(status_awal)

        # Kembalikan ke status awal agar kondisi baseline tetap terjaga
        set_status_pembatalan(status_awal)
        print("Dokumen setelah dikembalikan ke kondisi awal:", ambil_dokumen_target())
    finally:
        conn.close()