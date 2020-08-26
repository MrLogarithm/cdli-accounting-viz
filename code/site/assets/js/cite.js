function cite_bibtex() {
  return `<pre style='text-indent:0px;padding:0px;white-space:pre-wrap; word-wrap:break-word;'>
@misc{,
  author={Cuneiform Digital Library Initiative},
  title={CDLI Commodity Explorer},
  howpublished={\\url{`+window.location+`}},
  note={Accessed: `+(new Date().toISOString().split('T')[0])+`}
}
</pre>`;
}

function cite_mla() {
  var d = new Date();
  return "Cuneiform Digital Library Initiative. \"CDLI Commodity Explorer.\" <i>CDLI</i>, <a href=\'"+window.location+"\'>"+window.location+"</a>. Accessed "+d.getDate()+" "+d.toLocaleString('default', { month: 'long' })+" "+d.getFullYear()+".";
}

function cite_apa() {
  var d = new Date();
  return "Cuneiform Digital Library Initiative. <i>CDLI Commodity Explorer</i> [Infographic]. Retrieved "+d.toLocaleString('default',{month:'long'})+" "+d.getDate()+", "+d.getFullYear()+", from <a href=\""+window.location+"\">"+window.location+"</a>";
}

function cite_chicago() {
  var d = new Date();
  return "Cuneiform Digital Library Initiative. \"CDLI Commodity Explorer.\" CDLI. Accessed "+d.toLocaleString('default',{month:'long'})+" "+d.getDate()+", "+d.getFullYear()+". <a href=\""+window.location+"\">"+window.location+"</a>.";
}

$("#cite-button").click(function(e){
  $('#modal-title').html("Cite this page");
  var html = `
  <div>
    <div id='cite-bibtex-div' class='citation'>
    `+cite_bibtex()+`
    </div>
    <div id='cite-mla-div' class='citation'>
    `+cite_mla()+`
    </div>
    <div id='cite-apa-div' class='citation'>
    `+cite_apa()+`
    </div>
    <div id='cite-chicago-div' class='citation'>
    `+cite_chicago()+`
    </div>
  </div><br/>

  <p>The URL in these citations will reproduce this page with your current search term and parameter settings.</p>

  <div class='text-center'>
    <button id='cite-bibtex-btn' class="btn-cite btn btn-outline-secondary border" type="button" title="BibTeX">
      BibTeX
    </button>
    <button id='cite-mla-btn' class="btn-cite btn btn-outline-secondary border" type="button" title="BibTeX">
      MLA
    </button>
    <button id='cite-apa-btn' class="btn-cite btn btn-outline-secondary border" type="button" title="BibTeX">
      APA
    </button>
    <button id='cite-chicago-btn' class="btn-cite btn btn-outline-secondary border" type="button" title="BibTeX">
      Chicago
    </button>
  </div>`;
  $('#modal-body').html(html);
  $('.citation').hide();
  $("#cite-bibtex-btn").click(function(){
    $('.citation').hide();
    $('#cite-bibtex-div').show();
  });
  $("#cite-mla-btn").click(function(){
    $('.citation').hide();
    $('#cite-mla-div').show();
  });
  $("#cite-apa-btn").click(function(){
    $('.citation').hide();
    $('#cite-apa-div').show();
  });
  $("#cite-chicago-btn").click(function(){
    $('.citation').hide();
    $('#cite-chicago-div').show();
  });
  $("#modal-welcome").modal("show");
});
