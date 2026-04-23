from constants_and_enums import DarkPattern, ElementType, lightness_bottom_threshold, lightness_top_threshold, saturation_threshold
from colorsys import rgb_to_hls

# limited options dark pattern tests
def check_for_no_initial_reject_all(accept, reject, found_patterns: set[DarkPattern]):
    if accept != None and reject == None:
        found_patterns.add(DarkPattern.LIMITEDOPTIONS)

# no options dark pattern tests
def check_for_consent_options_presence(accept, reject, options, found_patterns: set[DarkPattern]):
    if accept == None and reject == None and options == None:
        found_patterns.add(DarkPattern.NOOPTIONS)

# visual interface interference dark pattern tests
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

def check_for_false_hierarchy(accept, reject, options, found_patterns: set[DarkPattern]):
    if accept == None:
        return
    if reject == None and options == None:
        return
    
    # check the background color prominence
    accept_color = get_rgb_values_from_string(accept[12])
    accept_color_prominence = get_color_prominence(accept_color[0], accept_color[1], accept_color[2])
    
    if reject != None:
        reject_color = get_rgb_values_from_string(reject[12])
        reject_color_prominence = get_color_prominence(reject_color[0], reject_color[1], reject_color[2])
        if reject_color_prominence < 0 and accept_color_prominence >= 0:
            found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)
    
    if options != None:
        options_color = get_rgb_values_from_string(options[12])
        options_color_prominence = get_color_prominence(options_color[0], options_color[1], options_color[2])
        if options_color_prominence < 0 and accept_color_prominence >= 0:
            found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)

def check_for_visual_prominence(accept, reject, options, found_patterns: set[DarkPattern]):
    if accept == None:
        return
    if reject == None and options == None:
        return
    
    # check the background color prominence
    accept_color = get_rgb_values_from_string(accept[12])
    accept_color_prominence = get_color_prominence(accept_color[0], accept_color[1], accept_color[2])
    
    if reject != None:
        reject_color = get_rgb_values_from_string(reject[12])
        reject_color_prominence = get_color_prominence(reject_color[0], reject_color[1], reject_color[2])
        if reject_color_prominence <= 0 and accept_color_prominence > 0:
            found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)
    
    if options != None:
        options_color = get_rgb_values_from_string(options[12])
        options_color_prominence = get_color_prominence(options_color[0], options_color[1], options_color[2])
        if options_color_prominence <= 0 and accept_color_prominence > 0:
            found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)

def safe_float(value):
    """Return float(value) or None if it cannot be converted."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def check_for_size_differences(accept, reject, options, found_patterns: set[DarkPattern]):
    if accept is None:
        return
    if reject is None and options is None:
        return

    # extract width/height safely, some values are set to auto or other non numbers
    accept_w = safe_float(accept[13])
    accept_h = safe_float(accept[14])

    if accept_w is None or accept_h is None:
        return

    # allow a small margin of size difference due to possible longer text on accept button
    # we only care if the reject and options button are smaller / less noticeable, so we reduce the accept area by 10%
    accept_area = accept_w * accept_h * 0.9

    if reject is not None:
        reject_w = safe_float(reject[13])
        reject_h = safe_float(reject[14])

        if reject_w is not None and reject_h is not None:
            reject_area = reject_w * reject_h
            if reject_area < accept_area:
                found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)

    if options is not None:
        options_w = safe_float(options[13])
        options_h = safe_float(options[14])

        if options_w is not None and options_h is not None:
            options_area = options_w * options_h
            if options_area < accept_area:
                found_patterns.add(DarkPattern.VISUALINTERFACEINTERFERENCE)

# functional interface interference dark pattern tests
def check_for_options_presence_dark_patterns(accept, reject, options, found_patterns: set[DarkPattern]):
    # check for limited options
    check_for_no_initial_reject_all(accept, reject, found_patterns)
    # check for no options
    check_for_consent_options_presence(accept, reject, options, found_patterns)

# interface interference dark pattern tests
def check_for_visual_interface_interference_dark_patterns(accept, reject, options, found_patterns: set[DarkPattern]):
    # check if less desired options are designed to be less noticeable (false hierarchy)
    check_for_false_hierarchy(accept, reject, options, found_patterns)
    # check if more desired options are designed to be more noticeable (visual prominence)
    check_for_visual_prominence(accept, reject, options, found_patterns)
    # check if there is a significant size diefference between more and less desired options
    # check_for_size_differences(accept, reject, options, found_patterns)

def check_for_functional_interface_interference_dark_patterns(accept, reject, options, found_patterns: set[DarkPattern]):
    # current version of the script will only check for options presence dark patterns
    check_for_options_presence_dark_patterns(accept, reject, options, found_patterns)

# object-based dark pattern tests
def get_element_of_type(elements, type: ElementType):
    elements_of_type = list(filter(lambda e: e[3] == type.value, elements))
    if len(elements_of_type) < 1:
        return None
    if len(elements_of_type) > 1:
        raise Exception(f'Found multiple ELEMENTS OF TYPE {type.name}')
    return elements_of_type[0]

def check_for_interface_interference_dark_patterns(elements, found_patterns: set[DarkPattern]):
    # Check if a cookie dialog was found first since there is no point checking anything else if not
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None or dialog[5] == 'No cookie dialog found during visit':
        # if no dialog was found it is an automatic no options dark pattern
        found_patterns.add(DarkPattern.NOOPTIONS)
        return
    
    accept = get_element_of_type(elements, ElementType.ACCEPT)
    reject = get_element_of_type(elements, ElementType.REJECT)
    options = get_element_of_type(elements, ElementType.OPTONS)
    
    # check for visual interface interference if we have more than a single element with visual data (colors, size)
    elements_with_visual_data = 0
    if accept != None and accept[12] != None:
        elements_with_visual_data += 1
    if reject != None and reject[12] != None:
        elements_with_visual_data += 1
    if options != None and options[12] != None:
        elements_with_visual_data += 1
    if elements_with_visual_data > 1:
        check_for_visual_interface_interference_dark_patterns(accept, reject, options, found_patterns)

    # check for functional interface interference if we are missing certain options
    if accept == None or reject == None or options == None:
        check_for_functional_interface_interference_dark_patterns(accept, reject, options, found_patterns)

def check_for_skipped(elements: list, found_patterns: set[DarkPattern]):
    dialog = get_element_of_type(elements, ElementType.DIALOG)
    if dialog == None:
        return True
    
    result_text = dialog[5]
    if result_text is None:
        found_patterns.add(DarkPattern.SKIPPED)
        return True

    if 'Normal visit' not in result_text and 'No cookie dialog found during visit' not in result_text:
        found_patterns.add(DarkPattern.SKIPPED)
        return True
    
    return False

# entry point
def check_for_object_based_dark_patterns(elements, found_patterns: set[DarkPattern]):
    # check if site was skipped
    skipped = check_for_skipped(elements, found_patterns)
    if skipped:
        return
    
    # currently all object-based patterns lead to interface interference patterns. No testing needed
    check_for_interface_interference_dark_patterns(elements, found_patterns)