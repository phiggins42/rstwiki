var profile = {
	action: "release",
	basePath: "_static",
	releaseName: "trunk",
	copyTests: true,
	mini: false,
	cssOptimize: "comments.keepLines",
	optimize: "",
	layerOptimize: "closure",
	selectorEngine: "acme",

	packages:[{
		name: "dojo",
		location: "../dojo"
	},{
		name: "dijit",
		location: "../dijit"
	},{
		name: "dojox",
		location: "../dojox"
	},{
		name: "docs",
		location: "../docs"
	}],

	defaultConfig: {
		cdn: "//ajax.googleapis.com/ajax/libs/dojo/1.8.0/",
		hasCache:{
			"dojo-built": 1,
			"dojo-loader": 1,
			"dom": 1,
			"host-browser": 1,
			"config-selectorEngine": "acme"
		}
	},

	layers: {
		"docs/wiki": {
			include: []
		},
		"docs/guide": {
			include: []
		}
	},
	
	staticHasFeatures: {
		"dojo-firebug": 0,
		"host-browser": 1
	}
};