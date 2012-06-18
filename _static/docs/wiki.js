require([
	"dojo/_base/lang", // lang.trim, lang.replace
	"dojo/dom", // dom.byId
	"dojo/dom-construct", // domConst.create, domConst.place
	"dojo/dom-class", // domClass.toggle
	"dojo/on", // on
	"dojo/parser", // parser.parse
	"dojo/query", // query
	"dojo/ready", // ready
	"docs/CodeGlassViewerMini",
	"dijit/Dialog",
	"docs/MiniGlass"
], function(lang, dom, domConst, domClass, on, parser, query, ready, CodeGlassViewerMini, Dialog){

	ready(function(){
		parser.parse();
		
		var dialog = new Dialog({ title:"CodeGlass" });
		lang.setObject("docs.masterviewer", new CodeGlassViewerMini(dialog));
		query(".live-example").forEach(function(n){
			var link = domConst.place("<a href='#' title='Example Code'><span class='a11y'>?</span></a>", n, "first");
			var data = query(".closed", n)[0];
			on(link, "click", function(e){
				e && e.preventDefault();
				domClass.toggle(data, "closed");
			});
		});
		
		var linknode = dom.byId("redirectlink");
		if(linknode){

			// redirect a/b/c to dtk.org/ref-guide/a/b/c.html

			var base = 'http://dojotoolkit.org/reference-guide/';

			var str = "<a href='{href}'>Read the release version of this documentation instead</a> (if it exists).";
			var data = {
				href: (function(){

					var parts = window.location.pathname.split("/");

					var hrefparts = dojo.filter(parts, function(p){
						return lang.trim(p).length;
					});
					console.log(hrefparts.length, "!!!");
					if(!hrefparts.length){
						console.warn(hrefparts);
						hrefparts.push("index");	
					}

					return base + hrefparts.join("/") + ".html";

				})()
			};

			domConst.place(domConst.toDom(lang.replace(str, data)), linknode);

		}
	});
	
});
