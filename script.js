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

    $scope.entries = [];

    $scope.selected_feed = -1;

    $scope.select_feed = function(feed_id) {
        if (feed_id !== $scope.selected_feed) {
            console.log("Selected feed: " + $scope.feeds[feed_id].title);
            $scope.selected_feed = feed_id;
            $scope.entries = [];
            $scope.load_entries();
        }
    };

    $scope.load_entries = function() {
        var endpoint = "test_api/feeds/" + $scope.selected_feed + "/entries.json";
        if ($scope.entries.length > 0) {
            var last_entry_id = $scope.entries[$scope.entries.length - 1].id;
            endpoint += "?after=" + last_entry_id;
        }
        $http.get(endpoint).success(function (data, status) {
            $scope.entries = $scope.entries.concat(data);
        });
    }

    $scope.load_more_entries = function() {
        var last_entry_id = $scope.entries

    }

    $scope.load_subscriptions = function() {
        $http.get("test_api/subscriptions.json").success(function (data, status) {
            $scope.feeds = data;
            $scope.select_feed("1");
        });
    }

    $scope.load_subscriptions();
}

