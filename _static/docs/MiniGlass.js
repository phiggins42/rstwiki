define([
	"dojo/_base/array", // array.forEach
	"dojo/_base/config", // config.baseUrl
	"dojo/_base/declare", // declare
	"dojo/_base/lang", // lang.trim
	"dojo/_base/sniff", // has
	"dojo/dom-attr", // domAttr.get
	"dojo/dom-class", // domClass.toggle
	"dojo/dom-construct", // domConst.place
	"dojo/json", // JSON
	"dojo/query", // query
	"dijit/_WidgetBase",
	"dijit/Dialog",
	"dojo/text!./resources/CodeGlassMini.html"
], function(array, config, declare, lang, has, domAttr, domClass, domConst, JSON, query, _WidgetBase, Dialog, template){
	
	var scriptopen = "<scr" + "ipt>",
		scriptclose = "</" + "scri" + "pt>";

	return declare("docs.MiniGlass", [_WidgetBase], {
		djconfig:"",
		width:700,
		height:480,
		type:"dialog",
		version:"",
		toolbar:"",
		debug:false,
		themename:"claro",
		renderedTemplate: "",
		baseUrl: config.baseUrl + "../",
		pluginArgs:null,
		
		constructor: function(args){
			this.parts = args.parts || {};
		},
		
		postCreate: function(){
			// all we do it put a button in our self to run ourself. We don't process the content at all
			this.closer = domConst.place("<a href='#' title='Collapse Example Code' class='CodeGlassMiniCollapser'><span class='a11y'>Collapse</span></a>", this.domNode, "first");
			this.showcode = domConst.place("<a href='#' title='Show Raw HTML' class='CodeGlassMiniRawHtml'><span class='a11y'>Source</span></a>", this.domNode, "first");
			this.button = domConst.place("<a href='#' title='Run Example' class='CodeGlassMiniRunner'><span class='a11y'>Run</span></a>", this.domNode, "first");
			this.connect(this.button, "onclick", "_run");
			this.connect(this.showcode, "onclick", "_showCode");
			this.connect(this.closer, "onclick", "_toggle");
			this.inner = query(".CodeGlassMiniInner", this.domNode)[0];
		},

		
		// only run processing once:
		_hasRun: false,
		_generateTemplate: function(){
			if(!this._hasRun){ 
				this._hasRun = true;
				try{
					query("textarea", this.domNode).forEach(this.handlePart, this);
					this._buildTemplate();
				}catch(er){
					console.warn("running miniglass threw", er);
				}
			}
		},

		_run: function(e){
			e && e.preventDefault();
			this._generateTemplate();
			this.show();
		},
		
		_showCode: function(e){
			e && e.preventDefault();
			this._generateTemplate();
			var dialog = new Dialog({
				title: "Source",
				content: domConst.create("textarea", {
					value: this.renderedTemplate,
					spellcheck: false,
					style: {
						width: this.width + "px",
						height: this.height + "px"
					}
				}),
				onHide: function(){
					dialog.destroyRecursive();
				}
			});
			dialog.show();
		},

		_toggle: function(e){
			e && e.preventDefault();
			domClass.toggle(this.domNode, "closed");
		},
		
		handlePart: function(n){
			// this is testing the label="" and lang="" attribute. it's html/javascript/css enum
			var t = domAttr.get(n.parentNode, "lang");
			t && this._processPart(t, n.value);
			// rip the old label="" attr and move to a block before. this is the new syntax
			// for codeglass examples, and will be removed from the markup slowly
			var label = domAttr.get(n.parentNode, "label");
			label && domConst.place("<p>" + label + "</p>", n.parentNode, "before");
		},
		
		_processPart: function(type, content){
			if(!this.parts[type]){
				this.parts[type] = [];
			}
			
			var orig = content;
			var openswith = lang.trim(orig).charAt(0);
			if(type == "javascript" && openswith == "<"){
				// strip the `script` text, this is a special consideration
				// also, this limits each .. js block to a single script tag, FIXME
				orig = orig
					.replace(/<script[\s+]?.*?>/g, "")
					.replace(/[\s+]?<\/script>/g, "")
				;
			}else if(type == "css" && openswith != "<"){
				orig = '<style type="text/css">' + orig + '</style>';
			}

			this.parts[type].push(orig)

		},
		
		template: template,
		_buildTemplate: function(){
			
			var args = this.pluginArgs,
				dojoConfig = args.dojoConfig || args.djConfig,
				uri = document.createElement('a');

			uri.href = this.domNode.ownerDocument.URL;

			var templateParts = {
				javascript: (dojoConfig ? scriptopen + "dojoConfig = {" + dojoConfig + "}" + scriptclose : "") +
					"<scr" + "ipt src='" + (has("ie") ? config.cdn ? config.cdn + "dojo/" : config.baseUrl : config.baseUrl) +
					"dojo.js'>" + scriptclose,
				
				htmlcode:"", 
				
				// if we have a theme set include a link to {baseUrl}/dijit/themes/{themename}/{themename}.css first
				css:'\t<link rel="stylesheet" href="' + this.baseUrl + 'dijit/themes/' + this.themename + '/' + this.themename + '.css">\n\t',
				
				// if we've set RTL include dir="rtl" i guess?
				htmlargs:"",
				
				// if we have a theme set, include class="{themename}"
				bodyargs:'class="' + this.themename + '"',
				
				// 
				head:""
				
			};
			
			var cgMiniRe = /\{\{\s?([^\}]+)\s?\}\}/g,
				locals = {
					dataUrl: this.baseUrl,
					baseUrl: this.baseUrl,
					theme: this.themename
				};
			
			for(var i in this.parts){
				array.forEach(this.parts[i], function(item){
					
					var processed = lang.replace(item, locals, cgMiniRe);
					switch(i){
						case "javascript":
							templateParts.javascript += scriptopen + processed + scriptclose;
							break;
						case "html":
							templateParts['htmlcode'] += processed;
							break;
						case "css":
							templateParts['css'] += processed;
					}
				}, this);
			}
						
			// do the master template/html, then the {{codeGlass}} double ones:

			this.renderedTemplate = lang.replace(this.template, templateParts);
		},
		
		show: function(){
			if(this.type == "dialog"){
				docs.masterviewer.show(this);
			}else{
				console.warn("intended to be injected inline");
				docs.masterviewer.show(this);
			}
		}
	});
});