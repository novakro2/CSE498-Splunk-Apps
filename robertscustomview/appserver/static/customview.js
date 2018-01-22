/* customview.js */

require([
    "/static/app/robertscustomview/Chart.js-1.0.2/chart.js",
    "splunkjs/mvc",
    "underscore",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/textinputview",
    "splunkjs/mvc/simplexml/ready!"
], function( 
    // Keep these variables in the same order as the libraries above:
    chart,
    mvc,
    _,
    SearchManager, 
    TextInputView
) {

    // Create a text input for the number of artists to show
    var myTextBox = new TextInputView({
        id: "txtNum",
        value: mvc.tokenSafe("$headNum$"),
        default: "10",
        el: $("#txtNum")
    }).render();

    // Downloads per artist
    var mySearch = new SearchManager({
        id: "mysearch",
        preview: true,
        cache: true,
        search: mvc.tokenSafe("| inputlookup musicdata.csv | search bc_uri=/sync/addtolibrary* | stats count by artist_name | table artist_name, count | head $headNum$")
    });

    // Get the result data
    var myResults = mySearch.data("results");
    
    // When data changes...
    myResults.on("data", function() {
        // This is the data object (a wrapper) that contains the results
        console.log("Here is the data object: ", myResults.data());

        // This is the Backbone collection with the same results
        console.log("Here is the Backbone collection: ", myResults.collection());
        var chartLabels = [];
        var chartData = [];
        var maxDload = 0;

        // Get the number of rows and the results
        var numResults = myResults.data().rows.length; // Number of results
        var artistData = myResults.data().rows;        // The search results

        // Populate the chart (labels, data) with the search result data
        _.each(artistData, function(artistDatum, i) {
            // Use artist names as labels
            chartLabels[i] = artistDatum[0];
            // Use the number of downloads as the dataset
            chartData[i] = parseInt(artistDatum[1])+1;
            // Determine what the top download number is to set the chart scale
            if (chartData[i] > maxDload) {
                maxDload = chartData[i];
            }
        });

        // Set the radar chart data
        var radarChartData = {
            labels: chartLabels,
            datasets: [
                {
                    fillColor: "rgba(151,187,205,0.5)",
                    strokeColor: "rgba(151,187,205,1)",
                    pointColor: "rgba(151,187,205,1)",
                    pointStrokeColor: "#fff",
                    data: chartData
                }
            ]
        }

        // Set radar chart options if different from the default
        var radarOptions = {
            scaleOverride: true,
            scaleSteps: maxDload, // Set chart scale to top number of downloads
            scaleStepWidth: 1,
            scaleStartValue: 0,
            scaleShowLabels: true,
            scaleShowLabelBackdrop: false,
        }

        // Create the radar chart
        var myRadar = new Chart(document.getElementById("mychart").getContext("2d")).Radar(radarChartData,radarOptions);

    });

});