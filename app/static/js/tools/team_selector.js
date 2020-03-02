$(document).ready(function(){
    $('#not_right').hide();
    $('#table').html('<img src="/static/images/loading.gif" style="width:16px;height:16px">');
    $.post('/tools/predictions', {
        }).done(function(response) {
            $('#top_heading').html('<h3>Squad expected points for ' + response['squadName'] + ' for Gameweek ' + response['gameweek'] + ':</h3>');
            $('#table').html(response['squadPredictions']);
            $('#heading').html('<img src="/static/images/loading.gif" style="width:16px;height:16px">');
            $.post('/tools/get_optimal_team', {
                team: $('#table').html()
            }).done(function(response) {
                $('#heading').html('<h3>Optimal Expected Score: ' + response['best_score'] + '</h3><br>');
                $('#tableId').html(response['best_team']);
                $('#not_right').show();
            }).fail(function() {
                $('#heading').html('<p>Failed to find optimal team</p>');
            });
        }).fail(function() {
            $('#top_heading').text("Error");
        });
});