define([
	"dojo", "dijit", 
	"dojo/text!./CodeGlassMini.html", 
	"dojo/parser", "dojo/fx", 
	"dijit/_Widget", "dijit/form/Button", 
	"dojox/widget/Dialog", 
	"./RstEditor"
], function(dojo, dijit, CodeGlassTemplate){

	var ta = dojo.create("textarea"),
		scriptopen = "<scr" + "ipt>",
		scriptclose = "</" + "scri" + "pt>",
		masterviewer, dialog;

	dojo.declare("docs.MiniGlass", dijit._Widget, {
		
		djconfig:"",
		width:700,
		height:480,
		type:"dialog",
		version:"",
		toolbar:"",
		debug:false,
		themename:"claro",
		baseUrl: dojo.config.baseUrl + "../",
		pluginargs:null,
		
		constructor: function(args){
			this.parts = args.parts || {}
		},
		
		postCreate: function(){
			// all we do it put a button in our self to run ourself. We don't process the content at all
			this.closer = dojo.place("<a href='#' title='Collapse Example Code' class='CodeGlassMiniCollapser'><span class='a11y'>collapse</span></a>", this.domNode, "first");
			this.showcode = dojo.place("<a href='#' title='Show Raw HTML'><span class='a11y'>raw html</span></a>", this.domNode, "first");
			this.button = dojo.place("<a href='#' title='Run Example' class='CodeGlassMiniRunner'><span class='a11y'>run</span></a>", this.domNode, "first");
			this.connect(this.button, "onclick", "_run");
			this.connect(this.showcode, "onclick", "_showCode");
			this.connect(this.closer, "onclick", "_toggle");
			this.inner = dojo.query(".CodeGlassMiniInner", this.domNode)[0];
		},

		
		// only run processing once:
		_hasRun: false,
		_generateTemplate: function(){
			if(!this._hasRun){ 
				this._hasRun = true;
				try{
					dojo.query("textarea", this.domNode).forEach(this.handlePart, this);
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
			var dialog = new dijit.Dialog({
				title: "Raw HTML",
				content: dojo.create("textarea", {
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
			dojo.toggleClass(this.domNode, "closed");
		},
		
		handlePart: function(n){
			// this is testing the label="" and lang="" attribute. it's html/javascript/css enum
			var t = dojo.attr(n.parentNode, "lang");
			t && this._processPart(t, n.value);
			// rip the old label="" attr and move to a block before. this is the new syntax
			// for codeglass examples, and will be removed from the markup slowly
			var label = dojo.attr(n.parentNode, "label");
			label && dojo.place("<p>" + label + "</p>", n.parentNode, "before");
		},
		
		_processPart: function(type, content){
			if(!this.parts[type]){
				this.parts[type] = []
			}
			
			var orig = content;
			var openswith = dojo.trim(orig).charAt(0);
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
		
		template: CodeGlassTemplate,
		_buildTemplate: function(){
			
			var args = this.pluginargs;

			var templateParts = {
				javascript:"<scr" + "ipt src='" + 
					this.baseUrl + "dojo/dojo.js'" +
					(args.djConfig ? " data-dojo-config='" + args.djConfig + "'": "") +
					">" + scriptclose,
				
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
				dojo.forEach(this.parts[i], function(item){
					
					var processed = dojo.replace(item, locals, cgMiniRe);
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

			this.renderedTemplate = dojo.replace(this.template, templateParts);
		},
		
		show: function(){
			if(this.type == "dialog"){
				masterviewer.show(this);
			}else{
				console.warn("intended to be injected inline");
				masterviewer.show(this);
			}
		}
				
	});
	
	var loadingMessage = "<p>Preparing Example....</p>";
	dojo.declare("docs.CodeGlassViewerMini", null, {

		show: function(who){
			// some codeglassmini instance wants us to show them. 

			if(this.iframe){ dojo.destroy(this.iframe); }
			dialog.set("content", loadingMessage);

			dojo.style(dialog.containerNode, {
				width: who.width + "px",
				height: who.height + "px"
			});
			
			dialog.show();

			setTimeout(dojo.hitch(this, function(){

				var frame = this.iframe = dojo.create("iframe", {
					style:{
						height: who.height + "px",
						width: who.width + "px",
						border:"none",
						visibility:"hidden"
					}
				});

				dialog.set("content", frame);
				frame.setAttribute("src", "javascript: '" +
					who.renderedTemplate.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n") + "'");

				function display(){
					dojo.style(frame, {
						"visibility": "visible",
						opacity: 0
					});

					dojo.anim(frame, { opacity:1 });
				}

				var e;
				if(frame.addEventListener){
					e = frame.addEventListener("load", display, false)
				}else if(frame.attachEvent){
					e = frame.attachEvent("onload", display);
				}
				

			}), dialog.duration + 450);			

		}

	});
		
	dojo.ready(function(){
		
		dojo.parser.parse();
		dialog = new dijit.Dialog({ title:"CodeGlass" });
		masterviewer = new docs.CodeGlassViewerMini();
		dojo.query(".live-example").forEach(function(n){
			var link = dojo.place("<a href='#' title='Example Code'><span class='a11y'>?</span></a>", n, "first");
			var data = dojo.query(".closed", n)[0];
			dojo.connect(link, "onclick", function(e){
				e && e.preventDefault();
				dojo.toggleClass(data, "closed");
			});
		});
		
		var linknode = dojo.byId("redirectlink");
			if(linknode){

				// redirect a/b/c to dtk.org/ref-guide/a/b/c.html

				var base = 'http://dojotoolkit.org/reference-guide/';

				var str = "Try <a href='{href}'>the last static version</a> of this doc (if it exists).";
				var data = {
					href: (function(){

						var parts = window.location.pathname.split("/");

						var hrefparts = dojo.filter(parts, function(p){
							return dojo.trim(p).length;
						});
						console.log(hrefparts.length, "!!!");
						if(!hrefparts.length){
							console.warn(hrefparts);
							hrefparts.push("index");	
						}

						return base + hrefparts.join("/") + ".html";

					})()
				};

				dojo.place(dojo._toDom(dojo.replace(str, data)), linknode);

			}
	});
	
	
});
