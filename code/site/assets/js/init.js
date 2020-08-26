api_base_url = "http://127.0.0.1:8087";

// Set initial input element values on DOM elements:
$("#n-bins-histogram").val( params["n-bins-histogram"] );
$("#n-links-colloc").val( params["n-links-colloc"] );
$("#n-terms-colloc").val( params["n-terms-colloc"] );
if ( params["showCliques-colloc"] == "true" ) {
  $("#showCliques-colloc").click();
}
$("#n-links-desc").val( params["n-links-desc"] );
$("#n-terms-desc").val( params["n-terms-desc"] );
if ( params["showCliques-desc"] == "true" ) {
  $("#showCliques-desc").click();
}

/* Make tables sortable: */
var table_format_base = {
  sDom:"frtlp",
  // r: pRocessing (show spinner when working)
  // t: show Table
  order: [[1,"desc"]],
  language: {
    search:"",
    searchPlaceholder:'Filter',
    lengthMenu:"_MENU_ rows per page",
  },
  deferRender: true,
  paging: true,
  orderClasses: false,
}; 

function change_focus( word ) {
  $("#search-input").val(word);
  $("#search-button").click();
}

var table_format_nearby = Object.assign({}, table_format_base)
table_format_nearby.columnDefs = [
  {
    targets: 0,
    render: function( data, type, row ) {
      if (type == "display") {
	if (json_data["all_objects"].includes(data)) {
	  return "<a href='' title='Click to focus this word.' onclick=\"change_focus(\'"+data+"\'); return false;\">"+data+"</a>";
	}
      }
      return data;
    }
  },
  {
    targets: 1,
    render: function( data, type, row ) {
      if (type == "display") {
	var ids = getCollocationCDLINumbers(row[0].replace(/<\/?b>/g,""));
        return "<a href='https://cdli.ucla.edu/search/search_results.php?SearchMode=Text&ObjectID="+ids.join(",")+"'>"+data+" text"+(data>1?'s':'')+"</a><div class='cdliNos'>"+ids.join("<br/>")+"</div>";
      } else {
	return data;
      }
    },
    createdCell: function (td, cellData, rowData, row, col) {
      $(td).css('position', 'relative')
    }
  }
];
// Init tables with format:
var dt_nearby = $("#table-nearby").DataTable(table_format_nearby);
dt_nearby.on(
  'search.dt',
  function() {
    params["filter-nearby"] = dt_nearby.search();
    updateURLParameters();
  }
);
dt_nearby.on(
  'page.dt',
  function(){
    document.getElementById("table-div-colloc").scrollTo({top:0});
  }
);

var table_format_desc = Object.assign({}, table_format_base);
table_format_desc.columnDefs = [
  {
    targets: 0,
    render: function( data, type, row ) {
      if (type == "display") {
	var string = '';
	for (word of data.split(" ")) {
	  if (json_data["all_objects"].includes(word)) {
	    string += " <a href='' title='Click to focus this word.' onclick=\"change_focus(\'"+word+"\'); return false;\">"+word+"</a>";
	  } else {
	    string += " " + word
	  }
	}
	return string;
      }
      return data;
    }
  }, {
    targets: 1,
    render: function( data, type, row ) {
      if (type == "display") {
	var ids = getDescriptionCDLINumbers(row[0].replace(/<\/?b>/g,""));
        return "<a href='https://cdli.ucla.edu/search/search_results.php?SearchMode=Text&ObjectID="+ids.join(",")+"'>"+data+" line"+(data>1?'s':'')+"</a><div class='cdliNos'>"+ids.join("<br/>")+"</div>";
      } else {
	return data;
      }
    },
    createdCell: function (td, cellData, rowData, row, col) {
      $(td).css('position', 'relative')
    }
  }
];
var dt_desc = $("#table-desc").DataTable(table_format_desc);
dt_desc.on(
  'search.dt',
  function() {
    params["filter-descriptors"] = dt_desc.search();
    updateURLParameters();
  }
);
dt_desc.on(
  'page.dt',
  function(){
    document.getElementById("table-div-desc").scrollTo({top:0});
  }
);

var table_format_concord = Object.assign({}, table_format_base);
// This table should be ordered by column 2:
table_format_concord.order[0][0] = 2;
table_format_concord.columns = [
  {type:"string"},
  {type:"num"},
  {type:"num"},
];
table_format_concord.columnDefs = [
  {
    targets: 0,
    render: function( data, type, row ) {
      if (type == "display") {
	var string = '';
	for (word of data.split(" ")) {
	  word = word.replace(/<\/?b>/g, '');
	  if (json_data["all_objects"].includes(word)) {
	    string += " <a href='' title='Click to focus this word.' onclick=\"change_focus(\'"+word+"\'); return false;\">"+word+"</a>";
	  } else {
	    string += " " + word
	  }
	}
	return string;
      }
      return data;
    }
  }, {
    targets: 1,
    render: function( data, type, row ) {
      // Convert to int for sorting
      if (type != "display") {
	return parseFloat( data.split(" ")[0] );
      }
      return data;
    }
  }, {
    targets: 2,
    render: function( data, type, row ) {
      if (type == "display") {
	var ids = getConcordanceCDLINumbers(row[0].replace(/<\/?b>/g,""));
        return "<a href='https://cdli.ucla.edu/search/search_results.php?SearchMode=Text&ObjectID="+ids.join(",")+"'>"+data+" line"+(data>1?'s':'')+"</a><div class='cdliNos'>"+ids.join("<br/>")+"</div>";
      } else {
	return data;
      }
    },
    createdCell: function (td, cellData, rowData, row, col) {
      $(td).css('position', 'relative')
    }
  }
];
var dt_concordance = $("#table-concordance").DataTable(table_format_concord);
dt_concordance.on(
  'search.dt',
  function() {
    params["filter-concordance"] = dt_concordance.search();
    updateURLParameters();
  }
);
dt_concordance.on(
  'page.dt',
  function(){
    document.getElementById("table-div-concord").scrollTo({top:0});
  }
);

