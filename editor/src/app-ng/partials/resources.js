'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.fonts = [];

    var init = function(e) {
        $scope.fres = DomService.findElements(null, ["special", "sil:external-resources"]);
        if ($scope.fres) {
            var fonts = [];
            angular.forEach($scope.fres.children, function(f) {
                if (f.tag == 'sil:font') {
                    fonts.push(f);
                }
                f.urls = [];
                angular.forEach(f.children, function(u) {
                    if (u.tag == 'sil:url') {
                        f.urls.push(u)
                    }
                });
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
        $scope.vm.currentFont.children = [];
        angular.forEach($scope.vm.currentFont.urls, function (u) {
            $scope.vm.currentFont.children.push(u);
        });
        angular.copy($scope.vm.currentFont, $scope.vm.fonts[$scope.vm.currentIndex]);
        $scope.vm.currentEditor = null;
    };
    $scope.cancelFont = function() {
        $scope.vm.currentEditor = null;
    }
    $scope.delFont = function(index) {
        //var index = $scope.vm.fonts.indexOf(f);
        var f = $scope.vm.fonts[index];
        $scope.vm.fonts.splice(index, 1);
        for (var i = 0; i < $scope.fres.children.length; i++) {
            if ($scope.fres.children == f) {
                $scope.fres.children.splice(i, 1);
                break;
            }
        }
    };
    $scope.addFont = function() {
        $scope.vm.fonts.push({'tag' : 'sil:font', 'attributes' : { 'name' : '' }, 'children' : []})
    };
    $scope.addFontUrl = function() {
        $scope.vm.currentFont.urls.push({'tag' : 'sil:url', 'text' : ''})
    };
    $scope.delFontUrl = function(u) {
        var index = $scope.vm.currentFont.urls.indexOf(u);
        $scope.vm.currentFont.urls.splice(index, 1);
    };
  }])
  ;

