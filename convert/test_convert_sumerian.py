from convert.convert_sumerian import *

#print(convert( "2(disz) kusz3", Length))
test_cases = [
        ("3(u) 2(disz) 5(disz) gin2 2(disz) sze", Ordinal, 32.08351851851852),
        ("3(disz) 1/3(disz) 9(disz) 2/3(disz) gin2 4(disz) igi-4(disz)-gal2 sze", Ordinal, 3.494837962962963),
        ("1(disz) 1(u) gin2", Ordinal, 1.1666666666666667),
        ("1(disz) 1(u) 1(disz) gin2", Ordinal, 1.1833333333333333),
        ("1(disz) 1/2(disz) 1/4(disz) 1(disz) 1/2(disz) 1/4(disz) gin2", Ordinal,1.7791666666666668),
        ("igi-6(disz)-gal2 sze", Ordinal, 1/64800),
        ("1(gesz2) 2(u) 1(disz) 1/2(disz) ninda", Length, 163),
        ("1(szargal){gal} 7(szar2) 1(bur'u) 4(bur3) 2(esze3) 5(iku) 1/2(iku) 1/4(iku) GAN2", Surface, 435778500.0),
        ("1(u) 5/6(disz) sar 2(disz) 2/3(disz) gin2 2(u) sze", Volume, 652.7777777777777777),
        ("1(bur3)", Volume, 108000),
        ("1(esze3)", Volume, 36000),
        ("1(bur3) 2(esze3)", Volume, 180000),
        ("1(bur3) 2(esze3) 1(iku) 1/4(iku) iku", Volume, 187500),
        ("1(bur3) 1(esze3) 1(u) 1(disz) sar 1(disz) sze", Volume, 144660.00555555554),
        ("1(bur3) 1(esze3) 1(iku) iku 1(u) 1(disz) sar", Volume, 150660),
        ("1(gesz2) 2(u) 1(asz) 2(barig) 3(ban2) 2(disz) 1/2(disz) sila3 sze gur", DryCapacity,24452.5),
        ("6(disz) 1/3(disz) sar 7(disz) gin2", Brick, 4644),
        ("2(gesz2) 2(u) 2(disz) sar 1(u) 2(disz) gin2", Brick, 102384),
    ]
#
if __name__ == "__main__":
    all_passing = True
    for test_case, system, expected in test_cases:
        #print(test_case)
        result = convert( test_case, system )[0]["value"]
        if not np.isclose( result, expected):
            print( test_case, "expected", expected, "got", result )
            all_passing = False

    if all_passing:
        print("All tests passing.")

    for test_case, test_system, _ in test_cases:
        #print(test_case)
        for system in num_systems:
            if system.canParse( test_case ):
                pass
                #try:
                    #print( "\t", system.name, convert( test_case, system ) )
                #except:
                    #print( "\terror parsing", test_case, "with", system.name)
            elif system.name == test_system.name:
                print( system.name, "should be able to parse", test_case )

