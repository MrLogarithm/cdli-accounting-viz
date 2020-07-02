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
    data: new URLSearchParams({"word": query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      draw_fdg(result);
    },
  });
}

transform = undefined;
function draw_fdg( data ) {

      var fdg_margin = {top: 10, right: 30, bottom: 30, left: 40},
          //fdg_width = 460 - fdg_margin.left - fdg_margin.right,
          fdg_height = 385 - fdg_margin.top - fdg_margin.bottom;

      d3.select("#graph-nearby-div").select("svg").remove();
      var svg = d3.select("#graph-nearby-div")
        .append("svg")
  .attr("viewBox", "0 0 900 350")
          .attr("class", "svg-fdg-colloc") //fdg_width + fdg_margin.left + fdg_margin.right)
          .attr("width", "100%") //fdg_width + fdg_margin.left + fdg_margin.right)
          .attr("height", fdg_height + fdg_margin.top + fdg_margin.bottom)
          .attr("style", "vector-effect: non-scaling-stroke;")
        ;
  var rect = svg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "white");
      var g = svg.append("g")
          .attr("transform",
                "translate(" + fdg_margin.left + "," + fdg_margin.top + ")");
      ;
  //        //add zoom capabilities
      var min_zoom = 0.2;
      var max_zoom = 5;
        var zoom_handler = d3.zoom()
            .scaleExtent([min_zoom,max_zoom])
            .on("zoom", zoom_actions);
        svg.on("wheel", function(d){
            zoom_actions(d);
        });
        zoom_handler(svg);
	//Zoom functions 
  	svg = g;

      //var color = d3.scaleOrdinal().range(d3.schemeCategory10);
      var color = function(id){
	if (id==1) {
	  return "#b3697a";
	}
	return "#69b3a2";
      }
      
      var simulation = d3.forceSimulation()
          .force("link", d3.forceLink()
	    .id(function(d) { return d.id; })
	    .strength(function(d) { return Math.pow(d.value, 2); })
	  )
          .force("charge", d3.forceManyBody()
	    .strength(-30)
	  )
          .force("center", d3.forceCenter(/*fdg_width / 2*/ 150, fdg_height / 2)
	  )
          ;
      
      function build_fdg(graph) {
      
        var link = svg.append("g")
            .attr("class", "links")
          .selectAll("line")
          .data(graph.links)
          .enter().append("line")
            .attr("stroke-width", function(d) { return 2*Math.pow(d.value,2); })
	;
      
        var node = svg.append("g")
            .attr("class", "nodes")
          .selectAll("g")
          .data(graph.nodes)
          .enter().append("g")
      
        var circles = node.append("circle")
	    .attr("class", "fdg_circle")
            .attr("r", 5)
            .attr("fill", function(d) { return color(d.group); });

	node
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended)
	    );
      
        var lables = node.append("text")
            .text(function(d) {
              return d.id;
            })
            .attr('x', 6)
            .attr('y', 3)
	    .attr('font-size', 18)
	    .attr("class", "fdg_text")
	    .attr("fill", "#000")
	;
      
        node.append("title")
            .text(function(d) { return d.id + "\n" + d.freq; });
      
        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);
      
        simulation.force("link")
            .links(graph.links);
      
        function ticked() {
          link
              .attr("x1", function(d) { return d.source.x; })
              .attr("y1", function(d) { return d.source.y; })
              .attr("x2", function(d) { return d.target.x; })
              .attr("y2", function(d) { return d.target.y; })
              .attr("stroke", "#69b3a2");
      
          node
              .attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
              })
	  ;
        }
      }
      build_fdg(data);
  /*{
	"nodes": [
	  {"id":"1","group":1},
	  {"id":"2","group":1},
	  {"id":"3","group":1},
	  {"id":"4","group":2},
	  {"id":"5","group":2},
	  {"id":"6","group":2},
	],
	"links": [
	  {"source":"1", "target":"2", "value":1},
	  {"source":"1", "target":"3", "value":1},
	  {"source":"3", "target":"2", "value":1},
	  {"source":"3", "target":"4", "value":0.1},
	  {"source":"4", "target":"5", "value":1},
	  {"source":"4", "target":"6", "value":1},
	  {"source":"5", "target":"6", "value":1},
	]});*/
      
      function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      
      function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
      }
      
      function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
        //var real_svg = d3.select("#graph-nearby-div").select("svg");
        function zoom_actions() {
	    if (d3.event.transform != undefined) {
	      transform = d3.event.transform;
	    }
	    if ( transform ) {
            svg.attr("transform", transform);//.toString().replace(/scale\(([^)]*)\)/,"scale3d($1, $1, $1)"));
	    d3.selectAll(".fdg_circle").attr("r", 5/transform.k);
	    d3.selectAll(".fdg_text")
	      .attr("font-size", Math.max(18/transform.k,2))
	      .attr("x", 6/transform.k)
	      .attr("y", 3/transform.k)
	      ;
	    }
        }
      
    }
