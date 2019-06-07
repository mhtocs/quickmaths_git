from quickmaths.utils.misc import DotDict

c = 1 / 4
subt = 0.25  # sub
supt = -0.25  # super
t = 1 / 6

r = DotDict({
    "NULL": "NULL",
    "ABOVE": "ABOVE",
    "BELOW": "BELOW",
    "SUPER": "SUPER",
    "SUBSC": "SUBSC",
    "UPPER": "UPPER",
    "LOWER": "LOWER",
    "TLEFT": "TLEFT",
    "BLEFT": "BLEFT",
    "CONTAINS": "CONTAINS",
    "EXPRESSION": "EXPRESSION",
    "UPPER": "UPPER",
})


s = DotDict({
    "FRACTION_BAR": 1,
    "DIGIT": 2,
    "NON_SCRIPTED": 3,
    "OPEN_BRACKET": 4,
    "ROOT": 5,
    "VARIABLE_RANGE": 6,
    "CENTERED": 7,
    "INTEGER": 8,
    "REAL": 9,
    "FUNCTION": 10,
    "CLOSE_BRACKET": 11,
    "BRACKETED": 12
})
