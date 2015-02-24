'use strict';

angular.module('ldmlEdit.dates', [
    'ldmlEdit.service'
  ])
  .controller('DatesCtrl', [ '$scope', 'DomService', function($scope, DomService) {

    $scope.vm = { calendars : {}, changed : false };
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
                            width.elements.push(angular.copy(it));
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
                var aWidth = {tag : basetag + 'Width', children : width.elements, attributes : {type : widthk}};
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
                        temp[c.tag] = angular.copy(c);
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
                res.children.push({tag : 'default', text : fk});
                return;
            }
            var aFormat = {tag : eltag + 'Length', children : [], attributes : {type : fk}};
            res.children.push(aFormat);
            angular.forEach(f, function(v) {
                aFormat.children.push(angular.copy(v));
            });
        });
        return res;
    };
        
    var init = function() {
        $scope.vm = { calendars : {}, fields : {}, timeZones : { regions : [], zone : {}, metazone : {}, temp : {}} };
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
                        else if (el.tag == 'eras') {
                            var eras = {};
                            aCal.eras = eras;
                            DomService.forEach(el.children, function(er) {
                                if (er.tag.slice(0, 3) == 'era') {
                                    var anEra = [];
                                    eras[er.tag] = anEra;
                                    DomService.forEach(er.children, function (e) {
                                        if (e.tag == 'era')
                                            anEra.push(angular.copy(e));
                                    });
                                }
                            });
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
                                    res.lengths[dt.attributes.type] = readFormatLength(dt);
                                else if (dt.tag == 'availableFormats') {
                                    var avs = [];
                                    DomService.forEach(dt.children, function(c) {
                                        if (c.tag == 'dateFormatItem')
                                            avs.push(angular.copy(c));
                                    });
                                    res.availableitems = avs;
                                }
                                else if (dt.tag == 'appendItems') {
                                    var ais = [];
                                    DomService.forEach(dt.children, function(c) {
                                        if (c.tag == 'appendItem')
                                            ais.push(angular.copy(c));
                                    });
                                    res.appenditems = ais;
                                }
                                else if (dt.tag == 'intervalFormats') {
                                    var is = { items : {}};
                                    DomService.forEach(dt.children, function(c) {
                                        if (c.tag == 'intervalFormatFallback')
                                            is.fallback = c.text;
                                        if (c.tag != 'intervalFormatItem')
                                            return
                                        var fitem = [];
                                        is.items[c.attributes.id] = fitem;
                                        DomService.forEach(c.children, function(d) {
                                            if (d.tag == 'greatestDifference')
                                                fitem.push(angular.copy(d));
                                        });
                                    });
                                    res.intervals = is;
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
                    var aField = { relatives : [], times : []};
                    $scope.vm.fields[f.attributes.type] = aField;
                    DomService.forEach(f.children, function (el) {
                        if (el.tag == 'displayName')
                            aField.name = el.text;
                        else if (el.tag == 'relative')
                            aField.relatives.push(angular.copy(el));
                        else if (el.tag == 'relativeTime') {
                            var aTime = {type: el.attributes.type, patterns : []};
                            aField.times.push(aTime);
                            DomService.forEach(el.children, function(t) {
                                if (t.tag == 'relativeTimePattern')
                                    aTime.patterns.push(angular.copy(t));
                            });
                        }
                    });
                });
            }
            else if (aDate.tag == 'timeZoneNames')
            {
                DomService.forEach(aDate.children, function(t) {
                    if (t.tag == 'hourFormat' || t.tag == 'gmtFormat' || t.tag == 'gmtZeroFormat' || t.tag == 'fallbackFormat')
                        $scope.vm.timeZones[t.tag] = t;
                    else if (t.tag == 'regionFormat') {
                        var temp = angular.copy(t);
                        $scope.vm.timeZones.regions.push(temp);
                        if (!temp.attributes)
                            temp.attributes = {};
                        if (!temp.attributes.type)
                            temp.attributes.type = 'generic';
                    }
                    else if (t.tag == 'zone' || t.tag == 'metazone') {
                        var aZone = {};
                        $scope.vm.timeZones[t.tag][t.attributes.type] = aZone;
                        DomService.forEach(t.children, function(z) {
                            if (z.tag == 'long' || z.tag == 'short') {
                                var info = {};
                                aZone[z.tag] = info;
                                DomService.forEach(z.children, function(i) {
                                    if (i.tag == 'generic' || i.tag == 'standard' || i.tag == 'daylight')
                                        info[i.tag] = angular.copy(i);
                                });
                            }
                            else if (z.tag == 'exemplarCity')
                                aZone[z.tag] = angular.copy(z);
                        });
                    }
                });
            }
        });
    };

    var update_model = function() {
        if (!$scope.fres)
            $scope.fres = {tag : 'dates', children : []}
        if (Object.keys($scope.vm.calendars).length) {
            var aCals = null;
            angular.forEach($scope.fres.children, function(c) {
                if (c.tag == 'calendars')
                    aCals = c;
            });
            if (!aCals) {
                aCals = {tag : 'calendars', children : []};
                $scope.fres.children.push(aCals);
            }
            angular.forEach($scope.vm.calendars, function(cal, calname) {
                var aCal = null;
                angular.forEach(aCals.children, function(c) {
                    if (c.tag == 'calendar' && c.attributes.type == calname)
                        aCal = c;
                });
                if (!aCal) {
                    aCal = {tag : 'calendar', children : [], attributes : {type : calname}};
                    aCals.children.push(aCal);
                }
                aCal.children = [];
                angular.forEach($scope.contextuals, function(v, cont) {
                    if (cal[cont])
                        aCal.children.push(writeContextual(cal[cont], cont, cont.slice(0, -1)));
                });
                if (cal.eras) {
                    var anEras = {tag : 'eras', children : []};
                    angular.forEach(cal.eras, function (era, erak) {
                        var anEra = {tag : erak, children : era };
                        anEras.children.push(anEra);
                    });
                }
                if (cal.cyclics) {
                    var aCycleSet = {tag : 'cyclicNameSets', children : []};
                    aCal.children.push(aCycleSet);
                    angular.forEach(cal.cyclics, function (cycle, cyclek) {
                        var aCycle = writeContextual(cycle, 'cyclicNameSet', 'cyclicName');
                        aCycle.attributes.type = cyclek;
                        aCycleSet.children.push(aCycle);
                    });
                }
                angular.forEach($scope.formats, function(v, f) {
                    var tag = f.slice(0, -1);
                    if (cal[tag])
                        aCal.children.push(writeFormatLength(cal[tag], tag));
                });
                if (cal.dateTimeFormat) {
                    var aDate = {tag : 'dateTimeFormats', children : []};
                    aCal.children.push(aDate);
                    angular.forEach(cal.dateTimeFormat, function (dt, dtk) {
                        if (dtk == 'availableitems' || dtk == 'appenditems') {
                            var tag = dtk == 'availableitems' ? 'availableFormat' : 'appendItem';
                            var anAvail = {tag : tag + 's', children : dt};
                            aDate.children.push(anAvail);
                        }
                        if (dtk == 'intervals') {
                            var aIF = {tag : 'intervalFormats', children : []};
                            aDate.children.push(aIF);
                            if (dt.fallback)
                                aIF.children.push({tag : 'intervalFormatFallback', text : dt.fallback});
                            angular.forEach(dt.items, function(item, itemk) {
                                var anItem = {tag : 'intervalFormatItem', children : item, attributes : {id : itemk}};
                                aIF.children.push(anItem);
                            });
                        }
                        else if (dtk == 'dflt') {
                            aDate.children.push({tag : 'default', text : dt});
                        }
                        else if (dtk == 'lengths') {      // dateTimeFormatLength
                            angular.forEach(dt, function (len, lenk) {
                                var aLength = {tag : 'dateTimeFormatLength', children : [], attributes : {type : lenk}};
                                aDate.children.push(aLength);
                                angular.forEach(len, function(c, ck) {
                                    var temp = {tag : 'dateTimeFormat', children : c, attributes : {type : ck}};
                                    aLength.children.push(temp);
                                });
                            });
                        }
                    });
                }
            });
        }
        if (Object.keys($scope.vm.fields).length) {
            var aFields = null;
            angular.forEach($scope.fres.children, function(c) {
                if (c.tag == 'fields')
                    aFields = c;
            });
            if (!aFields) {
                aFields = {tag : 'fields', children : []};
                $scope.fres.children.push(aFields);
            }
            aFields.children = [];
            angular.forEach($scope.vm.fields, function (field, fieldk) {
                var aField = {tag : 'field', children : [], attributes : {type : fieldk}};
                aFields.children.push(aField);
                if (field.name)
                    aField.children.push({tag : 'displayName', children : field.relatives, text : field.name});
                angular.forEach(field.relatives, function(el) {
                    aField.children.push(el);
                });
                angular.forEach(field.times, function (rel) {
                    var aTime = {tag : 'relativeTime', children : rel.patterns, attributes : { type : rel.type}};
                    aField.children.push(aTime);
                });
            });
        }
        if (Object.keys($scope.vm.timeZones).length) {
            var aTZ = null;
            angular.forEach($scope.fres.children, function(c) {
                if (c.tag == 'timeZoneNames')
                    aTZ = c;
            });
            if (!aTZ) {
                aTZ = {tag : 'timeZoneNames', children : [] };
                $scope.fres.children.push(aTZ);
            }
            aTZ.children = [];
            angular.forEach($scope.vm.timeZones, function (el, elk) {
                if (elk == 'hourFormat' || elk == 'gmtFormat' || elk == 'gmtZeroFormat' || elk == 'fallbackFormat')
                    aTZ.children.push({tag : elk, text : el});
                else if (elk == 'regions') {
                    angular.forEach(el, function(reg, regk) {
                        if (reg.text) {
                            var temp = angular.copy(reg);
                            aTZ.children.push(temp);
                            if (temp.attributes.type == 'generic')
                                delete temp.attributes.type;
                        }
                    });
                }
                else if (elk == 'zone' || elk == 'metazone') {
                    angular.forEach(el, function (z, zk) {
                        var aZone = {tag : elk, attributes : {type : zk}, children : []};
                        aTZ.children.push(aZone);
                        angular.forEach(z, function (c, ck) {
                            var aChild = {tag : ck, children : c};
                            aZone.children.push(aChild);
                        });
                    });
                }
            });
        }
        DomService.updateTopLevel($scope.fres);
    };

    init();

    $scope.addValue = function(newkey, base, existing, init) {
        if (newkey && !base[newkey]) {
            $scope.vm.changed = true;
            base[newkey] = init;
            return base[newkey];
        }
        else
            return existing;
    };
    $scope.delValue = function(id, base) {
        for (var key in base) {
            if (base[key] === id) {
                $scope.vm.changed = true;
                delete base[key];
            }
        }
        return null;
    };
    $scope.appendValue = function(list, value) {
        $scope.vm.changed = true;
        list.splice(list.length, 0, value);
    };
    $scope.removeValue = function(index, list) {
        $scope.vm.changed = true;
        list.splice(index, 1);
    };
    $scope.changed = function() {
        $scope.vm.changed = true;
    };
    $scope.cancelBtn = function() {
        init();
        $scope.vm.changed = false;
    };
    $scope.saveBtn = function() {
        update_model();
        $scope.vm.changed = false;
    };
}]);
