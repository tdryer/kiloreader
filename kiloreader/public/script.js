var module = angular.module('scroll', [])

// directive to invert checkbox value
// from http://stackoverflow.com/a/13926335
module.directive('inverted', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(val) { return !val; });
      ngModel.$formatters.push(function(val) { return !val; });
    }
  };
});

module.directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        // TODO: stop when there's no more content
        var raw = elm[0];
        var reachedBottom = function() {
            return raw.scrollTop + raw.offsetHeight >= raw.scrollHeight;
        };
        var checkScroll = function() {
            if (reachedBottom()) {
                // pagination is disabled for now
                //if(!scope.$$phase) {
                //    scope.$apply(attr.whenScrolled);
                //} else {
                //    scope.$eval(attr.whenScrolled);
                //}
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
    $scope.feeds = {};

    $scope.entries = [];

    $scope.selected_feed = -1;

    // whether an error has occurred fetching entries for the selected feed
    $scope.selected_feed_error = false;

    // whether there are no more entries for the selected feed
    $scope.selected_feed_done = false;

    // the list index of the selected entry in the selected feed
    $scope.selected_entry = -1;

    $scope.select_feed = function(feed_id) {
        console.log("select_feed called");
        if (feed_id !== $scope.selected_feed) {
            console.log("Selected feed: " + $scope.feeds[feed_id].title);
            $scope.selected_feed = feed_id;
            $scope.entries = [];
            // start with no entry selected (only sorta works)
            $scope.selected_entry = -1;
            $scope.selected_feed_error = false;
            $scope.selected_feed_done = false;
            $scope.load_entries();
        }
    };

    // TODO: let the checkboxes mark read/unread

    // when selected_entry changes, the new entry is marked as read
    $scope.$watch("selected_entry", function(new_val, old_val) {
        if (new_val > -1) {
            $scope.mark_entry_read(new_val);
        }
    });

    // when entry read status is changed
    //$scope.$watch("entries", function(new_val, old_val) {
    //    console.log("something in entries changed");
    //});

    // instead of watching entries for change, let it call this function
    $scope.on_keep_unread_changed = function(entry) {
        $scope.change_entry_read_status(entry.id, entry.is_read);
    };

    $scope.change_entry_read_status = function(entry_id, is_read) {
        var endpoint = "api/entries/" + entry_id;
        $http({method: "PATCH", url: endpoint, data: {is_read: is_read}}).
            success(function (data, status) {
                console.log("successfully marked entry " + entry_id +
                            " is_read " + is_read);
            }).
            error(function (data, status) {
                console.log("failed to mark entry " + entry_id + " read: "
                            + status);
            });
    };

    // mark entry with given ID as read on the server
    // TODO: update unread count for the entry's feed
    $scope.mark_entry_read = function(entry_index) {
        // only mark as read if unread
        if (! $scope.entries[entry_index].is_read) {
            $scope.entries[entry_index].is_read = true;
            var entry_id = $scope.entries[entry_index].id;
            $scope.change_entry_read_status(entry_id, true);
        }
        //var endpoint = "api/entries/" + entry_id;
        //$http({method: "PATCH", url: endpoint, data: {is_read: true}}).
        //    success(function (data, status) {
        //        console.log("successfully marked entry " + entry_id + " as read");
        //    }).
        //    error(function (data, status) {
        //        console.log("failed to mark entry " + entry_id + " as read: " + status);
        //    });
    };

    $scope.load_entries = function() {
        console.log("load_entries called");
        if ($scope.selected_feed > -1 && !$scope.selected_feed_error && !$scope.selected_feed_done) {
            var endpoint = "api/entries?is_read=false&feed=" + $scope.selected_feed;
            if ($scope.entries.length > 0) {
                var last_entry_id = $scope.entries[$scope.entries.length - 1].id;
                endpoint += "&after=" + last_entry_id;
            }
            $http.get(endpoint).
                success(function (data, status) {
                    if (data.length === 0) {
                        console.log("No more entries to load");
                        $scope.selected_feed_done = true;
                    }
                    else {
                        console.log("Loaded entries");
                        $scope.entries = $scope.entries.concat(data);

                        // XXX: for now, no pagination
                        console.log("No more entries to load");
                        $scope.selected_feed_done = true;
                    }
                }).
                error(function (data, status) {
                    console.log("Error loading entries: " + status);
                    $scope.selected_feed_error = true;
                });
        }
    };

    $scope.list_to_index = function(list, key) {
        index = {};
        for (var i = 0; i < list.length; i++) {
            index[list[i][key]] = list[i];
        }
        return index
    };

    $scope.load_feeds = function() {
        console.log("load_feeds called");
        $http.get("api/feeds").success(function (data, status) {
            $scope.feeds = $scope.list_to_index(data, "id");
            $scope.select_feed("1");
        });
    };

    $scope.subscribe_button_clicked = function() {
        var feed_url = prompt("Enter feed URL:", "http://");
        console.log("subscribe to " + feed_url);
        var endpoint = "api/feeds";
        $http.post(endpoint, {feed_url: feed_url}).
            success(function (data, status) {
                console.log("success! " + status + " : " + data);
                $scope.load_feeds();
                // TODO: doesn't work, need callback when feeds are loaded?
                //$scope.select_feed(data.id);
                console.log("select feed " + data.id);
            }).
            error(function (data, status) {
                console.log("error: " + status + " : " + data);
            });
    };

    $scope.unsubscribe_button_clicked = function(feed_id) {
        res = confirm("Unsubscribe from feed '" +
                $scope.feeds[feed_id].title + "'?");
        if (res === true) {
            $scope.unsubscribe_feed(feed_id);
        }
    };

    $scope.unsubscribe_feed = function(feed_id) {
        console.log("unsubscribe from feed " + feed_id);
        var endpoint = "api/feeds/" + feed_id;
        $http.delete(endpoint).
            success(function(data, status) {
                console.log("success");
                $scope.load_feeds();
                // TODO: select different feed
            }).
            error(function(data, status) {
                console.log("failure");
            });
    };

    $scope.refresh_button_clicked = function() {
        console.log("refreshing feeds");
        var endpoint = "api/refreshes/";
        $http.post(endpoint).
            success(function(data, status) {
                console.log("success");
                // TODO
            }).
            error(function(data, status) {
                console.log("failure");
            });
    };

    $scope.alert = function(text) {
        alert(text);
    };

    $scope.load_feeds();
}

