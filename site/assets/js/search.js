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

function update_summary_stats( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/summaryStats",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query, "system": system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      for (item of result) {
	for (entry of Object.entries(item)) {
	  var stat_name = entry[0];
	  var value = entry[1];
	  if ( typeof value == 'number' ) {
	    value = Math.round(100*value)/100;
	  }
	  $("#"+stat_name).html( value );
	}
      }
    },
  });
}

function redraw_main_histogram( query ) {
  $.ajax({
    async: false,
    url: api_base_url + "/getNumberSystems",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      /* Add radio buttons for filtering histogram: */
      $('#histogram-radio').empty();
      
      var radio_template = `
        <div class="form-check">
          <input class="form-check-input hist-select"
                 type="radio"
	         name="histogram-radio"
	         id="radio_BUTTON_LABEL" 
		 value='BUTTON_LABEL'
		 CHECK />
          <label class="form-check-label"
               for="radio_BUTTON_LABEL">
          BUTTON_LABEL
        </label>
      </div>`

      for (label of result) {
	if (label == "unknown")
	  continue;
        $('#histogram-radio').append(
          radio_template.replace(/BUTTON_LABEL/g, label)
        );
      }

      $('.hist-select').change(function(){
	if ( this.checked ) {
	  // update histogram
	  //console.log("redrawing histogram with system",this.value);
          
	  draw_histogram( query, this.value );
          update_summary_stats( query, this.value );
          
	  show_modifier_list( query, this.value );
	  show_modifier_graph( query, this.value );

          show_colloc_list( query, this.value );
	  show_colloc_graph( query, this.value );
          
	  show_concordance( query, this.value );

	  draw_all_similarity( query, this.value );
	}
      });

      // click the first button to prompt a redraw:
      $('.hist-select').first().click();
    
    },
  });
}

/* If the search term is in the dataset, 
 * redraw the figures and update the page.
 */
function do_search() {
  $('#loading-indicator').show();
  
  query = $("#search-input").val();

  // TODO handle modifiers and number system filters
  labeled_query = query + "_COM";
  console.log(query, json_data.all_objects);
  if ( json_data.all_objects.includes(query) ) {
    set_header( query );

    redraw_main_histogram( labeled_query );
  } else {
    /* Show "Word not recognized" tooltip */
    $('.search-tooltip').css("opacity",1);
    setTimeout(function() {
      $('.search-tooltip').css("opacity",0);
    }, 1500);
  }
    $('#loading-indicator').hide();
}

/* Set the header above the main histogram
 * equal to the search term; update the
 * definition if the word is in the dictionary.
 */
function set_header( query ) {
  $('#histogram-header').html(query);
  if ( json_data.dictionary.hasOwnProperty(query) ) {
    console.log(json_data.dictionary);
    var definition = json_data.dictionary[query].join(", ");
    $('#translation').html( "[" + definition + "]" );
  } else {
    $('#translation').html();
  }
}
