function appendPost(i, post_json) {
    var post_template = '\
        <div class="post">\
            <a class="post-title" href="#">{title}</a>\
            <p>{content}</p>\
        </div>\
    ';
    console.log("append post " + post_json + " with title " + post_json["title"]);
    $('#content').append(post_template.replace("{title}", post_json["title"]).replace("{content}", post_json["content"])
    );
}

function setFeedList(feeds) {
    var list = $('#sidebar ul');
    $.each(feeds, function(i, feed) {
        console.log("add feed " + feed);
        var handler = 'javascript:selectFeed(\'' + feed + '\')';
        $("<li>", {}).append($("<a>", {'href': handler, 'text': feed, 'id': feed})).appendTo(list);
    });

}

function selectFeed(feed) {
    console.log("Selected feed: " + feed);
}

$( document ).ready(function() {

    setFeedList(["The Verge", "XKCD", "Planet Ubuntu"]);

    $('#content').infiniteScroll({
        threshold: 50,
        onEnd: function() {
            console.log('No more results!');
        },
        onBottom: function(callback) {
            console.log('At the end of the page. Loading more!');

            $.getJSON("test_data.json", function (data) {
                $.each(data["posts"], appendPost);
            });

            // (load results & update views)
            var moreResults = true;

            callback(moreResults);
        }
    });
});
