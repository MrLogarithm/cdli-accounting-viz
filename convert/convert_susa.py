#########################
# SUSA / Proto-Elamite:
# By convention sign values are given as multiples of N01
# Values from 
# http://cdli.ox.ac.uk/wiki/doku.php?id=susa_metrological_systems

S = {
        "N08a": 0.5,
        "N01": 1,
        "N14": 10,
        "N34": 60,
        "N48": 600,
        "N45": 3600
    }
D = {
        "N01": 1,
        "N14": 10,
        "N23": 60,
        "N51": 600,
        "N51g": 600,
        "N54g": 3600
    }
B = {
        "N01": 1,
        "N14": 10,
        "N34": 60,
        "N51": 120,
        "N54": 1200
    }
B_sharp = { num+"b": B[num] for num in B }
C = {
        "N39c": 1./120,
        "N30d": 1./60,
        "N30c": 1./30,
        "N24": 1./10,
        "N39b": 1./5,
        "N01": 1,
        "N14": 6,
        "N45": 60,
        "N34": 180,
        "N48": 1800,
        "N46": 1800*6
    }
C_sharp = { num+"@b": C[num] for num in C if num not in ["N39c", "N48", "N46"] }
C_prime = { num+"@c": C[num] for num in C if num not in ["N39c", "N45", "N34", "N48", "N46"] }

num_systems = {
        "S": S, 
        "D": D, 
        "B": B, 
        "B#": B_sharp, 
        "C": C, 
        "C#": C_sharp, 
        "C\'\'": C_prime
    }

unique_signs = {
            sys: set( 
                sign for sign in num_systems[sys]
                for sys2 in num_systems 
                if sign not in num_systems[sys2] 
                and sys != sys2
            ) for sys in num_systems
        }

def convert( numeral_string ):
    # "2(N14) 1(N01)" -> ["2(N14)", "1(N01)"]
    digits = numeral_string.split(" ")

    # Record a value for each possible number system:
    values = { sys:0 for sys in num_systems }

    for digit in digits:
        # 1(N14) -> 1
        sign_count = digit[ :digit.index("(") ]
        # 1(N14) -> N14
        sign_name = digit[ digit.index("(")+1:-1 ]

        # Try to evaluate in every possible system:
        for sys in num_systems:
            try:
                if values[ sys ] != -1:
                    sign_value = num_systems[sys][sign_name] 
                    values[ sys ] += sign_value * int(sign_count)
            except ValueError:
                # cannot convert sign_count to integer,
                # e.g. if digit is n(N01)
                values[ sys ] = -1
            except KeyError:
                # not a valid number system for this sign string
                values[ sys ] = -1

    # Omit impossible number systems (with value == -1):
    return { sys: values[sys] for sys in values if values[sys] >= 0 }

#def is_ambiguous( numeral_string ):
    #return len( convert_num_susa( numeral_string ) ) == 1

