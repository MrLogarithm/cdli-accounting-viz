/* Get URL parameters: */
/* Adapted from https://stackoverflow.com/questions/5448545/how-to-retrieve-get-parameters-from-javascript */
function getSearchParameters() {
      var prmstr = window.location.search.substr(1);
      return prmstr != null && prmstr != "" ? transformToAssocArray(prmstr) : {};
}

function transformToAssocArray( prmstr ) {
    var params = {};
    var prmarr = prmstr.split("&");
    // Decompress parameters if needed:
    // Compressed parameters will never
    // contain = or &
    if ( prmarr.length == 1 && !prmarr[0].includes('=') ) {
      // Split on , instead of &:
      prmarr = decodeURIComponent(prmarr);
      // If corpus is the only parameter
      // specified, there will be no ,
      if ( prmarr.includes(',') ) {
        prmarr = prmarr.split(',');
        params.query = prmarr[0];
        params["filter-concordance"] = prmarr[1];
        params["filter-nearby"] = prmarr[2];
        params["filter-descriptors"] = prmarr[3];
        params["n-bins-histogram"] = prmarr[4];
        params["n-terms-colloc"] = prmarr[5];
        params["n-links-colloc"] = prmarr[6];
        params["n-terms-desc"] = prmarr[7];
        params["n-links-desc"] = prmarr[8];
        var bool_terms = [
          'toggle-similar',
          'toggle-nearby',
          'toggle-descriptors',
          'showCliques-colloc',
          'showCliques-desc'
        ];
        for (var idx = 0; idx < 5; idx++) {
	  params[bool_terms[idx]] = prmarr[9][idx]=='t'?'true':'false';
        }
        var systems_dict = {
	  "d": "date",
	  "c": "cardinal",
	  "l": "length",
	  "s": "surface",
	  "v": "volume",
	  "r": "dry capacity",
	  'q': "liquid capacity",
	  "w": "weight",
	  "b": "bricks"
        };
        params.system = systems_dict[prmarr[9][5]];
        params.corpus = url_decompress_corpus(prmarr[9].substr(6));
      } else {
	params.corpus = url_decompress_corpus(prmarr);
      }
    } else {
      for ( var i = 0; i < prmarr.length; i++) {
        var tmparr = prmarr[i].split("=");
        params[tmparr[0]] = decodeURIComponent(tmparr[1]);
      }
    }
    return params;
}

/* Code for corpus compression.
 * Essentially a Huffman encoding 
 * limited to URL-safe characters.
 */
var corpus_encoding = {',':'A','0':'B','1':'C','2':'D','3':'E','4':'F','5':'G','6':'H','7':'I','8':'J','9':'K','1,1,':'L','0,':'M','1,':'N','2,':'O','3,':'P','4,':'Q','5,':'R','6,':'S','7,':'T','8,':'U','9,':'V',',0':'W',',1':'X',',2':'Y',',3':'Z',',4':'a',',5':'b',',6':'c',',7':'d',',8':'e',',9':'f','00':'g','11':'h','22':'i','33':'j','44':'k','55':'l','66':'m','77':'n','88':'o','99':'p','0,1':'q','1,1':'r','2,1':'s','3,1':'t','4,1':'u','5,1':'v','6,1':'w','7,1':'x','8,1':'y','9,1':'z',',0,':'0',',1,':'1',',2,':'2',',3,':'3',',4,':'4',',5,':'5',',6,':'6',',7,':'7',',8,':'8',',9,':'9'};
function url_compress_corpus( corpus ) {
  // Convert to list:
  corpus = corpus.includes('+') ? corpus.split("+") : corpus.split(' ');
  // Remove P and convert to integers:
  corpus = corpus.map(
    function(x){
      if ( x.includes("P") ) { 
	return parseInt(x.substr(1,6)); 
      } else { 
	return parseInt(x); 
      }
    }
  );
  // Sort numerically
  // Why in the world does JS default to lexicographic order?
  corpus.sort(
    function(a,b){
      return a>b?1:-1;
    }
  ); 
  // Compute difference between successive numbers
  var deltas = corpus.map(
    function(x,i){
      if (i>0) {
	return corpus[i] - corpus[i-1]
      } else {
	return 0;
      }
    }
  );
  // First number should be the full artifact id, not a delta:
  deltas[0] = corpus[0];
  // Back to string, which we be encoded:
  var string = deltas.join(',');
  // Find length of longest string which can be
  // encoded by a single character:
  var max_length = Object.keys( corpus_encoding ).reduce(
    function(a, b) { return a.length > b.length ? a : b}
  ).length;
  var i = 0;
  var encoding = '';
  // Iteratively replace substrings
  // with their encoded equivalent:
  while (i < string.length) {
    for (var length=max_length; length>0; length--) {
      key = string.substr(i,length);
      if (corpus_encoding.hasOwnProperty(key)) {
	encoding += corpus_encoding[key];
	i += length;
	break;
      }
    }
  }
  return encoding;
}

