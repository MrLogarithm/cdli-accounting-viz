// List mapping lines to
// cdli numbers where that
// line occurs
cdliNos = new Object();
function getConcordanceCDLINumbers( line ) {
  return cdliNos[line];
}
function show_concordance( query, system, corpus ) {
  return $.ajax({
    async: false,
    url: api_base_url + "/concordance",
    type: "POST",
    data: new URLSearchParams({
      "query": query,
      "system":system,
      "corpus":corpus
    }).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {

      // Remove _COM and _MOD annotation:
      // (Do not need them now, but might need to distinguish
      // commodity from modifier for advanced search in the future.)
      query = query.replace(/_[^ ]*/g, "");

      var dt = $('#table-concordance').DataTable();
      // Empty current table:
      dt.clear();
      // Append all rows:
      var rows = [];
      cdliNos = new Object();
      // Reset list of P numbers
      for (row of result) {
	cdliNos[row.line] = row.sources;
	rows.push([
	  // Bold the query word for ease of identification:
	  row.line.replace(new RegExp(query, "g"), "<b>"+query+"</b>"),
	  // If there is a number in the line, 
	  // record its value in the second column
	  (row.value.match(/[0-9]/g)) ? row.value : "none",
	  row.count
	]);
      }
      dt.rows.add(rows);
      // Redraw and sort:
      dt.search( params["filter-concordance"] );
      dt.order([2,'desc']).draw();
    
    },
  });
}

