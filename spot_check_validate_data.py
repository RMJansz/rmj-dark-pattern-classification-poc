import sqlite3

conn = sqlite3.connect('merged-cookie-dialog-data.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS spot_check_validation (
        site_nr bigint,
        sitename varchar(255),
        acceptall varchar(2),
        consentoptionspresence varchar(2),
        falsehierarchy varchar(2),
        nodisclaimer varchar(2),
        visualprominence varchar(2)
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
    site_nr, sitename, acceptall_spot_check, consent_spot_check, hierarchy_spot_check, disclaimer_spot_check, prominence_spot_check = row

    cursor.execute("""
        SELECT acceptall, consentoptionspresence, falsehierarchy, nodisclaimer, visualprominence
        FROM patterns WHERE site_nr = ?
    """, (site_nr,))
    original = cursor.fetchone()

    if original is None:
        raise Exception("Missing data for site nr " + str(site_nr))

    acceptall_original, consent_original, hierarchy_original, disclaimer_original, prominence_original = original

    acceptall_result = validate(acceptall_original, acceptall_spot_check)
    consent_result = validate(consent_original, consent_spot_check)
    hierarchy_result = validate(hierarchy_original, hierarchy_spot_check)
    disclaimer_result = validate(disclaimer_original, disclaimer_spot_check)
    prominence_result = validate(prominence_original, prominence_spot_check)

    cursor.execute("""
        INSERT INTO spot_check_validation (site_nr, sitename, acceptall, consentoptionspresence, falsehierarchy, nodisclaimer, visualprominence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (site_nr, sitename, acceptall_result, consent_result, hierarchy_result, disclaimer_result, prominence_result))

conn.commit()