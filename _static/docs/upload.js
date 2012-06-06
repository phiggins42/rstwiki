define([
	"dojo/_base/lang", // lang.replace
	"dojo/dom-construct", // domConst.place
	"dojo/dom-style", // style.set
	"dojo/fx", // coreFx.wipeIn
	"dojo/query", // query
	"dojo/domReady!"
], function(lang, domConst, style, coreFx, query){

	var template = "<div class='bloc'><label for='uploadfile{count}'>Select File:</label>" +
				"<input type='file' name='uploadfile{count}' id='uploadfile{count}'></div>"

	var count = 1;
	query("#morefiles").onclick(function(e){
		e.preventDefault();
		var n = domConst.place(lang.replace(template, { count: count++ }), "files", "first");
		style.set(n, "height", "1px");
		coreFx.wipeIn({ node:n }).play();
	});

	query("form").onsubmit(function(e){
		query("input[type=file]", e.target)
			.forEach(function(n){
				if(!n.value){
					domConst.destroy(n.parentNode);
				}
			});
	});

	return {};
});
