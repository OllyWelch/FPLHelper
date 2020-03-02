$(document).ready(function() {
    $.post('/get_notifications', {
    }).done(function(response) {
        if (response.new_notifications.length > 0 | response.old_notifications.length > 0) {
            $('#new_notifications').append('<button class="btn btn-md btn-default" onclick="clear_notifications();">Clear all</button><hr>')
        };
        if (response.new_notifications.length > 0) {
            $('#new_notifications').append('<h2>New Notifications</h2><br>')
            $.each(response.new_notifications, function(index, notification) {
                $('#new_notifications').append(new_notification_html(index, notification));
            });
        } else {
            $('#new_notifications').append('<p>No new notifications.</p><hr>');
        };
        if (response.old_notifications.length > 0) {
            $('#old_notifications').append('<h2>Older</h2><br>')
            $.each(response.old_notifications, function(index, notification) {
                $('#old_notifications').append(new_notification_html(index, notification));
            });
            if (response.old_notifications.length > 3) {
                $('#old_notifications').append('<button id="show_more" class="btn btn-md btn-default">Show more</button>');
                $('#old_notifications .n:visible').addClass('visible');
                $('#old_notifications .n.visible:lt(3)').addClass('active');
                $('#old_notifications .n.visible').hide();
                $('#old_notifications .n.active').show();
                $('#show_more').on('click', function(e) {
                    e.preventDefault();
                    var $rows = $('#old_notifications .n.visible');
                    var lastActiveIndex = $rows.filter('#old_notifications .active:last').index();
                    $rows.filter(':lt(' + (lastActiveIndex + 3) + ')').addClass('active');
                    $('#old_notifications .n').hide();
                    $('#old_notifications .n.active').show();
                    if ($('#old_notifications .n.visible').length == $('#old_notifications .n.active').length){
                        $('#show_more').hide();
                    };
                });
            };
        } else {
            $('#old_notifications').append('<p>No older notifications.</p><hr>');
        };
        activate_user_popup();
    }).fail(function() {
        alert('fail')
    });
});

function new_notification_html(index, notification) {
    if (notification['name'] == 'new_post'){
        return '<div class="n"><div class="row"><div class="col col-md-1"><img src="' + notification.data['avatar'] + '" class="img'
         + ' img-thumbnail img-responsive"></div>'
    + '<div class="col col-md-4"><p><i>New post: ' + moment(notification.time).fromNow() + '</i></p>'
    + '<p><span class="user_popup"><a href="/profile/' + notification.data['author_username'] + '">'
     + notification.data['author_username'] + '</a></span> posted in ' + notification.data['thread_name'] + ':</p>'
     + '<p>"' + notification.data['post_body'] + '"</p></div></div><hr></div>'
    } else {
        return '<div class="n"><div class="row"><div class="col col-md-1"><img src="' + notification.data['avatar'] + '" class="img'
         + ' img-thumbnail img-responsive"></div>'
    + '<div class="col col-md-4"><p><i>New like: ' + moment(notification.time).fromNow() + '</i></p>'
    + '<p><span class="user_popup"><a href="/profile/' + notification.data['liked_by'] + '">'
     + notification.data['liked_by'] + '</a></span> liked your post in ' + notification.data['thread_name'] + ':</p>'
     + '<p>"' + notification.data['post_body'] + '"</p></div></div><hr></div>'
    };
};

function clear_notifications() {
    $.post('/clear_notifications', {
    }).done(function(response) {
        if (response.status == 1) {
            location.reload();
        } else {
            location.reload();
        };
    }).fail(function() {
        location.reload();
    });
};