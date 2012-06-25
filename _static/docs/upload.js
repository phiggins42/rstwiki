define([
	"dojo/_base/lang", // lang.replace
	"dojo/dom", // dom.byId
	"dojo/dom-construct", // domConst.place
	"dojo/dom-style", // style.set
	"dojo/fx", // coreFx.wipeIn
	"dojo/on", // on
	"dojo/query", // query
	"dojo/ready" // ready
], function(lang, dom, domConst, style, coreFx, on, query, ready){

	var template = "<div class='bloc'><label for='uploadfile{count}'>Select File:</label>" +
				"<input type='file' name='uploadfile{count}' id='uploadfile{count}'></div>"

	var count = 1;
	ready(function(){
		on(dom.byId("morefiles"), "click", function(e){
			e.preventDefault();
			var n = domConst.place(lang.replace(template, { count: count++ }), "files", "first");
			style.set(n, "height", "1px");
			coreFx.wipeIn({ node:n }).play();
		});

		on(dom.byId("rstwiki-upload"), "submit", function(e){
			query("input[type=file]", e.target)
				.forEach(function(n){
					if(!n.value){
						domConst.destroy(n.parentNode);
					}
				});
		});
	});

	return {};
});
