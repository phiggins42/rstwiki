require([
	"dojo/_base/lang", // lang.trim, lang.replace
	"dojo/_base/fx", // baseFx.fadeOut
	"dojo/cookie", // cookie
	"dojo/dom", // dom.byId
	"dojo/dom-construct", // domConst.create, domConst.place
	"dojo/dom-class", // domClass.toggle
	"dojo/dom-style", // style.set
	"dojo/on", // on
	"dojo/parser", // parser.parse
	"dojo/query", // query
	"dojo/ready", // ready
	"docs/CodeGlassViewerMini",
	"dijit/Dialog",
	"docs/MiniGlass",
	"docs/RstEditor"
], function(lang, baseFx, cookie, dom, domConst, domClass, style, on, parser, query, ready, CodeGlassViewerMini, Dialog, RstEditor){

	ready(function(){
		lang.setObject("docs.RstEditor", RstEditor);
		parser.parse();
		
		var dialog = new Dialog({ title:"CodeGlass" });
		lang.setObject("docs.masterviewer", new CodeGlassViewerMini(dialog));
		query(".live-example").forEach(function(n){
			var link = domConst.place("<a href='#' title='Example Code'><span class='a11y'>?</span></a>", n, "first");
			var data = query(".closed", n)[0];
			on(link, "click", function(e){
				if(e) e.preventDefault();
				domClass.toggle(data, "closed");
			});
		});
		
		var linknode = dom.byId("redirectlink");
		if(linknode){

			var hideWarning = cookie("hideWarning");

			if(!hideWarning){
				style.set(linknode, "display", "inline");
				on(dom.byId("closer"), "click", function(e){
					e.preventDefault();
					style.set(linknode, "opacity", "1");
					var fade = baseFx.fadeOut({
						node: linknode
					});
					on(fade, "End", function(){
						style.set(linknode, "display", "none");
						cookie("hideWarning", true, { expires: 7 });
					});
					fade.play();
				});
			}

			// redirect a/b/c to dtk.org/ref-guide/a/b/c.html

			var base = 'http://dojotoolkit.org/reference-guide/';

			var str = "<a href='{href}'>Read the release version of this documentation instead</a> (if it exists).";
			var data = {
				href: (function(){

					var parts = window.location.pathname.split("/");

					var hrefparts = dojo.filter(parts, function(p){
						return lang.trim(p).length;
					});

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
