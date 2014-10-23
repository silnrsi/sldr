'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {
    var fres = DomService.getXPathFromRoot('/special/sil:external-resources/sil:font');
            
  }])
  ;

