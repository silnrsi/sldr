'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {
    var fres = DomService.getXPathFromRoot('/special/sil:external-resources');
    if (fres) {
        $scope.data = DomService.asElementTree(fres.iterateNext());
    }
  }])
  ;

