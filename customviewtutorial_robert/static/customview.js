/* customview.js */

/* customview.js */

require([
    "/static/app/customviewtutorial/demoview.js",
    "splunkjs/mvc/simplexml/ready!"
], function(DemoView) {

    // Create a custom view
    var customView = new DemoView({
        id: "mycustomview",
        el: $("#mycustomview")
    }).render();

});