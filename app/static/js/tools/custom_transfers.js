$(document).ready(function(){
    $('#out_table').html('<img src="/static/images/loading.gif" style="width:16px;height:16px">');
    $('#transfers_in').click(function() {
        location.reload();
    });
    $('#transfers_out').click(function() {
        $('#transfers_in').removeClass('btn-primary');
        $('#transfers_in').addClass('btn-default');
        $('#transfers_out').removeClass('btn-default');
        $('#transfers_out').addClass('btn-primary');
        $.post('/tools/get_custom_transfers', {
        }).done(function(response) {
            $('.make').hide();
            $('#transfers_table').html(response['transfers']);
            if (response['transfers'] != '<h4>No custom transfers made.</h4><br>'){
                $('#remove').html('<button class="btn btn-lg btn-default" id="reset">Reset all transfers</button>')
                $('#reset').click(function() {
                    $.post('/tools/reset_transfers', {
                    }).done(function() {
                        location.reload();
                    }).fail(function() {
                        alert('Transfer reset failed.');
                    });
                });
            };
        }).fail(function() {
            alert('fail');
        });
    });
    $.post('/tools/predictions', {
        }).done(function(response) {
            $('#out_table').html(response['squadPredictions']);
            $('#out_table tbody tr').each(function(){
                $(this).addClass('row' + $(this).index() );
                $(this).attr("onclick", "record_player_out(" + $(this).index() + ")");
            });
        }).fail(function() {
            $('#table').text("Error");
        });
});

function record_player_out(row){
    firstName = $('#out_table tbody tr.row' + row + ' td:nth-child(2)').html();
    secondName = $('#out_table tbody tr.row' + row + ' td:nth-child(3)').html();
    $('#out').html('<h4>OUT: ' + firstName + ' ' + secondName + '</h4>')
    $('#out_table').hide();
    $('#choose_in_out').html('<h4>Choose player to transfer in:</h4>')
    $('#in_table').html('<img src="/static/images/loading.gif" style="width:16px;height:16px">');
    $.post('/tools/get-valid-transfers', {
        row: row
    }).done(function(response) {
        $('#in_table').html(response['validPlayers']);
        $('#in_table tbody tr:visible').addClass('visible');
        $('#in_table tbody tr.visible:lt(10)').addClass('active');
        $('#in_table tbody tr').hide();
        $('#in_table tbody tr.active').show();
        $('#show_more').html('<button class="btn btn-default btn-md">Show more</button>');
        $('#in_table thead th:nth-child(1)').remove();
        $('#in_table thead tr:nth-child(2)').remove();
        $('#in_table tbody tr').each(function(){
            $(this).attr("onclick", "record_transfer(" + response['out_id'] + "," + $(this).children('th').html() + ",'" + $(this).children('td:nth-child(4)').html() + "','" + $(this).children('td:nth-child(5)').html() + "')");
            $(this).children('th').remove();
        });
        $('#show_more').on('click', function(e) {
          e.preventDefault();
          var $rows = $('#in_table tbody tr.visible');
          var lastActiveIndex = $rows.filter('.active:last').index();
          $rows.filter(':lt(' + (lastActiveIndex + 20) + ')').addClass('active');
          $('#in_table tbody tr').hide();
          $('#in_table tbody tr.active').show();
          if ($('#in_table tbody tr.visible').length == $('#in_table tbody tr.active').length){
            $('#moreRows').hide();
          };
        });
    }).fail(function() {
        alert('Failure.');
    });
};

function record_transfer(out_id, in_id, in_first_name, in_second_name){
    $('#in').html('<h4>IN: ' + in_first_name + ' ' + in_second_name + '</h4>');
    $('#in_table').hide();
    $('#choose_in_out').hide();
    $('#show_more').hide();
    $('#confirm').html('<button class="btn btn-md btn-default" id="confirm_button">Confirm</button>');
    $('#cancel').html('<button class="btn btn-md btn-default">Cancel</button>');
    $('#cancel').click(function() {
        location.reload();
    });
    $('#confirm').attr('onclick', 'add_to_db(' + out_id + ',' + in_id + ')');
};

function add_to_db(out_id, in_id){
    $.post('/tools/add_transfer', {
        out_id: out_id,
        in_id: in_id
    }).done(function(response) {
        location.reload();
    }).fail(function() {
    });
};