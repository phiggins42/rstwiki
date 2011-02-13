dojo.provide("docs.wiki");
dojo.require("CodeGlass.base");
dojo.require("dojo.parser");
dojo.require("dijit.Dialog");
dojo.ready(function(){

	var d = dojo;

    dojo.query("#loginanchor").onclick(function(e){
        
    })

	var dlg = new dijit.Dialog({ title:"Action:" });
	d.query("#nav a[rel]").forEach(function(n){
		var rel = d.attr(n, "href");
		if(rel){
			d.connect(n, "onclick", function(e){
				e.preventDefault();
				dlg.set("title", "Running: " + rel);
				dlg.set("content", "..............................");
				dlg.show();
				dojo.xhrGet({
					url: rel,
					load: function(data){
						dlg.set("title", "Output: " + rel);
						dlg.set("loading", false);
						dlg.set("content", "<pre style='width:720px; height:400px; overflow:auto'>" + data.replace(/</g, "&lt;") + "</pre>");
					}
				});
			});
		}
	});
	
	dojo.parser.parse();

});