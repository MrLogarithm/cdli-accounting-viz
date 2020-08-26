// Adapted from: //
// https://www.d3-graph-gallery.com/graph/histogram_binSize.html
// https://www.d3-graph-gallery.com/graph/histogram_tooltip.html

// Figure proportions:
var sim_width = 370,
    sim_margin = 80,
    sim_height = 120;

// Draw similarity histogram for one word:
function draw_one_similarity( word, delta, distribution ) {

  // Create div for this word:
  var row = d3.select("#similarity-div")
    .append("div")
    .attr("class", "row mb-2")
  ;
  row.append("div")
    .attr("class", "col-2 align-self-center")
    .html(json_data["all_objects"].includes(word)?"<a href='' title='Click to focus this word.' onclick='change_focus(\""+word+"\"); return false'>"+word+"</a>":word)
  ;
  // Unique Id for each div:
  var id = new Date().getTime();
  var svg_div = row.append("div")
    .attr("class", "col-10 align-self-center div-sim-"+id)
  ;
  // Div to hold the delta histogram:
  var svg_delta = svg_div.append("svg")
    .attr("class", "bg-white similarity-reduced")
      .attr("width", sim_width + sim_margin )
      .attr("height", sim_height + sim_margin )
      .append("g")
        .attr("transform",
              "translate(" + (30 + sim_margin/2) + "," + (sim_margin/2) + ")")
  ;
  // Div to hold the full histogram:
  var svg_full  = svg_div.append("svg")
    .attr("class", "bg-white similarity-full d-none")
      .attr("width", sim_width + sim_margin )
      .attr("height", sim_height + sim_margin )
      .append("g")
        .attr("transform",
              "translate(" + (10 + sim_margin/2) + "," + (sim_margin/2) + ")")
  ;

  // Render the figure as svg:
  function draw_svg( svg, data ) {
    // Y axis: initialization
    var reduced = svg.select(function(){return this.parentNode;}).classed("similarity-reduced");
    
    var y = (reduced ? d3.scaleLinear() : d3.scaleSymlog())
      .range([sim_height, 0])
      .domain([
	d3.min( data, d => d.value ),
	d3.max( data, d => d.value )
      ])
      .nice()
    ;
    var yAxis = svg.append("g");
    yAxis.call(d3.axisLeft(y).tickFormat(d3.format(
      reduced ? ".2e" : ",d"
    )));

    // X axis: scale and draw:
    var x = d3.scaleLinear()
      .domain([0, data.length])
      .range([0, sim_width])
    ;

    // Show bar height on hover:
    var tooltip = d3.selectAll(".div-sim-"+id)
      .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "black")
        .style("color", "white")
        .style("border-radius", "5px")
        .style("padding", "10px")
    ;
    var showTooltip = function(d) {
      tooltip
        .style("opacity", 1)
      ;
      tooltip
        .html( d.label )
        .style("left", x(d.index) + "px")
        .style("top", y(0) + "px")
      ;
    }
    var moveTooltip = function(d) {
    }
    var hideTooltip = function(d) {
      tooltip
        .style("left", "0px")
        .style("top", "0px")
        .style("opacity", 0)
      ;
    }

    // Draw bars:
    var rects = svg.selectAll("mybar")
      .data(data)
      .enter()
      .append("g")
      .on("mouseover",  showTooltip )
      .on("mousemove",  moveTooltip )
      .on("mouseleave", hideTooltip )
    ;

    var r_width = 0.9 *x(data.length)/data.length;
    var r_pad   = 0.05*x(data.length)/data.length;
    rects.append("rect")
      .attr("x", function(d) { 
	return x(d.index)+r_pad; 
      })
      .attr("y", function(d) { 
	return y(Math.max(d.value,0)); 
      })
      .attr("width", r_width)
      .attr("height", function(d) {
	h = y(Math.min(0,d.value)) - y(Math.max(0,d.value)); 
	return h;
      })
      .attr("fill", "#69b3a2")
    ;

    // Axis labels: show range of each bar:
    var yLabel = svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "end")
      .attr("transform", "rotate(-90)")
      .style("font-size", "0.9rem")
      .attr("y", reduced?-70:-50)
    ;
    // Axis label depends on which figure we are drawing:
    if ( reduced ) {
      yLabel
        .attr("dy", ".75em")
        .html( "relative frequency (%)" )
      ;
    } else {
      yLabel
        .attr("dy", ".75em")
        .attr("x", -30)
        .html("frequency (%)")
      ;
    }

    // Offset tick locations by .5 to center
    var tickValues = Array(data.length).fill().map((_, idx) => idx+0.5 );
    svg.append("g")
      .style("font-size", "6pt")
      .attr("transform", "translate(0," + y(0) + ")")
      .call(d3.axisBottom(x)
        .tickValues(tickValues)
        .tickFormat(function(n) { 
	  return data.map( d => d.bin )[tickValues.indexOf(n)]; 
	})
      )
    ;
  }
  draw_svg(svg_delta, delta);
  draw_svg(svg_full, distribution);
}

function draw_all_similarity( query, system,corpus ) {
  return $.ajax({
    url: api_base_url + "/similar",
    type: "POST",
    data: new URLSearchParams({"query":query,"system":system,"corpus":corpus}).toString(),
    dataType: "jsonp",
    start_time: new Date().getTime(),
    success: function( result ) {
      // Clear old figures
      d3.select("#similarity-div").selectAll(".row").remove();
      for ( var i = 0; i < result.similarities.length; i++ ) {
	data = result.similarities[i];
        draw_one_similarity( data.word, data.delta, data.distribution );
      }
      if ( $("#toggle-delta").is(":checked") ) {
        $(".similarity-full").toggleClass("d-none");
        $(".similarity-reduced").toggleClass("d-none");
      }
    }
  });
}

