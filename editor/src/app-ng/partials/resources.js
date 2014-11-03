'use strict';

angular.module('ldmlEdit.resources', [
    'ldmlEdit.service'
  ])
  .controller('ResourcesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.fonts = [];
    $scope.vm.kbds = [];
    $scope.base = null;
    $scope.kbdtypes = ['kmn', 'kmx', 'ldml', 'msklc'];
    var restypes = {
        'sil:font' : 'fonts',
        'sil:kbd' : 'kbds',
        'sil:spell-checking' : 'spells',
        'sil:transform' : 'transforms'
    };

    var update_model = function() {
        $scope.fres.children = [];
        angular.forEach(restypes, function(v) {
            for (var i = 0; i < $scope.vm[v].length; i++)
                $scope.fres.children.push($scope.vm[v][i]);
        });
        $scope.vm.changed = false;
    };

    var init = function(e) {
        $scope.fres = DomService.findElements(null, ["special", "sil:external-resources"]);
        if ($scope.fres == null) {
            $scope.fres = {'tag' : 'sil:external-resources', 'attributes' : {}, 'children' : []}
            $scope.base = {'tag' : 'special', 'attributes' : {}, 'children' : [ $scope.fres ]};
        }
        var temp = { fonts : [], kbds : [], spells : [], transforms : [] };
        angular.forEach($scope.fres.children, function(f) {
            if (f.tag in restypes)
                temp[restypes[f.tag]].push(f);
            f.urls = [];
            angular.forEach(f.children, function(u) {
                if (u.tag == 'sil:url') {
                    f.urls.push(u);
                }
            });
        });
        angular.forEach(restypes, function(v) {
            $scope.vm[v] = temp[v];
        });
        $scope.vm.changed = false;
        // console.log(JSON.stringify($scope.vm.fonts));
        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();

    $scope.onEditClick = function(index, type) {
        $scope.vm.currentEditor = type;
        $scope.vm.currentElement = angular.copy($scope.vm[type + 's'][index]);
        $scope.vm.currentIndex = index;
        $scope.vm.changed = false;
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
        update_model();
        if ($scope.base != null) {
            DomService.updateTopLevel($scope.base);
            $scope.base = null;
        }
    };
    $scope.cancelBtn = function() {
        $scope.vm.currentEditor = null;
    }
    $scope.editChange = function() {
        $scope.vm.changed = true;
    };
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
        update_model();
    };
    $scope.addUrl = function() {
        $scope.vm.currentElement.urls.push({'tag' : 'sil:url', 'text' : ''})
        $scope.vm.changed = true;
    };
    $scope.delUrl = function(u) {
        var index = $scope.vm.currentElement.urls.indexOf(u);
        $scope.vm.currentElement.urls.splice(index, 1);
        $scope.vm.changed = true;
    };

    $scope.addFont = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        var res = {'tag' : 'sil:font', 'attributes' : { 'name' : '' }, 'children' : [url], 'urls' : [url]};
        $scope.vm.fonts.push(res);
        update_model();
    };
    $scope.addKbd = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        var res = {'tag' : 'sil:kbd', 'attributes' : { 'id' : '' }, 'children' : [url], 'urls' : [url]};
        $scope.vm.kbds.push(res);
        update_model();
    };
    $scope.changeKbdType = function(ktype) {
        $scope.vm.currentElement.attributes.type = ktype;
        $scope.vm.changed = true;
    };
    $scope.addSpell = function() {
        var url = {'tag' : 'sil:url', 'text' : ''};
        var res = {'tag' : 'sil:spell-checking', 'attribute' : {'type' : ''}, 'children' : [url], 'urls' : [url]};
        $scope.vm.spells.push(res);
        update_model();
    };
  }])
  ;

