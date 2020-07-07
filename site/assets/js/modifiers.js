fdg_data_desc = undefined;
$("#n-terms-desc").on("input", function() {
  draw_fdg(fdg_data_desc, "desc");
});

$("#n-links-desc").on("input", function() {
  draw_fdg(fdg_data_desc, "desc");
});

function show_modifier_list( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/modifiers",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      var dt = $('#table-desc').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      for (row of result) {
	dt.row.add([row.modifier,row.count]);
      }
      // Redraw and sort:
      dt.order([1,'desc']).draw();
    },
  });
}

function show_modifier_graph( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/modifiersGraph",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      fdg_data_desc = result;
      draw_fdg(fdg_data_desc, "desc");
    },
  });
}
