'use strict';

angular.module('ldmlEdit.delimiters', [
    'ldmlEdit.service'
  ])
  .controller('DelimitersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.vm.quotes = [ {}, {} ];
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
        if ($scope.fres == null) return;
        for (var k in quotemap) {
            curr = DomService.findElement($scope.fres, k);
            if (curr != null)
                $scope.vm.quotes[quotemap[k][0]][quotemap[k][1]] = curr.text;
        }
        var spec = DomService.findElements($scope.fres, ["special", "sil:quotation-marks"]);
        if (spec != null) {
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
        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();
}]);
