'use strict';

angular.module('ldmlEdit.delimiters', [
    'ldmlEdit.service'
  ])
  .controller('DelimitersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.quotes = [ {}, {} ];
    $scope.vm.puncs = [];
    $scope.vm.pairs = [];
    $scope.vm.paraContType = null;
    $scope.vm.paraContMark = null;
    var quotemap = {
        'quotationStart' : [0, 'start'],
        'quotationEnd' : [0, 'end'],
        'alternateQuotationStart' : [1, 'start'],
        'alternateQuotationEnd' : [1, 'end']
    };
    var silquotemap = {
        'sil:quotationContinue' : [0, 'continue'],
        'sil:alternateQuotationContinue' : [1, 'continue']
    };

    var init = function(e) {
        var curr;
        $scope.fres = DomService.findElement(null, "delimiters");
        if ($scope.fres == null)
            $scope.fres = {tag : 'delimiters', attributes : {}, children : []};
        for (var k in quotemap) {
            curr = DomService.findElement($scope.fres, k);
            if (curr != null)
                $scope.vm.quotes[quotemap[k][0]][quotemap[k][1]] = curr.text;
        }
        var spec = DomService.findElements($scope.fres, ["special", "sil:quotation-marks"]);
        if (spec != null) {
            if ('paraContinueType' in spec.attributes)
                $scope.vm.paraContType = spec.attributes['paraContinueType'];
            if ('paraContinueMark' in spec.attributes)
                $scope.vm.paraContMark = spec.attributes['paraContinueMark'];

            for (var k in silquotemap) {
                curr = DomService.findElement(spec, k);
                if (curr != null)
                    $scope.vm.quotes[silquotemap[k][0]][silquotemap[k][1]] = curr.text;
            }
            for (var i = 0; i < spec.children; i++)
            {
                if (spec.children[i].tag == 'sil:quotation')
                    $scope.vm.quotes.push(angular.copy(spec.children[i].attributes));
            }
        }
        spec = DomService.findElements($scope.fres, ["special", "sil:punctuation-patterns"]);
        if (spec != null)
        {
            var puncs = [];
            angular.forEach(spec.children, function (p) {
                if (p.tag == 'sil:punctuation-pattern')
                    puncs.push(p);
            });
            $scope.vm.puncs = puncs;
        }
        spec = DomService.findElements($scope.fres, ["special", "sil:matched-pairs"]);
        if (spec != null)
        {
            var pairs = [];
            angular.forEach(spec.children, function (m) {
                if (m.tag == 'sil:matched-pair')
                    pairs.push(m);
            });
            $scope.vm.pairs = pairs;
        }
        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();

    var update_model = function() {
        var special = {tag : 'special', attributes : {}, children : []};
        $scope.fres.children = [];
        for (var k in quotemap)
            $scope.fres.children.push({tag : k, attributes : {}, text : $scope.vm.quotes[quotemap[k][0]][quotemap[k][1]] });
        if ($scope.vm.quotes.length > 2 || ($scope.vm.paraContType != null && $scope.vm.paraContType != 'None') || $scope.vm.paraContMark != null) {
            var spec = {tag : 'sil:quotation-marks', attributes : {}, children : []};
            if ($scope.vm.paraContType != null && $scope.vm.paraContType != 'None')
                spec.attributes.paraContinueType = $scope.vm.paraContType;
            if ($scope.vm.paraContMark != null)
                spec.attributes.paraContinueMark = $scope.vm.paraContMark;
            for (var i = 2; i < $scope.vm.quotes.length; i++) {
                var s = $scope.vm.quotes[i];
                spec.children.push({tag : 'sil:quotation', attributes : { open : s.start, close : s.end, 'continue' : s['continue'] } });
            }
            special.children.push(spec);
        }
        if ($scope.vm.pairs.length > 0) {
            var spec = {tag : 'sil:matched-pairs', attributes : {}, children : []};
            angular.forEach($scope.vm.pairs, function(p) {
                spec.children.push(p);
            });
            special.children.push(spec);
        }
        if ($scope.vm.puncs.length > 0) {
            var spec = {tag : 'sil:punctuation-patterns', attributes : {}, children : []};
            angular.forEach($scope.vm.puncs, function(p) {
                spec.children.push(p);
            });
            special.children.push(spec);
        }
        if (special.children.length > 0)
            $scope.fres.children.push(special);
        DomService.updateTopLevel($scope.fres);
    };
            
    $scope.addQuote = function() {
        $scope.vm.quotes.push({start : '', end : '', 'continue' : ''});
    };
    $scope.delQuote = function(ind) {
        $scope.vm.quotes.splice(ind, 1);
    };
    $scope.saveBtn = function() {
        update_model();
    };
    $scope.cancelBtn = function() {
        init();
    };
    $scope.addPunc = function() {
        $scope.vm.puncs.push({tag : 'sil:punctuation-pattern', attributes : { string : '' }});
    };
    $scope.delPunc = function(i) {
        $scope.vm.puncs.splice(i, 1);
    };
    $scope.addPair = function() {
        $scope.vm.pairs.push({tag : 'sil:matched-pair', attributes : { open : '', close : '' }});
    };
    $scope.delPair = function(i) {
        $scope.vm.pairs.splice(i, 1);
    };

}]);
