dependencies = {
    
    action:"release",
    version: "0.0.0-" + (+new Date()),
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
        },

        {
            name:"../docs/guide.js",
            dependencies:[
                "docs.guide"
            ]
        }
    ],

    
    prefixes:[
        ["dijit", "../dijit"],
        ["dojox", "../dojox"],
        ["docs", "../docs"]
    ]
    
}