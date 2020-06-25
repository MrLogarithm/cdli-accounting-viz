/* Trigger search function when the user
 * presses Enter or clicks the search button:
 */
$("#search-input").keypress(function(e){
  if (e.which == 13) { // 13 == Enter
    do_search();
  }
});
$("#search-button").click(function(e){
  do_search();
});

function summary_stats( arr ) {
  arr = arr.sort();
  var sum = 0;
  var sum_sq = 0;
  var mode = undefined;
  var mode_count = 0;
  var curr_mode = undefined;
  var curr_mode_count = 0;
  for ( var elem of arr ) {
    sum += elem;
    sum_sq += elem*elem;
    if (curr_mode === undefined) {
      curr_mode = elem;
    }
    if (elem == curr_mode) {
      curr_mode_count += 1;
    } else {
      if (curr_mode_count>mode_count){
	mode = curr_mode;
	mode_count = curr_mode_count;
      }
      curr_mode = elem;
      curr_mode_count = 1;
    }
  }
  var mean = sum/arr.length;
  var variance = (sum_sq/arr.length) + ((sum*sum)/(arr.length*arr.length));
  return {
    'mean':Math.round(100*mean)/100,
    'median':Math.round(
      100*arr[Math.round(arr.length/2)]
    )/100,
    'mode':Math.round(100*mode)/100,
    "stdev":Math.round(100*Math.sqrt(variance))/100,
  };
}

/* If the search term is in the dataset, 
 * redraw the figures and update the page.
 */
function do_search() {
  query = $("#search-input").val();

  // TODO handle modifiers and number system filters
  labeled_query = query + "_COM";
  if ( json_data.all_objects.includes(query) ) {
    set_header( query );

    /* Get total number of instances: */
    var counts = json_data.counts_by_commodity[ labeled_query ];
    var n_instances = 0;
    Object.keys(counts).forEach(function(key){
      n_instances += counts[key];
    });
    $("#label-total-entries").html( n_instances );

    /* Get total value of counted objects: */
    var values = json_data.values_by_commodity[ labeled_query ];
    var total_values = {};
    var values_by_system = {}
    var units = {};
    values.forEach(function(readings) {
      readings.forEach(function(reading) {
	if (! total_values.hasOwnProperty(reading.system)) {
	  total_values[reading.system] = 0;
	  values_by_system[reading.system] = [];
	  units[reading.system] = reading.unit;
	}
	if (reading.value != "none" ) {
	  total_values[reading.system] += reading.value;
	  values_by_system[reading.system].push( reading.value );
	}
      });
    });
    // TODO get this from the radio buttons
    var system = "cardinal";
    hist_data = values_by_system[system].map(x => Object({value:x}));
    draw_histogram( hist_data );
    //console.log(total_values);
    $("#label-total-value").html( Math.round(total_values[system]) + " " + units[system] );

    var stats = summary_stats( values_by_system[system] );
    $("#mean").html( stats['mean'] );
    $("#median").html( stats['median'] );
    $("#mode").html( stats['mode'] );
    $("#stdev").html( stats['stdev'] );
    // TODO redraw radio buttons based on observed counts
  } else {
    /* Show "Word not recognized" tooltip */
    $('.search-tooltip').css("opacity",1);
    setTimeout(function() {
      $('.search-tooltip').css("opacity",0);
    }, 1500);
  }
}

/* Set the header above the main histogram
 * equal to the search term; update the
 * definition if the word is in the dictionary.
 */
function set_header( query ) {
  $('#histogram-header').html(query);
  if ( json_data.dictionary.hasOwnProperty(query) ) {
    var definition = json_data.dictionary[query];
    $('#translation').html( "[" + definition + "]" );
  } else {
    $('#translation').html();
  }
}
