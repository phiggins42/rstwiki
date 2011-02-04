{
    
    action:"release",
    releaseName:"trunk",
    copyTests:true,
    mini:false,
    cssOptimize:"comments.keepLines",
    optimize:"shrinksafe",
    
    layers:[
        { 
            name:"../docs/wiki.js",
            dependencies:[
                "docs.wiki"
            ]
        }
    ],
    
    prefixes:[
        ["../dojo", "dojo"],
        ["../dijit", "dijit"],
        ["../dojox", "dojox"],
        ["../CodeGlass", "CodeGlass"],
        ["../docs", "docs"]
    ]
    
}