$(function () {
  $('[data-toggle="popover"]').popover();
  $('[data-toggle="dropdown"]').dropdown();
  activate_user_popup();
});


function sanitize(string) {
  const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      "/": '&#x2F;',
  };
  const reg = /[&<>"'/]/ig;
  return string.replace(reg, (match)=>(map[match]));
};


function get_sorted_table(destElem, column) {
    $(destElem).html('<img src="/static/images/loading.gif">');
    $.post('/get_sorted_table', {
        column: column
    }).done(function(response) {
        $('#index_table').html(response['predictions']);
        const cols = [1, 2, 3, 4, 5, 6, 7];
        $.each(cols, function() {
            $('#index_table td:nth-child(' + this + ')').addClass('col' + this);
            $('#index_table th:nth-child(' + this + ')').append(
            '<p><a id="link' + this + '"><img id="img' + this + '" src="/static/images/down_arrow.png" '
            +'style="width:15px;height:15px;" align="center"></a></p>' );
            $('#link' + this).attr("href", "javascript:get_sorted_table('#link" + this + "', " + this + ");" );
        });
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
    }).fail(function() {
        $(destElem).text("Error");
    });
};

function get_new_team(choice, n_trans){
    $("html, body").animate({scrollTop: $(document).height()}, 4000);
    $('#new_score').html('<img src="/static/images/loading.gif" style="width:16px;height:16px">');
    $('#new_team').html('');
    if (n_trans == 1) {
        $.post('/tools/get_new_team', {
            n_trans: n_trans,
            out_id: $('.out_id' + choice).text(),
            in_id: $('.in_id' + choice).text()
        }).done(function(response) {
            $('#new_score').html('<h3>New expected score: ' + response['best_score'] + '</h3><p>New optimal team selection:</p><br>');
            $('#new_team').html(response['new_team'])
            $("html, body").animate({scrollTop: $(document).height()}, 1000);
        }).fail(function() {
            $('#recommended').text("Error");
        });
    } else {
        $.post('/tools/get_new_team', {
            n_trans: n_trans,
            out_id1: $('.out_id1_' + choice).text(),
            out_id2: $('.out_id2_' + choice).text(),
            in_id1: $('.in_id1_' + choice).text(),
            in_id2: $('.in_id2_' + choice).text()
        }).done(function(response) {
            $('#new_score').html('<h3>New expected score: ' + response['best_score'] + '</h3><p>New optimal team selection:</p><br>');
            $('#new_team').html(response['new_team'])
            $("html, body").animate({scrollTop: $(document).height()}, 1000);
        }).fail(function() {
            $('#recommended').text("Error");
        });
    };
};

function get_post_html(post) {
    var delete_value = '';
    if (post.is_current_user) {
        delete_value = '<button class="btn btn-default btn-sm" onclick="delete_post(' + post.id + ',' + post.thread_id + ')">Delete</button>';
    };
    if (post.current_user_has_liked) {
        var likes_value = (post.likes==1) ? post.likes + ' Like' : post.likes + ' Likes';
        like_button = '<div id="likeButton' + post.id + '"><button class="btn btn-primary btn-md" onclick="like_action(' + post.id + ', 0);"'
       + '><span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span></button><br><a id="showLikes' + post.id + '" style="color:#000000"'
       + 'href="javascript:get_likes(' + post.id + ');">'
        + likes_value + '</a></div>'
    } else {
        var likes_value = (post.likes==1) ? post.likes + ' Like' : post.likes + ' Likes';
        like_button = '<div id="likeButton' + post.id + '"><button class="btn btn-default btn-md" onclick="like_action(' + post.id + ', 1);"'
        + '><span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span></button><br><a id="showLikes' + post.id + '" style="color:#000000"'
        + 'href="javascript:get_likes(' + post.id + ');">'
        + likes_value + '</a></div>'
    };
    return '<div class="post post' + post.thread_id + '" id="post' + post.id + '"><div class="row"><div class="col col-md-1">'
    + '<a href="/profile/' + sanitize(post.author) + '"><img '
    + 'class="img-thumbnail img-responsive" src=' + post.avatar + '></a></div>'
    + '<div class="col col-md-4 inner_col' + post.thread_id + '"><h4>'
    + '<span class="user_popup"><a href="/profile/' + sanitize(post.author)
    + '">' + sanitize(post.author) + '</a></span></h4><p>' + sanitize(post.body) + '</p><p><i>'
    + moment(post.timestamp).fromNow() + '</i></p></div><div class="col col-md-4">' + like_button + '<br><br>' + delete_value +
    '</div></div><hr></div>'
};

