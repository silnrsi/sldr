'use strict';

angular.module('ldmlEdit', [
     'ngRoute',
     'ui.bootstrap',
     'ldmlEdit.identity',
     'ldmlEdit.characters',
     'ldmlEdit.collations',
     'ldmlEdit.delimiters',
     'ldmlEdit.displays',
     'ldmlEdit.misc',
     'ldmlEdit.numbers',
     'ldmlEdit.resources',
     'ldmlEdit.segmentations',
     'ldmlEdit.service'
   ])
  .config([ '$routeProvider', function($routeProvider) {
    $routeProvider.when('/loadnsave', {
      templateUrl : 'app-ng/partials/loadnsave.html',
      controller : 'MainCtrl'
    });
    $routeProvider.when('/identity', {
      templateUrl : 'app-ng/partials/identity.html',
      controller : 'IdentityCtrl'
    });
    $routeProvider.when('/characters', {
      templateUrl : 'app-ng/partials/characters.html',
      controller : 'CharactersCtrl'
    });
    $routeProvider.when('/collation', {
      templateUrl : 'app-ng/partials/collation.html',
      controller : 'CollationsCtrl'
    });
    $routeProvider.when('/delimiters', {
      templateUrl : 'app-ng/partials/delimiters.html',
      controller : 'DelimitersCtrl'
    });
    $routeProvider.when('/displays', {
      templateUrl : 'app-ng/partials/displays.html',
      controller : 'DisplaysCtrl'
    });
    $routeProvider.when('/misc', {
      templateUrl : 'app-ng/partials/misc.html',
      controller : 'MiscCtrl'
    });
    $routeProvider.when('/numbers', {
      templateUrl : 'app-ng/partials/numbers.html',
      controller : 'NumbersCtrl'
    });
    $routeProvider.when('/resources', {
      templateUrl : 'app-ng/partials/resources.html',
      controller : 'ResourcesCtrl'
    });
    $routeProvider.when('/segmentations', {
      templateUrl : 'app-ng/partials/segmentations.html',
      controller : 'SegmentationsCtrl'
    });
    $routeProvider.otherwise({
      redirectTo : '/loadnsave'
    });
  }])
  .directive("fileread", ["DomService", function(DomService) {
    return {
        scope: {
            fileread: "&",
        },
        link: function (scope, element, attributes) {
            element.bind("change", function(changeEvent) {
                var aFile = changeEvent.target.files[0];
                scope.fileread({aFile: aFile});
            });
        }};
    }])
  .controller('MainCtrl', [ '$scope', '$timeout', 'DomService', function($scope, $timeout, DomService) {
    $scope.doFileOpen = function(aFile) {
        $scope.fileName = aFile.name;
        DomService.loadFromFile(aFile, function(dat) {
            // console.log("broadcasting dom");
            $scope.$broadcast('dom');
        });
    };
    $scope.onFileOpen = function (files) {
        console.log("FileOpen");
        $timeout(function() {
            $("#FileOpen").trigger("click");
        }, 0);
    };
    $scope.onUrlOpen = function() {
        DomService.loadFromURL($scope.openurl, function(dat) {
            $scope.broadcast('dom');
        });
    };
    $scope.onFileSaveAs = function() {
        var complist = ['script', 'territory', 'variant'];
        if ($scope.fileName == null) {
            var ident = DomService.findElement(null, "identity");
            if (ident == null)
                $scope.fileName = 'NoName.xml';
            else {
                var l = DomService.findElement(ident, 'language');
                if (l != null)
                    $scope.fileName = l.attributes['type'];
                angular.forEach(complist, function (c) {
                    var l = DomService.findElement(ident, c);
                    if (l != null)
                        $scope.fileName = $scope.fileName + "_" + l.attributes['type'];
                });
                if ($scope.fileName == null)
                    $scope.fileName = 'NoName';
                $scope.fileName = $scope.fileName + ".xml";
            }
        }
        console.log("Filename: " + $scope.fileName);
        saveAs(DomService.getBlob(), $scope.fileName);  
    };
    }])
;
