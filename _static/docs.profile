dependencies = {
    
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
        ["dijit", "../dijit"],
        ["dojox", "../dojox"],
        ["CodeGlass", "../CodeGlass"],
        ["CodeMirror", "../CodeMirror"],
        ["docs", "../docs"]
    ]
    
}