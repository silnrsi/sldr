'use strict';

angular.module('ldmlEdit', [
     'ngRoute',
     'ui.bootstrap',
     'ldmlEdit.resources',
     'ldmlEdit.characters',
     'ldmlEdit.service'
   ])
  .config([ '$routeProvider', function($routeProvider) {
    $routeProvider.when('/resources', {
      templateUrl : 'app-ng/partials/resources.html',
      controller : 'ResourcesCtrl'
    });
    $routeProvider.when('/characters', {
      templateUrl : 'app-ng/partials/characters.html',
      controller : 'CharactersCtrl'
    });
    $routeProvider.otherwise({
      redirectTo : '/'
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
        console.log("Filename: " + $scope.fileName);
        saveAs(DomService.getBlob(), $scope.fileName);  
    };
    }])
;
