'use strict';

angular.module('ngApp', [
     'ngRoute',
     'ui.bootstrap'
   ])
  .config([ '$routeProvider', function($routeProvider) {
    $routeProvider.when('/a', {
      templateUrl : 'app-ng/partials/a.html',
      controller : 'ACtrl'
    });
    $routeProvider.otherwise({
      redirectTo : '/a'
    });
  }])
  .controller('MainCtrl', [ '$scope', function($scope) {
  }])
  ;