// Show help tooltips on hover:
$('.help').each(function(idx,elem){
  var tooltip_selector = "#" + elem.id + "-explanation";
  $("#"+elem.id).hover(function(){
    $(tooltip_selector).css("opacity",1);
    $(tooltip_selector).css("z-index",2);
  }, function(){
    $(tooltip_selector).css("opacity",0);
    $(tooltip_selector).css("z-index",-2);
  })
});

/* Setup toggles to show force directed graphs: */
$('#toggle-nearby').click(function() {
  $('#graph-div-colloc').toggleClass('d-none');
  $('#table-div-colloc').toggleClass('d-none');
  params["toggle-nearby"] = not(params["toggle-nearby"]);
  updateURLParameters();
});
if ( params["toggle-nearby"] == "true" ) {
  params["toggle-nearby"] = not(params["toggle-nearby"]);
  $("#toggle-nearby").click();
}

$('#toggle-desc').click(function() {
  $('#graph-div-desc').toggleClass('d-none');
  $('#table-div-desc').toggleClass('d-none');
  params["toggle-descriptors"] = not(params["toggle-descriptors"]);
  updateURLParameters();
});
if ( params["toggle-descriptors"] == "true" ) {
  params["toggle-descriptors"] = not(params["toggle-descriptors"]);
  $("#toggle-desc").click();
}

$('#toggle-delta').click(function() {
  $('.similarity-reduced').toggleClass('d-none');
  $('.similarity-full').toggleClass('d-none');
  params["toggle-similar"] = not(params["toggle-similar"]);
  updateURLParameters();
});
if ( params["toggle-similar"] == "true" ) {
  params["toggle-similar"] = not(params["toggle-similar"]);
  $("#toggle-delta").click();
}

/* Disable mousewheel when over figures: */
// https://stackoverflow.com/questions/7571370/jquery-disable-scroll-when-mouse-over-an-absolute-div
$('#graph-nearby-div').hover(function() {
  $(document).bind('mousewheel DOMMouseScroll',function(){ 
    stopWheel(); 
  });
}, function() {
  $(document).unbind('mousewheel DOMMouseScroll');
});
function stopWheel(e){
  if(!e){ /* IE7, IE8, Chrome, Safari */
    e = window.event;
  }
  if(e.preventDefault) { /* Chrome, Safari, Firefox */
    e.preventDefault();
  }
  e.returnValue = false; /* IE7, IE8 */
}

// Autocomplete, since some ePSD spellings are not
// what the user will expect:
// https://www.w3schools.com/howto/howto_js_autocomplete.asp
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      // Show list of all words if search bar is empty:
      // if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.insertBefore(a, document.getElementById("search-button-div"));
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
	      do_search();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
        closeAllLists();
	do_search();
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}


$('#help-button').click(function(){
  $('#modal-title').html("CDLI Commodity Explorer");
  $('#modal-body').html(`<p>The tools on this page are designed to help users explore how commodities were recorded in ancient accounting corpora.</p>

	<p>Hover over the help buttons 
	<span class="text-center help" style='line-height:20px;' id='none'>
	  ?
	</span>
	to see an explanation for each module, or access the full user guide <a href='https://github.com/MrLogarithm/cdli-accounting-viz/blob/master/docs/UserGuide.md'>here</a>.
	</p>

	<p class='text-center'>
	  <img class='mr-2' style='height:50px;' src='/cdli-accounting-viz/assets/fa-firefox.svg'/> 
	<p>
	<p>
	This page renders best in Firefox. We are aware of rendering issues in other browsers and are working to fix them.
	</p>

	<p>
	Please note the following:
	<ul>
	  <li>All English translations are taken from the <a href='http://psd.museum.upenn.edu/nepsd-frame.html'>ePSD</a>
	  </li>
	  <li>All data has been extracted using automated tools built around the ePSD definitions. Where these definitions are ambiguous or a word does not occur in the ePSD, the extracted data may be inaccurate. 
	  </li>
	  <li>
	    The citation button will generate a link which preserves your current search term and parameter settings, allowing you to cite the figures exactly as you have them set up. However, the data in the figures may change over time if the underlying transliterations are ever updated or revised. 
	  </li>
	  <li>
	    If you are exploring a large corpus, the figures may be slow to load. We are working on increasing the speed, but for large corpora there is a limit to how quickly we can process the data.
	  </li>
	</ul>
	</p>

	<p>
	If you encounter any errors or inaccuracies in the data, open an issue or contact us on <a href='https://gitlab.com/cdli/framework/-/issues'>gitlab</a>.
	</p>`);
  $("#modal-welcome").modal("show");
});



/* Fetch json data: */
json_data = {};
$(document).ready(function(){
  $.ajax({
    async: false,
    url: api_base_url + "/dictionary",
    type: "POST",
    dataType: "jsonp",
    data:"corpus="+url_compress_corpus(params.corpus),
    start_time: new Date().getTime(),
    success: function( result ) {
	json_data = result;

        // Setup autocomplete
	var all_commodities = json_data["all_objects"].filter( x => x.split(" ").length == 1 );
	if ( !all_commodities.includes(params.query) ) {
	  params.query = all_commodities[0];
	  updateURLParameters();
	}
	autocomplete(document.getElementById("search-input"), all_commodities); 
  
  	$('#search-input').val(
	  params.query
	);

        do_search();
    },
  });
  $('#help-button').click();
});
