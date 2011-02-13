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
    
    dojo.query("#editorhandle")
        .forEach(function(n){
            
            var target = dojo.byId("editor");
            var cury = 0;
            function mover(e){
                var nowy = e.pageY,
                    diff = nowy - cury,
                    curheight = dojo.style(target, "height")
                ;

                cury = e.pageY;    
                dojo.style(target, "height", (curheight + diff) + "px");
            

            }
            
            var connects = [], listener;
            function startdrag(){
                if(!listener){
                    listener = dojo.connect(window, "onmousemove", mover)
                }
            }
            
            function stopdrag(){
                listener && dojo.disconnect(listener)
                listener = null;
            }
            
            dojo.connect(n, "onmousedown", function(e){
                cury = e.pageY;
                startdrag()
            });
            
            dojo.connect(window, "onmouseup", stopdrag)
            
            
        })
        
    // always attempt to unlock the edited file when they leave
    dojo.addOnUnload(unlock);

//    CodeMirror.fromTextArea('editor', {
//        height: '520px',
//        parserfile: 'parsedummy.js',
//        stylesheet: '/_static/CodeMirror/css/rstcolors.css',
//        path: '/_static/CodeMirror/js/',
//        lineNumbers:true,
//        minHeight:400,
//        textWrapping:false,
//        iframeClass:'docmirrorframe',
//        indentUnit:4,
//        tabMode:"spaces",
//        enterMode:"keep"
//    }); 
    
});
