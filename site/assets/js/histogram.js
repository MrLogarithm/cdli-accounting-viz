// Adapted from: //
// https://www.d3-graph-gallery.com/graph/histogram_binSize.html
// https://www.d3-graph-gallery.com/graph/histogram_tooltip.html

var hist_margin = {top: 10, right: 30, bottom: 30, left: 40},
    hist_width = 460 - hist_margin.left - hist_margin.right,
    hist_height = 400 - hist_margin.top - hist_margin.bottom;

var hist_max = 1;

function draw_histogram( query, system ) {

  $.ajax({
    url: api_base_url + "/allValues",
    type: "POST",
    crossDomain: true,
    data: new URLSearchParams({"word":query,"system":system}).toString(),
    dataType: "jsonp",
    success: function( result ) {

      hist_data = result;

  d3.select("#histogram-main").select("svg").remove();
  var svg = d3.select("#histogram-main")
    .append("svg")
      .attr("width", hist_width + hist_margin.left + hist_margin.right)
      .attr("height", hist_height + hist_margin.top + hist_margin.bottom)
    .append("g")
      .attr("transform",
            "translate(" + hist_margin.left + "," + hist_margin.top + ")");

  hist_max = d3.max(hist_data, d => +d.value);

  // X axis: scale and draw:
  var x = d3.scaleLinear()
      .domain([0,1.2*hist_max]) // Multiply max value by >1 to add a little padding
      .range([0, hist_width]);
  svg.append("g")
      .attr("transform", "translate(0," + hist_height + ")")
      .call(d3.axisBottom(x));

  // Y axis: initialization
  var y = d3.scaleSymlog()
      .range([hist_height, 0]);
  var yAxis = svg.append("g")

  // A function that builds the graph for a specific value of bin
  function update(nBin) {

    // set the parameters for the histogram
    var histogram = d3.histogram()
        .value(function(d) { return d.value; })   // I need to give the vector of value
        .domain(x.domain())  // then the domain of the graphic
        .thresholds(x.ticks(nBin)); // then the numbers of bins

    // And apply this function to data to get the bins
    var bins = histogram(hist_data);

    // Y axis: update now that we know the domain
    y.domain([0, d3.max(bins, function(d) { return d.length; })]);   // d3.hist has to be called before the Y axis obviously
    yAxis
        .transition()
        .duration(0)
        .call(d3.axisLeft(y));


  var tooltip = d3.select("#histogram-main")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "black")
    .style("color", "white")
    .style("border-radius", "5px")
    .style("padding", "10px")

  var showTooltip = function(d) {
    tooltip
      .transition()
      .duration(100)
      .style("opacity", 1)
    tooltip
      .html("Values: " + d.x0 + " - " + (d.x0+raw_bar_width) + "<br/>Occurrences: " + d.length)
      //.style("left", (d3.event.pageX)-10 + "px")
      //.style("top", (d3.event.pageY)-85 + "px")
      .style("left", x(d.x0) + "px")
      .style("top", y(d.length)+18 + "px")
  }
  var moveTooltip = function(d) {
    tooltip
      //.style("left", (d3.event.pageX)-10 + "px")
      //.style("top", (d3.event.pageY)-85 + "px")
  }
  // A function that change this tooltip when the leaves a point: just need to set opacity to 0 again
  var hideTooltip = function(d) {
    tooltip
      .transition()
      .duration(100)
      .style("opacity", 0)
  }


    // Join the rect with the bins data
    var u = svg.selectAll("rect")
        .data(bins)

    // Manage the existing bars and eventually the new ones:
    var bar_width = -1; // The last bar has the wrong width; record 
    var raw_bar_width = -1;
    // the width from the first bar and reuse it to fix appearance.
    u
        .enter()
        .append("rect") // Add a new rect for each new elements
        .merge(u) // get the already existing elements as well
        //.transition() // and apply changes to all of them
        //.duration(0)
          .attr("x", 1)
          .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; })
          .attr("width", function(d) { if (bar_width==-1){raw_bar_width = d.x1-d.x0; bar_width = x(d.x1) - x(d.x0) -1 ;}; return bar_width; })
          .attr("height", function(d) { return hist_height - y(d.length); })
          .style("fill", "#69b3a2")
          .on("mouseover",  showTooltip )
          .on("mousemove",  moveTooltip )
          .on("mouseleave", hideTooltip )


    // If less bar in the new histogram, I delete the ones not in use anymore
    u
        .exit()
        .remove()

    }


  // Initialize with 20 bins
  update($("#n-bins-histogram").val());


  // Listen to the button -> update if user change it
  d3.select("#n-bins-histogram").on("input", function() {
    update(Math.round(this.value));
  });

  } // end success function(){}
  }); // End $.ajax

}
