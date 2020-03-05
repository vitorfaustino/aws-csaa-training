$(function(){
 
    $('#serverless-form').submit(function(e){
        e.preventDefault();
        var formdata = toJSONString(this);
        console.log(formdata);
        $.ajax({
            type: "POST",
            url: URL,
            dataType: "json",
            contentType: "application/json",
            data: formdata,
            beforeSend: function(data) {
                $('#submit').attr('disabled', true);
                $('#status').html('<i class="fa fa-refresh fa-spin"></i> Sending POST...').show();
            },
            success: function(data) {
                console.log(data);
                $('#status').text('POST Sent to AWS API Gateway with success!').show();
                    var audio = $("#player");      
                    $("#mp3_src").attr("src", data['body']);
                    /****************/
                    audio[0].pause();
                    audio[0].load();//suspends and restores all audio element

                    //audio[0].play(); changed based on Sprachprofi's comment below
                    audio[0].oncanplaythrough = audio[0].play();

                $('#submit').removeProp('disabled');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#status').text('POST Failed').show();
                $('#submit').removeProp('disabled');
            }
        });
    });

    function toJSONString (form) {
		var obj = {};
		var elements = form.querySelectorAll("input, select, textarea");
		for(var i = 0; i < elements.length; ++i) {
			var element = elements[i];
			var name = element.name;
			var value = element.value;
			if(name) {
				obj[name] = value;
			}
        }
        return JSON.stringify(obj);
    }
});
