// Adapted from: //
// https://www.d3-graph-gallery.com/graph/histogram_binSize.html
// https://www.d3-graph-gallery.com/graph/histogram_tooltip.html

// Histogram size and margins:
var hist_margin = {top: 10, right: 30, bottom: 30, left: 40},
    hist_width = 460 - hist_margin.left - hist_margin.right,
    hist_height = 400 - hist_margin.top - hist_margin.bottom;

// Remember the max value in the data
// This needs to be widely scoped so all the
// d3 functions can access it.
var hist_max = 1;

function draw_histogram( query, system, corpus ) {

  return $.ajax({
    url: api_base_url + "/allValues",
    type: "POST",
    data: new URLSearchParams({"query":query,"system":system,"corpus":corpus}).toString(),
    dataType: "jsonp",
    success: function( result ) {

      hist_data = result;

      // Delete old svg if one exists
      d3.select("#histogram-main").select("svg").remove();
      // Create svg and format size and margins
      var svg = d3.select("#histogram-main")
        .append("svg")
          .attr("width", hist_width + hist_margin.left + hist_margin.right)
          .attr("height", hist_height + hist_margin.top + hist_margin.bottom)
          .append("g")
            .attr("transform",
              "translate(" + hist_margin.left + "," + hist_margin.top + ")");

      // Get max to scale histogram axes
      hist_max = d3.max(hist_data, d => +d.value);

      // X axis: scale and draw:
      var x = d3.scaleLinear()
        .domain([0,1.2*hist_max]) // Multiply max value by >1 to add a little padding
        .range([0, hist_width])
      ;
      svg.append("g")
        .attr("transform", "translate(0," + hist_height + ")")
        .call(d3.axisBottom(x))
      ;

      // Y axis: initialize, but don't draw until
      // we know the number of bins/axis scale
      var y = d3.scaleSymlog()
        .range([hist_height, 0])
      ;
      var yAxis = svg.append("g")
      ;

      // build the graph with a specific number of bins
      function update(nBin) {

        // set the parameters for the histogram
        var histogram = d3.histogram()
          .value(function(d) { return d.value; })
          .domain(x.domain())
          .thresholds(x.ticks(nBin))
	;
      
        // apply this function to data to get the bins
        var bins = histogram(hist_data);
      
        // Y axis: update now that we know the domain
        y.domain([0, d3.max(bins, function(d) { return d.length; })]);
        yAxis
          .transition()
          .duration(0)
          .call(d3.axisLeft(y))
        ;

        var tooltip = d3.select("#histogram-main")
          .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0)
            .style("background-color", "black")
            .style("color", "white")
            .style("border-radius", "5px")
            .style("padding", "10px")
	;
      
        var showTooltip = function(d) {
          tooltip
            .transition()
            .duration(100)
            .style("opacity", 1)
	  ;
          tooltip
            .html("Values: " + d.x0 + " - " + (d.x0+raw_bar_width) + "<br/>Occurrences: " + d.length)
            .style("left", x(d.x0) + "px")
            .style("top", y(d.length)+18 + "px")
	  ;
        }
        var moveTooltip = function(d) {
        }
        var hideTooltip = function(d) {
          tooltip
            .transition()
            .duration(100)
            .style("opacity", 0)
        }


        // Attach data to rect elements:
        var u = svg.selectAll("rect")
          .data(bins)
	;
      
        // Manage the existing bars and eventually the new ones:
        var bar_width = -1; // The last bar has the wrong width; record 
        // the width from the first bar and reuse it to fix appearance.
	// Also record the width in pixels rather than axis units
        var raw_bar_width = -1;
        u
          .enter()
          .append("rect") // Add a new rect for each new elements
            .merge(u) // get the already existing elements as well
              .attr("x", 1)
              .attr("transform", function(d) { 
		return "translate(" + x(d.x0) + "," + y(d.length) + ")"; 
	      })
              .attr("width", function(d) { 
		if (bar_width==-1) {
		  raw_bar_width = d.x1-d.x0; 
		  bar_width = x(d.x1) - x(d.x0) -1 ;
		}; 
		return bar_width; 
	      })
              .attr("height", function(d) { 
		return hist_height - y(d.length); 
	      })
              .style("fill", "#69b3a2")
              .on("mouseover",  showTooltip )
              .on("mousemove",  moveTooltip )
              .on("mouseleave", hideTooltip )
	;
      
      
        // Delete bars not in use anymore, if any exist:
        u
          .exit()
          .remove()
	;
      }

      // Initialize from current slider value:
      update($("#n-bins-histogram").val());

      // Update figure if user changes number of bins:
      d3.select("#n-bins-histogram").on("input", function() {
	params["n-bins-histogram"] = this.value;
	updateURLParameters();
        update(Math.round(this.value));
      });

    } // end success function
  }); // End $.ajax
}
