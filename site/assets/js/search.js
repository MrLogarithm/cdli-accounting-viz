function do_search() {
  query = $("#search-input").val();
  console.log("searching for");
  console.log( query );
  // TODO handle modifiers and number system filters
  if ( json_data.all_objects.includes(query) ) {
    $('#histogram-header').html(query);
    if ( json_data.dictionary.includes(query) ) {
      defintion = json_data.dictionary[query];
      $('#translation').html( "[" + definition + "]" );
    } else {
      $('#translation').html();
    }
  }
}

$("#search-input").keypress(function(e){
  if (e.which == 13) { // 13 == Enter
    do_search();
  }
});
$("#search-button").click(function(e){
  do_search();
});
