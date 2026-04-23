import sqlite3
import csv

conn = sqlite3.connect('merged-cookie-dialog-data.db')
cursor = conn.cursor()

buckets = [
    (1, 5000),
    (5001, 25000),
    (25001, 100000),
    (100001, 1000000)
]

results = []

for start, end in buckets:
    cursor.execute("""
        SELECT site_nr, sitename
        FROM patterns
        WHERE site_nr BETWEEN ? AND ? AND skipped = 0
        ORDER BY RANDOM()
        LIMIT 50
    """, (start, end))
    results.extend(cursor.fetchall())

with open('spot_check_samples.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['site_nr', 'sitename'])
    writer.writerows(results)

conn.close()
