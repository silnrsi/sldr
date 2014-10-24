'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.fonts = [];

    var init = function(e) {
        var fres = DomService.findElements(null, ["special", "sil:external-resources"]);
        if (fres) {
            var fonts = [];
            angular.forEach(fres.children, function(f) {
                if (f.tag == 'sil:font') { fonts.push(f); }
            });
            $scope.vm.fonts = fonts; 
            // console.log(JSON.stringify($scope.vm.fonts));
            if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
                $scope.$apply();
        }
    };
    $scope.$on('dom', init);
    init();

    $scope.onFontClick = function(index) {
        $scope.vm.currentEditor = "font";
        $scope.vm.currentFont = angular.copy($scope.vm.fonts[index]);
        $scope.vm.currentIndex = index;
    };
    $scope.editFont = function() {
        angular.copy($scope.vm.currentFont, $scope.vm.fonts[$scope.vm.currentIndex]);
    };
  }])
  ;

