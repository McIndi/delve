window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        if (localStorage.getItem('sb|sidebar-toggle') == "true") {
            document.body.classList.add('sb-sidenav-toggled');
        }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            // document.body.classList.toggle('sb-sidenav-toggled');
            // localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.toggle('sb-sidenav-toggled'));
        });
    }

});

import "../scss/fl-base.scss";


import $ from "jquery";
import * as bootstrap from 'bootstrap';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-moment';
import JSZip from 'jszip';
// import pdfMake from 'pdfmake';
// import pdfFonts from 'pdfmake/build/vfs_fonts';
import DataTable from 'datatables.net-bs5';
import 'datatables.net-buttons';
import 'datatables.net-buttons-bs5';
import 'datatables.net-buttons/js/buttons.html5';
import 'datatables.net-searchpanes';
import 'datatables.net-searchpanes-bs5';
import 'datatables.net-searchbuilder';
import 'datatables.net-searchbuilder-bs5';
import 'datatables.net-rowreorder';
import 'datatables.net-rowreorder-bs5';
import 'datatables.net-colreorder';
import 'datatables.net-colreorder-bs5';

require( 'datatables.net-buttons/js/buttons.colVis.js' );
require( 'datatables.net-buttons/js/buttons.html5.js' );
require( 'datatables.net-buttons/js/buttons.print.js' );

DataTable.Buttons.jszip(JSZip);
// DataTable.Buttons.pdfMake(pdfMake);
// pdfMake.vfs = pdfFonts.pdfMake.vfs;


const objectPop = function( object, propertyName ){
  let temp = object[propertyName];
  delete object[propertyName];
  return temp;
}

