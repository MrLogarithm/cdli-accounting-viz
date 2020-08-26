// Figure data needs global scope to access
// inside of d3 functions:
fdg_data_desc = undefined;
cdliNos_desc = new Object();
function getDescriptionCDLINumbers( line ) {
  return cdliNos_desc[line];
}

// Update figure on slider interactions:
$("#n-terms-desc").on("input", function() {
  params["n-terms-desc"] = $("#n-terms-desc").val();
  updateURLParameters();
  draw_fdg(fdg_data_desc, "desc");
});
$("#n-links-desc").on("input", function() {
  params["n-links-desc"] = $("#n-links-desc").val();
  updateURLParameters();
  draw_fdg(fdg_data_desc, "desc");
});
$("#showCliques-desc").on("input", function() {
  params["showCliques-desc"] = $("#showCliques-desc").prop("checked") ? "true" : "false";
  updateURLParameters();
});

// Show modifiers as a table:
function show_modifier_list( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/modifiers",
    type: "POST",
    data: new URLSearchParams({"query": query,"system":system,"corpus":corpus}).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {
      var dt = $('#table-desc').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      cdliNos_desc = new Object();
      for (row of result) {
	cdliNos_desc[row.modifier] = row.sources;
	dt.row.add([row.modifier,row.count]);
      }
      dt.search( params["filter-descriptors"] );
      // Redraw and sort:
      dt.order([1,'desc']).draw();
    },
  });
}

// Show modifiers as a graph:
function show_modifier_graph( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/modifiersGraph",
    type: "POST",
    data: new URLSearchParams({"query": query,"system":system,"corpus":corpus}).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {
      fdg_data_desc = result;
      draw_fdg(fdg_data_desc, "desc");
    },
  });
}
