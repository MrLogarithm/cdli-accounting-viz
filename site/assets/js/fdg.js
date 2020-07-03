fdg_transform = undefined;
fdg_blue = "#69b3a2";
fdg_red = "#b3697a";
function draw_fdg( fullData, position ) {


  var max = parseInt($("#n-terms-"+position).prop("max"));
  var val = parseInt($("#n-terms-"+position).val());
  var min_times_attested = (max - val) / max;

  max = parseInt($("#n-links-"+position).prop("max"));
  val = parseInt($("#n-links-"+position).val());
  var min_link_strength  = (max - val) / max;

  data = {
    "nodes":fullData.nodes,
    "links":fullData.links
  };
  function hasEndpoints( edge, nodes ) {
    // Return true if source and target are in the node list:
    return nodes.filter( n => (n.id == edge.source) || (n.id == edge.target) ).length == 2;
  }
  function hasConnection( node, edges ) {
    return edges.filter( e => (e.source == node.id) || (e.target == node.id) ).length > 0;
  }
  var max_freq = data.nodes.reduce(function(prev, current) {
    return (prev.freq >= current.freq) ? prev : current;
  }, {"freq":0}).freq;

  console.log( data.nodes.filter( n=>n.id=='dur3') );
  console.log( 1/max_freq, min_times_attested );
  
  data.nodes = data.nodes.filter( n => (n.freq/max_freq)  >= min_times_attested );
  data.links = data.links.filter( e => hasEndpoints( e, data.nodes ) );
  data.links = data.links.map( function(e) {
    var clone = Object.assign({}, e);
    if (clone.value > 0) {
      clone.value = Math.log( clone.value );
    } else {
      clone.value = 0;
    }
    return clone;
  });
  var max_wt = data.links.reduce(function(prev, current) {
    return (prev.value >= current.value) ? prev : current;
  }, {"value":0}).value;
  data.links = data.links.map( function(e) {
    var clone = Object.assign({}, e);
    clone.value = clone.value / max_wt;
    return clone;
  });
  data.links = data.links.filter( e => e.value >= min_link_strength );
  data.nodes = data.nodes.filter( n => hasConnection( n , data.links ) );

      var fdg_margin = {top: 10, right: 30, bottom: 30, left: 40},
          //fdg_width = 460 - fdg_margin.left - fdg_margin.right,
          fdg_height = 385 - fdg_margin.top - fdg_margin.bottom;
      var fig_x_offset = 150;
      var fig_y_offset = 150;


      var divName = "graph-div-"+position;
      var svgClass = "svg-fdg-"+position;
      var circleClass = "fdg_circle-"+position;
      var textClass = "fdg_text-"+position;
      var tooltipID = "tooltip-"+position;
  

      d3.select("#"+divName).select("svg").remove();
      var svg = d3.select("#"+divName)
        .append("svg")
          .attr("viewBox", "0 0 900 350")
          .attr("class", svgClass) 
          .attr("width", "100%")
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
	  return fdg_red;
	}
	return fdg_blue;
      }
      
      var simulation = d3.forceSimulation()
          .force("link", d3.forceLink()
	    .id(function(d) { return d.id; })
	    .strength(function(d) { return 0.1*Math.pow(d.value, 2); })
	  )
          .force("charge", d3.forceManyBody()
	    .strength(-250)
	  )
          /*.force("center", d3.forceCenter(150, fdg_height / 2)
	    .strength(1)
	  )*/
	  .force("centerX", d3.forceX( 0 )
	    .strength(0.05)
	  )
	  .force("centerY", d3.forceY( 0 /*fdg_height / 2*/ )
	    .strength(0.05)
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
	    .attr("class", circleClass)
            .attr("r", 5)
            .attr("fill", function(d) { return color(d.group); });

	node
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended)
	    );
      
        var labels = node.append("text")
            .text(function(d) {
              return d.id;
            })
            .attr('x', 6)
            .attr('y', 3)
	    .attr('font-size', 18)
	    .attr("class", textClass)
	    .attr("fill", "#000")
	;
      
        // Title text interferes with hovering to see connected nodes:
	/*
	node.append("title")
            .text(function(d) { 
	      //return d.id + "\n" + d.freq; 
	      return d.def == "" ? "" : "[" + d.def + "]";
	    });
	    /**/
      
        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);
      
        simulation.force("link")
            .links(graph.links);
	    
	link.append("title")
	      .text(function(d){ return d.source.id+" "+d.target.id+": "+d.count; })
	;

	// https://bl.ocks.org/martinjc/7aa53c7bf3e411238ac8aef280bd6581
	node
	    .on("mouseover", mouseOver(0.2))
	    .on("mouseout", mouseOut)
	;


	// https://bl.ocks.org/martinjc/7aa53c7bf3e411238ac8aef280bd6581
    // build a dictionary of nodes that are linked
    var linkedByIndex = {};
    graph.links.forEach(function(d) {
        linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });

    // check the dictionary to see if nodes are linked
    function isConnected(a, b) {
        return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
    }
	function mouseOver(opacity) {
        return function(d) {
            // check all other nodes to see if they're connected
            // to this one. if so, keep the opacity at 1, otherwise
            // fade
            node.style("stroke-opacity", function(o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
            node.style("fill-opacity", function(o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
	    var showCliques = $("#showCliques-"+position).prop("checked");
            // also style link accordingly
            link.style("stroke-opacity", function(o) {
	        var isCliqueEdge = showCliques && 
		    (isConnected( o.source, d ) && isConnected(o.target, d) );
                return o.source.id === d.id || o.target.id === d.id || isCliqueEdge ? 1 : opacity;
            });
            link.style("stroke", function(o){
	        var isCliqueEdge = showCliques && 
		    (isConnected( o.source, d ) && isConnected(o.target, d) );
                return o.source.id === d.id || o.target.id === d.id || isCliqueEdge ? o.source.colour : "#ddd";
            });
	    $("#"+tooltipID).html( d.def );
	    if (d.def != "")
	      $("#"+tooltipID).removeClass("d-none");
        };
    }

    function mouseOut() {
        node.style("stroke-opacity", 1);
        node.style("fill-opacity", 1);
        link.style("stroke-opacity", 1);
        link.style("stroke", fdg_blue);
	  
	//if ($("#"+tooltipID).hasClass("d-none"))
	  $("#"+tooltipID).addClass("d-none");
    }


      
        function ticked() {
          link
              .attr("x1", function(d) { return d.source.x+fig_x_offset; })
              .attr("y1", function(d) { return d.source.y+fig_y_offset; })
              .attr("x2", function(d) { return d.target.x+fig_x_offset; })
              .attr("y2", function(d) { return d.target.y+fig_y_offset; })
              .attr("stroke", fdg_blue);
      
          node
              .attr("transform", function(d) {
                return "translate(" + (fig_x_offset+d.x) + "," + (fig_y_offset+d.y) + ")";
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
        function zoom_actions() {
	    if (d3.event.transform != undefined) {
	      fdg_transform = d3.event.transform;
	    }
	    if ( fdg_transform ) {
              svg.attr("transform", fdg_transform);//.toString().replace(/scale\(([^)]*)\)/,"scale3d($1, $1, $1)"));
	      d3.selectAll('.'+circleClass).attr("r", 5/fdg_transform.k);
	      d3.selectAll('.'+textClass)
	        .attr("font-size", Math.max(18/fdg_transform.k,2))
	        .attr("x", 6/fdg_transform.k)
	        .attr("y", 3/fdg_transform.k)
	      ;
	    }
        }
      
    }

