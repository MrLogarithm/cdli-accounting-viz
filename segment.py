import re
import convert
import data

def segment( text, greedy=True ):
    """
    Given a transliterated text, tokenize it and split into entries
    using the numerals as delimiters. 

    text:   the document to segment
    greedy: if True, missing material will be interpreted as part of
            a number where possible. E.g. 1(u) ... 1(asz) will be
            parsed as one (partly unreadable) number in greedy mode,
            or as 3 tokens (1(u) = 10, ..., and 1(asz) = 1) otherwise.

    returns:    an array of (word, reading) tuples. If word is a numeral,
                reading will list its possible values; else reading is None.
    """

    # Output array:
    segmented = []

    i = 0
    while i < len(text):
        sign = text[i]

        # Record how many tokens of input we have processed
        length = 1

        # Is this sign a numeral?
        if re.match( "(igi-)?[0-9]/?[0-9]*\(", sign ):
            # Find the end of the number:
            while i + length < len(text):
                # If we encounter a broken sign, only
                # continue if we're in greedy mode:
                if text[i+length] in set(["...", "x"]) and not greedy:
                    break

                string = " ".join(text[ i : i + length + 1])
                string = convert.convert_sumerian.normalize( string )

                # If we can parse the string as a number, keep going:
                if any([ system.canParse( string ) 
                    for system in convert.convert_sumerian.num_systems ]):
                    length += 1

                    # In cases like 1(iku) gan2 1(asz) gur, enforce a break
                    # after gan2:
                    if text[i+length-1].lower() == "gan2":
                        break

                # If we can't parse the string as a number, we must have
                # reached the end of the numeral string:
                else:
                    break

            # Convert the number:
            string = " ".join(text[ i : i + length ])
            string = convert.number_system.normalize( string )
            conversion = convert.convert_sumerian.convert( string )

            segmented.append( (string, conversion) )
        else:
            string = text[i]
            segmented.append( (string, None) )

        # How many tokens did we consume?
        i += length

    return segmented

if __name__ == "__main__":
    for text in data.girsu:
        print("\n\n\n")
        for word, value in segment( text, greedy=False ):
            print( word, value is None )
