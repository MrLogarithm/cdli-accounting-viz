/* Make tables sortable: */
table_format = {
  sDom:"frt",
  order: [[1,"desc"]],
  language: {
    search:"",
    searchPlaceholder:'Filter'
  },
}; 
// r: pRocessing (show spinner when working)
// t: show Table
$("#table-nearby").DataTable(table_format);
$("#table-desc").DataTable(table_format);
// This table should be ordered by column 2:
table_format.order[0][0] = 2;
$("#table-concordance").DataTable(table_format);



/* Setup toggles for force directed graphs: */
$('#toggle-nearby').click(function() {
  $('#graph-nearby-div').toggleClass('d-none');
  $('#table-nearby-div').toggleClass('d-none');
});
$('#toggle-desc').click(function() {
  $('#graph-desc-div').toggleClass('d-none');
  $('#table-desc-div').toggleClass('d-none');
});
$('#toggle-delta').click(function() {
  $('.similarity-reduced').toggleClass('d-none');
  $('.similarity-full').toggleClass('d-none');
});



/* Add radio buttons for filtering histogram: */
var radio_labels = [
  "Area",
  "Cardinal",
  "Capacity",
  "Length",
];
var radio_template = `
  <div class="form-check">
    <input class="form-check-input"
           type="radio"
	     name="histogram-radio"
	     id="radio_BUTTON_LABEL" />
    <label class="form-check-label"
           for="radio_BUTTON_LABEL">
      BUTTON_LABEL
    </label>
  </div>`
for (label of radio_labels) {
  $('#histogram-radio').append(
    radio_template.replace(/BUTTON_LABEL/g, label)
  );
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
    },
  });
});
