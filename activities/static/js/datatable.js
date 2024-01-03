$(function() {

    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////

    $('#data_table').DataTable({
            searching: false,
            pageLength: 10
        }
    );
    $('#data_table_list').DataTable({
            searching: true,
            pageLength: 25,
            columnDefs: [
                {
                    orderable: false,
                    targets: 1  // icon
                },
                {
                    targets: 0,
                    searchable: true,
                    visible: false
                }
            ],
            // order: [[11, 'asc']],
            processing: true,
            deferRender: true,
            initComplete: function () {
                this.api()
                    .columns('.head')
                    .every(function () {
                        let column = this;
                        let select = $('<select><option value=""></option></select>')
                            .appendTo($("#data_table_list thead tr:eq(1) th").eq(column.index()).empty())
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                column.search(val ? '^' + val + '$' : '', true, false).draw();
                            });
                        column
                            .data()
                            .unique()
                            .sort()
                            .each(function (d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>');
                            });
                    });
            }
        }
    );
})
