// Define FDG data globally for sharing between functions:
fdg_data_colloc = undefined;
cdliNos_colloc = new Object();
function getCollocationCDLINumbers( line ) {
  return cdliNos_colloc[line];
}

// Redraw graph when sliders are adjusted:
$("#n-terms-colloc").on("input", function() {
  params["n-terms-colloc"] = $("#n-terms-colloc").val();
  updateURLParameters();
  draw_fdg(fdg_data_colloc, "colloc");
});
$("#n-links-colloc").on("input", function() {
  params["n-links-colloc"] = $("#n-links-colloc").val();
  updateURLParameters();
  draw_fdg(fdg_data_colloc, "colloc");
});
$("#showCliques-colloc").on("input", function() {
  params["showCliques-colloc"] = $("#showCliques-colloc").prop("checked") ? "true" : "false";
  updateURLParameters();
});

// Redraw collocation table with new search term:
function show_colloc_list( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/collocations",
    type: "POST",
    data: new URLSearchParams({
      "query": query,
      "system":system,
      "corpus":corpus
    }).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {
      
      var dt = $('#table-nearby').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      cdliNos_colloc = new Object();
      for (row of result) {
	cdliNos_colloc[row.term] = row.sources;
	dt.row.add([row.term,row.count]);
      }
      dt.search( params["filter-nearby"] );
      // Redraw and sort:
      dt.order([1,'desc']).draw();

    },
  });
}

// Redraw FDG with new search term:
function show_colloc_graph( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/collocationsGraph",
    type: "POST",
    data: new URLSearchParams({
      "query": query,
      "system":system, 
      "corpus":corpus
    }).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {

      fdg_data_colloc = result;
      draw_fdg(fdg_data_colloc, "colloc");
    
    },
  });
}
