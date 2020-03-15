$(document).ready(function() {
    $('#see_more_posts').hide();
    $('#all_posts').click(function() {
        $('#all_posts').removeClass('btn-default');
        $('#all_posts').addClass('btn-primary');
        $('#threads').removeClass('btn-primary');
        $('#threads').addClass('btn-default');
        $('#show_threads').remove();
        $.post('/forum/get_all_posts', {
        }).done(function(response) {
            $('.post').removeClass('active');
            $('.post').removeClass('visible');
            $.each(response.posts, function(index, post) {
                $('#all_posts_div').append(get_post_html(post));
            });
            $.each(response.threads, function(index, thread) {
                $('.inner_col' + thread.id).append('<p>In <i>' + sanitize(thread.name) + '</i></p>');
            });
            $('#see_more_posts').show();
            $('.post:visible').addClass('visible');
            $('.post.visible:lt(5)').addClass('active');
            $('.post').hide();
            $('.post.active').show();
            $('#see_more_posts').on('click', function(e) {
              e.preventDefault();
              var $rows = $('.post.visible');
              var lastActiveIndex = $rows.filter('.active:last').index();
              $rows.filter(':lt(' + (lastActiveIndex + 5) + ')').addClass('active');
              $('.post.active').show();
              if ($('.post.visible').length == $('.post.active').length){
                $('#see_more_posts').hide();
              };
            });
            activate_user_popup();
        }).fail(function() {
            alert('fail');
        });
    });
    $('#threads').click(function() {
        location.reload();
    });
});

function get_posts(Id){
    $('#see_more_' + Id).html('<img src="/static/images/loading.gif">');
    $.post("/forum/get_thread_posts", {
        thread_id: Id
    }).done(function(response) {
        $('.post' + Id).remove();
        $('#see_more_' + Id).html('<p onclick="hide_posts(' + Id + ');"><b>Collapse</b><img style="width:15px;height:15px" src="/static/images/up_arrow.png"></p>');
        $.each(response.posts, function(index, post) {
            $('#posts_' + Id).append(get_post_html(post));
        });
        $('.post' + Id + ':visible').addClass('visible');
        $('.post' + Id + '.visible:lt(3)').addClass('active');
        $('.post' + Id).hide();
        $('.post' + Id + '.active').show();
        if (Object.keys(response.posts).length > 3) {
            $('#posts_' + Id).append('<button id="more_posts_' + Id + '" class="btn btn-md btn-default">See more</button>');
            $('#more_posts_' + Id).on('click', function(e) {
              e.preventDefault();
              var $rows = $('.post' + Id + '.visible');
              var lastActiveIndex = $rows.filter('.active:last').index();
              $rows.filter(':lt(' + (lastActiveIndex + 3) + ')').addClass('active');
              $('.post' + Id + '.active').show();
              if ($('.post' + Id + '.visible').length == $('.post' + Id + '.active').length){
                $('#more_posts_' + Id).hide();
              };
            });
        };
        activate_user_popup();
    }).fail(function() {
        $('#see_more_' + Id).html('');
        $('#posts_' + Id).html('<p>Error retrieving posts.</p>');
    });
};

function hide_posts(Id) {
    $('#see_more_' + Id).html('<p onclick="get_posts(' + Id + ');"><b>Show posts</b><img style="width:15px;height:15px" src="/static/images/down_arrow.png"></p>');
    $('#posts_' + Id + ' .post').remove();
    $('#posts_' + Id + ' button').remove();
};

function make_post(threadId) {
    $.post('/forum/make_post', {
        body: $('#post_textarea_' + threadId).val(),
        threadId: threadId
    }).done(function(response) {
        if (response['status'] == 1) {
            var nPosts = parseInt($('#count' + threadId).text());
            $('#count' + threadId).html((parseInt(nPosts) + 1) + ' post(s)');
            $('#posts_' + threadId).prepend(get_post_html(response.post));
            activate_user_popup();
        } else {
            alert('Please add some content to post first!');
        };
    }).fail(function() {
        alert('fail');
    });
};

function delete_thread(threadId) {
    $('#delete' + threadId).html('<br><br><div class="alert alert-warning"><b>Warning!</b> Deleting this thread will delete all associated posts!</div>'
    + '<button id="confirm" class="btn btn-md btn-primary">Confirm</button>')
    $('#confirm').on('click', function(e) {
        e.preventDefault();
        $.post('/forum/delete/thread', {
            thread_id: threadId
        }).done(function(response) {
            location.reload();
        }).fail(function () {
            location.reload();
        });
    });
};

function show_create_thread_form() {
    $('#createThreadButton').html($('#createThreadForm').html());
};
