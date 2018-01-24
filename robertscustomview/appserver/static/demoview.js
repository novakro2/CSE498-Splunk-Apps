/* demoview.js */

define(function(require, exports, module){
    // Base class for custom views
    var SimpleSplunkView = require('splunkjs/mvc/simplesplunkview');

    // Require Underscore.js to work with a list of search results
    var _ = require("underscore");

    // Define the custom view class
    var DemoView = SimpleSplunkView.extend({
        className: "demoview",

        // Change the value of the "data" property
        options: {
            data: "results"
        },

        // Override this method to format your data in a specific way
        // Our view expects HTML, so reformat the results array accordingly
        formatData: function(data) {
            // Display the data object to the console
            console.log("The data object: ", data);
            var mydatastring = "";

            // Format each row of results as an HTML list
            _.each(data, function(row, index){
                mydatastring = mydatastring + "<li><b>" + row[0] + "</b>:  " + row[1] + "</li>";
            });

            // Wrap the string with the unordered list tag
            mydatastring = "<ul>" + mydatastring + "</ul>";
            return mydatastring;
        },

        // Override this method to configure your view
        createView: function() {
            return this;
        },

        // Override this method to put the Splunk data into the view
        updateView: function(viz, data) {
            // Display the reformatted data object to the console
            console.log("HTML-formatted data: ", data);
            this.$el.html("Count by sourcetype:" + data);
        }
    });

    return DemoView;

});