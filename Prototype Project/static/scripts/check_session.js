//function for checking if somebody is logged in
    function check_user()
    //function designed to grab the current user in the session
    {
        var info
        //ajax call to get information from the server
        $.ajax({
            type:'GET',
            //url with current session key
            url:'{{url_for("session_check")}}'+'?state='+"{{state}}",
            //if server response successfully
            success:function(result){
                console.log(result);
                console.log(result["bool"])
                var check_user = result
                console.log(check_user)
                state = "{{state}}"

                if(check_user["bool"] === true)
                {
                var text_to_insert = '<a href="#" class="dropdown-toggle"  data-toggle="dropdown" style="color:#33c480" ><strong>Signed in as: '+check_user['username']+'</strong><b class="caret"></b></a> \
                    <ul class="dropdown-menu"> \
                     <li class="dropdown-header">Account Management</li>\
                      <li>\
                      <li><a id= "profile" href="{{url_for('profile')}}?user='+check_user["username"]+'&state='+'{{state}}'+'">Profile</a>\
                      </li>\
                      <li><a  >Add Advertisement</a>\
                      </li>\
                      <li class="divider"></li>\
                        <li><a id = "logout"  >Logout</a></li>\
                    </ul>'

                    $('#login-account').html(text_to_insert);
                }
            },
            //if there is no user logged in the server responds with internal server error
            error: function(message){
                console.log('error');
            }
        });
    }