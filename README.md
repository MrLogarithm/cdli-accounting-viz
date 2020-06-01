# cdli-accounting-viz
Utilities and visualizations for CDLI accounting corpora. *Confer* https://cdli-gh.github.io/blog/gsoc20/numerals/index

#### convert/
Module for converting numbers from cuneiform and cuneiform-adjacent scripts into arabic numerals. Currently supports proto-Elamite and ED IIIb Sumerian. `convert_flask.py` contains the skeleton of a Flask API for querying this module.

#### dict/
Module which sets up a simple Sumerian-English dictionary derived from the [ePSD](http://psd.museum.upenn.edu/nepsd-frame.html). Where possible, dictionary items are annotated with a POS tag projected from the English definition. **This is a rudimentary proof-of-concept** which will eventually be replaced by a proper Sumerian POS tagger. Please do not use this module unless you are willing to manually verify its output and make corrections.

#### doc/
Additional documentation and notes.

#### segment.py
Script to detect and parse the numbers in a transliterated text. The result is a text which has been segmented into "entries" delimited by numbers. 

#### commodify.py
Script to extract counted objects ("commodities") from a transliterated text. The result is a CLAWS-style annotation where counted objects are labeled with `_COM`, as in *2(disz) ku6\_COM dar-ra* where *ku6* "fish" has been labeled as a commodity accompanying the count 2(disz).


## Notes & To-Do
- Confirm: asz can be used as a cardinal, as in *2(asz) ku6 dar-ra*?
- Confirm: tablet-final \|ASZxDISZ\| records the year the document was inscribed?
- Add option to toggle greedy handling of *...* and *x* when detecting numerals
- (asz){sza}, as in *2/3(asz){sza} sar* 
- If we fetch details from the ePSD, note that some sign names differ between the CDLI corpus and the ePSD (e.g. ePSD has *zid2* where CDLI has *zi3*, but these are apparently [the same sign](http://etcsl.orinst.ox.ac.uk/edition2/signlist.php)).
- Handle discontinuities: *4(asz) siki ma-na* records *4(asz) ma-na* (~2kg) of *siki* (wool), not *4(asz) siki* of *ma-na*.
- Handle subtraction: *u4 1(u) la2 1(disz)-kam* "the 9th day" written as "the 10 - 1th day"
- Surface measures seem to have more variability than other notations. See `doc/issues_surface.txt` for problem cases.
- *{gisz}...* and *{gisz}x* etc are not commodities
- Check morphology: are e.g. *{gisz}RU* and *{gisz}RU-ur-ka* the same thing?
