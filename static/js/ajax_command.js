$(document).ready(function(){
    var path = window.location.pathname.split('/')
    var user = path[path.length - 2]
    $('#submit').click(function(){
        var text = $('#text').val() || ''
        var time = $('#time').val() || 0
        var command_xmlhttp = $.ajax({
            url: '/task/',
            type: 'POST',
            async: false,
            timeout: 8000,
            data: {
                'text': text,
                'time': time || 0,
                'user': user,
            }  
        })    

        var task_xmlhttp = $.ajax({
            url: '/task/',
            type: 'GET',
            async: false,  
        })
        var task_data = eval(task_xmlhttp.responseText)
        var data = task_data[task_data.length-1]
        $('tbody').append('<tr><td class="taskcmd">'+data.data.cmd+'</td><td class="taskuser">'+data.data.time+'</td><td class="tasktime">'+data.data.user+'</td><td><button type="button" class="btn btn-primary">delete</button></td></tr>')
        $('td button:last').click(function(){
            this.parentNode.parentNode.remove()
        })
      
    })

    var user_xmlhttp = $.ajax({
        url: '/user/' ,
        type: 'GET',
        async: false 
    })
    var user_data = eval(user_xmlhttp.responseText)
    for(var i=0; i<user_data.length; i++){
        $('#userelem').append('<li><a href="##">'+user_data[i]+'</a></li>') 
        $('#userelem a:last').click(function(){
            var username = this.text
            $('#users').html(username+'<span class="caret"></span>')
            var password = prompt('password:')
            var result = $.ajax({
                url: '/user/' + username + '/',
                type: 'POST',
                async: false,
                data:{'password': password}
            })
            if(result == 'false'){
                $('#users').html(user+'<span class="caret"></span>')
                alert('error password')
            }
        })
    }


    var group_xmlhttp = $.ajax({
        url:'/group/' + user + '/',
        type: 'GET',
        async: false   
    })
    var group_data = group_xmlhttp.responseText.split(' ')
    for(var i=0; i<group_data.length; i++){
        $('#groupelem').append('<li><a href="##">'+group_data[i]+'</a></li>')  
        $('#groupelem a:last').click(function(){
            var groupname = this.text
            var password = prompt('group password')
            $.ajax({
                url: '/group/'+groupname+'/',
                type: 'POST',
                async: false,
                data: {'password': password}  
            })    
            if(result == 'true'){
                $('#groups').html(groupname + '<span class="caret"></span>')
            }else{
                alert('error password')
            }
        })
    }


   //TODO  run the task
    setInterval(function(){ 
        var tasks = []
        var task = {
            'cmd':'',
            'time':'',
            'user':'',
        }
        var task_cmds = $('.taskcmd')
        var task_user = $('.taskuser')
        var task_time = $('.tasktime')
        for(var i=0; i<task_cmds.length; i++){
            task.cmd = task_cmds[i].innerHTML
            task.time = parseInt(task_time[i].innerHTML)
            task.user = task_user[i].innerHTML
            tasks.push(task)
            task_time[i].innerHTML = task.time - 1
            if(task.time == 0){
                var result = $.ajax({
                    url: '/command/',
                    type: 'GET',
                    async: false,
                    data:{'text':task.cmd, 'user':task.user}
                })
                $('#result').text(result.responseText)
                task_cmds[i].parentNode.remove()
            }
        }
        
    }, 1000)
    

})

function run(cmd, user, time){
    setTimeout(function(){
        var result = $.ajax({
        url: '/command/',
        type:'POST',
        data:{
            'text': cmd,
            'user': user
        }})
        $('#result').text(result)
        //TODO remove the task 
        //this.parentNode.parentNode.remove()
    }, parseInt(time)*1000)
}
