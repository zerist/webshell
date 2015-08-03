$(document).ready(function(){
    $('#submit').click(function(){
        var text = $('#text').val() || ''
        var time = $('#time').val() || 0
        var command_xmlhttp = $.ajax({
            url: '/task/',
            type: 'POST',
            async: false,
            data: {
                'text': text,
                'time': time,
                'user': $('li[checked=checked]').text() || 'root'
            }  
        })    
        alert('new task')
    })

    var user_xmlhttp = $.ajax({
        url: '/user/' ,
        type: 'GET',
        async: false 
    })
    var user_data = eval(user_xmlhttp.responseText)
    for(var i=0; i<user_data.length; i++){
        $('#userelem').append('<li><a href="##">'+user_data[i]+'</a></li>')  //TODO for a link
    }

    var user_btns = $('#userelem a')

})