function isJsonString(str) {
  try {
      JSON.parse(str);
  } catch (e) {
      return false;
  }
  return true;
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

var application = {

  init: async function(){
      // A lot of the application is driven by the following event handlers
      $( "form#queryForm" ).on(
          "submit",
          application.update_report,
      );

      $( "form#new_upload_form" ).on(
          "submit",
          application.save_file_upload,
      );

      $( "#saved_queries" ).on(
          "click",
          ".load-query",
          application.load_query,
      );

      $( "#saved_queries" ).on(
          "click",
          ".delete-query",
          application.delete_query,
      );

      $( "#local_contexts" ).on(
          "click",
          ".load-context",
          application.load_context,
      );
      
      $( "#local_contexts" ).on(
          "click",
          ".delete-context",
          application.delete_context,
      );

      $( "#file_uploads" ).on(
          "click",
          ".delete-file",
          application.delete_file,
      )
      
      $( "form#currentContextForm" ).on(
          "submit",
          application.save_current_context,
      );

      // Gather initial state
      application.saved_queries = application.retrieve_saved_queries();
      application.search_commands = application.retrieve_search_commands();
      application.local_contexts = application.retrieve_local_contexts();
      application.file_uploads = application.retrieve_file_uploads();

      // Initialize static query lookup table
      new DataTable( "#lookup-table" );

      // patching for JSON display colors
      var foregroundColor = $("#foreground-color").text();
      var backgroundColor = $("#background-color").text();

      $( ".json-string" ).css(
          {
              "color": "var(--bs-" + foregroundColor + ")"
          }
      )
      $( ".json-literal" ).css(
          {
              "color": "var(--bs-" + foregroundColor + ")"
          }
      )
      
  },

  create_spinner: function(){
      var el = $( "<div class='spinner-border text-primary' role='status'><span class='sr-only'>Loading...</span></div>" );
      return el
  },

  update_file_uploads: async function( response ){
      var response_json = await response.json();
    //   console.log(response_json)
      response_json = response_json.results.map(
          function( item ){
              // contextNode = $( "<div class='context-json'></div>" )
              // contextNode.jsonViewer(item.context)
              // item.context = contextNode.html()
              // JSON.stringify(item.context, null, 2);
              // item.load_button = "<a class='btn btn-primary load-context'>Load</a>"
              item.delete_button = "<a class='btn btn-danger delete-file' href='/api/files/" + item.id + "/'>Delete</a>"
              return item
          }
      )
    //   console.log(response_json)
      var file_uploads_table  = $( "<table style='width: 100%;' class='display compact table table-striped table-hover table-bordered table-sm'></table>" )

      $( "#file_uploads" ).empty();
      $( "#file_uploads" ).append(file_uploads_table)

      var table_options = {
          autowidth: false,
          columns: [
              {
                  title: "filename",
                  data: "title",
                  // width: "12.5%",
              },
              {
                  title: "delete_button",
                  data: "delete_button",
                  width: "25%",
              },
          ],
          data: response_json,
          layout: {
              topEnd: null,
              topStart: null,
              top: [
                  'pageLength',
                  'info',
                  'paging',
                  'search',
                ],
                bottom: [
                  'paging',
                ],
                bottomStart: null,
                bottomEnd: null,
          }
      }

    //   console.log(table_options);

      new DataTable(
          file_uploads_table,
          table_options,
      )
  },

  retrieve_file_uploads: async function(){
      const requestOptions = {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      };
      var response = await fetch("/api/files/", requestOptions)
          .then( application.update_file_uploads );
      return response
  },

  save_file_upload: async function( event ){
      event.preventDefault()
      var spinner = application.create_spinner()
      $( event.target ).parent().append(spinner)
      // console.log("HERE: ", requestOptions.body)
      // var title = $( "form#new_upload_form > input#id_title" ).val();
      // var content = $( "form#new_upload_form > input#id_content" ).val();
      var form_data = new FormData( document.getElementById( "new_upload_form" ) )
      // console.log("FORM DATA: ", form_data)
      const requestOptions = {
          method: "POST",
          headers: { 
              // "Content-Type": "multipart/form-data",
              "X-CSRFToken": getCookie("csrftoken"),

          },
          body: form_data,
      };
      var response = await fetch("/api/files/", requestOptions)
          .then( application.retrieve_file_uploads );
      spinner.remove()
      return response
  },

  update_saved_queries: async function( response ){
      var response_json = await response.json();
    //   console.log(response_json)
      response_json.results = response_json.results.map(
          function( item ){
              item.text = item.text.replace("\n", "<br />")
              // item.name = $( "<a href='"  "'>" )
              item.load_button = "<a class='btn btn-primary load-query'>Load</a>"
              item.delete_button = "<a class='btn btn-danger delete-query' href='/api/queries/" + item.id + "/'>Delete</a>"
              return item
          }
      )
    //   console.log(response_json)
      var query_table  = $( "<table style='width: 100%;' class='display compact table table-striped table-hover table-bordered table-sm'></table>" )

      $( "#saved_queries" ).empty();
      $( "#saved_queries" ).append(query_table)

      var table_options = {
          // columnDefs: [{ width: 200, targets: "_all" }],
          // fixedColumns: true,
          autowidth: true,
          columns: [
              {
                  title: "name",
                  data: "name",
                  // width: "25%",
              },
              {
                  title: "text",
                  data: "text",
                  // width: "50%",
              },
              {
                  title: "id",
                  data: "id",
                  // width: "25%",
              },
              {
                  title: "load_button",
                  data: "load_button",
                  // width: "25%",
              },
              {
                  title: "delete_button",
                  data: "delete_button",
                  // width: "25%",
              },
          ],
          data: response_json.results,
          layout: {
              topEnd: null,
              topStart: null,
              top: [
                  'pageLength',
                  'info',
                  'paging',
                  'search',
                ],
                bottom: [
                  'paging',
                ],
                bottomStart: null,
                bottomEnd: null,
          }
      }

    //   console.log(table_options);

      new DataTable(
          query_table,
          table_options,
      )


  },

  retrieve_saved_queries: async function(){
      const requestOptions = {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      };
      var response = await fetch("/api/queries/", requestOptions)
          .then( application.update_saved_queries );
      return response
  },

  update_search_commands: async function( response ){
      var response_json = await response.json();
    //   console.log(response_json)
      response_json = response_json.map(
          function( item ){
              item.help = item.help.replace("\n", "<br />") + "<br />"
              return item
          }
      )
    //   console.log(response_json)
      var search_command_table  = $( "<table style='width: 100%;' class='display compact table table-striped table-hover table-bordered table-sm'></table>" )

      $( "#search_commands" ).empty();
      $( "#search_commands" ).append(search_command_table)

      var table_options = {
          // columnDefs: [{ width: 200, targets: "_all" }],
          // fixedColumns: true,
          autowidth: false,
          columns: [
              {
                  title: "name",
                  data: "name",
                  width: "12.5%",
              },
              // {
              //     title: "prog",
              //     data: "prog",
              //     // width: "50%",
              // },
              // {
              //     title: "description",
              //     data: "description",
              //     width: "12.5%",
              // },
              // {
              //     title: "usage",
              //     data: "usage",
              //     width: "12.5%",
              // },
              {
                  title: "help",
                  data: "help",
                  width: "50%",
              },
          ],
          data: response_json,
          layout: {
              topEnd: null,
              topStart: null,
              top: [
                  'pageLength',
                  'info',
                  'paging',
                  'search',
                ],
                bottom: [
                  'paging',
                ],
                bottomStart: null,
                bottomEnd: null,
          }
      }

    //   console.log(table_options);

      new DataTable(
          search_command_table,
          table_options,
      )
  },

  retrieve_search_commands: async function(){
      const requestOptions = {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      };
      var response = await fetch("/api/search_commands/", requestOptions)
          .then( application.update_search_commands );
      return response
  },

  update_local_contexts: async function( response ){
      var response_json = await response.json();
    //   console.log(response_json)
      response_json = response_json.results.map(
          function( item ){
              // contextNode = $( "<div class='context-json'></div>" )
              // contextNode.jsonViewer(item.context)
              // item.context = contextNode.html()
              // JSON.stringify(item.context, null, 2);
              item.load_button = "<a class='btn btn-primary load-context'>Load</a>"
              item.delete_button = "<a class='btn btn-danger delete-context' href='/api/locals/" + item.id + "/'>Delete</a>"
              return item
          }
      )
    //   console.log(response_json)
      var local_contexts_table  = $( "<table style='width: 100%;' class='display compact table table-striped table-hover table-bordered table-sm'></table>" )

      $( "#local_contexts" ).empty();
      $( "#local_contexts" ).append(local_contexts_table)

      var table_options = {
          autowidth: false,
          columns: [
              {
                  title: "name",
                  data: "name",
                  width: "12.5%",
              },
              {
                  title: "id",
                  data: "id",
                  width: "50%",
              },
              {
                  title: "context",
                  data: "context",
                  width: "50%",
                  render: function (data, type, row, meta)  {
                      return JSON.stringify(data);
                  },
              },
              {
                  title: "load_button",
                  data: "load_button",
                  width: "25%",
              },
              {
                  title: "delete_button",
                  data: "delete_button",
                  width: "25%",
              },
          ],
          data: response_json,
          layout: {
              topEnd: null,
              topStart: null,
              top: [
                  'pageLength',
                  'info',
                  'paging',
                  'search',
                ],
                bottom: [
                  'paging',
                ],
                bottomStart: null,
                bottomEnd: null,
          }
      }

    //   console.log(table_options);

      new DataTable(
          local_contexts_table,
          table_options,
      )
  },

  show_alert: function( message ){
      var outer_div = $( "<div class='text-center'></div>" );
      var inner_div = $( "<div class='alert alert-info alert-dismissible fade show' role='alert'>" + message + "<button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button></div>" );
      outer_div.append( inner_div );
      $( "#layoutSidenav_content > main:nth-child(1) > div:nth-child(1)" ).prepend( outer_div );
      window.scrollTo( 0, 0 );
  },

  retrieve_local_contexts: async function(){
      const requestOptions = {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      };
      var response = await fetch("/api/locals/", requestOptions)
          .then( application.update_local_contexts );
      return response
  },

  load_context: async function( event ){
      var spinner = application.create_spinner()
      var target = $( event.target );
      target.parent().append( spinner )
      var parent = target.parent().parent();
      // console.log( "found parent: ", parent );
      var name = parent.find( "td" ).eq( 0 ).text();
      var id = parent.find( "td" ).eq( 1 ).text();
      var context = parent.find( "td" ).eq( 2 ).text();
    //   console.log( "found name: ", name );
    //   console.log( "found context: ", context );

      $( "form#currentContextForm > div > textarea#id_context" ).val( JSON.stringify(JSON.parse(context), null, 2) );
      $( "form#currentContextForm > div > input#id_name" ).val( name );
      spinner.remove();
  },

  save_current_context: async function( event ){
      event.preventDefault()
      // console.log("HERE: ", requestOptions.body)
      var context = $( "form#currentContextForm > div > textarea#id_context" ).val();
      context = JSON.parse(context);
      var name = $( "form#currentContextForm > div > input#id_name" ).val();
      const requestOptions = {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              'X-CSRFToken': getCookie("csrftoken"),
          },
          body: JSON.stringify(
              {
                  name: name,
                  context: context,
              }
          ),
      };
      var response = await fetch("/api/locals/", requestOptions)
          .then( application.retrieve_local_contexts );
      return response
  },

  delete_context: async function( event ){
      event.preventDefault();
      var spinner = application.create_spinner()
      // console.log( "found event: ", event );
      var target = $( event.target )[0];
      $( event.target ).parent().append( spinner );
      var href = target.href;
      const requestOptions = {
          method: "DELETE",
          headers: {
              "Content-Type": "application/json",
              'X-CSRFToken': getCookie("csrftoken"),
          },
      };

      var response = await fetch(
          href,
          requestOptions,
      ).then( application.retrieve_local_contexts )
    //   console.log(target.href)
      spinner.remove()
  },

  delete_file: async function( event ){
      event.preventDefault();
      var spinner = application.create_spinner()
      var target = $( event.target )[0];
      $( event.target ).parent().append( spinner );
      var href = target.href;
      const requestOptions = {
          method: "DELETE",
          headers: {
              "Content-Type": "application/json",
              'X-CSRFToken': getCookie("csrftoken"),
          },
      };

      var response = await fetch(
          href,
          requestOptions,
      ).then( application.retrieve_file_uploads )
    //   console.log(target.href)
      spinner.remove()
  },

  delete_query: async function( event ){
      event.preventDefault();
      // console.log( "found event: ", event );
      var target = $( event.target )[0];
      var href = target.href;
      const requestOptions = {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': getCookie("csrftoken")
          },
      };

      var response = await fetch(
          href,
          requestOptions,
      ).then( application.retrieve_saved_queries )
    //   console.log(target.href)
  },

  load_query: async function( event ){
      event.preventDefault();
      // console.log( "found event: ", event );
      var target = $( event.target );
      var parent = target.parent().parent();
      // console.log( "found parent: ", parent );
      var name = parent.find( "td" ).eq( 0 ).text();
      var text = parent.find( "td" ).eq( 1 ).html().replace("<br>", "\n");
    //   console.log( "found text: ", text )

      $( "form#queryForm > div > textarea#id_text" ).val( text )
      $( "form#queryForm > div > input#id_name" ).val( name )
      $( "form#queryForm > div > input#id__save" ).attr('checked', false)
      application.show_alert( "Successfully loaded Query." );
  },

  update_report: async function( event ){
      event.preventDefault()
      // console.log("HERE: ", requestOptions.body)
      event = $( event.target )
      var spinner = application.create_spinner()
      event.parent().append(spinner);
      application.data = await application.resolve_query( event );
    //   console.log("application.data", application.data)
      await application.redrawResult( event );
      await application.retrieve_saved_queries();
      $( "form#queryForm > div > input#id__save" ).attr('checked', true)
      spinner.remove()
  },

  resolve_query: async function( event ){
      var name = $( "form#queryForm > div > input#id_name" ).val()
      var text = $( "form#queryForm > div > textarea#id_text" ).val()
      var currentContext = $( "form#currentContextForm > div > textarea#id_context" ).val()
      var contextIsJson = isJsonString(currentContext)
      if (contextIsJson!=true){
          currentContext = "{}";
      }
      var _save = $( "form#queryForm > div > div > input#id__save" ).prop( "checked" )
    //   console.log("name: ", name)
    //   console.log("text: ", text)
    //   console.log("_save: ", _save)
      const requestOptions = {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              'X-CSRFToken': getCookie("csrftoken"),
          },
          body: JSON.stringify(
              {
                  text: text,
                  name: name,
                  local_context: currentContext,
                  _save: _save,
              }
          ),
      };
      var response = await fetch("/api/query/", requestOptions)
          .then(response => response.json());
      return response
  },

  redrawResult: async function( event ){
      $( "#report" ).empty();
      switch ( typeof application.data ){
          case "undefined":
            //   console.log( "We found an Undefined!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "string":
            //   console.log( "We found a String!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "number":
            //   console.log( "We found a Number!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "bigint":
            //   console.log( "We found a BigInt!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "boolean":
            //   console.log( "We found a Boolean!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "symbol":
            //   console.log( "We found a Symbol!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "function":
            //   console.log( "We found a Function!!" );
              $( "#report" ).html( "<h1>" + application.data + "</h1>" )
              break;
          case "object":
              if ( Array.isArray( application.data ) ){
                //   console.log( "We found an Array!!" );
                  switch ( typeof application.data[0] ){
                      case "undefined":
                        //   console.log( "We found an undefined!!" );
                          await application.draw_list_of_values();
                          break;
                      case "object":
                          if ( Array.isArray( application.data[0] ) ){
                              await application.draw_list_of_lists();
                              break;
                          } else if ( application.data[0] === null ) {
                              await application.draw_list_of_values();
                              break;
                          } else {
                              await application.draw_generic_table();
                              break;
                          }
                      case "string":
                        //   console.log( "We found a String!!" );
                          await application.draw_list_of_values();
                          break;
                      case "number":
                        //   console.log( "We found a Number!!" );
                          await application.draw_list_of_values();
                          break;
                      case "bigint":
                        //   console.log( "We found a BigInt!!" );
                          await application.draw_list_of_values();
                          break;
                      case "boolean":
                        //   console.log( "We found a Boolean!!" );
                          await application.draw_list_of_values();
                          break;
                  }
              } else if ( application.data === null ){
                //   console.log( "We found an null!!" );
                  break;
              } else {
                //   console.log( "We found an Object!!" , application.data);
                  const visualization = objectPop( application.data, "visualization" );
                //   console.log( "Found visualization: " + visualization );
                  switch ( visualization ) {
                      case "chartjs":
                          await application.draw_chart();
                          break;
                      case "table":
                          await application.draw_table();
                          break;
                      case undefined:
                          application.data = [application.data]
                          await application.draw_generic_table();
                  }
              }
      }
  },

  draw_list_of_values: async function( event ){
      var list  = $( "<ul class='list-group'></ul>" );
      $( "#report" ).append(list);
    //   console.log(application.data)
      if ( application.data.length === 0 ) {
          list.append( $( "<li>No Data</li>" ) )
      } else {
          $.each(
              application.data,
              function( index, value ){
                //   console.log("List: " + list)
                //   console.log("Index: " + index)
                //   console.log("Value: " + value)
                  var item = $( "<li class='list-group-item'>" + value + "</li>" )
                  list.append(item);
              },
          )    
      }
  },

  draw_list_of_lists: async function ( event ){
      var table  = $( "<table class='display compact table table-striped table-hover table-bordered table-sm'></table>" );
    //   console.log( "Table: " + table )
      $( "#report" ).append( table );
      $.each(
          application.data,
          function ( index, row ){
              var table_row = $( "<tr></tr>" );
              table.append( table_row );
              $.each(
                  row,
                  function( index, item ){
                      item = $( "<td>" + item + "</td>" );
                      table_row.append( item )
                  }
              )
          }
      )
  },

  draw_chart: async function( event ){
    //   console.log("Drawing chart");
      var canvas = $( '<canvas id="chartreport" class="animated fadeIn" height="150"></canvas>' );
      $( "#report" ).append(canvas);
    //   console.log("Creating chart with following data: \n", application.data)
      new Chart(
          canvas,
          application.data,
      )
  },

  draw_table: async function( event ){
      var table  = $( "<table class='display compact table table-striped table-hover table-bordered table-sm'></table>" )
      $( "#report" ).append( table )
      new DataTable(
          table,
          application.data
      )
  },

  draw_generic_table: async function( event ){
      var table  = $( "<table class='display w-100 table table-striped table-hover table-bordered table-sm'></table>" )
      $( "#report" ).append( table )

      var columns = new Set()                            
      application.data.map(
          ( item ) => Object.keys(item).map(
              ( _item ) => columns.add(_item)
          )
      )

      columns = Array.from(columns)
      columns = columns.map(
          ( item ) => (
              {
                  title: item,
                  data: item,
                  render: function (data, type, row, meta)  {
                    data = JSON.stringify(data);
                    // console.log(data)
                    data = data.replace( /</g, '&lt;' );
                    // console.log(data)
                    data = data.replace( />/g, '&gt;' );
                    // console.log(data)
                    data = data.replace( /&/g, '&amp;' );
                    // console.log(data)
                    return data
                  },
              }
          )
      )

      // var data = []
      // $.each( application.data, function( index, item ){
      //     var _item = {} 
      //     $.each( item, function( k, v ){
      //         _item[k] = JSON.stringify(v)
      //     } )
      //     data.push(_item)
      // } )
      new DataTable(
          table,
          {
              columns: columns,
              data: application.data,
              autowidth: true,
              colReorder: true,
              // rowReorder: true,
              order: [],
              columnDefs: [
                  {
                      targets: "_all",
                      className: 'dt-body-left'
                  }
              ],
              layout: {
                  topEnd: null,
                  topStart: {
                      buttons: [
                          'colvis',
                          'print',
                          'copy',
                          'csv',
                          'excel',
                          {
                              text: 'JSON',
                              action: function (e, dt, button, config) {
                                  var data = dt.buttons.exportData();
              
                                  DataTable.fileSave(new Blob([JSON.stringify(data)]), 'Export.json');
                              },
                          },
                      ]
                  },
                  top: [
                      'pageLength',
                      'info',
                      'paging',
                      'search',
                    ],
                    bottom: [
                      'paging',
                    ],
                    bottomStart: null,
                    bottomEnd: null,
              }
              //         buttons: [
              //             {
              //                 text: 'JSON',
              //                 action: function (e, dt, button, config) {
              //                     var data = dt.buttons.exportData();
              
              //                     DataTable.fileSave(new Blob([JSON.stringify(data)]), 'Export.json');
              //                 },
              //             },
              //         ],
              //     },
              // },
          },
      )
  },
}
$( document ).ready(
  function(){
      application.init();
  }
);

