import sqlite3
import string
from check_for_object_based_dark_patterns import check_for_object_based_dark_patterns
from constants_and_enums import DarkPattern


classify_event_based_test_subjects = False
classify_object_based_test_subjects = False
print('Please specify data sources')
events_datasource = input('Source for event-based test subjects data. Default = None\n')
objects_datasource = input('Source for object-based test subjects data (HTML & CSS Elements of cookie dialogs). Default = ./merged-cookie-dialog-data.db\n')

if events_datasource == '':
    events_datasource = None

if objects_datasource == '':
    objects_datasource = './merged-cookie-dialog-data.db'

if events_datasource != None:
    print('Classification for event-based test subjects not yet implemented and will be skipped')
else:
    print('Classification for event-based test subjects will be skipped')

if len(objects_datasource) == 0:
    print('Classification for object-based test subjects will be skipped')
else:
    classify_object_based_test_subjects = True

if not classify_event_based_test_subjects and not classify_object_based_test_subjects:
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


# event-based test subjects detection
if classify_event_based_test_subjects:
    print('Starting detection for event-based test subjects')
    print('Detection of event-based dark patterns complete')

# object-based test subjects detection
if classify_object_based_test_subjects:
    print('Starting detection for object-based test subjects')
    print('Setting up database connection')
    html_elements_database_connection = sqlite3.connect(objects_datasource)
    ordered_website_rank_numbers = get_all_website_rank_numbers(html_elements_database_connection)

    cursor = html_elements_database_connection.cursor()
    cursor.execute("""
        CREATE TABLE if not exists patterns (
            visit_id bigint,
            site_nr int,
            sitename varchar(255),
            skipped tinyint, 
            nooptions tinyint,
            limitedoptions tinyint,
            visualinterfaceinterference tinyint
        )
    """)
    cursor.close()

    for website_rank in ordered_website_rank_numbers:
        elements = get_cookie_dialog_elements_for_website_with_rank(html_elements_database_connection, website_rank)
        foundPatterns = set()
        check_for_object_based_dark_patterns(elements, foundPatterns)
        element = elements[0]
        cursor = html_elements_database_connection.cursor()
        cursor.execute("INSERT OR REPLACE INTO patterns (visit_id, site_nr, sitename, skipped, nooptions, limitedoptions, visualinterfaceinterference) VALUES (?,?,?,?,?,?,?)",
                        (element[0], element[1], element[2], found_pattern(DarkPattern.SKIPPED, foundPatterns), found_pattern(DarkPattern.NOOPTIONS, foundPatterns), found_pattern(DarkPattern.LIMITEDOPTIONS, foundPatterns), found_pattern(DarkPattern.VISUALINTERFACEINTERFERENCE, foundPatterns)))
        html_elements_database_connection.commit()
        cursor.close()
        print('Website with rank ' + str(website_rank) + ' contains the following dark patterns: ' + ', '.join(map(lambda p:p.value, foundPatterns)))

    html_elements_database_connection.close()
    print('Detection of object-based dark patterns complete. Database connection closed')