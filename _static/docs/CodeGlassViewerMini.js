define([
	"dojo/_base/declare", // declare
	"dojo/_base/fx", // baseFx.anim
	"dojo/_base/lang", // lang.hitch
	"dojo/dom-construct", // domConst.destory, domConst.create
	"dojo/dom-style", // style.set
	"dijit/focus"
], function(declare, baseFx, lang, domConst, style, focus){
	return declare("docs.CodeGlassViewerMini", null, {
		
		dialog: null,
		
		loadingMessage: "<p>Preparing Example....</p>",
		
		constructor: function(dialog){
			this.dialog = dialog;
		},

		show: function(who){
			// some codeglassmini instance wants us to show them. 

			if(this.iframe){ domConst.destroy(this.iframe); }
			this.dialog.set("content", this.loadingMessage);

			style.set(this.dialog.containerNode, {
				width: who.width + "px",
				height: who.height + "px"
			});
			
			this.dialog.show();

			setTimeout(lang.hitch(this, function(){

				var frame = this.iframe = domConst.create("iframe", {
					src: "javascript: '" +
						who.renderedTemplate.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n") + "'",
					style:{
						height: who.height + "px",
						width: who.width + "px",
						border:"none",
						visibility:"hidden"
					}
				});


				// After the iframe finishes loading, then make it visible.   Setup listener early, before adding
				// the iframe to the DOM; otherwise we might miss the load event.
				if(frame.addEventListener){
					frame.addEventListener("load", onLoad, false)
				}else if(frame.attachEvent){
					frame.attachEvent("onload", onLoad);
				}

				this.dialog.set("content", frame);

				function onLoad(){
					// Need to register the iframe or otherwise can't click an element to focus it, because the focus
					// manager thinks the click came from outside the Dialog, so the Dialog tries to move focus back
					// to itself.
					focus.registerIframe(frame);

					style.set(frame, {
						"visibility": "visible",
						opacity: 0
					});

					baseFx.anim(frame, { opacity:1 });
				}

			}), this.dialog.duration + 450);			

		}

	});
})