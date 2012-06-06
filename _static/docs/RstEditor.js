define([
	"dojo/_base/declare", // declare
	"dojo/_base/Deferred", // Deferred
	"dojo/_base/event", // event.stop
	"dojo/_base/fx", // baseFx.animateProperty
	"dojo/_base/kernel", // kernel.global
	"dojo/_base/lang", // lang.hitch
	"dojo/_base/xhr", // xhr.post
	"dojo/dom", // dom.byId
	"dojo/dom-style", // style.set
	"dojo/on", // on
	"dijit/_WidgetBase",
	"dijit/_HasDropDown",
	"dijit/form/TextBox",
	"dijit/form/Button"
],function(declare, Deferred, event, baseFx, kernel, lang, xhr, dom, style, on, _WidgetBase, _HasDropDown, TextBox,
		Button){

	return declare("docs.RstEditor", [_Widget, _HasDropDown],{
		toggleButtonId: "rstwiki-editActionButton",
		saveButtonId: "rstwiki-saveButton",
		previewPanelId: "rstwiki-previewPanel",
		contentPanelId: "rstwiki-contentPanel",
		editControlsId: "rstwiki-editControls",
		resetButtonId: "rstwiki-resetButton",
		editorMessageId: "rstwiki-editorMessage",
		noticeId:"rstwiki-noticenode",
		height: 400,
		_dropDownPosition: ["below"],

		buildRendering: function(){
			this.editing = false;
			console.log("editor start");
			this.previewPanel = dom.byId(this.previewPanelId);
			this.contentPanel = dom.byId(this.contentPanelId);
			this.editControls = dom.byId(this.editControlsId);
			this.toggleButton = dom.byId(this.toggleButtonId);
			this.saveButton = dom.byId(this.saveButtonId);
			this.resetButton = dom.byId(this.resetButtonId);
			this.editorMessage = dom.byId(this.editorMessageId);
			this.notice = dom.byId(this.noticeId);
			this._aroundNode = this.saveButton;
			this._buttonNode = this.saveButton
			this.inherited(arguments);
		},

		postCreate: function(){
			//connect to external buttons

			console.log(this.toggleButton, this.saveButton,this.resetButton)
			if(this.toggleButton){
				this.connect(this.toggleButton,"onclick", "toggle")
				this.connect(this.saveButton,"onclick", "save")
				this.connect(this.resetButton,"onclick", "reset")
			}
			// catch a bunch of text editor events so we know
			// when things have changed
			this.connect(kernel.global,"onkeydown", "onKeyDown");
			this.connect(this.domNode, "onkeyup", "onChange");
			this.connect(this.domNode, "onchange", "onChange");
			this.connect(this.domNode, "onpaste", "_onCopyPaste");
			this.connect(this.domNode, "oncut", "_onCopyPaste");

			// ha!
			this.dropDown = new dijit.TooltipDialog({
				content:
				'<div>Please describe your changes</div><textarea cols=40 rows=3 id="' + this.id + '_textarea" name="message"></textarea><br>' +
				'<button id="' + this.id + '_commit" data-dojo-type="dijit.form.Button" type="submit">Save</button>'+
				'<button id="' + this.id + '_cancel" data-dojo-type="dijit.form.Button" type="button">Cancel</button>'
			});

		},

		onKeyDown: function(evt){
			//global shortcuts
			//  metaKey + E  toggles edit mode
			//  metaKey + S  saves editor content if it is dirty
			var code = evt.which;
			switch(code){
				case 69:
					if(!evt.metaKey)return;
					this.toggle(evt);
				break;
				case 83:
					if(!evt.metaKey)return;
					this.save(evt);
					break;
				//default:
				//  console.log(code);
			}
		},

		onChange: function(){
			// on change, wait a bit then get a preview, cancel previous if another change happens
			if(!this.editing) return;
			if(this._delayedFetch){
				clearTimeout(this._delayedFetch);
			}

			if(this.domNode.value != this._previousContent){
				this.editorMessage.innerHTML = "Content has changed."
			}else{
				this.editorMessage.innerHTML = "";
			}

			this._delayedFetch = setTimeout(lang.hitch(this, function(){
				this.getPreview();
			}),500);

		},

		_onCopyPaste: function(){
			//trigger onchange on a slight delay
			setTimeout(lang.hitch(this,"onChange"),10);
		},

		save: function(e){
			console.log("save dialog");
			if(e){
				event.stop(e);
			}
			if(this._previousContent && this.domNode.value != this._previousContent){
				this.saving = true;
				this.editorMessage.innerHTML = "Saving.";
				this.openDropDown();
				var self = this;
				var h = on(dom.byId(this.id + "_commit"), 'click', function(evt){
					event.stop(evt);
					self.commit(dom.byId(this.id+"_textarea").value);
					self.closeDropDown();
					h.remove();
				});
				var h = on(dom.byId(this.id + "_cancel"), 'click', this, function(evt){
					event.stop(evt);
					this.closeDropDown();
					h.remove();
				});

			}
		},

		commit: function(message){
			//save the editor content and close the panel.
			//use the preview content as the editor content unless
			//the response comes back with something different
			console.log('editing: ', this.editing);
			if(this._previousContent && this.domNode.value != this._previousContent){
				this.saving = true;
				this.editorMessage.innerHTML = "Saving.";

				xhr.post({
					url: window.location,
					content: {content: this.domNode.value,message:message,action:"bare"},
					handleAs: "text",
					load: lang.hitch(this, function(content){
						this.saving = false;
						console.log('saved');
						delete this._previousContent;
						if(content && this.contentPanel.innerHTML != content){
							this.contentPanel.innerHTML = content;
						}
						this.editorMessage.innerHTML = "";
					}),
					error: lang.hitch(this, function(){
						this.editorMessage.innerHTML = "";
						this.saving = false;
					})

				})
				//this.contentPanel.innerHTML = this.previewPanel.innerHTML;
				this.hide();
			}
		},

		show: function(){
			this._showDef = new Deferred();
			style.set(this.domNode, { "display": "","height": "" });
			baseFx.animateProperty({
				node: this.domNode,
				duration: 150,
				properties: {
					height: this.height
				},
				onEnd: lang.hitch(this._showDef, "resolve", true)
			}).play();
			if(!this._previousContent || this._previousContent == this.domNode.value){
				this._previousContent = this.domNode.value;
			}
			style.set(this.contentPanel, "display", "none");
			style.set(this.previewPanel, "display", "");
			style.set(this.editControls, "display", "");
			style.set(this.notice, "display", "");
			this.toggleButton.innerHTML = "hide editor"
			return this._showDef.then(lang.hitch(this,"onShow"));
		},

		hide: function(){
			if(this._delayedFetch){
				clearTimeout(this._delayedFetch);
			}
			this._hideDef = new Deferred();
			var height = 0;
			baseFx.animateProperty({
				node: this.domNode,
				duration: 150,
				properties: {
					height: height
				},
				onEnd: lang.hitch(this._hideDef, "resolve", true)
			}).play();
			style.set(this.contentPanel, "display", "block");
			style.set(this.previewPanel, "display", "none");
			style.set(this.editControls, "display","none");
			style.set(this.notice, "display", "none");

			return this._hideDef.then(lang.hitch(this,function(){
				style.set(this.domNode, "display", "none");
				this.toggleButton.innerHTML = "edit"
			})).then(lang.hitch(this, "onHide"));
		},

		toggle: function(evt){
			if(evt){
				event.stop(evt);
			}

			if(style.get(this.domNode, "display") == "none"){
				this.show();
			}else{
				this.hide();
			}
		},

		reset: function(evt){
			if(confirm("Are you sure? Your changes will be lost.")){
				event.stop(evt);
				console.log("reset");
				this.domNode.value = this._previousContent;
			}
		},

		getPreview:function(force){
			if(!force && (!this.editing || this.saving)){ return; }
			this.previewPanel.innerHTML = this.contentPanel.innerHTML;
			if(!this.previewPanel.innerHTML || !this._previewContent || this.domNode.value != this._previewContent){
				console.log("posting: ", { preview: this.domNode.value });
				this._previewContent = this.domNode.value;
				xhr.post({
					url: window.location,
					content: { preview: this._previewContent, id_prefix:"preview_" },
					handleAs: "text",
					load: lang.hitch(this, function(content){
						style.set(this.contentPanel, "display", "none");
						if(!this.saving && content != this.previewPanel.innerHTML && this.domNode.value == this._previewContent){
							this.previewPanel.innerHTML = content;
						}
					})
				});
			}
		},

		onShow:function(){
			this.editing = true;
			if(!this.previewPanel.innerHTML){
				this.getPreview()
				//this.previewPanel.innerHTML = this.contentPanel.innerHTML;
			}

			if(this._previousContent && this.domNode.value != this._previousContent){
				this.editorMessage.innerHTML = "Content has changed."
			}else{
				this.editorMessage.innerHTML = ""
			}
			this.domNode.focus();
		},

		onHide:function(){
			this.editing = false;
			if(this._previousContent && this.domNode.value != this._previousContent){
				if(!this.saving){
					this.editorMessage.innerHTML = "Content has changed.";
				}
			}else{
				this.editorMessage.innerHTML = "";
			}
		}
	});

});