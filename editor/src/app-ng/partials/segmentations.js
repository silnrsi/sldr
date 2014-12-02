'use strict';

angular.module('ldmlEdit.segmentations', [
    'ldmlEdit.service'
  ])
  .controller('SegmentationsCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.sublists = {'variables' : {title : 'Variables', tag : 'variable'}, 'segmentRules' : {title: 'Rules', tag : 'rule'}};
    $scope.types = ['variables', 'segmentRules'];

    var init = function(e) {
        $scope.fres = DomService.findLdmlElement(null, "segmentations");
        if ($scope.fres == null) 
            $scope.fres = {'tag' : 'segmentations', 'attributes' : {}, 'children' : []};
        $scope.vm.model = [];
        DomService.forEach($scope.fres.children, function(seg) {
            if (seg.tag == "segmentation") {
                var m = {variables : [], rules : [], type : seg.attributes['type']};
                DomService.forEach(seg.children, function(e) {
                    if (e.tag in $scope.sublists) {
                        m[e.tag] = angular.copy(e.children);
                        DomService.forEach(m[e.tag], function (v) {
                            if (e.tag == 'segmentRules')
                                v.sortkey = parseFloat(v.attributes.id);
                            else
                                v.sortkey = v.attributes.id;
                        });
                    }
                });
                m.children = seg.children;
                $scope.vm.model.push(m);
            }
        });
    };
    init();

    var update_model = function() {
        $scope.fres.children = [];
        angular.forEach($scope.vm.model, function(s) {
            var kids = [];
            angular.forEach(s.children, function (c) {
                if (c.tag != 'variables' && c.tag != 'segmentRules')
                    kids.push(c);
            });
            for (t in $scope.sublists) {
                if (s[t].length > 0)
                    kids.push({tag : t, attributes : {}, children : s[t]});
            }
            $scope.fres.children.push({tag : 'segmentation', attributes : {type : s.type}, children : kids});
        });
        DomService.updateTopLevel($scope.fres);
    };

    $scope.saveBtn = function() {
        $scope.vm.changed = false;
    };
    $scope.cancelBtn = function() {
        init();
        $scope.vm.changed = false;
    };
    $scope.editChange = function() {
        $scope.vm.changed = true;
    };
    $scope.addElement = function(type, seg) {
        var res = {tag : $scope.sublists[type].tag, attributes : {id : ''}, text : ''};
        seg[type].push(res);
        $scope.vm.changed = true;
    };
    $scope.delElement = function(index, list) {
        list.splice(index, 1);
        $scope.vm.changed = true;
    };
    $scope.upBtn = function(index, list) {
        list.splice(index-1, 2, list[index], list[index-1]);
        $scope.vm.changed = true;
    };
    $scope.downBtn = function(index, list) {
        list.splice(index, 2, list[index+1], list[index]);
        $scope.vm.changed = true;
    };
    $scope.addSegment = function() {
        $scope.vm.model.push({variables : [], rules : [], type : ''});
        $scope.vm.changed = true;
    };
}]);

    
        
