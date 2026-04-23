import sqlite3
import csv

conn = sqlite3.connect('merged-cookie-dialog-data.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS spot_check_results (
        site_nr bigint,
        sitename varchar(255),
        acceptall tinyint,
        consentoptionspresence tinyint,
        falsehierarchy tinyint,
        nodisclaimer tinyint,
        visualprominence tinyint
    )
""")
conn.commit()

with open('spot_check_results.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows_to_insert = [
        (
            int(row['site_nr']),
            row['sitename'],
            int(row['acceptall']),
            int(row['consentoptionspresence']),
            int(row['falsehierarchy']),
            int(row['nodisclaimer']),
            int(row['visualprominence'])
        )
        for row in reader
    ]

cursor.executemany("""
    INSERT INTO spot_check_results (
        site_nr, sitename, acceptall, consentoptionspresence,
        falsehierarchy, nodisclaimer, visualprominence
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", rows_to_insert)

conn.commit()
conn.close()