/* Given an encoded corpus, convert back
 * to a list of p-numbers.
 */
function url_decompress_corpus( string ) {
  // Reverse the encoding map to get a code for decipherment:
  var decode_dict = {};
  Object.keys(corpus_encoding).forEach(
    key => {decode_dict[corpus_encoding[key]]=key;}
  );

  var corpus = '';
  // Replace each character with the decoded equivalent:
  for (var idx = 0; idx<string.length; idx++) {
    corpus += decode_dict[string[idx]];
  }
  // Split and convert to ints:
  corpus = corpus.split(',');
  corpus = corpus.map(x => parseInt(x));
  // Convert from deltas to full ids:
  for (var i = 1; i < corpus.length; i++) {
    corpus[i] += corpus[i-1];
  }
  // Prepend P and zero pad
  corpus = corpus.map(x => 'P'+x.toString().padStart(6, '0'));
  corpus = corpus.join('+');
  return corpus;
}

/* Compress all search parameters and figure 
 * settings into a short URL-safe encoding.
 */
function url_compress_params( params ) {
  // Record the search terms and numeric values
  // in full. These will be short enough that 
  // most compression schemes will just make them
  // larger.
  compressed  = params.query+',';
  compressed += params["filter-concordance"]+',';
  compressed += params["filter-nearby"]+',';
  compressed += params["filter-descriptors"]+',';
  compressed += params["n-bins-histogram"]+',';
  compressed += params["n-terms-colloc"]+',';
  compressed += params["n-links-colloc"]+',';
  compressed += params["n-terms-desc"]+',';
  compressed += params["n-links-desc"]+',';
  // Convert booleans to string of t and f chars:
  var bools = [
    params['toggle-similar'],
    params['toggle-nearby'],
    params['toggle-descriptors'],
    params['showCliques-colloc'],
    params['showCliques-desc']
  ];
  for (bool of bools) {
    compressed += (bool=="true")?'t':'f';
  }
  // Single-letter representation of the number system:
  if ( params.system == 'liquid capacity' ) {
    compressed += 'q';
  } else if ( params.system == 'dry capacity' ) {
    compressed += 'r';
  } else {
    compressed += params.system[0];
  }
  return compressed;
}
/* Get a URL-safe string encoding all of the
 * search parameters as well as the current
 * corpus.
 */
function url_compress( params ) {
  var compressed = '';
  compressed += url_compress_params( params );
  compressed += url_compress_corpus( params.corpus );
  return compressed;
}

/* 'not' operator for strings */
/* This makes it easier to work with
 * string-type URL params without 
 * converting back and forth to bools */
function not(x) {
  return x == "true" ? "false" : "true";
}



// params must be a global var so all modules can access them:
params = getSearchParameters();

// Set default URL parameters if not provided by user:
var defaultParams = {
  "query": "udu",

  "n-bins-histogram": 40,
  
  "toggle-similar": "false",
  "toggle-nearby": "false",
  "toggle-descriptors": "false",
  
  "filter-concordance": "",
  "filter-nearby": "",
  "filter-descriptors": "",

  "n-terms-colloc": 99,
  "n-links-colloc": 25,
  "showCliques-colloc": "false",

  "n-terms-desc": 99,
  "n-links-desc": 25,
  "showCliques-desc": "false",

  "system": "",

  "corpus": "P100839",
};
for ( const [key, value] of Object.entries(defaultParams) ) {
  if (!params.hasOwnProperty(key)) {
    params[key] = value;
  }
}

/* Encode the parameters if they are too long,
 * and store them in the URL. Also add a new
 * history state so the user can use the back
 * button to revert changes.
 */
function updateURLParameters() {
  var urlString = "/cdli-accounting-viz/?";
  for (const [key,value] of Object.entries(params)) {
    urlString += encodeURIComponent(key)+"="+encodeURIComponent(value)+"&";
  }
  urlString = urlString.substring( 0, urlString.length - 1 );
  // If string is too large, use encoded version instead.
  if ( (window.location.host+window.location.pathname+urlString).length >= 2048 ) {
    urlString = "/cdli-accounting-viz/?"+url_compress( params );
  }
  window.history.replaceState("object or string", "Title", urlString );
}

// Update URL with default parameters:
updateURLParameters();
