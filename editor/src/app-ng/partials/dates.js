'use strict';

angular.module('ldmlEdit.dates', [
    'ldmlEdit.service'
  ])
  .controller('DatesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = { calendars : {} };
    $scope.contextuals = { days : 1, months : 2, quarters : 3, monthPatterns : 4, dayPeriods : 5 };
    $scope.formats = { dateFormats : 1, timeFormats : 2 };

    var readContextual = function(el, eltag) {
        var anEl = {}
        // anEl[context.type][width.type][index] = anEltag (full xml element)
        DomService.forEach(el.children, function(aContext) {
            if (aContext.tag != eltag + 'Context')
                return;
            var context = {};
            anEl[aContext.attributes.type] = context;
            var defWidth = '';
            DomService.forEach(aContext.children, function(aWidth) {
                if (aWidth.tag == 'default')
                    defWidth = aWidth.text;
                else if (aWidth.tag == eltag + 'Width') {
                    var width = { elements : [], dflt : false};
                    context[aWidth.attributes.type] = width;
                    DomService.forEach(aWidth.children, function(it) {
                        if (it.tag == eltag)
                            width.elements.push(it);
                    });
                }
            });
            if (context[defWidth])
                context[defWidth].dflt = true;
        });
        return anEl;
    };

    var writeContextual = function(el, eltag, basetag) {
        var res = {tag : eltag, children : [], attributes : {}}
        angular.forEach(el, function(con, conk) {
            var aCon = {tag : basetag + 'Context', children : [], attributes : {type : conk}};
            res.children.push(aCon);
            angular.forEach(con, function(width, widthk) {
                var aWidth = {tag : basetag + 'Width', children : width.elements, atttributes : {type : widthk}};
                aCon.children.push(aWidth);
                if (width.dflt)
                    aCon.children.splice(0, 0, {tag : 'default', text : widthk});
            });
        });
        return res;
    };

    var readFormatLength = function(el) {
        var res = { dflt : false };
        DomService.forEach(el.children, function (f) {
            if (f.tag == 'default')
                res.dflt = f.text;
            else if (f.tag == el.tag.slice(0, -6)) {
                var temp = {}
                DomService.forEach(f.children, function(c) {
                    if (c.tag == 'pattern' || c.tag == 'displayName')
                        temp[c.tag] = c.text;
                });
                res[f.attributes.type] = temp;
            }
        });
        return res;
    };

    var writeFormatLength = function(el, eltag) {
        var res = {tag : eltag = 's', children : []};
        angular.forEach(el, function (f, fk) {
            if (fk == 'dflt') {
                res.children.push({tag : 'default', text : f});
                return;
            }
            var aFormat = {tag : eltag + 'Length', children : [], attributes : {type : fk}};
            res.children.push(aFormat);
            angular.forEach(f, function(c, ck) {
                aFormat.children.push({tag : ck, text : c});
            });
        });
        return res;
    };
        
    var init = function() {
        $scope.vm = { calendars : {}, fields : {}, timeZones : { regions : {}, zone : {}, metazone : {}, temp : {}} };
        $scope.fres = DomService.findLdmlElement(null, "dates");
        if ($scope.fres == null)
            $scope.fres = {tag : 'dates', attributes : {}, children : []};
        DomService.forEach($scope.fres.children, function(aDate) {
            if (aDate.tag == 'calendars') {
                DomService.forEach(aDate.children, function(cal) {
                    if (cal.tag != 'calendar')
                        return;
                    var aCal = { };
                    $scope.vm.calendars[cal.attributes.type] = aCal;
                    DomService.forEach(cal.children, function(el) {
                        if (el.tag in $scope.contextuals) {
                            aCal[el.tag] = readContextual(el, el.tag.slice(0, -1));
                        }
                        else if (el.tag == 'cyclicNameSets') {
                            aCal.cyclics = {};
                            DomService.forEach(el.children, function(aSet) {
                                if (aSet.tag == 'cyclicNameSet')
                                    aCal.cyclics[aSet.attributes.type] = readContextual(aSet, aSet.tag.slice(0, -3));
                            });
                        }
                        else if (el.tag in $scope.formats) {
                            var res = { };
                            var dflt = '';
                            DomService.forEach(el.children, function (aLength) {
                                if (aLength.tag == 'default')
                                    dflt = aLength.text;
                                else if (aLength.tag == el.tag.slice(0, -1) + "Length")
                                    res[aLength.attributes.type] = readFormatLength(aLength);
                            });
                            if (res[dflt])
                                res[dflt].dflt = true;
                            aCal[el.tag.slice(0, -1)] = res;
                        }
                        else if (el.tag == 'dateTimeFormats') {
                            res = { lengths : {}};
                            aCal.dateTimeFormat = res;
                            DomService.forEach(el.children, function (dt) {
                                if (dt.tag == 'dateTimeFormatLength')
                                    res[dt.attributes.type] = readFormatLength(dt);
                                else if (dt.tag == 'availableFormats') {
                                    var avs = {};
                                    DomService.forEach(dt.children, function(c) {
                                        if (dt.tag == 'dateTimeFormatItem')
                                            avs[dt.attributes.id] = dt.text;
                                    });
                                    res.availableitems = avs;
                                }
                                else if (dt.tag == 'appendItems') {
                                    var ais = {};
                                    DomService.forEach(dt.children, function(c) {
                                        if (dt.tag == 'appendItem')
                                            ais[dt.attributes.request] = dt.text;
                                    });
                                    res.appenditems = ais;
                                }
                                else if (dt.tag == 'intervalFormats') {
                                    var is = { items : {}};
                                    DomService.forEach(dt.children, function(c) {
                                        if (dt.tag == 'intervalFormatFallback')
                                            is.fallback = dt.text;
                                        else if (dt.tag != 'intervalFormatItem')
                                            return
                                        var fitem = {};
                                        is.items[dt.attributes.id] = fitem;
                                        DomService.forEach(dt.children, function(d) {
                                            if (dt.tag == 'greatestDifference')
                                                fitem[dt.attributes.id] = dt.text;
                                        });
                                    res.intervals = is;
                                    });
                                }
                            });
                        }
                    });
                });
            }
            else if (aDate.tag == 'fields')
            {
                DomService.forEach(aDate.children, function (f) {
                    if (f.tag != 'field')
                        return;
                    var aField = { relatives : {}, times : {}};
                    $scope.vm.fields[f.attributes.type] = aField;
                    DomService.forEach(f.children, function (el) {
                        if (el.tag == 'displayName')
                            aField.name = el.text;
                        else if (el.tag == 'relative')
                            aField.relatives[el.attributes.type] = el.text;
                        else if (el.tag == 'relativeTime') {
                            var aTime = {};
                            aField.times[el.attributes.type] = aTime;
                            DomService.forEach(el.children, function(t) {
                                if (t.tag == 'relativeTimePattern')
                                    aTime[t.attributes.type] = t.text;
                            });
                        }
                    });
                });
            }
            else if (aDate.tag == 'timeZoneNames')
            {
                DomService.forEach(aDate.children, function(t) {
                    if (t.tag == 'hourFormat' || t.tag == 'gmtFormat' || t.tag == 'gmtZeroFormat' || t.tag == 'fallbackFormat')
                        $scope.vm.timeZones[t.tag] = t.text;
                    else if (t.tag == 'regionFormat')
                        $scope.vm.timeZones.regions[t.attributes && t.attributes.type ? t.attributes.type : 'generic'] = t.text;
                    else if (t.tag == 'zone' || t.tag == 'metazone') {
                        var aZone = {};
                        $scope.vm.timeZones[t.tag][t.attributes.type] = aZone;
                        DomService.forEach(t.children, function(z) {
                            if (z.tag == 'long' || z.tag == 'short') {
                                var info = {};
                                aZone[z.tag] = info;
                                DomService.forEach(z.children, function(i) {
                                    if (i.tag == 'generic' || i.tag == 'standard' || i.tag == 'daylight')
                                        info[i.tag] = i.text;
                                });
                            }
                            else if (z.tag == 'exemplarCity')
                                aZone[z.tag] = z.text;
                        });
                    }
                });
            }
        });
        $scope.vm = $scope.vm;
    };

    var update_model = function() {
        var res = {tag : 'dates', children : []};
        if (Object.keys($scope.vm.calenders).length()) {
            var aCals = {tag : 'calendars', children : []};
            res.children.push(aCals);
            angular.forEach($scope.vm.calendars, function(cal, calname) {
                var aCal = {tag : 'calendar', children : [], attributes : {type : calname}};
                aCals.children.push(aCal);
                angular.forEach($scope.contextuals, function(cont) {
                    if (cal[cont])
                        aCal.children.push(writeContextual(cal[cont], cont, cont.slice(0, -1)));
                });
                if (cal.cyclics) {
                    var aCycleSet = {tag : 'cyclicNameSets', children : []};
                    aCal.children.push(aCycleSet);
                    angular.forEach(cal.cyclics, function (cycle, cyclek) {
                        var aCycle = writeContextual(cycle, 'cyclicNameSet', 'cyclicName');
                        aCycle.attributes.type = cyclek;
                        aCycleSet.children.push(aCycle);
                    });
                }
                angular.forEach($scope.formats, function(f) {
                    var tag = f.slice(0, -1);
                    if (cal[tag])
                        aCal.children.push(writeFormat(cal[tag], tag));
                });
                if (cal.dateTimeFormat) {
                    var aDate = {tag : 'dateTimeFormats', children : []};
                    aCal.children.push(aDate);
                    angular.forEach(cal.dateTimeFormat, function (dt, dtk) {
                        if (dtk == 'availableitems' || dtk == 'appenditems') {
                            var tag = dtk == 'availableitems' ? 'availableFormat' : 'appendItem';
                            var anAvail = {tag : tag + 's', children : []};
                            aDate.children.push(anAvail);
                            angular.forEach(dt, function(dti, dtik) {
                                var temp = {tag : (dtk == 'availableitems' ? 'dateFormatItem' : tag),
                                            text : dti, attributes : {}};
                                anAvail.children.push(temp);
                                if (dtk == 'availableitems')
                                    temp.attributes.id = dtik;
                                else
                                    temp.attributes.request = dtik;
                            });
                        }
                        if (dtk == 'intervals') {
                            var aIF = {tag : 'intervalFormats', children : []};
                            aDate.children.push(aIF);
                            if (dt.fallback)
                                aIF.children.push({tag : 'intervalFormatFallback', text : dt.fallback});
                            angular.forEach(dt.items, function(item, itemk) {
                                var anItem = {tag : 'intervalFormatItem', children : [], attributes : {id : itemk}};
                                aIF.children.push(anItem);
                                angular.forEach(item, function(gdiff, gdiffk) {
                                    anItem.children.push({tag : 'greatestDifference', text : gdiff, attributes : {id : diffk}});
                                });
                            });
                        }
                        else if (dtk == 'dflt') {
                            aDate.children.push({tag : 'default', text : dt});
                        }
                        else {      // dateTimeFormatLength
                            var aLength = {tag : 'dateTimeFormatLength', children : [], attributes : {type : dtk}};
                            aDate.children.push(aLength);
                            angular.forEach(dt, function(c, ck) {
                                var temp = {tag : 'dateTimeFormat', children : [], attributes : {type : ck}};
                                aLength.children.push(temp);
                                angular.forEach(c, function(el, elk) {
                                    temp.children.push({tag : elk, text : el});
                                });
                            });
                        }
                    });
                }
            });
        }
        if (Object.keys($scope.vm.fields).length) {
            var aFields = {tag : 'fields', children : []};
            res.children.push(aFields);
            angular.forEach($scope.vm.fields, function (field, fieldk) {
                var aField = {tag : 'field', children : [], attributes : {type : fieldk}};
                aFields.children.push(aField);
                if (field.name)
                    aField.children.push({tag : 'displayName', text : field.name});
                angular.forEach(field.relatives, function (rel, relk) {
                    aField.children.push({tag : 'relative', text : rel, attributes : { type : relk}});
                });
                angular.forEach(field.times, function (rel, relk) {
                    var aTime = {tag : 'relativeTime', children : [], attributes : { type : relk}};
                    aField.chilren.push(aTime);
                    angular.forEach(rel, function(pat, patk) {
                        aTime.children.push({tag : 'relativeTimePattern', text : pat, attributes : {type : patk}});
                    });
                });
            });
        }
        if (Object.keys($scope.vm.timeZones).length) {
            var aTZ = {tag : 'timeZoneNames', children : [] };
            res.children.push(aTZ);
            angular.forEach($scope.vm.timeZones, function (el, elk) {
                if (elk == 'hourFormat' || elk == 'gmtFormat' || elk == 'gmtZeroFormat' || elk == 'fallbackFormat')
                    aTZ.children.push({tag : elk, text : el});
                else if (elk == 'regions') {
                    angular.forEach(el, function(reg, regk) {
                        var aReg = {tag : 'regionFormat', text : reg, attributes : {}};
                        aTZ.children.push(aReg);
                        if (regk != 'generic')
                            aReg.attributes.type = regk;
                    });
                }
                else if (elk == 'zone' || elk == 'metazone') {
                    angular.forEach(el, function (z, zk) {
                        var aZone = {tag : elk, attributes : {type : zk}, children : []};
                        aTZ.children.push(aZone);
                        angular.forEach(z, function (c, ck) {
                            aChild = {tag : ck, children : []};
                            aZone.children.push(aChild);
                            if (ck == 'exemplarCity') {
                                aChild.text = c;
                                return;
                            }
                            angular.forEach(c, function (t, tk) {
                                aChild.children.push({tag : tk, text : t});
                            });
                        });
                    });
                }
            });
        }
    };

    init();

    $scope.addCalendar = function() {
        if ($scope.newcal && !$scope.vm.calendars[$scope.newcal]) {
            $scope.vm.calendars[$scope.newcal] = {};
            vm.temp.currcals = $scope.newcal;
        }
    };
    $scope.addContext = function(currcal, id) {
    };
    $scope.addWidth = function(currcal, id, currcontext) {
    };
}]);
