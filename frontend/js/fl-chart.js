import $ from "jquery";
import * as bootstrap from 'bootstrap';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-moment';

const objectPop = function( object, propertyName ){
    let temp = object[propertyName];
    delete object[propertyName];
    return temp;
}  

$( document ).ready(
    function(){
        $( '.fl-chart' ).map(
            function( index, elem ){
                var data = JSON.parse($(elem).find("script").text());
                console.log("Found chart data: ", data)
                var id = $(elem).find( "script" ).attr( "id" )
                const visualization = objectPop( data, "visualization" );
                var canvas = $( '<canvas id="chartreport_' + id + '" class="animated fadeIn" height="150"></canvas>' );
                console.log(canvas, typeof(canvas))
                // var canvas = document.createElement( 'canvas' );
                // canvas.setAttribute("class", "animated fadeIn")
                // canvas.setAttribute("height", "150")
                $( elem ).find( "div.canvas-container" ).append(canvas);
                new Chart(
                    canvas,
                    data,
                )
            }
        );
    }
  );
  