import $ from "jquery";

import JSZip from 'jszip';
// import pdfMake from 'pdfmake';
// import pdfFonts from 'pdfmake/build/vfs_fonts';
// import DataTable from 'datatables.net-bs5';
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

$( document ).ready(
    function(){
        $( '.fl-table' ).DataTable(
            {
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
            }
        );
    }
  );
  