var profile = (function(){
	var copyOnly = function(filename, mid){
		var list = {
			"docs/docs.profile":1,
			"docs/package.json":1
		};
		return (mid in list) || (/^docs\/resources\//.test(mid) && !/\.(css|html)$/.test(filename)) || /(png|jpg|jpeg|gif|tiff)$/.test(filename);
	};

	return {
		resourceTags: {
			copyOnly: function(filename, mid){
				return copyOnly(filename, mid);
			},

			amd: function(filename, mid){
				return !copyOnly(filename, mid) && /\.js$/.test(filename);
			}
		},

		trees:[
			[".", ".", /(\/\.)|(~$)/]
		]
	};
})();
