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
    var capkeyattributes = {'opengroup' : 1, 'closegroup' : 2};

    var update_model = function() {
        $scope.fres.children = [];
        angular.forEach(restypes, function(v) {
            for (var i = 0; i < $scope.vm[v].length; i++)
                $scope.fres.children.push($scope.vm[v][i]);
        });
        angular.forEach($scope.vm.transforms, function (t) {
            var tc = angular.copy(t.children);
            t.children = [];
            angular.forEach(tc, function (c) {
                if (c.tag == 'sil:url')
                    t.children.push(c);
                else if (c.tag == 'sil:transform-dict' && t.dict.urls[0].text != '')
                    t.children.push(c);
                else if (c.tag == 'sil:transform-capitals') {
                    for (a in capkeyattributes) {
                        if (a in t.caps.attributes && t.caps.attributes[a] != '') {
                            t.children.push(c);
                            break;
                        }
                    }
                }
            });
            if (!hasdict && t.dict.urls[0].text != '')
                t.children.push(t.dict);
            if (!hascaps && ('opengroup' in t.caps.attributes || 'closegroup' in t.caps.attributes))
                t.children.push(t.caps);
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
        angular.forEach($scope.vm.transforms, function (t) {
            angular.forEach(t.children, function (c) {
                if (c.tag == 'sil:transform-capitals')
                    t.caps = c;
                else if (c.tag == 'sil:transform-dict') {
                    t.dict = c;
                    c.urls = [];
                    angular.forEach(c.children, function (u) {
                        if (u.tag == 'sil:url')
                            c.urls.push(u);
                    });
                }
            });
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
        $scope.vm.currentElement.urls.push({'tag' : 'sil:url', 'text' : ''});
        $scope.vm.changed = true;
    };
    $scope.delUrl = function(index) {
        $scope.vm.currentElement.urls.splice(index, 1);
        $scope.vm.changed = true;
    };
    $scope.addSubUrl = function(sub) {
        $scope.vm.currentElement[sub].urls.push({'tag' : 'sil:url', 'text' : ''});
        $scope.vm.changed = true;
    };
    $scope.delSubUrl = function(sub, index) {
        $scope.vm.currentElement[sub].urls.splice(index, 1);
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
        var res = {'tag' : 'sil:spell-checking', 'attributes' : {'type' : ''}, 'children' : [url], 'urls' : [url]};
        $scope.vm.spells.push(res);
        update_model();
    };
    $scope.addTransform = function() {
        var url = {tag : 'sil:url', text : ''};
        var dicturl = {tag : 'sil:url', text : ''};
        var res = {tag : 'sil:transform', attributes : {from : '', to : '', type : '', direction : 'forward'}, children : [url], urls : [url],
                    dict : {tag : 'sil:transform-dict', attributes : {incol : '0', outcol : '1', nf : 'nfc'}, children : [dicturl], urls : [dicturl] },
                    caps : {tag : 'sil:transform-capitals', attributes : { } }};
        $scope.vm.transforms.push(res);
        update_model();
    };
  }])
  ;

