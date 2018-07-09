fetchvds = function(evt){
    var s=document.getElementById('system');
    var systemid=s.value;
    var qurl="http://localhost:5000/ajax/detectors";
    $.ajax({
            type: "GET",
            cache: false,
            data:{systemid:systemid},
            url: qurl,
            dataType: "json",
            success: function(data) { 
                var vds=document.getElementsByClassName('vds');
                for(var j = 0; j < vds.length; j++){
                    vd=vds[j]
                    var length = vd.options.length;
                    for (var i = length-1; i >= 0; i--) {
                        vd.options[i] = null;
                    }
                    var option=document.createElement("option");
                    vd.add(option)
                    for(var i = 0; i < data.length; i++){
                        option = document.createElement("option");
                        option.text = data[i].name;
                        option.value=data[i].id;
                        vd.add(option)
                    }   
                }
            },
            error: function(jqXHR) {
                alert("error: " + jqXHR.status);
                console.log(jqXHR);
            }
        })
}


window.onload = function(evt){
    sys=document.getElementById("system");
    sys.oninput=fetchvds
    sys.onchange=fetchvds
}