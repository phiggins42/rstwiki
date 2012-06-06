define([
	"dojo/_base/declare", // declare
	"dojo/_base/fx", // baseFx.anim
	"dojo/dom-construct", // domConst.destory, domConst.create
	"dojo/dom-style" // style.set
], function(declare, baseFx, domConst, style){
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

			setTimeout(dojo.hitch(this, function(){

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

				this.dialog.set("content", frame);

				function display(){
					style.set(frame, {
						"visibility": "visible",
						opacity: 0
					});

					baseFx.anim(frame, { opacity:1 });
				}

				var e;
				if(frame.addEventListener){
					e = frame.addEventListener("load", display, false)
				}else if(frame.attachEvent){
					e = frame.attachEvent("onload", display);
				}

			}), this.dialog.duration + 450);			

		}

	});
})