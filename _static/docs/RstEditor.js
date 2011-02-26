dojo.provide("docs.RstEditor");
dojo.require("dijit._Widget");

dojo.declare("docs.RstEditor", [dijit._Widget],{
	toggleButtonId: "editActionButton",
        saveButtonId: "saveButton",
	previewPanelId: "previewPanel",
	contentPanelId: "contentPanel",
	editControlsId: "editControls",
        resetButtonId: "resetButton",
        editorMessageId: "editorMessage",
		noticeId:"noticenode",
	height: 400,
	postCreate: function(){
		this.editing=false;
		console.log("editor start");
		this.previewPanel = dojo.byId(this.previewPanelId);
		this.contentPanel= dojo.byId(this.contentPanelId);
		this.editControls = dojo.byId(this.editControlsId);
		this.toggleButton = dojo.byId(this.toggleButtonId);
		this.saveButton = dojo.byId(this.saveButtonId);
		this.resetButton = dojo.byId(this.resetButtonId);
		this.editorMessage= dojo.byId(this.editorMessageId);	
		this.notice = dojo.byId(this.noticeId);
		
		//connect to external buttons

		console.log(this.toggleButton, this.saveButton,this.resetButton)
		if (this.toggleButton) {
	            	this.connect(this.toggleButton,"onclick", "toggle") 
       		     	this.connect(this.saveButton,"onclick", "save") 
       		     	this.connect(this.resetButton,"onclick", "reset") 
		}

		// catch a bunch of text editor events so we know
		// when things have changed
		this.connect(dojo.global,"onkeydown", "onKeyDown");
	        this.connect(this.domNode, "onkeyup", "onChange");
                this.connect(this.domNode, "onchange", "onChange");
                this.connect(this.domNode, "onpaste", "_onCopyPaste");
                this.connect(this.domNode, "oncut", "_onCopyPaste");
	},

	onKeyDown: function(evt){
		//global shortcuts
		//	metaKey + E  toggles edit mode
		//	metaKey + S  saves editor content if it is dirty
		var code = evt.which;
		switch(code){
			case 69:
				if (!evt.metaKey)return;
				this.toggle(evt);
			break;
			case 83:
				if (!evt.metaKey)return;
				this.save(evt);
				break;
			//default:
			//	console.log(code);
		}
	},

	onChange: function(){
		// on change, wait a bit then get a preview, cancel previous if another change happens
		if (!this.editing) return;
		if (this._delayedFetch){
			clearTimeout(this._delayedFetch);
		}

		if (this.domNode.value != this._previousContent){
			this.editorMessage.innerHTML="Content has changed."
		}else{
			this.editorMessage.innerHTML="";
		}

		this._delayedFetch=setTimeout(dojo.hitch(this, function(){
			this.getPreview();
		}),500);

	},

	_onCopyPaste: function(){
		//trigger onchange on a slight delay
		setTimeout(dojo.hitch(this,"onChange"),10);
	},

	save: function(e){
		//save the editor content and close the panel.
		//use the preview content as the editor content unless
		//the response comes back with something different 
		dojo.stopEvent(e);
		console.log('editing: ', this.editing);
		if (this._previousContent && this.domNode.value != this._previousContent){
			this.saving=true;
			this.editorMessage.innerHTML="Saving.";

			dojo.xhrPost({
				url: window.location,
				content: {content: this.domNode.value,message:"Update from Wiki",action:"bare"},
				handleAs: "text",
				load: dojo.hitch(this, function(content){
					this.saving=false;
					console.log('saved');
					delete this._previousContent;
					if (content && this.contentPanel.innerHTML != content){
						this.contentPanel.innerHTML=content;
					}	
					this.editorMessage.innerHTML="";
				}),
				error: dojo.hitch(this, function(){
					this.editorMessage.innerHTML="";
					this.saving=false;
				})
				
			})
			this.contentPanel.innerHTML = this.previewPanel.innerHTML;
			this.hide();
		}
	},

	show: function(){
		this._showDef=new dojo.Deferred()
		dojo.style(this.domNode,{"display":"","height":""});
		dojo.animateProperty({
			node: this.domNode,
			duration: 150,
			properties: {
				height: this.height 
			},
			onEnd: dojo.hitch(this._showDef,"resolve",true)
		}).play();	
		if (!this._previousContent || this._previousContent == this.domNode.value){
			this._previousContent = this.domNode.value;
		}
		if (!this.previewPanel.innerHTML){
			this.previewPanel.innerHTML = this.contentPanel.innerHTML;
		}
		dojo.style(this.contentPanel,"display","none");
		dojo.style(this.previewPanel,"display","");
		dojo.style(this.editControls, "display","");
		dojo.style(this.notice, "display", "");
		this.toggleButton.innerHTML="hide editor"
		return this._showDef.then(dojo.hitch(this,"onShow"));
	},

	hide: function(){
		if (this._delayedFetch){
			clearTimeout(this._delayedFetch);
		}
		this._hideDef=new dojo.Deferred()
		var height=0;
		dojo.animateProperty({
			node: this.domNode,
			duration: 150,
			properties: {
				height: height 
			},
			onEnd: dojo.hitch(this._hideDef,"resolve",true)
		}).play();	
		dojo.style(this.contentPanel,"display", "block");
		dojo.style(this.previewPanel,"display", "none");
		dojo.style(this.editControls, "display","none");
		dojo.style(this.notice,"display","none");
	
		return this._hideDef.then(dojo.hitch(this,function(){
			dojo.style(this.domNode, "display", "None");
			this.toggleButton.innerHTML="edit"
		})).then(dojo.hitch(this,"onHide"));
	},

	toggle: function(evt){
		if (evt){
			dojo.stopEvent(evt);
		}

		if (dojo.style(this.domNode,"display")=="none"){
			this.show()
		}else{
			this.hide();
		}
	},

	reset: function(evt){
		if (confirm("Are you sure? Your changes will be lost.")){
			dojo.stopEvent(evt);
			console.log("reset");
			this.domNode.value = this._previousContent;
		}
	},
	
	getPreview:function(){
		if (!this.editing || this.saving){return;}
		this.previewPanel.innerHTML = this.contentPanel.innerHTML;
		dojo.style(this.contentPanel,"display","none");
		if (!this._previewContent || this.domNode.value != this._previewContent){
			console.log("posting: ",{preview:this.domNode.value});
			this._previewContent = this.domNode.value;
			dojo.xhrPost({
				url: window.location,
				content:{preview:this._previewContent},
				handleAs: "text",
				load: dojo.hitch(this, function(content){

					if (!this.saving &&  content != dojo.byId("previewPanel").innerHTML && this.domNode.value==this._previewContent){
						this.previewPanel.innerHTML=content;
					}
				})
			});
		}
	},
	onShow:function(){
		this.editing=true;
		if (this._previousContent && this.domNode.value != this._previousContent){
			this.editorMessage.innerHTML="Content has changed."
		}else{
			this.editorMessage.innerHTML=""
		}
		this.domNode.focus();
	},
	onHide:function(){
		this.editing=false;
		if (this._previousContent && this.domNode.value != this._previousContent){
			if (!this.saving){
				this.editorMessage.innerHTML="Content has changed."
			}
		}else{
			this.editorMessage.innerHTML=""
		}
	}
});