function delete_post(Id, threadId) {
    $.post('/forum/delete_post', {
        id: Id
    }).done(function(response) {
        $('#post' + Id).remove();
        var nPosts = parseInt($('#count' + threadId).text());
        $('#count' + threadId).html((nPosts - 1) + ' post(s)');
    }).fail(function() {
        $('#post' + Id).html('Post delete failed.')
    });
    $('#post' + Id).remove()
};

function like_action(postId, action) {
    if (action == 1) {
        $.post('/forum/like', {
            postId: postId,
            action: 'like'
        }).done(function(response) {
            if (response.new_count == -1) {
                window.location.href = '/auth/login';
            } else {
                var likes_value = (response.new_count==1) ? response.new_count + ' Like' : response.new_count + ' Likes';
                hide_likes(postId);
                $('#likeButton' + postId).html('<button class="btn btn-primary btn-md" onclick="like_action(' + postId + ', 0);"'
                + '><span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span></button><br><a id="showLikes' + postId + '"'
                + 'style="color:#000000" '
                + 'href="javascript:get_likes(' + postId + ');">'
                + likes_value + '</a>');
            };
        }).fail(function() {
            $('#likeButton' + postId).html('<p>An error occurred.</p>');
        });
    } else {
        $.post('/forum/like', {
            postId: postId,
            action: 'unlike'
        }).done(function(response) {
            if (response.new_count == -1) {
                window.location.href = '/auth/login';
            } else {
                var likes_value = (response.new_count==1) ? response.new_count + ' Like' : response.new_count + ' Likes';
                hide_likes(postId);
                $('#likeButton' + postId).html('<button class="btn btn-default btn-md" onclick="like_action(' + postId + ', 1);"'
                + '><span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span></button><br><a id="showLikes' + postId + '"'
                + ' style="color:#000000"'
                + 'href="javascript:get_likes(' + postId + ');">'
                + likes_value + '</a>');
            };
        }).fail(function() {
            $('#likeButton' + postId).html('<p>An error occurred.</p>');
        });
    };
};

function get_likes(postId) {
    $.post('/forum/get_post_likes', {
        post_id: postId
    }).done(function(response) {
        if (response.likes != '') {
            $('#showLikes' + postId).attr("href", "javascript:hide_likes(" + postId + ");");
            $('#post' + postId).append('<div id="likes' + postId + '" class="container"><h4>Likes</h4></div>');
            $.each(response.likes, function(index, user) {
                $('#likes' + postId).append(get_user_html(user.username, user.about, user.avatar));
            });
            activate_user_popup();
        };
    }).fail(function() {
        alert('fail');
    });
};

function hide_likes(postId) {
    $('#likes' + postId).remove();
    $('#showLikes' + postId).attr("href", "javascript:get_likes(" + postId + ");");
};

function get_user_html(username, about, avatar) {
    if (about) {
        return '<div class="row user_like"><div class="col col-md-1"><img class="img img-thumbnail img responsive" src="'
                + avatar + '"></div><div class="col col-md-4"><h4><span class="user_popup"><a href="/profile/' + sanitize(username)
                + '">' + sanitize(username) + '</a></h4>'
                + '</span><p>' + sanitize(about) + '</p></div></div><hr>'
    } else {
        return '<div class="row user_like"><div class="col col-md-1"><img class="img img-thumbnail img responsive" src="'
                + avatar + '"></div><div class="col col-md-4"><h4><span class="user_popup"><a href="/profile/' + sanitize(username)
                + '">' + sanitize(username) + '</a></h4>'
                + '</span></div></div><hr>'
    };
};

function activate_user_popup() {
    var timer = null;
    var xhr = null;
    $('.user_popup').hover(
        function(event) {
            var elem = $(event.currentTarget);
            timer = setTimeout(function() {
                timer = null;
                xhr = $.ajax(
                    '/profile/' + elem.first().text().trim() + '/popup').done(
                        function(data) {
                            xhr = null;
                            elem.popover({
                                    trigger: 'manual',
                                    html: true,
                                    animation: false,
                                    container: elem,
                                    content: data
                            }).popover('show');
                            flask_moment_render_all();
                        }
                    );
            }, 500);
        },
        function(event) {
            var elem = $(event.currentTarget);
            if (timer) {
                clearTimeout(timer);
                timer = null;
            }
            else if (xhr) {
                xhr.abort();
                xhr = null;
            }
            else {
                elem.popover('destroy');
            }
        }
    );
};