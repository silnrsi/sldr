'use strict';

angular.module('ldmlEdit.misc', [
    'ldmlEdit.service'
  ])
  .controller('MiscCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.layout = {};
    $scope.posix = {};
    var orientationmap = {
        'Left to Right' : 'left-to-right',
        'Right to Left' : 'right-to-left',
        'Top to Bottom' : 'top-to-bottom',
        'Bottom to Top' : 'bottom-to-top'
    };

    var init = function(e) {
        $scope.flayout = DomService.findElement(null, "layout");
        $scope.layout = {};
        if ($scope.flayout != null)
            angular.forEach($scope.flayout.children, function (c) {
                if (c.tag == 'orientation')
                    $scope.layout = c.attributes;
            });
        $scope.fposix = DomService.findElements(null, "posix");
        if ($scope.fposix != null)
            angular.forEach($scope.fposix.children, function (m) {
                if (m.tag == 'messages')
                    angular.forEach(m.children, function(c) {
                        $scope.posix[c.tag] = c.text;
                    });
            });
    };
    $scope.$on('dom', init);
    init();

    var update_model = function() {
        var have_orientation = false;
        angular.forEach($scope.layout, function(a) {
            if (a != null && a != '')
                have_orientation = true;
        });
        if (have_orientation) {
            var orientation = null;
            if ($scope.flayout == null) {
                $scope.flayout = {tag : 'layout', attributes : {}, children : []};
                DomService.updateTopLevel($scope.flayout);
            }
            angular.forEach($scope.flayout.children, function (m) {
                if (m.tag == 'orientation')
                    orientation = m;
            });
            if (orientation == null) {
                orientation = {tag : 'orientation', attributes : {}, children : []};
                $scope.flayout.children.push(orientation);
            }
            angular.forEach($scope.layout, function (v, k) {
                if (v != null && v != '')
                    orientation.attributes[k] = orientationmap[v];
            });
        }
        var have_posix = false;
        angular.forEach($scope.posix, function(p) {
            if (p.text != '')
                have_posix = true;
        });
        if (have_posix) {
            var messages = null;
            if ($scope.fposix == null) {
                $scope.fposix = {tag : 'posix', attributes : {}, children : []};
                DomService.updateTopLevel($scope.fposix);
            }
            angular.forEach($scope.fposix.children, function (m) {
                if (m.tag == 'messages')
                    messages = m;
            });
            if (messages == null) {
                messages = {tag : 'message', attributes : {}};
                $scope.fposix.children.push(messages);
            }
            messages.children = [];
            angular.forEach($scope.posix, function (v, k) {
                if (v != null && v != '')
                    messages.children.push({tag : k, attributes : {}, text : v});
            });
        }
    };
}]);
