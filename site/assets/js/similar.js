// Adapted from: //
// https://www.d3-graph-gallery.com/graph/histogram_binSize.html
// https://www.d3-graph-gallery.com/graph/histogram_tooltip.html

var sim_width = 370,
    sim_margin = 80,
    sim_height = 120;

function draw_one_similarity( word, delta, distribution ) {

  var row = d3.select("#similarity-div")
    .append("div")
    .attr("class", "row mb-2")
  ;
  row.append("div")
    .attr("class", "col-2 align-self-center")
    .html(word)
  ;
  var svg_div = row.append("div")
    .attr("class", "col-10 align-self-center div-sim-"+word)
  ;
  var svg_delta = svg_div.append("svg")
    .attr("class", "bg-white similarity-reduced")
      .attr("width", sim_width + sim_margin )
      .attr("height", sim_height + sim_margin )
      .append("g")
        .attr("transform",
              "translate(" + (sim_margin/2) + "," + (sim_margin/2) + ")")
  ;
  var svg_full  = svg_div.append("svg")
    .attr("class", "bg-white similarity-full d-none")
      .attr("width", sim_width + sim_margin )
      .attr("height", sim_height + sim_margin )
      .append("g")
        .attr("transform",
              "translate(" + (sim_margin/2) + "," + (sim_margin/2) + ")")
  ;

  function draw_svg( svg, data ) {
  // Y axis: initialization
  var y = d3.scaleLinear()
      .range([sim_height, 0])
      .domain([d3.min( data, d => d.value ),d3.max( data, d => d.value )])
    ;
  var yAxis = svg.append("g");
  yAxis.call(d3.axisLeft(y)
    //.tickValues([])
  );

  // X axis: scale and draw:
  var x = d3.scaleLinear()
      .domain([0,data.length])
      .range([0, sim_width])
    ;

  var tooltip = d3.selectAll(".div-sim-"+word)
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
    tooltip
      .html( d.label )
      //.style("left", (d3.event.pageX)-10 + "px")
      //.style("top", (d3.event.pageY)-85 + "px")
      .style("left", x(d.index) + "px")
      .style("top", y(0) + "px")
  }
  var moveTooltip = function(d) {
    tooltip
      //.style("left", (d3.event.pageX)-10 + "px")
      //.style("top", (d3.event.pageY)-85 + "px")
  }
  // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
  var hideTooltip = function(d) {
    tooltip
      //.transition()
      //.duration(100)
      .style("left", "0px")
      .style("top", "0px")
      .style("opacity", 0)
  }




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
    .attr("x", function(d) { return x(d.index)+r_pad; })
    .attr("y", function(d) { return y(Math.max(d.value,0)); })
    .attr("width", r_width)
    .attr("height", function(d) { return y(Math.min(0,d.value)) - y(Math.max(0,d.value)); })
    .attr("fill", "#69b3a2")
  ;
  var yLabel = svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "end")
    .attr("transform", "rotate(-90)")
    .style("font-size", "0.9rem")
    .attr("y", -40)
    ;
  if (svg.select(function(){return this.parentNode;}).classed("similarity-reduced") ) {
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

  var tickValues = Array(data.length).fill().map((_, idx) => idx+0.5 );
  svg.append("g")
      .style("font-size", "6pt")
      .attr("transform", "translate(0," + y(0) + ")")
      .call(d3.axisBottom(x)
        .tickValues(tickValues)
        .tickFormat(function(n){ return data.map( d => d.bin )[tickValues.indexOf(n)]; })
      )
    ;

  }
  draw_svg(svg_delta, delta);
  draw_svg(svg_full, distribution);
}

function draw_all_similarity( query, system ) {
  $.ajax({
    url: api_base_url + "/similar",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word":query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {
      console.log(result);
      // Clear old figures
      d3.select("#similarity-div").selectAll(".row").remove();
      for ( var i = 0; i < result.similarities.length; i++ ) {
	data = result.similarities[i];
        draw_one_similarity( data.word, data.delta, data.distribution );
      }
    }
  });
}

