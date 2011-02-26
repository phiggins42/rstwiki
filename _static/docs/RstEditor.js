dojo.provide("docs.RstEditor");
dojo.require("dijit._Widget");

dojo.declare("docs.RstEditor", [dijit._Widget],{
	toggleButtonId: "editActionButton",
        saveButtonId: "saveButton",
	previewPanelId: "previewPanel",
	contentPanelId: "contentPanel",
	editControlsId: "editControls",
        resetButtonId: "resetButton",
	height: 400,
	postCreate: function(){
		console.log("editor start");
		this.previewPanel = dojo.byId(this.previewPanelId);
		this.contentPanel= dojo.byId(this.contentPanelId);
		this.editControls = dojo.byId(this.editControlsId);
		this.toggleButton = dojo.byId(this.toggleButtonId);
		this.saveButton = dojo.byId(this.saveButtonId);
		this.resetButton = dojo.byId(this.resetButtonId);
	
		//connect to external buttons
            	this.connect(dojo.byId(this.toggleButtonId),"onclick", "toggle") 
            	this.connect(dojo.byId(this.saveButtonId),"onclick", "save") 
            	this.connect(dojo.byId(this.resetButton),"onclick", "reset") 

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
		var code = evt.which;
		switch(code){
			case 69:
				dojo.stopEvent(evt);
				this.toggle();
			break;
		}
	},

	onChange: function(){
		// on change, wait a bit then get a preview, cancel previous if another change happens
		if (this._delayedFetch){
			clearTimeout(this._delayedFetch);
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
		if (this.domNode.value != this._previousContent){
			dojo.xhrPost({
				url: window.location,
				content: {content: this.domNode.value,message:"Update from Wiki",action:"bare"},
				handleAs: "text",
				load: function(content){
					console.log('saved');
					if (this.contentPanel.innerHTML != content){
						this.contentPanel.innerHTML=content;
					}	
				}
				
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

		return this._hideDef.then(dojo.hitch(this,function(){
			dojo.style(this.domNode, "display", "None");
			dojo.style(this.contentPanel,"display", "");
			dojo.style(this.previewPanel,"display", "none");
			dojo.style(this.editControls, "display","none");
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
			dojo.style(this.previewPanel, "display", "none")
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
		this.previewPanel.innerHTML = this.contentPanel.innerHTML;
		dojo.style(this.contentPanel,"display","none");
		if (!this._previewContent || this.domNode.value != this._previewContent){
			console.log("posting: ",{preview:this.domNode.value});
			this._previewContent = this.domNode.value;
			dojo.xhrPost({
				content:{preview:this._previewContent},
				handleAs: "text",
				load: dojo.hitch(this, function(content){
					if (content != dojo.byId("previewPanel").innerHTML && this.domNode.value==this._previewContent){
						dojo.style(this.contentPanel, "display", "none")
						dojo.style(this.previewPanel,"display", "");
						this.previewPanel.innerHTML=content;
					}
				})
			});
		}
	},
	onShow:function(){
	},
	onHide:function(){
	}
});
