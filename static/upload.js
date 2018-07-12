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
        checkvalid();
}

fetchsurveys=function(evt){
    var s=document.getElementById('project');
    var projectid=s.value;
    var qurl="http://localhost:5000/ajax/surveys";
    $.ajax({
            type: "GET",
            cache: false,
            data:{projectid:projectid},
            url: qurl,
            dataType: "json",
            success: function(data) { 
                var survey=document.getElementById("survey")
                var length = survey.options.length;
                for (var i = length-1; i >= 0; i--) {
                    survey.options[i] = null;
                }
                var option=document.createElement("option");
                survey.add(option)
                for(var i = 0; i < data.length; i++){
                    option = document.createElement("option");
                    option.text = data[i].name;
                    option.value=data[i].id;
                    survey.add(option)
                }   
            },
            error: function(jqXHR) {
                alert("error: " + jqXHR.status);
                console.log(jqXHR);
            }
        })
    
    checkvalid();
}

checkvalid=function(){
    var token=document.getElementById("system");
    var valid=token.value>0;
    if (valid){
        var vds=document.getElementsByClassName('vds');
        var validvd=false;
        for(var j = 0; j < vds.length; j++){
            validvd = validvd || vds[j].value >0;
        }
        valid=valid && validvd;
    }
    if (valid){
        var validproj=document.getElementById('project').value>0;
        validproj=validproj || document.getElementById('project_new').value>"";
        valid = valid && validproj;
    }
    if (valid){
        var validsurv=document.getElementById('survey').value>0;
        validsurv=validsurv || document.getElementById('survey_new').value>"";
        valid = valid && validsurv;
    }
    document.getElementById("upload").disabled = !valid;
}


window.onload = function(evt){
    var sys=document.getElementById("system");
    sys.oninput=fetchvds;
    sys.onchange=fetchvds;
    var proj=document.getElementById("project");
    proj.oninput=fetchsurveys;
    proj.onchange=fetchsurveys;
    
}