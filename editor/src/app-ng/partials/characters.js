'use strict';

angular.module('ldmlEdit.characters', [
    'ldmlEdit.service'
  ])
  .controller('CharactersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.exemplars = [];
    var knowntypes = { 'main' : 0, 'auxiliary' : 1, 'punctuation' : 2, 'index' : 3 };

    var init = function(e) {
        $scope.fres = DomService.findElements(null, ["characters"]);
        if ($scope.fres == null) 
            $scope.fres = {'tag' : 'characters', 'attributes' : {}, 'children' : []};

        var exemplars = [];
        angular.forEach($scope.fres.children, function(f) {
            if (f.tag == 'exemplarCharacters') 
                exemplars.push({'type' : f.attributes['type'], 'text' : f.text});
            else if (f.tag == 'special') {
                angular.forEach(f.children, function (e) {
                    if (e.tag == 'sil:exemplarCharacters')
                        exemplars.push({'type' : e.attributes['type'], 'text' : e.text});
                });
            }
        });
        $scope.vm.exemplars = exemplars; 
        // console.log(JSON.stringify($scope.vm.exemplars));
        // $scope.$apply();
        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();

    $scope.editBtn = function() {
        var children = [];
        var extras = [];
        angular.forEach($scope.vm.exemplars, function (s) {
            var res = {'tag' : 'exemplarCharacters', 'attributes' : {'type' : s.type}, 'text' : s.text, 'children' : []};
            if (s.type in knowntypes || s.type == null || s.type == '')
                children.push(res);
            else {
                res['tag'] = 'sil:exemplarCharacters';
                extras.push(res);
            }
        });
        angular.forEach($scope.fres.children, function (s) {
            if (s.tag != 'exemplarCharacters' && (s.tag != 'special' || s.children[0]['tag'] != 'sil:exmplarCharacters'))
                children.push(s);
        });
        if (extras.length > 0)
            children.push({'tag' : 'special', 'attributes' : {}, 'children' : extras});
        $scope.fres.children = children;
        DomService.updateTopLevel($scope.fres);
    };
    $scope.cancelBtn = function() {
        init();
    };
    $scope.addBtn = function() {
        $scope.vm.exemplars.push({'type' : '', 'text' : ''});
    };
    $scope.delBtn = function(index) {
        $scope.vm.exemplars.splice(index, 1);
    };
  }])
  ;


