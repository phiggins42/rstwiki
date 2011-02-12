dojo.provide("docs.editor");

dojo.ready(function(){ 

    var path = window.location.pathname.replace("/edit", ""),
        unlock = dojo.partial(dojo.xhrGet, { url:"/unlock" + path })
    ;

    // if they click cancel, go back to non edit page and unlock
    dojo.query("#canceler").onclick(function(){
        unlock();
        window.location.href = path
    });
    
    // always attempt to unlock the edited file when they leave
    dojo.addOnUnload(unlock);

    CodeMirror.fromTextArea('editor', {
        height: '520px',
        parserfile: 'parsedummy.js',
        stylesheet: '/_static/CodeMirror/css/rstcolors.css',
        path: '/_static/CodeMirror/js/',
        lineNumbers:true,
        minHeight:400,
        textWrapping:false,
        iframeClass:'docmirrorframe',
        indentUnit:4,
        tabMode:"spaces",
        enterMode:"keep"
    }); 
    
});
