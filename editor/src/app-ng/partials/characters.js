'use strict';

angular.module('ldmlEdit.characters', [
    'ldmlEdit.service'
  ])
  .controller('CharactersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.exemplars = [];
    $scope.charactertypes = { 'Default' : 'Default', 'auxiliary' : 'auxiliary', 'punctuation' : 'punctuation', 'index' : 'index' };

    var init = function(e) {
        $scope.fres = DomService.findLdmlElement(null, "characters");
        if ($scope.fres == null) 
            $scope.fres = {'tag' : 'characters', 'attributes' : {}, 'children' : []};

        var exemplars = [];
        DomService.forEach($scope.fres.children, function(f) {
            if (f.tag == 'exemplarCharacters') {
                var t = f.attributes.type;
                if (!t) t = 'Default';
                exemplars.push({'type' : t, 'text' : f.text});
            }
            else if (f.tag == 'special') {
                DomService.forEach(f.children, function (e) {
                    if (e.tag == 'sil:exemplarCharacters')
                        exemplars.push({'type' : e.attributes.type, 'text' : e.text});
                });
            }
        });
        $scope.vm.exemplars = exemplars; 
    };
    init();

    $scope.editBtn = function() {
        var children = [];
        var extras = [];
        angular.forEach($scope.vm.exemplars, function (s) {
            var tname = s.type
            if (s.type == 'Default')
                tname = '';
            var res = {'tag' : 'exemplarCharacters', 'attributes' : {'type' : tname}, 'text' : s.text, 'children' : []};
            if (s.type in $scope.charactertypes || s.type == null || s.type == '')
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
        $scope.vm.changed = false;
    };
    $scope.cancelBtn = function() {
        init();
        $scope.vm.changed = false;
    };
    $scope.editChange = function() {
        $scope.vm.changed = true;
    };
    $scope.addBtn = function() {
        $scope.vm.exemplars.push({'type' : '', 'text' : ''});
        $scope.vm.changed = true;
    };
    $scope.delBtn = function(index) {
        $scope.vm.exemplars.splice(index, 1);
        $scope.vm.changed = true;
    };
  }])
  ;


