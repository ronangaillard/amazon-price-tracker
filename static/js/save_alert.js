$(function() {

  $('#new-save-alert-button').on('click',function(){
     saveAlert("new");
 });

});



function saveAlert(type) {
    var asin, locale, type, email, price;
    
    if(type == "new")
    {
        email = $('#email-new').val();
        price = $('#target-price-new').val();
    }
    else{
        email = $('#email-used').val();
        price = $('#target-price-used').val();
    }
    
    asin =  $('#asin').val();
    locale = $('#locale').val();
    
    $.ajax({
        url: '/save_alert',
        type: 'post',
        data: "asin="+ encodeURIComponent(asin) +"&locale="+ encodeURIComponent(locale)+"&type="+ encodeURIComponent(type)+"&email="+encodeURIComponent(email)+"&price="+encodeURIComponent(price),
        success: function (data) {
            console.log("Success with post ! : " + data);
            if (data != 'ok') {
                console.log("Error !");
                //alert("Unknown error...");
            }
            else {
                console.log("saved!");
            }
        }
    });
    
    return false;

}