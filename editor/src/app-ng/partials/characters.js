'use strict';

angular.module('ldmlEdit.characters', [
    'ldmlEdit.service'
  ])
  .controller('CharactersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.exemplars = [];

    var init = function(e) {
        var fres = DomService.findElements(null, ["characters"]);
        if (fres) {
            var exemplars = [];
            angular.forEach(fres.children, function(f) {
                if (f.tag == 'exemplarCharacters') { exemplars.push(f); }
            });
            $scope.vm.exemplars = exemplars; 
            // console.log(JSON.stringify($scope.vm.exemplars));
            $scope.$apply();
        }
    };
    $scope.$on('dom', init);
    init();
  }])
  ;


