$(document).ready(function(){
    $('#info').hide();
    $('#moreTransfers').hide();
});

function get_recommended_transfers(srcElem) {
    $('.active').removeClass('active');
    $('#moreTransfers').hide();
    $('#recommended').hide();
    $('#new_team').hide();
    $('#new_score').hide();
    $(srcElem).html('<div>'
    +'<img src="/static/images/loading.gif" style="width:16px;height:16px">'
    +'Finding best transfers... This may take some time.'
    +'</div>');
    $.post('/tools/get_current_user_team_id', {
    }).done(function(response) {
        var team_id = response.team_id
        $.post('/tools/get_recommended_transfers', {
            team_id: team_id,
            n_trans: $('#nTrans').val()
        }).done(function(response) {
            $('#info').show();
            $('#moreTransfers').show();
            $('#recommended').show();
            $('#new_team').show();
            $('#new_score').show();
            $(srcElem).html('<a class="btn btn-default btn-md"'
            +' href="javascript:get_recommended_transfers(\'#submit\');">Get recommended transfers</a>');
            $('#recommended').html(response['recommended']);
            $('#recommended thead th:nth-child(1)').hide();
            $('#recommended thead th:nth-child(2)').hide();
            $('#recommended tbody tr').each(function(){
                $(this).addClass('row' + $(this).index() );
                $(this).attr("onclick", "get_new_team(" + $(this).index() + ")");
                $('td:nth-child(1)', this).addClass('out_id' + $(this).index() ).hide();
                $('td:nth-child(2)', this).addClass('in_id' + $(this).index() ).hide();
            });
            $('#recommended tbody tr').hide();
            $('#recommended tbody tr:lt(10)').addClass('active').show();
             $('#moreTransfers').on('click', function(e) {
              e.preventDefault();
              var $rows = $('#recommended tbody tr');
              var lastActiveIndex = $rows.filter('.active:last').index();
              $rows.filter(':lt(' + (lastActiveIndex + 10) + ')').addClass('active');
              $('#recommended tbody tr').hide();
              $('#recommended tbody tr.active').show();
              if ($('#recommended tbody tr.active').length == $('#recommended tbody tr').length){
                $('#moreTransfers').hide();
              };
            });
        }).fail(function() {
            $('#loading').text("Error");
        });
    }).fail(function() {
        $('#loading').text("Error");
    });
};