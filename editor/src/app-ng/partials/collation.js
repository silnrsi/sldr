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
        $scope.vm.changed = false;

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
        $scope.vm.changed = false;
    };
    $scope.saveBtn = function() {
        angular.forEach($scope.vm.currentCollation.children, function (c) {
            if (c.tag == 'cr') 
                c.text = $scope.vm.currentText.replace(/\n(?!$)/g, "\n\t\t\t\t");
        });
        if ($scope.vm.currentCollation.format == 'Simple') {
            var r = {tag : 'sil:simple', attributes : {}};
            r.text = $scope.vm.currentSubText.replace(/\n(?!$)/g, "\n\t\t\t\t");
            $scope.vm.currentCollation.children.push({tag : 'special', attributes : {}, children : [r]});
        }
        else if ($scope.vm.currentCollation.format == 'PreProcessed') {
            var r = {tag : 'sil:reordered', attributes : {}, children : []};
            angular.forEach($scope.vm.currentCollation.rules, function (rule) {
                r.children.push(rule);
            });
            r.children.push({tag : 'cr', attributes : {}, text : $scope.vm.currentProcText.replace(/\n(?!$)/g, "\n\t\t\t\t") });
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
    $scope.editChange = function() {
        $scope.vm.changed = true;
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
                    else if (s.tag == 'sil:reordered') {
                        $scope.vm.currentCollation.format = 'PreProcessed';
                        removeme = ind;
                        angular.forEach(s.children, function (r) {
                            if (r.tag == 'sil:reorder')
                                $scope.vm.currentCollation.rules.push(r);
                            else if (r.tag == 'cr')
                                $scope.vm.currentProcText = r.text.replace(/^\t+/mg, "");
                        });
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
        update_model();
    };
    $scope.formatChange = function() {
        if ($scope.vm.currentCollation.format == 'Simple') {
            $scope.vm.currentCollation.dirty = 1;
        }
        else if ($scope.vm.currentCollation.format == 'PreProcessed') {
            $scope.vm.currentCollation.dirty = 1;
            $scope.vm.currentCollation.rules = [];
            $scope.vm.currentProcText = '';
        }
        $scope.vm.changed = true;
    };
    $scope.delRule = function(i) {
        $scope.vm.currentCollation.rules.splice(ind, 1);
        update_model();
    };
    $scope.addRule = function() {
        $scope.vm.currentCollation.rules.push({tag : 'sil:reorder', attributes : { match : '', reorder : '' }});
        update_model();
    };
    $scope.simpleChange = function() {
        $scope.vm.currentCollation.dirty = 1;
        $scope.vm.changed = true;
    };
 
  }])
  ;

