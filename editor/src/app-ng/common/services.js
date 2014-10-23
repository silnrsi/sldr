'use strict';

// Services
angular.module('app.services', [ 'ngResource' ])
  .service('PublicService', [ '$resource', function($resource) {
    return $resource('api/a/:id');
  }])
  ;
