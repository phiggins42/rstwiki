dojo.provide("docs.editor");

dojo.ready(function(){ 

    var ping = dojo.partial(dojo.xhrGet, { url:"/unlock" + path });

    var path = window.location.pathname.replace("/edit", "")

    // if they click cancel, go back to non edit page and unlock
    dojo.query("#canceler").onclick(function(){
        ping();
        window.location.href = path
    });
    
    // always attempt to unlock the edited file when they leave
    dojo.addOnUnload(ping);

    CodeMirror.fromTextArea('editor', {
        height: '520px',
        parserfile: 'parsedummy.js',
        stylesheet: '/_static/CodeMirror/css/rstcolors.css',
        path: '/_static/CodeMirror/js/',
        lineNumbers:true,
        minHeight:400,
        textWrapping:false,
        iframeClass:'docmirrorframe'
    }); 
    
});
