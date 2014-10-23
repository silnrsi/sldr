'use strict';

angular.module('ldmlEdit', [
     'ngRoute',
     'ui.bootstrap',
     'ldmlEdit.resources',
     'ldmlEdit.service'
   ])
  .config([ '$routeProvider', function($routeProvider) {
    $routeProvider.when('/resources', {
      templateUrl : 'app-ng/partials/resources.html',
      controller : 'ResourcesCtrl'
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
  .controller('MainCtrl', [ '$scope', 'DomService', function($scope, DomService) {
    $scope.onFileOpen = function(aFile) {
        // DomService.loadFromFile(aFile, function(dat) { console.log(DomService.asElementTree(DomService.getXPathFromRoot("/ldml/special").iterateNext())); });
        DomService.loadFromFile(aFile, function(dat) {
            console.log("broadcasting dom");
            $scope.$broadcast('dom');
            });
      };
    $scope.onFileSaveAs = function() {
        
    }; }])
  ;
