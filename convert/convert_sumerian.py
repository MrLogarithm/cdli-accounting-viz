import re
import numpy as np
from convert.number_system import *

#########################
# Conversion values from:
#   http://oracc.museum.upenn.edu/doc/downloads/numref.pdf
#   http://oracc.museum.upenn.edu/doc/help/editinginatf/metrology/metrologicaltables/index.html
#   http://cdli.ox.ac.uk/wiki/doku.php?id=ed_iii_metrological_systems
#
# All retrieved 13 May 2019
#########################

#########################
# Begin list of number systems:
#
Date = NumberSystem(
    "date",
    {
        # NUMERALS
        "|aszxdisz|":1,
        # UNITS
    },
    "",
    "", # years?
    1)
Cardinal = NumberSystem(
    "cardinal",
    {
        # NUMERALS
        "asz":1,
        "disz": 1,
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        # UNITS
        "gin2": 1./60,
        "sze":  1./10800,
    },
    "",
    "",
    1)

Length = NumberSystem(
    "length",
    {
        "asz": 1, # TODO verify
    # NUMERALS
    "disz": 1,
    "u":    10,
    "gesz2": 60,
    "geszu": 600,
    "szar2": 3600,
    "szar'u": 36000,
    "szargal": 216000,
    # UNITS
    "szu-si":1./180, # 1/30 of kusz3
    "|szu.bad|": 1./12, # 1/2 of kusz3
    "kusz3": 1./6,
    "gi": 1,
    "ninda":2,
    "esz2":20, # 10 times ninda
    "usz":120,# 6 times esz2
    "danna":3600,# 30 times USZ
    },
    "gi",
    "m",
    3)

Surface = NumberSystem(
    "surface",
    {
        "asz": 1, # TODO verify
        # NUMERALS without GAN2
        "disz": 1,
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        # NUMERALS with GAN2
        "iku": 1, # 1(iku) GAN2 is 100 times 1(disz) sar
                  # the multiple is built into GAN2 instead of iku
                  # but either way makes sense
        "esze3":6, # 6 times 1(iku) GAN2
        "bur3":18, # 3 times 1(esze) GAN2
        "bur'u":180, # 10 times 1(bur3) GAN2
        ("szar2","gan2"): 6480000, # 6 times 1(bur'u) GAN2
        ("szar'u","gan2"): 64800000, # 10 times szar2
        ("szargal","gan2"): 388800000, # 60 szar2
        # UNITS
        "sze":1./180,
        "gin2 tur":1./60,
        "gin2":1,
        "ma-na tur":1./3,
        "sar":60,
        "gan2":6000,
    },
    "gin2",
    "m^2",
    0.6)

Volume = NumberSystem(
    "volume",
    {
        "asz":1, # TODO verify
        "disz": 1,
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        #
        "sze":1./180,
        "gin2":1,
        "sar":60,
        # We find both 1(asz) iku and 1(iku) iku
        # with the same value:
        ("asz", "iku"):6000, # 100 times sar
        ("iku", "iku"):6000, # 100 times sar
        ("esze3",None):36000, # 6 times 1(iku) iku
        ("bur3",None):108000, # 3 times esze3
    },
    "gin2",
    "l",
    300, 
    resets={sign:None for sign in ["esze3","bur3"]})

DryCapacity = NumberSystem(
    "dry capacity",
    {
        "asz":1,
        "disz": 1, # UNIT #
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        #
        "sze":1./10800,
        "gin2":1./60,
        "sila3":1,
        "ban2":10 / 300, # 10 times sila3 # TODO the /300 is a hack to make this work
        # when we see 1(ban2) we are out of the sila3 regime, so we advance to gur
        # in expectation of an eventual 1(asz). but we don't incorporate the value
        # of gur into 1(ban2), so we divide by 1 gur to counteract 
        "ban2@v":10 / 300, 
        "barig":60 / 300, # 6 ban2
        #("ban2",None):10, # 10 times sila3
        #("ban2@v",None):10, 
        #("barig",None):60, # 6 ban2
        "gur":300,# 5 times barig
        "szar2":1080000,#3600 times gur
        "guru7":1080000,
        "szar'u":10800000,
        "szargal":64800000,
    },
    "sila3",
    "l",
    1,
    resets={sign:"gur" for sign in ["ban2","barig"]})

# From http://cdli.ox.ac.uk/wiki/doku.php?id=ur_iii_metrological_systems:
# La quantité [img] se note par exemple en translittération :
#    soit : 81,2.3. 2 1/2 sila3 še gur [système dit « Sollberger »]
#    soit : 1(geš2) 2(u) 1(aš) 2(bariga) 3(ban2) 2(diš) 1/2(diš) sila3 še gur [système CDLI]
# (Cela correspond, dans notre système de mesure, à un total de 24452,5 litres d’orge)

LiquidCapacity = NumberSystem(
    "liquid capacity",
    {
        "asz":1, # TODO verify
        "disz": 1, # UNIT #
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        #
        "gin2 tur":1./3600,
        "gin2":1./60,
        "sila3":1,
        "dug":30,
    },
    "sila3",
    "l",
    1)

