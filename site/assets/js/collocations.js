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
