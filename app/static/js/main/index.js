$(document).ready(function(){
    $('#no_results_div').hide();
    $('#buttons').hide();
    $('#filters').hide();
    $.post('/index-predictions', {
    }).done(function(response) {
        $('#loading_predictions').hide();
        $('#inside_table_div').html(response['predictions']);
        $('#main_heading').html('<h1>Explore Player Predictions for Gameweek ' + response['gameweek'] + ':</h1>');
        $('#filters').show();
        $('#buttons').show();
        const cols = [1, 2, 3, 4, 5, 6, 7];
        $.each(cols, function() {
            $('#index_table td:nth-child(' + this + ')').addClass('col' + this);
            $('#index_table th:nth-child(' + this + ')').append(
            '<p><a id="link' + this + '"><img id="img' + this + '" src="/static/images/down_arrow.png" '
            +'style="width:15px;height:15px;" align="center"></a></p>' );
            $('#link' + this).attr("href", "javascript:get_sorted_table('#link" + this + "', " + this + ");" );
        });
        $('#index_table tbody tr:visible').addClass('visible');
        $('#index_table tbody tr.visible:lt(10)').addClass('active');
        $('#index_table tbody tr').hide();
        $('#index_table tbody tr.active').show();
        $('#moreRows').on('click', function(e) {
              e.preventDefault();
              var $rows = $('#index_table tbody tr.visible');
              var lastActiveIndex = $rows.filter('.active:last').index();
              $rows.filter(':lt(' + (lastActiveIndex + 5) + ')').addClass('active');
              $('#index_table tbody tr').hide();
              $('#index_table tbody tr.active').show();
              if ($('#index_table tbody tr.visible').length == $('#index_table tbody tr.active').length){
                $('#moreRows').hide();
              };
            });
        $('select.filter').change(function() {
            $('#index_table tbody tr.active').removeClass('active');
            $('#index_table tbody tr.visible').removeClass('visible');
            $('#no_results_div').hide();
            $('#table_div').show();
            $('#moreRows').show();
            $("#index_table td.col1:contains('" + $('#position_filter').val() + "')").parent().show();
            $("#index_table td.col2:contains('" + $('#team_filter').val() + "')").parent().show();
            $("#index_table tbody tr").filter(function(){
                return parseFloat($(this).find('td.col5').html()) < $('#min_price_filter').val();
            }).hide()
            $("#index_table tbody tr").filter(function(){
                return parseFloat($(this).find('td.col5').html()) > $('#max_price_filter').val();
            }).hide()
            $("#index_table td.col1:not(:contains('" + $('#position_filter').val() + "'))").parent().hide();
            $("#index_table td.col2:not(:contains('" + $('#team_filter').val() + "'))").parent().hide();
            if ($('#index_table tbody tr:visible').length == 0){
                $('#no_results_div').show();
                $('#table_div').hide();
            }
            $('#index_table tbody tr:visible').addClass('visible');
            $('#index_table tbody tr.visible:lt(10)').addClass('active');
            $('#index_table tbody tr').hide();
            $('#index_table tbody tr.active').show();
        });
        $("#toTop").click(function () {
            $("html, body").animate({scrollTop: 0}, 500);
    });
    }).fail(function() {
        $('#loading_predictions').hide();
        $('#main_heading').html('<h1>Error retrieving predictions</h1>');
    });

});