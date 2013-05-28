angular.module('scroll', []).directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        var raw = elm[0];
        // TODO: stop when there's no more content
        // TODO: make sure enough content has loaded for initial scroll bar to appear
        var checkScroll = function() {
            if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
                scope.$apply(attr.whenScrolled);
            }
        }
        elm.bind('scroll', checkScroll);
        $(window).bind('resize', checkScroll);
    };
});

function MyController($scope, $http) {
    $scope.title = "TReader";

    $scope.feeds = {};

    $scope.posts = [];

    $scope.selected_feed = -1;

    $scope.select_feed = function(feed_id) {
        if (feed_id !== $scope.selected_feed) {
            console.log("Selected feed: " + $scope.feeds[feed_id].title);
            $scope.selected_feed = feed_id;
        }
    };

    $scope.add_post = function(i, post) {
        console.log("Added post " + post["title"]);
        $scope.posts.push(post);
    };

    $scope.load_subscriptions = function() {
        $http.get("subscriptions.json").success(function (data, status) {
            $scope.feeds = data;
            $scope.select_feed("1");
        });
    }

    $scope.load_subscriptions();

    $scope.add_more_posts = function() {
        console.log('At the end of the page. Loading more!');
        $http.get("test_data.json").success(function (data, status) {
            $.each(data["posts"], $scope.add_post);
        });
    };

    $scope.add_more_posts();
}

