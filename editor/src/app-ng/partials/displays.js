'use strict';

angular.module('ldmlEdit.displays', [
    'ldmlEdit.service'
  ])
  .controller('DisplaysCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.keytypes = {'languages' : 'Languages', 'scripts' : 'Scripts', 'territories' : 'Regions',
                        'variants' : 'Variants', 'keys' : 'Keys', 'types' : 'Types',
                        'transformNames' : "Transform Names", 'measurementSystemNames' : "Measurement System Names",
                        'codePatterns' : "Code Patterns"}

    var init = function(e) {
        $scope.fres = DomService.findElements(null, ["localeDisplayNames"]);
        if ($scope.fres == null) 
            $scope.fres = {'tag' : 'segmentations', 'attributes' : {}, 'children' : []};
        $scope.vm = { model : {}, specials : []};
        angular.forEach($scope.fres.children, function(disp) {
            if (disp.tag in $scope.keytypes) {
                $scope.vm.model[disp.tag] = { type : disp.tag, data : [], count : 0, currentPage : 1, itemsperpage : 10 };
                var curr = $scope.vm.model[disp.tag];
                angular.forEach(disp.children, function(c) {
                    if (c.tag != 'special') {
                        curr.data.push(c);
                        curr.count++;
                    }
                });
                curr.changed = false;
                // console.log($scope.vm.model[disp.tag].type + " - " + $scope.vm.model[disp.tag].count);
            } else if (disp.tag == 'localeDisplayPattern') {
                $scope.vm.localeDisplayPattern = {};
                angular.forEach(disp.children, function(c) {
                    $scope.vm.localeDisplayPattern[c.tag] = c.text;
                });
            } else if (disp.tag == 'special') {
                $scope.vm.specials.push(disp);
            }
        });
    };
    var update_model = function() {
        $scope.fres.children = [];
        var child = {tag : 'localeDisplayPattern', attributes : {}, children : []};
        angular.forEach($scope.vm.localeDisplayPattern, function(c, k) {
            child.children.push({tag : k, attributes : {}, children : [], text : c});
        });
        angular.forEach($scope.vm.model, function(v) {
            $scope.fres.children.push({tag : v.type, attributes : {}, children : v.data});
        });
        angular.forEach($scope.specials, function(v) {
            $scope.fres.children.push(v);
        });
    };
    $scope.$on('dom', init);
    init();

    $scope.paginate = function(submodel) {
        var start = (submodel.currentPage - 1) * submodel.itemsperpage;
        var end = start + submodel.itemsperpage;
        if (end > submodel.count)
            end = submodel.count;
        return submodel.data.slice(start, end);
    };
    $scope.addElement = function(sub) {
        var start = (sub.currentPage - 1) * sub.itemsperpage;
        sub.data.splice(start, 0, {tag : sub.type.slice(0, -1), attributes : {type : ''}, children : [], text : ''});
        sub.changed = true;
    }
    $scope.delElement = function(ind, sub) {
        var start = (sub.currentPage - 1) * sub.itemsperpage;
        sub.data.splice(start + ind, 1);
        sub.changed = true;
    };
    $scope.editBtn = function(sub) {
        update_model();
        sub.changed = false;
    };
    $scope.cancelBtn = function() {
        init();
    };
    $scope.addDisplay = function() {
        $scope.vm.model.push({ type : '', data : [], count : 0, currentPage : 1, itemsperpage : 10 });
        sub.changed = true;
    };
}]);


