import sqlite3
import string
from check_for_interface_interference_dark_patterns import check_for_interface_interference_patterns
from dark_pattern_enum import DarkPattern


classify_unstoppable_actions = False
classify_interface_interference = False
print('Please specify data sources')
notifications_alerts_datasource = input('Source for cookie dialog notifications / alerts. Default = None\n')
html_elements_datasource = input('Source for cookie dialog HTML element data. Default = ./merged-cookie-dialog-data.db\n')

if notifications_alerts_datasource == '':
    notifications_alerts_datasource = None

if html_elements_datasource == '':
    html_elements_datasource = './merged-cookie-dialog-data.db'

if notifications_alerts_datasource != None:
    print('Classification for Unstoppable Actions not yet implemented and will be skipped')
else:
    print('Classification for Unstoppable Actions will be skipped')

if len(html_elements_datasource) == 0:
    print('Classification for Interface Interference will be skipped')
else:
    classify_interface_interference = True

if not classify_unstoppable_actions and not classify_interface_interference:
    print('Both classification groups were skipped. Terminating...')
    exit()

def get_all_website_rank_numbers(connection: sqlite3.Connection):
    cursor = connection.cursor()
    get_all_website_rank_numbers_query = 'SELECT DISTINCT site_nr from elements ORDER BY site_nr'
    cursor.execute(get_all_website_rank_numbers_query)

    all_website_rank_numbers = cursor.fetchall()
    cursor.close()
    return map(lambda x:x[0], all_website_rank_numbers)

def get_cookie_dialog_elements_for_website_with_rank(connection: sqlite3.Connection, rank: int):
    cursor = connection.cursor()
    elements_for_website_with_rank_query = 'SELECT * FROM elements WHERE site_nr = ? ORDER BY element_type'
    cursor.execute(elements_for_website_with_rank_query, (rank,))
    elements = cursor.fetchall()
    cursor.close()
    return elements

def found_pattern(pattern: DarkPattern, found_patterns: set[DarkPattern]):
    if pattern in found_patterns:
        return 1
    return 0

print('Setting up database connection')
html_elements_database_connection = sqlite3.connect(html_elements_datasource)
ordered_website_rank_numbers = get_all_website_rank_numbers(html_elements_database_connection)

cursor = html_elements_database_connection.cursor()
cursor.execute("""
    CREATE TABLE if not exists patterns (
        visit_id bigint,
        site_nr int,
        sitename varchar(255),
        skipped tinyint, 
        acceptall tinyint,
        consentoptionspresence tinyint,
        falsehierarchy tinyint,
        nodisclaimer tinyint,
        visualprominence tinyint
    )
""")
cursor.close()

for website_rank in ordered_website_rank_numbers:
    elements = get_cookie_dialog_elements_for_website_with_rank(html_elements_database_connection, website_rank)
    foundPatterns = set()
    check_for_interface_interference_patterns(elements, foundPatterns)
    element = elements[0]
    cursor = html_elements_database_connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO patterns (visit_id, site_nr, sitename, skipped, acceptall, consentoptionspresence, falsehierarchy, nodisclaimer, visualprominence) VALUES (?,?,?,?,?,?,?,?,?)",
                    (element[0], element[1], element[2], found_pattern(DarkPattern.SKIPPED, foundPatterns), found_pattern(DarkPattern.ACCEPTALL, foundPatterns), found_pattern(DarkPattern.CONSENTOPTIONSPRESENCE, foundPatterns), found_pattern(DarkPattern.FALSEHIERARCHY, foundPatterns), found_pattern(DarkPattern.NODISCLAIMER, foundPatterns), found_pattern(DarkPattern.VISUALPROMINENCE, foundPatterns)))
    html_elements_database_connection.commit()
    cursor.close()
    print('Website with rank ' + str(website_rank) + ' contains the following dark patterns: ' + ', '.join(map(lambda p:p.value, foundPatterns)))

html_elements_database_connection.close()