import json
from rethinkdb import RethinkDB

r = RethinkDB()

# Koneksi ke database kua_database
conn = r.connect(
    host="localhost",
    port=28015,
    db="kua_database"
)

# Load file JSON
with open("Json/pegawai.json", "r", encoding="utf-8") as f:
    pegawai_list = json.load(f)

with open("Json/staff_administrasi.json", "r", encoding="utf-8") as f:
    staff_list = json.load(f)

with open("Json/penghulu.json", "r", encoding="utf-8") as f:
    penghulu_list = json.load(f)

with open("Json/penyuluh.json", "r", encoding="utf-8") as f:
    penyuluh_list = json.load(f)

# Mapping data pegawai berdasarkan NIP (tanpa menduplikasi key 'nip' di dalam object pegawai)
pegawai_by_nip = {
    p["nip"]: {k: v for k, v in p.items() if k != "nip"}
    for p in pegawai_list
}

def embed_pegawai(data_list):
    hasil = []
    for item in data_list:
        nip = item["nip"]
        # Pertahankan field khusus di dalam 'pegawai' jika ada (seperti 'spesialisasi' pada penyuluh)
        pegawai_lama = item.get("pegawai", {})
        pegawai_baru = {**pegawai_lama, **pegawai_by_nip.get(nip, {})}
        hasil.append({**item, "pegawai": pegawai_baru})
    return hasil

datasets = {
    "staff_administrasi": embed_pegawai(staff_list),
    "penghulu": embed_pegawai(penghulu_list),
    "penyuluh": embed_pegawai(penyuluh_list),
}

# Buat tabel (primary_key="nip") jika belum ada dan insert dokumen
tables = r.table_list().run(conn)

for table_name, records in datasets.items():
    if table_name not in tables:
        r.table_create(table_name, primary_key="nip").run(conn)
    res = r.table(table_name).insert(records, conflict="replace").run(conn)
    total = r.table(table_name).count().run(conn)
    print(f"{table_name} -> inserted: {res['inserted']}, replaced: {res['replaced']}, total: {total}")

conn.close()