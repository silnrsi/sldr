'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.fonts = [];
    $scope.vm.kbds = [];

    var init = function(e) {
        $scope.fres = DomService.findElements(null, ["special", "sil:external-resources"]);
        if ($scope.fres) {
            var fonts = [];
            var kbds = [];
            var spells = [];
            angular.forEach($scope.fres.children, function(f) {
                if (f.tag == 'sil:font') {
                    fonts.push(f);
                } else if (f.tag == 'sil:kbd') {
                    kbds.push(f);
                } else if (f.tag == 'sil:spell-checking') {
                    spells.push(f);
                }
                f.urls = [];
                angular.forEach(f.children, function(u) {
                    if (u.tag == 'sil:url') {
                        f.urls.push(u);
                    }
                });
            });
            $scope.vm.fonts = fonts;
            $scope.vm.kbds = kbds;
            $scope.vm.spells = spells;
            // console.log(JSON.stringify($scope.vm.fonts));
            if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
                $scope.$apply();
        }
    };
    $scope.$on('dom', init);
    init();

    $scope.onEditClick = function(index, type) {
        $scope.vm.currentEditor = type;
        $scope.vm.currentElement = angular.copy($scope.vm[type + 's'][index]);
        $scope.vm.currentIndex = index;
    };
    $scope.editBtn = function(type) {
        $scope.vm.currentElement.children = [];
        angular.forEach($scope.vm.currentElement.urls, function (u) {
            if (u.text) {
                $scope.vm.currentElement.children.push(u);
            }
        });
        angular.copy($scope.vm.currentElement, $scope.vm[type + 's'][$scope.vm.currentIndex]);
        $scope.vm.currentEditor = null;
    };
    $scope.cancelBtn = function() {
        $scope.vm.currentEditor = null;
    }
    $scope.delElement = function(index, type) {
        //var index = $scope.vm.fonts.indexOf(f);
        var f = $scope.vm[type + 's'][index];
        $scope.vm[type + 's'].splice(index, 1);
        for (var i = 0; i < $scope.fres.children.length; i++) {
            if ($scope.fres.children == f) {
                $scope.fres.children.splice(i, 1);
                break;
            }
        }
    };
    $scope.addUrl = function() {
        $scope.vm.currentElement.urls.push({'tag' : 'sil:url', 'text' : ''})
    };
    $scope.delUrl = function(u) {
        var index = $scope.vm.currentElement.urls.indexOf(u);
        $scope.vm.currentElement.urls.splice(index, 1);
    };

    $scope.addFont = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        $scope.vm.fonts.push({'tag' : 'sil:font', 'attributes' : { 'name' : '' }, 'children' : [url], 'urls' : [url]});
    };
    $scope.addKbd = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        $scope.vm.kbds.push({'tag' : 'sil:kbd', 'attributes' : { 'id' : '' }, 'children' : [url], 'urls' : [url]});
    };
    $scope.addSpell = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        $scope.vm.spells.push({'tag' : 'spell-checking', 'attribute' : {'type' : ''}, 'children' : [url], 'urls' : [url]});
    };
  }])
  ;

