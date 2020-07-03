fdg_data_colloc = undefined;
$("#n-terms-colloc").on("input", function() {
  draw_fdg(fdg_data_colloc, "colloc");
});

$("#n-links-colloc").on("input", function() {
  draw_fdg(fdg_data_colloc, "colloc");
});

function show_colloc_list( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/collocations",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      var dt = $('#table-nearby').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      for (row of result) {
	dt.row.add([row.term,row.count]);
      }
      // Redraw and sort:
      dt.order([1,'desc']).draw();
    },
  });
}

function show_colloc_graph( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/collocationsGraph",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({
      "word": query,
      "system":system, 
    }).toString(),
    dataType: "jsonp",
    success: function( result ) {
      fdg_data_colloc = result;
      draw_fdg(fdg_data_colloc, "colloc");
    },
  });
}
