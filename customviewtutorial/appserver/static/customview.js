/* customview.js */

require([
    "/static/app/customviewtutorial/demoview.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/simplexml/ready!"
], function(DemoView, SearchManager) {

    // Create a custom view
    var customView = new DemoView({
        id: "mycustomview",
        managerid: "mysearch",
        el: $("#mycustomview")
    }).render();

    var mysearch = new SearchManager({
        id: "mysearch",
        preview: true,
        cache: true,
        search: "index=_internal | head 1000 | stats count by sourcetype"
    });

});