Weight = NumberSystem(
    "weight",
    {
        "asz":1,
        "disz": 1, # UNIT #
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        ("|ninda2x(sze.1(asz))|",None):1, # TODO test
        #
        "sze":1./180,
        "gin2":1,
        "ma-na":60,
        "gu2":3600,
    },
    "gin2",
    "g",
    25./3)

Brick = NumberSystem(
    "bricks",
    {
        "asz":1, # TODO verify
        "disz": 1, # UNIT #
        "u":    10,
        "gesz2": 60,
        "geszu": 600,
        "szar2": 3600,
        "szar'u": 36000,
        "szargal": 216000,
        #
        "gin2":12,
        "sar":720,
    },
    "gin2",
    "bricks",
    12)

num_systems = set([
    Date,
    Cardinal,
    Length,
    Surface,
    Volume, 
    DryCapacity, 
    LiquidCapacity,
    Weight,
    Brick
    ])

# End list of number systems
#
#########################

def convert( num, sign_vals=None ):
    """
    Converts a Sumerian numeral into the equivalent arabic notation.

    num:        A string containing a Sumerian numeral, eg "1(disz) gin2"
    sign_vals:  (optional) A NumberSystem object to use for the conversion.
                If no system is specified, this function will iterate all
                of the standard number systems and return all possible
                readings for the given string.

    returns:    JSON object with one key called "readings" pointing to a list 
                of possible readings for the given number. Each reading is a
                JSON object with the following keys:
                    "system": name of the number system that gives this reading
                    "value": value of the number in Sumerian units
                    "unit": Sumerian unit represented by this value
                    "modern_value": value of the number in modern units
                    "modern_unit": modern equivalent to the Sumerian unit
                    "query": the original number string (equal to the num argument)

    For example, 
    { "readings": [ {
      "modern_unit": "g",
      "modern_value": 8.333333333333334,
      "query": "1(disz) gin2",
      "system": "weight",
      "unit": "gin2",
      "value": 1
    }]}
    describes the number "1(disz) gin2" which, according to the "weight" system of notation, is equivalent to 1 Sumerian gin2, or 8.33... modern grams.
    """

    num = normalize( num )

    if sign_vals is None:
        result = []
        for system in num_systems:
            if system.canParse( num ):
                try:
                    converted = convert( num, system )
                    result += converted 
                except:
                    pass
        return result

    if isinstance( sign_vals, str ):
        for system in num_systems:
            if system.name == sign_vals:
                sign_vals = system
                break
    if isinstance( sign_vals, str ):
        raise ValueError("Unknown number system: %s"%(sign_vals))


    digits = num.split(" ")

    # count = how many of the sign are there?
    # e.g. in 2(iku) the count is 2
    count = None
    last_count = None

    # unit = what sign is being counted?
    # e.g. in 2(iku) the unit is iku
    unit = None
    last_unit = None
    

    # Value of the number
    value = 0
    # Treat signs like gin2 as a "modifier" that 
    # multiplies the value of the digit. 
    modifier = 1
    last_modifier = 1
    last_sign_was_modifier = False

    for sign in digits[::-1]:

        if sign == "..." or sign == "x":
            return [{
                "system": "unknown",
                "unit": "",
                "value": "none",
                "modern_unit": "",
                "modern_value": "none",
                "query": num,
            }]

        if not last_sign_was_modifier:
            last_modifier = modifier

        # if sign does not start with [0-9]( or igi-[0-9](
        # then it is a modifier:
        if not re.match( "^(igi-)?[0-9/]+\(", sign ):
            modifier = sign
            last_sign_was_modifier = True

        else:
            last_count = count
            count = sign[ :sign.index("(") ]
            # igi- denotes fractions, e.g.
            # igi-4(disz)-gal2 is 1/4
            if count.startswith("igi-"):
                # all examples in the data have only single-digit denominators
                denom = int( count[4] )
                count = 1./denom
            elif "/" in count:
                # counts can be fractional, e.g. 1/2(disz)
                split = count.index("/")
                count = int(count[:split]) / int(count[split+1:])
            else:
                count = int(count)

            last_unit = unit
            # unit = re.search("\(([^)]*)\)",sign).group(1)
            # Units like 1/3(|NINDA2x(SZE.1(ASZ))|) have multiple parentheses
            # so we manually find the outermost rather than using a regex:
            unit = sign[ sign.index("(") + 1 : len(sign) - 1 - sign[::-1].index(")") ]
            # Sometimes we need to reset the modifier to a new value even
            # without having seen a new modifier sign. E.g. in 1(disz) 1(disz) gin2,
            # the modifier must reset to 1 in between the two instances of disz. reset_modifier
            # determines whether to reset and what value to set it to.
            do_reset, new_modifier = sign_vals.reset_modifier( 
                    unit, count, 
                    last_unit, last_count, 
                    modifier, last_modifier 
                ) 
            if do_reset and not last_sign_was_modifier:
                modifier = new_modifier

            # Get sign value for this number system and multiply
            # by the number of signs there are:
            value += sign_vals[ unit, modifier ] * count
            last_sign_was_modifier = False

    return [{
            "system": sign_vals.name, 
            "unit": sign_vals.unit_name,
            "value": value,
            "modern_unit": sign_vals.modern_unit,
            "modern_value": value * sign_vals.modern_equiv_per_unit,
            "query": num,
            }]

# TODO method to normalize variants: barig, bariga, ban2, ban2@t
