import re

class NumberSystem( object ):
    def __init__( self, name, sign_values, unit_name, modern_unit, modern_equiv_per_unit, resets=dict() ):
        self.name = name
        self.sign_values = sign_values
        self.unit_name = unit_name
        self.modern_unit = modern_unit
        self.modern_equiv_per_unit = modern_equiv_per_unit
        self.resets = resets

        self.possible_signs = set( 
                sign for sign in sign_values if isinstance(sign, str) 
            ).union(
                set( sign[0] for sign in sign_values if isinstance(sign, tuple) )
            ).union(
                set( sign[1] for sign in sign_values if isinstance(sign, tuple) )
            )

    def canParse( self, string, greedy=True ):
        string = normalize( string )
        for sign in string.split(" "):
            if re.match( "^(igi-)?[0-9/]+\(", sign ):
                if ")-kam" in sign and self.name != "cardinal":
                    # ordinal
                    return False # TODO special output for ordinals? e.g. append "th"? Should mark somehow so translation knows there might be additional morphology on this token
                sign = sign[ sign.index("(") + 1 : len(sign) - 1 - sign[::-1].index(")") ]
            if sign not in self.possible_signs: 
                if greedy and (sign == "..." or sign == "x"):
                    continue
                #print(sign,"not in",self.name)
                else:
                    return False
        return True

    #def __iter__(self):
        #return self.sign_values.__iter__()

    def __getitem__( self, arg ):
        if arg  in self.sign_values:
            return self.sign_values[ arg ]
        else:
            sign, mod = arg
            value = self.sign_values[ sign ]
            if mod is not None:
                if str( mod ).isnumeric():
                    value *= mod
                else:
                    value *= self.sign_values[ mod ]
            #print( arg, value )
            return value

    def reset_modifier( self, unit, count, last_unit, last_count, modifier, last_modifier ):
        if unit in self.resets:
            return True, self.resets[ unit ]
        # e.g. 3(disz) 2(disz) sze:
        # e.g. 1/2(disz) 1(disz) sze
        if unit == last_unit \
                and modifier == last_modifier \
                and (isinstance(count,int) and isinstance(last_count, int) \
                or count <= last_count):
            return True, None
        # 1(disz) 1(u) sze
        if unit != last_unit \
                and modifier == last_modifier \
                and last_unit is not None \
                and ( self[ (unit, modifier) ] < self[ (last_unit, last_modifier) ] ):
            return True, None
        return False, modifier

def normalize( string ):
    string = string.lower()
    string = re.sub( "@[a-z]", "", string )
    string = re.sub( "-bi ", " ", string )
    string = re.sub( "gesz'u", "geszu", string )
    string = re.sub( "š", "sz", string )
    return string



