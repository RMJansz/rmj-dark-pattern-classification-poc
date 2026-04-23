import sqlite3

conn = sqlite3.connect('merged-cookie-dialog-data.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS spot_check_validation (
        site_nr bigint,
        sitename varchar(255),
        nooptions tinyint,
        limitedoptions tinyint,
        visualinterfaceinterference tinyint
    )
""")
conn.commit()

cursor.execute("SELECT * FROM spot_check_results")
spot_check_rows = cursor.fetchall()

def validate(original, spot_check):
    if original == 1 and spot_check == 1:
        return "TP"
    elif original == 1 and spot_check == 0:
        return "FP"
    elif original == 0 and spot_check == 0:
        return "TN"
    elif original == 0 and spot_check == 1:
        return "FN"
    else:
        raise Exception("Unexpected integer or None value")
        
for row in spot_check_rows:
    site_nr, sitename, nooptions_spot_check, limitedoptions_spot_check, visualinterfaceinterference_spot_check = row

    cursor.execute("""
        SELECT nooptions, limitedoptions, visualinterfaceinterference
        FROM patterns WHERE site_nr = ?
    """, (site_nr,))
    original = cursor.fetchone()

    if original is None:
        raise Exception("Missing data for site nr " + str(site_nr))

    nooptions_original, limitedoptions_original, visualinterfaceinterference_original = original

    nooptions_result = validate(nooptions_original, nooptions_spot_check)
    limitedoptions_result = validate(limitedoptions_original, limitedoptions_spot_check)
    visualinterfaceinterference_result = validate(visualinterfaceinterference_original, visualinterfaceinterference_spot_check)

    cursor.execute("""
        INSERT INTO spot_check_validation (site_nr, sitename, nooptions, limitedoptions, visualinterfaceinterference)
        VALUES (?, ?, ?, ?, ?)
    """, (site_nr, sitename, nooptions_result, limitedoptions_result, visualinterfaceinterference_result))

conn.commit()