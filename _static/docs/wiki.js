dojo.provide("docs.wiki");
dojo.require("dojo.parser");
dojo.require("dijit._Widget");
dojo.require("dojo.fx");
dojo.require("dijit.form.Button");
dojo.require("dijit.Dialog");
(function(d){
    
    var ta = d.create("textarea"),
        dialog = new dijit.Dialog({ title:"Running Example" }),
        masterviewer,
        scriptopen = "<scr" + "ipt>",
        scriptclose = "</" + "scri" + "pt>"
    ;
    
    d.declare("docs.MiniGlass", dijit._Widget, {
        
        djconfig:"",
        width:700,
        height:480,
        type:"dialog",
        version:"",
        toolbar:"",
        debug:false,
        themename:"claro",
        baseUrl: dojo.config.baseUrl + "..",
        
        constructor: function(args){
            this.parts = args.parts || {}
        },
        
        postCreate: function(){
            // all we do it put a button in our self to run outself. We don't process the content at all
            this.closer = dojo.place("<a href='#' title='Collapse Example Code' class='CodeGlassMiniCollapser'><span class='a11y'>collapse</span></a>", this.domNode, "first");
            this.button = dojo.place("<a href='#' title='Run Example' class='CodeGlassMiniRunner'><span class='a11y'>run</span></a>", this.domNode, "first");
            this.connect(this.button, "onclick", "_run");
            this.connect(this.closer, "onclick", "_toggle");
            this.inner = d.query(".CodeGlassMiniInner", this.domNode)[0];
        },

        // only run processing once:
        _hasRun: false,
        _run: function(e){
            e && e.preventDefault();
            if(!this._hasRun){ 
                this._hasRun = true;
                try{
                    dojo.query("textarea", this.domNode).forEach(this.handlePart, this);
                    this._partsSurvived();
                }catch(er){
                    console.warn("running miniglass threw", er);
                }
            }
            this.show();
        },
        
        _toggle: function(e){
            e && e.preventDefault();
            dojo.toggleClass(this.domNode, "closed");
        },
        
        handlePart: function(n){
            // this is testing the label="" and lang="" attribute. it's html/javascript/css enum
            var t = dojo.attr(n.parentNode, "lang");
            t && this._processPart(t, n.value);
            var label = dojo.attr(n.parentNode, "label");
            label && dojo.place("<p>" + label + "</p>", n.parentNode, "before");
        },
        
        _processPart: function(type, content){
            if(!this.parts[type]){
                this.parts[type] = []
            }
            
            var orig = content;
            var openswith = d.trim(orig).charAt(0);
            if(type == "javascript" && openswith == "<"){
                // strip the `script` text, this is a special consideration
                orig = orig
                    .replace(/<script[\s+]?.*?>/g, "")
                    .replace(/[\s+]?<\/script>/g, "")
                ;
            }else if(type == "css" && openswith != "<"){
                orig = '<style type="text/css">' + orig + '</style>';
            }

            this.parts[type].push(orig)

        },
        
        
        _partsSurvived: function(){
            console.dir(this.parts)
            this._buildTemplate();
        },
        
        template: dojo.cache("docs", "CodeGlassMini.html"),
        _buildTemplate: function(){
            
            this.lazyScripts = [];
            var templateParts = {
                javascript:"<scr" + "ipt src='" + 
                    this.baseUrl + "/dojo/dojo.js' djConfig='" + 
                    (dojo.isIE ? "isDebug:true, " : "") + 
                    // (dojo.isIE ? 'afterOnLoad:true, ' : '') + 
                    "parseOnLoad:true'>" + scriptclose,
                
                htmlcode:"", 
                
                // if we have a theme set include a link to {baseUrl}/dijit/themes/{themename}/{themename}.css first
                css:'\t<link rel="stylesheet" href="' + this.baseUrl + '/dijit/themes/' + this.themename + '/' + this.themename + '.css">\n\t',
                
                // if we've set RTL include dir="rtl" i guess?
                htmlargs:"",
                
                // if we have a theme set, include class="{themename}"
                bodyargs:'class="' + this.themename + '"',
                
                // 
                head:"",
                
                baseUrl: this.baseUrl,
                dataUrl: this.dataUrl
                
            }
            
            for(var i in this.parts){
                dojo.forEach(this.parts[i], function(item){
                    switch(i){
                        case "javascript":
                            this.lazyScripts.push(item);
                            break
                        case "html":
                            templateParts['htmlcode'] += item;
                            break;
                        case "css":
                            templateParts['css'] += item
                    }
                }, this);
            }
            this.renderedTemplate = dojo.replace(this.template, templateParts);
        },
        
        show: function(){
            masterviewer.show(this);
        }
                
    });
    
    function addscripttext(doc, code){
        
        var e = doc.createElement("script"),
            how = "text" in e ? "text" :
                "textContent" in e ? "textContent" :
                "innerHTML" in e ? "innerHTML" :
                "appendChild"
        ;
            
        if(how == "appendChild"){
            e[how](d.doc.createTextNode(code));
        }else{
            e[how] = code;
        }
            
        doc.getElementsByTagName("body")[0].appendChild(e);

    }
    
    var loadingMessage = "<p>Preparing Example....</p>";
    dojo.declare("docs.CodeGlassViewerMini", null, {

        show: function(who){
            // some codeglassmini instance wants us to show them. 

            if(this.iframe){ dojo.destroy(this.iframe); }
            dialog.set("content", loadingMessage);
            dialog.show();
            
            setTimeout(dojo.hitch(this, function(){

                var frame = this.iframe = dojo.create("iframe", {
                        style:{
                            height: who.height + "px",
                            width: who.width + "px",
                            border:"none"
                        }
                    });
                
                dialog.set("content", frame);
                
                var doc = frame.contentDocument || frame.contentWindow.document;                
                doc.open();

                doc.write(who.renderedTemplate);

                if(dojo.isIE){
                    
                    // we're only here because '
                    console.log("IE branch to write scripts");
                    var scripts = who.lazyScripts, errors = [],
                        inject = dojo.partial(dojo.forEach, scripts, function(s){ 
                            console.log("injecting js to", doc);
                            try{
                                addscripttext(doc, s); 
                            }catch(er){
                                console.log("an error happened");
                                errors.push(er)
                            }
                        }, this)
                    ;
                    
                    var e;
                    if(frame.addEventListener){
                        e = frame.addEventListener("load", inject, false);
                    }else if(frame.attachEvent){
                        e = frame.attachEvent("onload", inject);
                    }
                    
                }else{

                    var joinedscripts = dojo.map(who.lazyScripts, function(body){
                        return scriptopen + body + scriptclose
                    }).join("");
                    doc.write(joinedscripts);
                }
                
                doc.close();

                
                
            }), dialog.duration + 450);            

        }

    });
    
    masterviewer = new docs.CodeGlassViewerMini();
    
    dojo.ready(function(){
        dojo.parser.parse();
    });
    
})(dojo);
