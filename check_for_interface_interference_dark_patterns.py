from dark_pattern_enum import DarkPattern, ElementType, lightness_bottom_threshold, lightness_top_threshold, saturation_threshold
from colorsys import rgb_to_hls

# Element of type selector
def get_element_of_type(elements, type: ElementType):
    elements_of_type = list(filter(lambda e: e[3] == type.value, elements))
    if len(elements_of_type) < 1:
        return None
    if len(elements_of_type) > 1:
        raise Exception(f'Found multiple ELEMENTS OF TYPE {type.name}')
    return elements_of_type[0]

# Get rgb color values from color info string
def get_rgb_values_from_string(color_string: str):
    color_string = color_string.removeprefix('rgba(').removesuffix(')')
    rgba_values = color_string.split(', ')
    return int(rgba_values[0]), int(rgba_values[1]), int(rgba_values[2])

# Determine if color is vibrant or muted (returns -1 for muted, 1 for vibrant, 0 for average)
def get_color_prominence(r: int, g: int, b: int):
    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        raise Exception('One or more value(s) out of range, rgb values range from 0 to 255')
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    _, l, s = rgb_to_hls(r, g, b)
    has_prominent_lightness = l > lightness_bottom_threshold and l < lightness_top_threshold
    has_prominent_saturation = s > saturation_threshold
    if has_prominent_lightness and has_prominent_saturation:
        return 1
    if not has_prominent_lightness and not has_prominent_saturation:
        return -1
    return 0

# Simple -> at first sight -> aesthetic manipulation patterns
def check_for_false_hierarchy(elements, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return
    reject = get_element_of_type(elements, ElementType.REJECT)
    options = get_element_of_type(elements, ElementType.OPTONS)
    if reject == None and options == None:
        return
    accept = get_element_of_type(elements, ElementType.ACCEPT)
    if accept == None:
        return
    
    accept_color = get_rgb_values_from_string(accept[12])
    accept_color_prominence = get_color_prominence(accept_color[0], accept_color[1], accept_color[2])
    if reject != None:
        reject_color = get_rgb_values_from_string(reject[12])
        reject_color_prominence = get_color_prominence(reject_color[0], reject_color[1], reject_color[2])
        if reject_color_prominence < 0 and accept_color_prominence >= 0:
            found_patterns.add(DarkPattern.FALSEHIERARCHY)
    if options != None:
        options_color = get_rgb_values_from_string(options[12])
        options_color_prominence = get_color_prominence(options_color[0], options_color[1], options_color[2])
        if options_color_prominence < 0 and accept_color_prominence >= 0:
            found_patterns.add(DarkPattern.FALSEHIERARCHY)

def check_for_visual_prominence(elements, found_patterns: set[DarkPattern]):
    # Maybe merge this with false hierarchy in the taxonomy, double check the differences and why I kept it separate?
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return
    reject = get_element_of_type(elements, ElementType.REJECT)
    options = get_element_of_type(elements, ElementType.OPTONS)
    if reject == None and options == None:
        return
    accept = get_element_of_type(elements, ElementType.ACCEPT)
    if accept == None:
        return
    
    accept_color = get_rgb_values_from_string(accept[12])
    accept_color_prominence = get_color_prominence(accept_color[0], accept_color[1], accept_color[2])
    if reject != None:
        reject_color = get_rgb_values_from_string(reject[12])
        reject_color_prominence = get_color_prominence(reject_color[0], reject_color[1], reject_color[2])
        if reject_color_prominence <= 0 and accept_color_prominence > 0:
            found_patterns.add(DarkPattern.VISUALPROMINENCE)
    if options != None:
        options_color = get_rgb_values_from_string(options[12])
        options_color_prominence = get_color_prominence(options_color[0], options_color[1], options_color[2])
        if options_color_prominence <= 0 and accept_color_prominence > 0:
            found_patterns.add(DarkPattern.VISUALPROMINENCE)

# Simple -> at first sight -> consent limitation patterns
# This is Accept All (+- blablabla in taxonomy, maybe rename)
def check_for_no_initial_reject_all(elements, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return
    accept = get_element_of_type(elements, ElementType.ACCEPT)
    reject = get_element_of_type(elements, ElementType.REJECT)
    if accept != None and reject == None:
        found_patterns.add(DarkPattern.ACCEPTALL)

def check_for_no_disclaimer(elements: list, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return True
    if dialog[5] == 'No cookie dialog found during visit':
        found_patterns.add(DarkPattern.NODISCLAIMER)
        return True
    return False

def check_for_consent_options_presence(elements, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return
    reject = get_element_of_type(elements, ElementType.REJECT)
    if reject == None:
        found_patterns.add(DarkPattern.CONSENTOPTIONSPRESENCE)

# Simple -> at first sight: aesthetic manipulation or consent limitation?
def check_for_aesthetic_manipulation_patterns(elements, found_patterns: set[DarkPattern]):
    check_for_false_hierarchy(elements, found_patterns)
    check_for_visual_prominence(elements, found_patterns)

def check_for_consent_limitation_patterns(elements, found_patterns: set[DarkPattern]):
    check_for_no_initial_reject_all(elements, found_patterns)
    check_for_consent_options_presence(elements, found_patterns)

# Simple: at first sight or in steps?
def check_for_at_first_sight_patterns(elements, found_patterns: set[DarkPattern]):
    check_for_aesthetic_manipulation_patterns(elements, found_patterns)
    check_for_consent_limitation_patterns(elements, found_patterns)

def check_for_in_steps_interference_patterns(elements, found_patterns: set[DarkPattern]):
    return

# Simple or Complex?
def check_for_simple_interface_interference_patterns(elements, found_patterns: set[DarkPattern]):
    check_for_at_first_sight_patterns(elements, found_patterns)
    check_for_in_steps_interference_patterns(elements, found_patterns)

def check_for_complex_interface_interference_patterns(elements, found_patterns: set[DarkPattern]):
    return

# entry point
def check_for_interface_interference_patterns(elements, found_patterns: set[DarkPattern]):
    # Check no disclaimer first since then there is no point checking others
    no_disclaimer = check_for_no_disclaimer(elements, found_patterns)
    if no_disclaimer:
        return

    check_for_simple_interface_interference_patterns(elements, found_patterns)
    check_for_complex_interface_interference_patterns(elements, found_patterns)