'use strict';

angular.module('ldmlEdit.collations', [
    'ldmlEdit.service'
  ])
  .controller('CollationsCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.def = null;

    var init = function(e) {
        $scope.fres = DomService.findElement(null, "collations");
        if ($scope.fres == null)
            $scope.fres = {tag : 'collations', attributes : {}, children : []};
        var colls = [];
        var def = null;
        angular.forEach($scope.fres.children, function (c) {
            if (c.tag == 'collation') {
                colls.push(c);
                if (c.attributes.type == 'eor' || c.attributes.type == 'search')
                    c.disabled = true;
            }
            else if (c.tag == 'defaultCollation')
                $scope.vm.def = c.text;
        });
        $scope.vm.collations = colls;

        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();

    var update_model = function() {
        $scope.fres.children = angular.copy($scope.vm.collations);
        if ($scope.vm.def != null)
            $scope.fres.children.push({tag: 'defaultCollation', attributes : {}, text : $scope.vm.def});
        DomService.updateTopLevel($scope.fres);
    };
    $scope.editBtn = function() {
        angular.forEach($scope.vm.currentCollation.children, function (c) {
            if (c.tag == 'cr') 
                c.text = $scope.vm.currentText.replace(/\n(?!$)/g, "\n\t\t\t\t");
        });
        if ($scope.vm.currentCollation.format == 'Simple') {
            var r = {tag : 'sil:simple', attributes : {}};
            r.text = $scope.vm.currentSubText.replace(/\n(?!$)/g, "\n\t\t\t\t");
            $scope.vm.currentCollation.children.push({tag : 'special', attributes : {}, children : [r]});
        }
        if ($scope.vm.currentCollation.dirty)
            $scope.vm.currentCollation.attributes['sil:needscompiling'] = '1';
        else
            delete $scope.vm.currentCollation.attributes['sil:needscompiling'];
        $scope.vm.mode = null;
        update_model();
    };
    $scope.cancelBtn = function() {
        init();
        $scope.vm.mode = null;
    };
    $scope.onEditClick = function (i) {
        $scope.vm.currentCollation = $scope.vm.collations[i];
        $scope.vm.currentText = "";
        $scope.vm.currentSubText = "";
        $scope.vm.mode = 'edit';
        $scope.vm.currentCollation.format = 'ICU';
        var removeme = null;
        angular.forEach($scope.vm.currentCollation.children, function (c, ind) {
            if (c.tag == 'cr')
                $scope.vm.currentText = c.text.replace(/^\t+/mg, "");
            else if (c.tag == 'special') {
                angular.forEach(c.children, function (s) {
                    if (s.tag == 'sil:simple') {
                        $scope.vm.currentSubText = s.text.replace(/^\t+/mg, "");
                        $scope.vm.currentCollection.format = 'Simple';
                        removeme = ind;
                    }
                });
            }
        });
        if (removeme != null)
            $scope.vm.currentCollation.children.splice(removeme, 1);
    };
    $scope.delCollation = function(i) {
        $scope.vm.collations.splice(index, 1);
        udpate_model();
    };
    $scope.addCollation = function() {
        $scope.vm.collations.push({tag : 'collation', attributes : {type : ''}, children : [
            {tag : 'cr', attributes : {}, text : ''}]});
        update_model;
    };
    $scope.formatChange = function() {
        if ($scope.vm.currentCollation.format == 'Simple') {
            $scope.vm.currentCollation.dirty = 1;
        }
    };
 
  }])
  ;

