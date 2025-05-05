import enum

#  Color prominence thresholds, saturation above this threshold and lightness between the bottom and top thresholds are considered prominent colors
saturation_threshold = 0.5
lightness_bottom_threshold = 0.4
lightness_top_threshold = 0.7

class ElementType(enum.Enum):
    DIALOG = 0
    ACCEPT = 1
    REJECT = 2
    OPTONS = 3

class DarkPattern(enum.Enum):
    ACCEPTALL = 'Accept all but no reject all' # Maybe rename this one
    CONSENTOPTIONSPRESENCE = 'Consent options presence'
    FALSEHIERARCHY = 'False hierarchy'
    NODISCLAIMER = 'No disclaimer'
    VISUALPROMINENCE = 'Visual prominence'