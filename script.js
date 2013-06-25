var module = angular.module('scroll', [])

module.directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        // TODO: stop when there's no more content
        var raw = elm[0];
        var reachedBottom = function() {
            return raw.scrollTop + raw.offsetHeight >= raw.scrollHeight;
        };
        var checkScroll = function() {
            if (reachedBottom()) {
                if(!scope.$$phase) {
                    scope.$apply(attr.whenScrolled);
                } else {
                    scope.$eval(attr.whenScrolled);
                }
            }
        };
        // Poll and load more entries if necessary. This is better than binding
        // the scroll event, becuase if loading one set of entries isn't enough
        // to fill the screen, we can keep loading more.
        setInterval(checkScroll, 0);
    };
});

module.directive('onScrollCurrent', function() {
    return function(scope, elm, attr) {
        var get_current = function() {
            var raw = elm[0];
            var scroll_pos = raw.scrollTop;
            var entries = $('.entry');
            // min distance between top of scroll area and entry top before the entry is selected
            var BUFFER = 50;
            for (var i = 0; i < entries.length; i++) {
                var entry = $(entries[i]);
                var entry_top = entry[0].offsetTop - BUFFER;
                var entry_height = entry.height();
                if (scroll_pos >= entry_top && scroll_pos < entry_top + entry_height) {
                    scope.$apply(function() {
                        scope.selected_entry = i;
                    });

                }

            }
        };
        elm.bind('scroll', get_current);
    };

});

function MyController($scope, $http) {
    $scope.title = "TReader";

    $scope.feeds = {};

    $scope.entries = [];

    $scope.selected_feed = -1;

    $scope.selected_entry = -1;

    $scope.select_feed = function(feed_id) {
        if (feed_id !== $scope.selected_feed) {
            console.log("Selected feed: " + $scope.feeds[feed_id].title);
            $scope.selected_feed = feed_id;
            $scope.entries = [];
            // start with no entry selected (only sorta works)
            $scope.selected_entry = -1;
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

    $scope.alert = function(text) {
        alert(text);
    }

    $scope.load_subscriptions();
}

