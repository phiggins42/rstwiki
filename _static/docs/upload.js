dojo.provide("docs.upload");
dojo.require("dojo.fx");
dojo.ready(function(){
    
    var template = "<div class='bloc'><label for='uploadfile{count}'>Select File:</label>" +
                "<input type='file' name='uploadfile{count}' id='uploadfile{count}'></div>"

    var count = 1;
    dojo.query("#morefiles").onclick(function(e){
        e.preventDefault()
        var n = dojo.place(dojo.replace(template, { count: count++ }), "files", "first");
        dojo.style(n, "height", "1px");
        dojo.fx.wipeIn({ node:n }).play()
    })

    dojo.query("form").onsubmit(function(e){
        dojo.query("input[type=file]", e.target)
            .forEach(function(n){
                if(!n.value){
                    dojo.destroy(n.parentNode);
                }
            });
    });
    
});