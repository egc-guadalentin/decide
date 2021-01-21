$.getJSON('static/js/lang.json', function(json){
  $('.translate').click(function(){
    let lang = $(this).attr('id');
    document.cookie = 'lang='+lang+';path=/;max-age=86400;';
    
    $('.lang').each(function(index, element){
      element.innerText=json[lang][element.id];
     // $(this).text(json[lang][$(this).attr('id')]);
    });
  });
  
  var cookies = document.cookie.split("; ");
  cookies.forEach((c) => {
    var cs = c.split("=");
    if (cs[0] == 'lang' && cs[1]) {
      $('#'+cs[1]).click();
    }
  });
});//Get json AJAX