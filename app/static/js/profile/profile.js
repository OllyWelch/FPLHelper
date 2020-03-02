$(document).ready(function() {
    var url = $(location).attr('href'),
    parts = url.split("/"),
    last_part = parts[parts.length-1];
    $.post('/get_user_posts', {
        username: last_part
    }).done(function(response) {
        $.each(response.posts, function(index, post) {
            $('#user_posts').append(get_post_html(post));
        });
        $.each(response.threads, function(index, thread) {
            $('.inner_col' + thread.id).append('<p>In <i>' + thread.name + '</i></p>');
        });
        if (Object.keys(response.posts).length > 3) {
            $('#show_more_posts').html('<button class="btn btn-md btn-default">Show more</button>')
            $('.post:visible').addClass('visible');
            $('.post.visible:lt(3)').addClass('active');
            $('.post').hide();
            $('.post.active').show();
            $('#show_more_posts').on('click', function(e) {
              e.preventDefault();
              var $rows = $('.post.visible');
              var lastActiveIndex = $rows.filter('.active:last').index();
              $rows.filter(':lt(' + (lastActiveIndex + 3) + ')').addClass('active');
              $('.post.active').show();
              if ($('.post.visible').length == $('.post.active').length){
                $('#show_more_posts').hide();
              };
            });
        };

    }).fail(function() {
        alert('failure')
    });
});