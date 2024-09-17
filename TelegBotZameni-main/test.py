import sqlite3

conn = sqlite3.connect(r'database.db')
cur = conn.cursor()
cur.execute(f"select * from group_st;")

groups = cur.fetchall()

cur.close()
conn.close()

for group_name in groups:
    print(f"id {group_name[1]} group {group_name[2]} ")