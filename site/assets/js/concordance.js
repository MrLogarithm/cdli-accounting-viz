function show_concordance( query, system ) {
  $.ajax({
    async: false,
    url: api_base_url + "/concordance",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word": query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      query = query.replace(/_[^ ]*/g, "");
      var dt = $('#table-concordance').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      for (row of result) {
	dt.row.add([
	  row.line.replace(new RegExp(query, "g"), "<b>"+query+"</b>"),
	  (row.value.length > 0) ? row.value[0].value : "none",//TODO
	  row.count]);
      }
      // Redraw and sort:
      dt.order([2,'desc']).draw();
    },
  });
}

