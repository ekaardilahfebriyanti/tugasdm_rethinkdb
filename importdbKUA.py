
import json
from rethinkdb import RethinkDB

r = RethinkDB()

conn = r.connect(
    host="172.28.224.1",
    port=28015,
    db="kua_database"
)

# Load JSON
with open("Json/pemeriksaan_pendaftaran.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create table with NIK as primary key if it doesn't exist
tables = r.table_list().run(conn)

if "pemeriksaan_pendaftaran" not in tables:
    r.table_create("pemeriksaan_pendaftaran", primary_key="id_pendaftaran").run(conn)

# Insert documents  
result = r.table("pemeriksaan_pendaftaran").insert(data).run(conn)

print("Insertion result:", result)

# Display total documents
count = r.table("pemeriksaan_pendaftaran").count().run(conn)
print("Total:", count)

conn.close()
