from constants_and_enums import DarkPattern, ElementType

def get_element_of_type(elements, type: ElementType):
    elements_of_type = list(filter(lambda e: e[3] == type.value, elements))
    if len(elements_of_type) < 1:
        return None
    if len(elements_of_type) > 1:
        raise Exception(f'Found multiple ELEMENTS OF TYPE {type.name}')
    return elements_of_type[0]

def check_for_skipped(elements: list, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        raise Exception('No dialog element found in elements list.')
    
    result_text = dialog[5]
    if result_text is None:
        found_patterns.add(DarkPattern.SKIPPED)
        return True

    if result_text != 'Normal visit' and result_text != 'No cookie dialog found during visit':
        found_patterns.add(DarkPattern.SKIPPED)
        return True
    
    return False