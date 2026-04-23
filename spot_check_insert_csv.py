import sqlite3
import csv

conn = sqlite3.connect('merged-cookie-dialog-data.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS spot_check_results (
        site_nr bigint,
        sitename varchar(255),
        nooptions tinyint,
        limitedoptions tinyint,
        visualinterfaceinterference tinyint
    )
""")
conn.commit()

with open('spot_check_results.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows_to_insert = []
    for row in reader:
        acceptall = int(row['acceptall'])
        consentoptionspresence = int(row['consentoptionspresence'])
        falsehierarchy = int(row['falsehierarchy'])
        nodisclaimer = int(row['nodisclaimer'])
        visualprominence = int(row['visualprominence'])

        # New computed columns
        nooptions = 1 if (nodisclaimer or consentoptionspresence) else 0
        limitedoptions = 1 if acceptall else 0
        visualinterfaceinterference = 1 if (falsehierarchy or visualprominence) else 0

        rows_to_insert.append((
            int(row['site_nr']),
            row['sitename'],
            nooptions,
            limitedoptions,
            visualinterfaceinterference
        ))

cursor.executemany("""
    INSERT INTO spot_check_results (
        site_nr, sitename, nooptions, limitedoptions, visualinterfaceinterference
    ) VALUES (?, ?, ?, ?, ?)
""", rows_to_insert)

conn.commit()
conn.close()
