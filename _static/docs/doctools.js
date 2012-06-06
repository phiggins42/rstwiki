define([
	"dojo/_base/array", // array.indexOf, array.forEach
	"dojo/_base/NodeList", // NodeList.prototype
	"dojo/dom-attr", // domAttr.get
	"dojo/dom-class", // domClass.contains
	"dojo/dom-construct", // domConst.toDom
	"dojo/dom-style", // style.set
	"dojo/on", // on
	"dojo/query", // query
	"dojo/ready", // ready
	"dojo/sniff" // has("mozilla")
], function(array, NodeList, domAttr, domClass, domConst, style, ready, has){
	
// ported from Sphinx basic theme doctools.js to use Dojo

var doctools = {};

/**
 * small helper function to urldecode strings
 */
doctools.urldecode = function(x){
	return decodeURIComponent(x).replace(/\+/g, ' ');
}

/**
 * small helper function to urlencode strings
 */
doctools.urlencode = encodeURIComponent;

/**
 * This function returns the parsed url parameters of the
 * current request. Multiple values per key are supported,
 * it will always return arrays of strings for the value parts.
 */
doctools.getQueryParameters = function(s){
	if(typeof s == 'undefined') s = document.location.search;
	var parts = s.substr(s.indexOf('?') + 1).split('&');
	var result = {};
	for(var i = 0; i < parts.length; i++){
		var tmp = parts[i].split('=', 2);
		var key = doctools.urldecode(tmp[0]);
		var value = doctools.urldecode(tmp[1]);
		if(key in result){
			result[key].push(value);
		}else{
			result[key] = [value];
		}
	}
	return result;
}

/**
 * small function to check if an array contains
 * a given item.
 */
doctools.contains = function(arr, item){
	return array.indexOf(arr, item) >= 0;
}

/**
 * highlight a given string on a jquery object by wrapping it in
 * span elements with the given class name.
 */
NodeList.prototype.highlightText = function(text, className){
	
	function highlight(node){
	
		if(node.nodeType == 3){
			var val = node.nodeValue;
			var pos = val.toLowerCase().indexOf(text);
			if(pos >= 0 && !domClass.contains(node.parentNode, className)){
				var span = document.createElement("span");
				span.className = className;
				span.appendChild(document.createTextNode(val.substr(pos, text.length)));
				node.parentNode.insertBefore(span, node.parentNode.insertBefore(
					document.createTextNode(val.substr(pos + text.length)),
					node.nextSibling)
				);
				node.nodeValue = val.substr(0, pos);
			}
		}else if(!query("button, select, textarea").indexOf(node) >= 0){
			array.forEach(node.childNodes, function(n){
				highlight(n)
			});
		}
	}

	return this.forEach(function(n){
		highlight(n);
	});
}

/**
 * Small JavaScript module for the documentation.
 */
window.Documentation = {

	init : function(){
		this.fixFirefoxAnchorBug();
		this.highlightSearchWords();
		this.initModIndex();
	},

	/**
	* i18n support
	*/
	TRANSLATIONS : {},
	PLURAL_EXPR : function(n){ return n == 1 ? 0 : 1; },
	LOCALE : 'unknown',

	// gettext and ngettext don't access this so that the functions
	// can savely bound to a different name (_ = Documentation.gettext)
	gettext : function(string){
		var translated = Documentation.TRANSLATIONS[string];
		if(typeof translated == 'undefined') return string;
		return (typeof translated == 'string') ? translated : translated[0];
	},

	ngettext : function(singular, plural, n){
		var translated = Documentation.TRANSLATIONS[singular];
		if(typeof translated == 'undefined') return (n == 1) ? singular : plural;
		return translated[Documentation.PLURALEXPR(n)];
	},

	addTranslations : function(catalog){
		for(var key in catalog.messages){
			this.TRANSLATIONS[key] = catalog.messages[key];
		}
		this.PLURAL_EXPR = new Function('n', 'return +(' + catalog.plural_expr + ')');
		this.LOCALE = catalog.locale;
	},

	/**
	* add context elements like header anchor links
	*/
	addContextElements : function(){
		return;	
		$('div[id] > :header:first').each(function(){
			$('<a class="headerlink">\u00B6</a>')
				.attr('href', '#' + this.id)
				.attr('title', _('Permalink to this headline'))
				.appendTo(this)
			;
		});

		$('dt[id]').each(function(){
			$('<a class="headerlink">\u00B6</a>')
				.attr('href', '#' + this.id)
				.attr('title', _('Permalink to this definition'))
				.appendTo(this)
			;
		});
	},

	/**
	* workaround a firefox stupidity
	*/
	fixFirefoxAnchorBug : function(){
		if(document.location.hash && has("mozilla")) window.setTimeout(function(){
			document.location.href += '';
		}, 10);
	},

	/**
	* highlight the search words provided in the url in the text
	*/
	highlightSearchWords : function(){
		var params = doctools.getQueryParameters();
		var terms = (params.highlight) ? params.highlight[0].split(/\s+/) : [];
		if(terms.length){
			var body = query("body");
			window.setTimeout(function(){
				array.forEach(terms, function(t){
					body.highlightText(t.toLowerCase(), 'highlight');
				});
			}, 10);
			var n = domConst.toDom('<li class="highlight-link"><a href="javascript:Documentation.' + 'hideSearchWords()">' + _('Hide Search Matches') + '</a></li>');

			var nn = query(".sidebar .this-page-menu");
			console.warn(nn);
		//	domConst.place(n, query('.sidebar .this-page-menu')[0]);
		}
	},

	/**
	* init the modindex toggle buttons
	*/
	initModIndex : function(){
		var nodes = query('img.toggler').forEach(function(n){
			
			var shower = function(e){
				var src = domAttr.get(n, "src");
				var id = n.id.substr(7);
				
				console.log(query("tr.cg-" + id));
				
				if(src.substr(-9) == 'minus.png'){
					domAttr.set(n, "src", src.substr(0, src.length - 9) + 'plus.png');
				}else{
					domAttr.set(n, "src", src.substr(0, src.length - 8) + 'minus.png');
				}
			}
			
			on(n, "click", shower);
			style.set(n, "display", "");
			
			if(DOCUMENTATION_OPTIONS.COLLAPSE_MODINDEX){
				shower();
			}
		});
		
		if(nodes.length){
			console.log('need to fix initModIndex');
		}
		
		/* original code
		 var togglers = $('img.toggler').click(function(){
			var src = $(this).attr('src');
			var idnum = $(this).attr('id').substr(7);
			console.log($('tr.cg-' + idnum).toggle());
			if(src.substr(-9) == 'minus.png') $(this).attr('src', src.substr(0, src.length-9) + 'plus.png');
			else $(this).attr('src', src.substr(0, src.length-8) + 'minus.png');
		}).css('display', '');

		if(DOCUMENTATION_OPTIONS.COLLAPSE_MODINDEX){
		togglers.click();
	}*/
	},

	/**
	* helper function to hide the search marks again
	*/
	hideSearchWords : function(){
		query('.sidebar .this-page-menu li.highlight-link').fadeOut({ duration:300 }).play();
		query('span.highlight').removeClass('highlight');
	},

	/**
	* make the url absolute
	*/
	makeURL : function(relativeURL){
		return DOCUMENTATION_OPTIONS.URL_ROOT + '/' + relativeURL;
	},

	/**
	* get the current relative url
	*/
	getCurrentURL : function(){
		var path = document.location.pathname;
		var parts = path.split(/\//);
		array.forEach(DOCUMENTATION_OPTIONS.URL_ROOT.split(/\//), function(item){
			if(item == '..') parts.pop();
		});
		var url = parts.join('/');
		return path.substring(url.lastIndexOf('/') + 1, path.length - 1);
	}
};

// quick alias for translations
_ = Documentation.gettext;

ready(Documentation, "init");

return doctools;

});