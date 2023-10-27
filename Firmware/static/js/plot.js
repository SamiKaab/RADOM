// app.js

var xData = [];
var yData = [];
// Initialize an array to keep track of the colors for each bar
var barColors = [];
var plotlyChart;

// Create an initial empty Plotly chart
var layout = {
    title: 'Sensor Data',
    // set font of title
    font: {
        family: 'calibri',
        size: 24
    },
    xaxis: {
        title: 'Time',
    },
    yaxis: {
        title: 'Height (mm)',
    },
    //annotations
    annotations: [
        {
            x: 0.5,
            y: 1.1,
            xref: 'paper',
            yref: 'paper',
            text: 'The height of the bar corresponds to the table height and the color of the bar corresponds to the presence of a person (blue = present, grey = not present)',
            showarrow: false,
            
        }
    ],

};
// remove all the buttons from the graph
var config = {
    modeBarButtonsToRemove: [
        'toImage', 
        'sendDataToCloud',
        'pan2d', 
        'select2d', 
        'lasso2d', 
        'zoomIn2d', 
        'zoomOut2d', 
        'autoScale2d', 
        'resetScale2d', 
        'hoverClosestCartesian', 
        'hoverCompareCartesian',
        'zoom2d',
        // toggle spike lines on hover
        'toggleSpikelines',
        // produced by plotly button


    ],
    editable: false, // remove all mouse interaction
    dragmode: false, // remove all mouse interaction
    displaylogo: false // remove "Produced with Plotly" button


  };

function updateTitleFontSize() {
    var windowWidth = window.innerWidth;

    // You can adjust the font size based on the window width as per your requirements
    var titleFontSize = 18 * (windowWidth / 1200); // Adjust 1200 to your desired breakpoint
    var plotWidth = windowWidth // Adjust 800 and 50 to your desired values

    var layout = {
        title: 'Sensor Data',
        font: {
            family: 'calibri',
            size: titleFontSize
        },
        xaxis: {
            title: 'Time',
        },
        yaxis: {
            title: 'Height (mm)',
        },
        annotations: [
            {
                x: 0.5,
                y: 1.1,
                xref: 'paper',
                yref: 'paper',
                text: 'The height of the bar corresponds to the table height and the color of the bar corresponds to the presence of a person (blue = present, grey = not present)',
                showarrow: false,
            }
        ],
        width: plotWidth,
    };

    // Update the chart layout with the adjusted font size
    Plotly.update('plotly-chart', {}, layout);
}

// Add an event listener to adjust title font size when the window resizes
window.addEventListener('resize', updateTitleFontSize);
// ...
plotlyChart = Plotly.newPlot('plotly-chart', [{
    x: xData,
    y: yData,
    // bar chart
    type: 'bar',
    mode: 'lines+markers',
}], layout, config);

var sampling_period = 1000;
var recording  = false;
// a function to update the graph: takes in barcolors, xdata, ydata
function updateGraph() {
    fetch('/get_device_info', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        sampling_period = data.SP * 1000;
        if (data.STATUS === "Not Recording") {
            recording = false;
        }
        else if (data.STATUS === "Recording") {
            recording = true;
        }

    })
    .catch(error => {
        console.error('Error fetching device info:', error);
    }   
    );

    if (recording == true) {
        fetch('/update_data', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        .then(response => response.json())
        .then(data => {
            //iterate over data.presence if presence is true, set color to green, else red
            for (var i = 0; i < data.presence.length; i++) {
                if (data.presence[i] == true) {
                    barColors[i] = '#5699b1';
                } else {
                    barColors[i] = '#C1c1c1';
                }
            }
            
            xData = data.datetime;
            yData = data.distance

            // Update the chart with the new data and colors
            Plotly.update('plotly-chart', {
                x: [xData],
                y: [yData],
                'marker.color': [barColors],
            },config);
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
        });
    }
    // sleep for sampling period
    setTimeout(updateGraph, sampling_period);

}

updateGraph();