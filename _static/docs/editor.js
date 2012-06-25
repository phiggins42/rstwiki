require([
	"dojo/_base/lang", // lang.partial
	"dojo/_base/unload", // baseUnload.addOnUnload
	"dojo/_base/xhr", // xhr.get
	"dojo/dom", // dom.byId
	"dojo/dom-style", // style.get
	"dojo/on", // on
	"dojo/query", // query
	"dojo/ready" // ready
], function(lang, baseUnload, xhr, dom, style, query, ready){
	
	var path = window.location.pathname.replace("/edit", ""),
		unlock = lang.partial(xhr.get, { url:"/unlock" + path });

	ready(function(){
		// if they click cancel, go back to non edit page and unlock
		dom.byId("rstwiki-canceler", "click", function(){
			unlock();
			window.location.href = path;
		});
	
		query("#rstwiki-editorhandle")
			.forEach(function(n){
			
				var target = dom.byId("rstwiki-editor");
				var cury = 0;
				function mover(e){
					var nowy = e.pageY,
						diff = nowy - cury,
						curheight = style.get(target, "height");

					cury = e.pageY;	
					style.set(target, "height", (curheight + diff) + "px");
				}
			
				var connects = [], listener;
				function startdrag(){
					if(!listener){
						listener = on(window, "mousemove", mover)
					}
				}
			
				function stopdrag(){
					listener && listener.remove();
					listener = null;
				}
			
				on(n, "mousedown", function(e){
					cury = e.pageY;
					startdrag();
				});
			
				on(window, "mouseup", stopdrag)
			
			});
		
		// always attempt to unlock the edited file when they leave
		baseUnload.addOnUnload(unlock);
	});

//	CodeMirror.fromTextArea('editor', {
//		height: '520px',
//		parserfile: 'parsedummy.js',
//		stylesheet: '/_static/CodeMirror/css/rstcolors.css',
//		path: '/_static/CodeMirror/js/',
//		lineNumbers:true,
//		minHeight:400,
//		textWrapping:false,
//		iframeClass:'docmirrorframe',
//		indentUnit:4,
//		tabMode:"spaces",
//		enterMode:"keep"
//	}); 
	
});
