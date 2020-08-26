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

/* Trigger search with random word when
 * user click the random word button.
 */
$("#random-button").click(function(e){
  var num_items = json_data.all_objects.length;
  var word = json_data.all_objects[Math.floor(Math.random() * num_items)];
  $("#search-input").val(word);
  $("#search-button").click();
});

// Draw summary statistics under the main histogram:
function update_summary_stats( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/summaryStats",
    type: "POST",
    data: new URLSearchParams({"query": query, "system": system,"corpus":corpus}).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {
      for (item of result) {
	var stat_name = item.statistic;
	var value = item.value;
	if ( typeof value == 'number' ) {
	  // Round to nearest hundredth:
	  value = Math.round(100*value)/100;
	}
	$("#"+stat_name).html( value );
      }
    },
  });
}

function redraw_figures( query, corpus ) {
  $.ajax({
    async: false,
    url: api_base_url + "/getNumberSystems",
    type: "POST",
    data: new URLSearchParams({"query": query, "corpus":corpus}).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {

      /* Add radio buttons for filtering histogram: */
      $('#histogram-radio').empty();
      
      var radio_template = `
        <div class="form-check px-3" style="margin-top: 6px; display: inline-block;">
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

      for (entry of result) {
	label = entry.system;
	if (label == "unknown")
	  continue;
        $('#histogram-radio').append(
          radio_template.replace(/BUTTON_LABEL/g, label)
        );
      }

      $('.hist-select').change(function(){

	// Redraw all figures:
	if ( this.checked ) {

          $('#loading-indicator').show();
	  
	  params.system = this.value;
	  updateURLParameters();

	  var promises = [
	    draw_histogram( query, this.value, url_compress_corpus(params.corpus) ),
            update_summary_stats( query, this.value, url_compress_corpus(params.corpus) ),
          
	    show_modifier_list( query, this.value, url_compress_corpus(params.corpus) ),
	    show_modifier_graph( query, this.value, url_compress_corpus(params.corpus) ),

            show_colloc_list( query, this.value, url_compress_corpus(params.corpus) ),
	    show_colloc_graph( query, this.value, url_compress_corpus(params.corpus) ),
          
	    draw_all_similarity( query, this.value, url_compress_corpus(params.corpus) ),

	    show_concordance( query, this.value, url_compress_corpus(params.corpus) )
	  ];
	  Promise.all(promises).then(
	    function() {
            $('#loading-indicator').hide();
	  }
          );
	}
      });

      matching_button = $('.hist-select').filter(function(){
	  return this.value == params.system;
      });
      // Click the button matching the current selection,
      // if one exists. Else click the first button:
      if ( matching_button.length == 1 ) {
        matching_button.click();
      } else {
        $('.hist-select').first().click();
      }
    
    },
  });
}

/* If the search term is in the dataset, 
 * redraw the figures and update the page.
 */
function do_search() {

  var _query = $("#search-input").val();
  if ( json_data.all_objects.includes(_query) ) {
    $('#loading-indicator').show();
    
    query = $("#search-input").val();
    params.query = query;
    updateURLParameters();
  
    // TODO handle modifiers and number system filters
    labeled_query = query + "_COM";

    set_header( query );

    redraw_figures( labeled_query, url_compress_corpus(params.corpus) );
  } else {
    /* Show "Word not recognized" tooltip */
    $('.search-tooltip').css("opacity",1);
    $('.search-tooltip').css("z-index",2);
    setTimeout(function() {
      $('.search-tooltip').css("opacity",0);
      $('.search-tooltip').css("z-index",-2);
    }, 1500);
  }
}

/* Set the header above the main histogram
 * equal to the search term; update the
 * definition if the word is in the dictionary.
 */
function set_header( query ) {
  $('#histogram-header').html(query);
  if ( json_data.dictionary.hasOwnProperty(query) && json_data.dictionary[query].join(", ")!="") {
    var definition = json_data.dictionary[query].join(", ");
    $('#translation').html( "[" + definition + "]" );
  } else {
    $('#translation').html("");
  }
}
