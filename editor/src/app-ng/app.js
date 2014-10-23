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
            fileread: "=",
        },
        link: function (scope, element, attributes) {
            element.bind("change", function(changeEvent) {
                scope.$apply(function() {
                    var afile = changeEvent.target.files[0];
                    DomService.loadFromFile(afile, function(dat) { 
                        var dateTree = DomService.asElementTree(DomService.getXPathFromRoot("/ldml/special").iterateNext());
                        console.log(JSON.stringify(dateTree));
                    });
                    //DomService.loadFromFile(afile, function(dat) { console.log("Loaded"); });
                });
            });
        }};
    }])
  .controller('MainCtrl', [ '$scope', 'DomService', function($scope, DomService) {
    $scope.onFileOpen = function(aFile) {
        DomService.loadFromFile(afile, function(dat) { console.log(DomService.asElementTree(DomService.getXPathFromRoot("/special").iterateNext())); });
      }
    }])
  ;
