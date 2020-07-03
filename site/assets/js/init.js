api_base_url = "http://localhost:5000";

/* Make tables sortable: */
table_format = {
  sDom:"frt",
  order: [[1,"desc"]],
  language: {
    search:"",
    searchPlaceholder:'Filter'
  },
  paging: false,
}; 
// r: pRocessing (show spinner when working)
// t: show Table
$("#table-nearby").DataTable(table_format);
$("#table-desc").DataTable(table_format);
// This table should be ordered by column 2:
table_format.order[0][0] = 2;
table_format.columns = [
  {type:"string"},
  {type:"num"},
  {type:"num"},
];
$("#table-concordance").DataTable(table_format);



/* Setup toggles for force directed graphs: */
$('#toggle-nearby').click(function() {
  $('#graph-div-colloc').toggleClass('d-none');
  $('#table-div-colloc').toggleClass('d-none');
});
$('#toggle-desc').click(function() {
  $('#graph-div-desc').toggleClass('d-none');
  $('#table-div-desc').toggleClass('d-none');
});
$('#toggle-delta').click(function() {
  $('.similarity-reduced').toggleClass('d-none');
  $('.similarity-full').toggleClass('d-none');
});

/* Disable mousewheel when over figures: */
// https://stackoverflow.com/questions/7571370/jquery-disable-scroll-when-mouse-over-an-absolute-div
$('#graph-nearby-div').hover(function() {
    $(document).bind('mousewheel DOMMouseScroll',function(){ 
        stopWheel(); 
    });
}, function() {
    $(document).unbind('mousewheel DOMMouseScroll');
});
function stopWheel(e){
    if(!e){ /* IE7, IE8, Chrome, Safari */
        e = window.event;
    }
    if(e.preventDefault) { /* Chrome, Safari, Firefox */
        e.preventDefault();
    }
    e.returnValue = false; /* IE7, IE8 */
}


json_data = {};
/* Fetch data: */
$(document).ready(function(){
  data_url="https://raw.githubusercontent.com/MrLogarithm/cdli-accounting-viz/master/commodities.json";
  $.ajax({
    dataType: "json",
    url: data_url,
    success: function( result ) {
	console.log( result );
	json_data = result;
  	$('#search-input').val("kusz");
  	do_search();
    },
  });
});
