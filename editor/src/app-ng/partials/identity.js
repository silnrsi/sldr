'use strict';

angular.module('ldmlEdit.identity', [
    'ldmlEdit.service'
  ])
  .controller('IdentityCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {};
    $scope.help = '';
    var localmap = {
        'language' : 'type',
        'script' : 'type',
        'territory' : 'type',
        'variant' : 'type',
        'version' : 'number',
        'generation' : 'date'
    };
    var specials = [ 'revid', 'windowsLCID', 'defaultRegion', 'variantName', 'usage' ];

    var init = function(e) {
        $scope.fres = DomService.findElement(null, "identity");
        if ($scope.fres == null)
            $scope.fres = {'tag' : 'identity', 'attributes' : {}, 'children' : []};
        var model = {};
        for (var key in localmap) {
            var e = DomService.findElement($scope.fres, key);
            if (e != null)
                model[key] = e.attributes[localmap[key]];
        }
        var e = DomService.findElement($scope.fres, "version");
        if (e != null)
            model['versionText'] = e.text;
        $scope.vm.model = model;
        var spec = DomService.findElements($scope.fres, ["special", "sil:identity"]);
        if (spec != null) {
            angular.forEach(specials, function (s) {
                if (spec.attributes[s] != null)
                    model[s] = spec.attributes[s];
            });
        }
        $scope.vm.model.changed = false;
        if ($scope.$$phase != "$apply" && $scope.$$phase != "$digest")
            $scope.$apply();
    };
    $scope.$on('dom', init);
    init();

    $scope.editBtn = function () {
        var idchildren = [];
        for (var key in localmap) {
            if ($scope.vm.model[key] != null && $scope.vm.model[key].length > 0) {
                var res = {'tag' : key, 'attributes' : { }, 'children' : []};
                res.attributes[localmap[key]] = $scope.vm.model[key];
                idchildren.push(res);
            }
        }
        var specattribs = {};
        angular.forEach(specials, function (s) {
            if ($scope.vm.model[s] != null && $scope.vm.model[s].length > 0)
                specattribs[s] = $scope.vm.model[s];
        });
        if (Object.keys(specattribs).length > 0) 
            idchildren.push({'tag' : 'special', 'attributes' : {}, 'children' : [
                {'tag' : 'sil:identity', 'attributes' : specattribs, 'children' : []} ]});
        $scope.fres.children = idchildren;
        DomService.updateTopLevel($scope.fres);
        $scope.vm.model.changed = false;
    };
    $scope.cancelBtn = function() {
        $scope.vm.model.changed = false;
        init();
        $scope.help = '';
    };
    $scope.editChange = function() {
        $scope.vm.model.changed = true;
        $scope.help = '';
    }
}]);

