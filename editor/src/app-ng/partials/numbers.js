'use strict';

angular.module('ldmlEdit.numbers', [
    'ldmlEdit.service'
  ])
  .controller('NumbersCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = {currencies : [], symbols : {}};
    $scope.symbolTypes = [
        {tag : 'decimal', label : 'Decimal Separator'},
        {tag : 'group', label : 'Group Separator'},
        {tag : 'list', label : 'List Separator'},
        {tag : 'percentSign', label : 'Percent Sign'},
        {tag : 'patternDigit', label : 'Digit Pattern'},
        {tag : 'minusSign', label : 'Minus Sign'},
        {tag : 'plusSign', label : 'Plus Sign'},
        {tag : 'exponential', label : 'Exponent Separator'},
        {tag : 'superscriptingExponent', label : 'Use Superscript Exponents?'},
        {tag : 'perMille', label : 'Per Mille Sign'},
        {tag : 'infinity', label : 'Infinity Sign'},
        {tag : 'nan', label : 'Not A Number Sign'},
        {tag : 'currencyDecimal', label : 'Currency Decimal Separator'},
        {tag : 'timeSeparator', label : 'Time Format Separator'}
    ];
    $scope.formatTypes = {
        decimalFormats : {id : 'decimalFormat', title : 'Decimal Formats', hasContexts : false },
        scientificFormats : {id : 'scientificFormat', title : 'Scientific Formats', hasContexts : false},
        percentFormats : {id : 'percentFormat', title : 'Percentage Formats', hasContext : false},
        currencyFormats : {id : 'currencyFormat', title : 'Currency Formats', hasContext : true}
    };
    $scope.lengthTypes = ['full', 'long', 'medium', 'short'];
    $scope.countTypes = ['zero', 'one', 'two', 'few', 'many', 'other'];
    var formatsList = ['decimalFormats', 'scientificFormats', 'percentFormats', 'currencyFormats'];
    angular.forEach($scope.formatTypes, function (f) {
        $scope.vm[f.id] = [];
    });
    var currencyMap = {currencyMatch : 'match', surroundingMatch : 'surrounding', insertBetween : 'insert'};

    var init = function() {
        $scope.vm.newlang = '';
        $scope.fres = DomService.findLdmlElement(null, "numbers");
        if ($scope.fres == null)
            $scope.fres = {tag : 'numbers', attributes : {}, children : []};
        $scope.vm = {currencies : [], symbols : {}};
        DomService.forEach($scope.fres.children, function (aNumber) {
            if (aNumber.tag == 'defaultNumberingSystem' || aNumber.tag == 'minimumGroupingDigits') {
                $scope.vm[aNumber.tag] = aNumber;
            } else if (aNumber.tag == 'otherNumberingSystems') {
                $scope.vm.otherNumberingSystems = [];
                DomService.forEach(aNumber.children, function (c) {
                    if (c.tag == 'native' || c.tag == 'traditional' || c.tag == 'finance')
                        $scope.vm.otherNumberingSystems.push(c);
                });
            } else if (aNumber.tag == 'symbols') {
                $scope.vm.symbolSystem = aNumber.attributes.numberSystem;
                DomService.forEach(aNumber.children, function (c) {
                    if (c != 'special')
                        $scope.vm.symbols[c.tag] = c;
                });
            } else if (aNumber.tag == 'currencies') {
                DomService.forEach(aNumber.children, function (curr) {
                    if (curr.tag == 'default')
                        $scope.vm.defaultCurrency = curr.text;
                    else if (curr.tag == 'currency') {
                        var thisCurr = { type : curr.attributes.type, symbol : '', name : '', subpatterns : [], subnames : [] };
                        $scope.vm.currencies.push(thisCurr);
                        DomService.forEach(curr.children, function(c) {
                            if (c.tag == 'displayName') {
                                if ('count' in c.attributes)
                                    thisCurr.subnames.push(c);
                                else
                                    thisCurr.name = c.text;
                            } else if (c.tag == 'pattern') {
                                if ('count' in c.attributes)
                                    thisCurr.subpatterns.push(c);
                                else
                                    thisCurr.pattern = c.text;
                            } else if (c.tag == 'symbol') {
                                thisCurr.symbol = c.text;
                            }
                        });
                    }
                });
            } else if (aNumber.tag in $scope.formatTypes) {
                var formats = [];
                var aType = $scope.formatTypes[aNumber.tag];
                var sys = aNumber.attributes.numberSystem
                if ($scope.vm[aType.id] == null)
                    $scope.vm[aType.id] = {};
                $scope.vm[aType.id][sys] = { formats : formats, id : sys };
                DomService.forEach(aNumber.children, function (l) {
                    if (l.tag == 'default')
                        $scope.vm.defaults[aType.id][sys] = l.attributes.type;
                    else if (l.tag == aType.id + "Length") {
                        var curr = {type : l.attributes.type, subpatterns : []};
                        formats.push(curr);
                        DomService.forEach(l.children, function (f) {
                            if (f.tag == aType.id) {
                                DomService.forEach(f.children, function (c) {
                                    if (c.tag == 'pattern') {
                                        if ('count' in c.attributes)
                                            curr.subpatterns.push(c);
                                        else
                                            curr.pattern = c.text;
                                    }
                                });
                            }
                        });
                    }
                    else if (l.tag == 'currencySpacing') {
                        DomService.forEach(l.children, function(s) {
                            var type = s.tag.slice(0, -8);
                            var curr = {};
                            $scope.vm[aType.id][sys][type] = curr;
                            DomService.forEach(s.children, function(c) {
                                curr[currencyMap[c.tag]] = c.text;
                            });
                        });
                    }
                });
            } else if (aNumber.tag == 'miscPatterns') {
                $scope.vm.misc = {}
                DomService.forEach(aNumber.children, function (c) {
                    if (c.tag == 'pattern')
                        $scope.vm.misc[c.attributes.type] = c.text;
                });
            }
        });
    };
    init();

    var update_model = function() {
        $scope.fres = {tag : 'numbers', attributes : {}, children : []};
        if ($scope.vm.defaultNumberingSystem && $scope.vm.defaultNumberingSystem.text != '')
            $scope.fres.children.push($scope.vm.defaultNumberingSystem);
        if ($scope.vm.minimumGroupingDigits && $scope.vm.minimumGroupingDigits.text != '')
            $scope.fres.children.push($scope.vm.minimumGroupingDigits);
        if ($scope.vm.otherNumberingSystems) {
            var other = {tag : 'otherNumberingSystems', attributes : {}, children : []};
            angular.forEach($scope.vm.otherNumberingSystems, function(s) {
                if (s.text)
                    other.children.push(s);
            });
            if (other.children.length() > 0)
                $scope.vm.otherNumberingSystems = other;
        }
        if ($scope.vm.symbols) {
            var other = {tag : 'symbols', attributes : {}, children : []};
            var addme = false;
            if ($scope.vm.symbolSystem) {
                other.attributes.numberSystem = $scope.vm.symbolSystem;
                addme = true;
            }
            angular.forEach($scope.vm.symbols, function (s) {
                if (s.text) {
                    other.children.push(s);
                    addme = true;
                }
            });
            if (addme)
                $scope.fres.children.push(other);
        }
        if ($scope.vm.misc) {
            var other = {tag : 'miscPatterns', attributes : {}, children : []};
            var addme = false;
            angular.forEach($scope.vm.misc, function (v, k) {
                if (v) {
                    other.children.push({tag : 'pattern', attributes : { type : k}, text : v});
                    addme = true;
                }
            });
            if (addme)
                $scope.fres.children.push(other);
        }
        if ($scope.vm.currencies) {
            var other = {tag : 'currencies', attributes : {}, children : []};
            var addme = false;
            if ($scope.vm.defaultCurrency)
                other.children.push({tag : 'default', text : $scope.vm.defaultCurrency});
            angular.forEach($scope.vm.currencies, function (c) {
                var thisCurr = {tag : 'currency', attributes : {type : c.type}, children : [], text : ''};
                angular.forEach(c.subnames, function (s) {
                    if (s.text)
                        thisCurr.children.push(s);
                });
                if (c.pattern)
                    thisCurr.children.push({tag : 'pattern', text : c.pattern});
                angular.forEach(c.subpatterns, function (s) {
                    if (s.text)
                        thisCurr.children.push(s)
                });
                if (c.symbol)
                    thisCurr.children.push({tag : 'symbol', text : c.symbol});
                other.children.push(thisCurr);
                addme = true;
            });
            if (addme)
                $scope.fres.children.push(other);
        }
        angular.forEach($scope.formatTypes, function (t, k) {
            angular.forEach($scope.vm[t.id], function (a, n) {
                var other = {tag : k, children : [], attributes : { numberSystem : n}};
                var addme = false;
                if ($scope.vm.defaults[t.id][n]) {
                    other.children.push({tag : 'default', attributes : {type : $scope.vm.defaults[t.id]}});
                    addme = true;
                }
                angular.forEach(a.formats, function(f) {
                    var format = {tag : t.id + "Length", attributes : {type : f.type}, children : []};
                    var formatc = {tag : t.id, children : []};
                    format.children.push(formatc);
                    if (f.pattern)
                        formatc.children.push({tag : 'pattern', text : f.pattern});
                    angular.forEach(f.subpatterns, function (s) {
                        if (s.text)
                            formatc.children.push(s);
                    });
                    other.children.push(format);
                    addme = true;
                });
                if (t.id == 'currency') {
                    var temp = {tag : 'currencySpacing', children : []};
                    angular.forEach(['before', 'after'], function(f) {
                        var res = {tag : f + 'Currency', children : []}
                        if (f in a) {
                            angular.forEach(currencyMap, function (v, k) {
                                res.children.push({tag : k, text : a[f][v]});
                            });
                        }
                        if (res.children.length)
                            temp.children.push(res);
                    });
                    if (temp.children.length)
                        other.children.push(temp);
                if (addme);
                    $scope.fres.children.push(other);
                }
            });
        });
        DomService.updateTopLevel($scope.fres);
    };
    $scope.addlang = function(id) {
        if ($scope.vm.newlang) {
            $scope.vm[id][$scope.vm.newlang] = {formats : [], id : $scope.vm.newlang};
        }
    };
    $scope.addNumSystem = function() {
        if ($scope.vm.otherNumberingSystems == null)
            $scope.vm.otherNumberingSystems = [];
        $scope.vm.otherNumberingSystems.push({tag : '', attributes : {}, text : ''});
        $scope.vm.changed = true;
    };
    $scope.delNumSystem = function(ind) {
        $scope.vm.otherNumberingSystems.splice(ind, 1);
        $scope.vm.changed = true;
    };
    $scope.editChange = function() {
        $scope.vm.changed = true;
    };
    $scope.cancelBtn = function() {
        init();
        $scope.vm.changed = false;
        $scope.subOpen = '';
    };
    $scope.addCurrency = function() {
        $scope.vm.currencies.push({type : '', name : '', pattern : '', symbol : '', subnames : [], subpatterns : []});
        $scope.vm.changed = true;
    };
    $scope.addFormat = function(f, id) {
        $scope.vm[f.id][id].formats.push({type : '', pattern : '', subpatterns : []});
        $scope.vm.changed = true;
    };
    $scope.delElement = function (e, ind) {
        e.splice(ind, 1);
        $scope.vm.changed = true;
    };
    $scope.delFormat = function(f, ind) {
        $scope.vm[f.id].splice(ind, 1);
        $scope.vm.changed = true;
    };
    $scope.openCompact = function(l, t) {
        if (l.subOpen != t) {
            l.subOpen = t;
            l.subs = l['sub' + t + 's'];
            if (!l.subs.length) 
                $scope.addSub(l, t);
        } else {
            l.subOpen = '';
        }
    };
    $scope.delSub = function(l, ind, t) {
        l['sub' + t + 's'].splice(ind, 1);
        $scope.vm.changed = true;
    };
    $scope.addSub = function(l, t) {
        l['sub' + t + 's'].push({tag : 'pattern', attributes : {}, text : ''});
        $scope.vm.changed = true;
    };
}]);
