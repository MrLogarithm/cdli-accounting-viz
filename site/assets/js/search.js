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
    var units = {};
    values.forEach(function(readings) {
      readings.forEach(function(reading) {
	if (! total_values.hasOwnProperty(reading.system)) {
	  total_values[reading.system] = 0;
	  units[reading.system] = reading.unit;
	}
	if (reading.value != "none" ) {
	  total_values[reading.system] += reading.value;
	}
      });
    });
    var system = "cardinal";
    console.log(total_values);
    $("#label-total-value").html( Math.round(total_values[system]) + " " + units[system] );


    // TODO redraw radio buttons based on observed counts
    // 
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
