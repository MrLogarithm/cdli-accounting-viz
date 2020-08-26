/* Code for drawing force directed graphs, shared between
 * collocation and modifier modules.
 */

// javascript's weird handling of variable
// scope means this needs to be global for
// sharing between functions:
fdg_transform = undefined;

// Colors:
fdg_blue = "#69b3a2";
fdg_red = "#b3697a";


function draw_fdg( fullData, position ) {

  // Get value of term frequency slider:
  var max = parseInt($("#n-terms-"+position).prop("max"));
  var val = parseInt($("#n-terms-"+position).val());
  var min_times_attested = (max - val) / max;

  // Get value of edge weight slider:
  max = parseInt($("#n-links-"+position).prop("max"));
  val = parseInt($("#n-links-"+position).val());
  var min_link_strength  = (max - val) / max;

  // Copy data for processing:
  data = {
    "nodes":fullData.nodes,
    "links":fullData.links
  };

  function hasEndpoints( edge, nodes ) {
    // Return true if source and target are in the node list:
    return nodes.filter( n => (n.id == edge.source) || (n.id == edge.target) ).length == 2;
  }
  function hasConnection( node, edges ) {
    // Return true if node is connected to some edge:
    return edges.filter( e => (e.source == node.id) || (e.target == node.id) ).length > 0;
  }

  // Get maximum frequency from node list:
  var max_freq = data.nodes.reduce(function(prev, current) {
    return (prev.freq >= current.freq) ? prev : current;
  }, {"freq":0}).freq;

  
  // Remove nodes that are too rare:
  data.nodes = data.nodes.filter( n => (n.freq/max_freq)  >= min_times_attested );
  // Remove edges that connect to nonexistent nodes:
  data.links = data.links.filter( e => hasEndpoints( e, data.nodes ) );
  // Scale edge weights to make figure look better
  // and more interpretable:
  data.links = data.links.map( function(e) {
    var clone = Object.assign({}, e);
    if (clone.value > 0) {
      /* offset by 1 so edges of weight 1 don't disappear */
      clone.value = Math.log( clone.value + 1 );
    } else {
      clone.value = 0;
    }
    return clone;
  });

  // Get maximum edge weight:
  var max_wt = data.links.reduce(function(prev, current) {
    return (prev.value >= current.value) ? prev : current;
  }, {"value":0}).value;
  // Filter edges with too few occurrences:
  data.links = data.links.map( function(e) {
    var clone = Object.assign({}, e);
    clone.value = clone.value / max_wt;
    return clone;
  });
  data.links = data.links.filter( e => e.value >= min_link_strength );
  // Filter orphaned nodes
  data.nodes = data.nodes.filter( n => hasConnection( n , data.links ) );



  // Setup figure appearance:
  var fdg_margin = {top: 10, right: 30, bottom: 30, left: 40},
      fdg_height = 385 - fdg_margin.top - fdg_margin.bottom;
  var fig_x_offset = 150;
  var fig_y_offset = 150;
 
  // Get name of classes and DOM elements associated with
  // this figure:
  var divName = "graph-div-"+position;
  var svgClass = "svg-fdg-"+position;
  var circleClass = "fdg_circle-"+position;
  var textClass = "fdg_text-"+position;
  var tooltipID = "tooltip-"+position;
  
  // Delete old figure, if one exists:
  d3.select("#"+divName).select("svg").remove();
  // Create SVG and add margins
  var svg = d3.select("#"+divName)
    .append("svg")
      .attr("viewBox", "0 0 900 350")
      .attr("class", svgClass) 
      .attr("width", "100%")
      .attr("height", fdg_height + fdg_margin.top + fdg_margin.bottom)
      .attr("style", "vector-effect: non-scaling-stroke;")
    ;
  // Add blank background to allow pan and zoom
  var rect = svg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "white")
  ;
  // Group to hold figure elements:
  var g = svg.append("g")
    .attr("transform",
          "translate(" + fdg_margin.left + "," + fdg_margin.top + ")");
  ;

  // Add zoom and pan:
  var min_zoom = 0.2;
  var max_zoom = 5;
  var zoom_handler = d3.zoom()
    .scaleExtent([min_zoom,max_zoom])
      .on("zoom", zoom_func);
  svg.on("wheel", function(d){
    zoom_func(d);
  });
  zoom_handler(svg);

  // From now on, all operations target the group
  // that holds figure elements rather than the whole
  // svg object
  svg = g;

  // Map node id to color:
  // We just color the central node 
  // separately from the rest
  var color = function(id) {
    if ( id == 1 ) {
      return fdg_red;
    }
    return fdg_blue;
  }

  // Initialize force simulation:
  var simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
      .id(function(d) { 
	return d.id; 
      })
      .strength(function(d) { 
	// Scale strength down to get a
	// nicely spread-out figure:
	return 0.1*Math.pow(d.value, 2); 
      })
    )
    .force("charge", d3.forceManyBody()
      .strength(-250)
    )
    .force("centerX", d3.forceX( 0 )
      .strength(0.05)
    )
    .force("centerY", d3.forceY( 0 )
      .strength(0.05)
    )
  ;

  function build_fdg(graph) {
  
    // Draw edges:
    var link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter()
        .append("line")
        .attr("stroke-width", function(d) { 
	  // Scale stroke width to exaggerate 
	  // differences and make figure more readable
	  return 2*Math.pow(d.value,2); 
	})
    ;
  
    var node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(graph.nodes)
      .enter()
        .append("g")
    ;
  
    // Draw circles to represent nodes
    var circles = node.append("circle")
      .attr("class", circleClass)
      .attr("r", 5)
      .attr("fill", function(d) { return color(d.group); })
    ;

    // Allow dragging to reposition nodes
    node
      .call(
	d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended)
      )
    ;
    
    // Label nodes with the word the represent:
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
    
    // Add data to simulation and run:
    simulation
      .nodes(graph.nodes)
      .on("tick", ticked);
    simulation.force("link")
      .links(graph.links)
    ;
    
    // Show edge weight on hover:
    link.append("title")
      .text(function(d){ 
        return d.source.id+" "+d.target.id+": "+d.count; 
      })
    ;
    
    node
      .on("mouseover", mouseOver(0.2))
      .on("mouseout", mouseOut)
    ;
    // Node fading on mouseover adapted from:
    // https://bl.ocks.org/martinjc/7aa53c7bf3e411238ac8aef280bd6581
    // Build a dictionary of nodes that are linked:
    var linkedByIndex = {};
    graph.links.forEach(function(d) {
      linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });
    // Check the dictionary to see if nodes are linked:
    function isConnected(a, b) {
      return linkedByIndex[a.index + "," + b.index] 
          || linkedByIndex[b.index + "," + a.index] 
          || a.index == b.index;
    }
  
    function mouseOver(opacity) {
      return function(d) {
        // Check all other nodes to see if they're connected
        // to this one. If so, keep the opacity at 1, otherwise
        // fade out to help user focus on their selection:
        node.style("stroke-opacity", function(o) {
          thisOpacity = isConnected(d, o) ? 1 : opacity;
          return thisOpacity;
        });
        node.style("fill-opacity", function(o) {
          thisOpacity = isConnected(d, o) ? 1 : opacity;
          return thisOpacity;
        });
        // Do we want to highlight cliques?
        var showCliques = $("#showCliques-"+position).prop("checked");
        // Fade out links just like nodes:
        link.style("stroke-opacity", function(o) {
	  // This is a clique edge if both ends are connected 
	  // to the source node:
          var isCliqueEdge = showCliques && 
                            (    isConnected(o.source, d) 
			      && isConnected(o.target, d))
	  ;
          return o.source.id === d.id 
	      || o.target.id === d.id 
	      || isCliqueEdge ? 1 : opacity;
        });
        link.style("stroke", function(o){
          var isCliqueEdge = showCliques && 
                            (    isConnected(o.source, d) 
			      && isConnected(o.target, d))
	  ;
          return o.source.id === d.id 
	      || o.target.id === d.id 
	      || isCliqueEdge ? o.source.colour : "#ddd";
        });
        // Show definition in corner tooltip:
        $("#"+tooltipID).html( d.defs.join(", ") );
        // If there is no definition for this word hide the tooltip
        if (d.defs.length != 0)
          $("#"+tooltipID).removeClass("d-none");
      };
    }
  
    function mouseOut() {
      // Undo fade-out effect on mouseout
      node.style("stroke-opacity", 1);
      node.style("fill-opacity",   1);
      link.style("stroke-opacity", 1);
      link.style("stroke",  fdg_blue);
      // Hide translation tooltip
      $("#"+tooltipID).addClass("d-none");
    }
  
    // This runs every tick of the simulation:
    function ticked() {
      // Update edge positions:
      link
        .attr("x1", function(d) { return d.source.x+fig_x_offset; })
        .attr("y1", function(d) { return d.source.y+fig_y_offset; })
        .attr("x2", function(d) { return d.target.x+fig_x_offset; })
        .attr("y2", function(d) { return d.target.y+fig_y_offset; })
        .attr("stroke", fdg_blue)
      ;
      // Update node positions:
      node
      .attr("transform", function(d) {
        return "translate(" + (fig_x_offset+d.x) + "," + (fig_y_offset+d.y) + ")";
      })
      ;
    }
  }
  build_fdg(data);

  /* Drag, drop, pan, and zoom functionality: */
  function dragstarted(d) {
    // Start simulation if not running:
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
  function zoom_func() {
    // Remember event in case it is later set to
    // "undefined" by d3:
    if (d3.event.transform != undefined) {
      fdg_transform = d3.event.transform;
    }
    // Semantic zoom: scale figure elements to make
    // graph structure clearer
    if ( fdg_transform ) {
      svg.attr("transform", fdg_transform);
       //.toString().replace(/scale\(([^)]*)\)/,"scale3d($1, $1, $1)"));
      d3.selectAll('.'+circleClass)
	.attr("r", 5/fdg_transform.k)
      ;
      d3.selectAll('.'+textClass)
        .attr("font-size", Math.max(18/fdg_transform.k,2))
        .attr("x", 6/fdg_transform.k)
        .attr("y", 3/fdg_transform.k)
      ;
    }
  }
}
