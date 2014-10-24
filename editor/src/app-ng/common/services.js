'use strict';

// Services
angular.module('ldmlEdit.service', [ ])
  .service('DomService', [ function() {
    var et = null;
    var nsResolver;

    this.loadFromFile = function(file, cb) {
        var reader = new FileReader();
        console.log("File type: " + file.type);
        reader.onload = function(e) {
            var dat = reader.result;
            var parser = new DOMParser();
            var dom = parser.parseFromString(dat,"text/xml");
            et = new ElementTree(dom);
            cb(et);
        };
        reader.readAsText(file);
    };
    this.findElement = function(tag, base) {
        if (base == null)
            base = et.root;
        if (base == null)
            return null;
        for (var i = 0; i < base.children.length; i++) {
            if (base.children[i].tag == tag)
                return base.children[i];
        }
        return null;
    }
    this.findElements = function(base, tags) {
        var res = base;
        if (res == null)
        {
            if (et == null)
                return null;
            else
                res = et.root;
        }
        for (var i = 0; i < tags.length; i++) {
            res = this.findElement(tags[i], res);
            if (res == null)
                return null;
        }
        return res;
    };
    this.getBlob = function() {
        return new Blob([et.asXML()], {type: "text/xml;charset=utf8"});
    };
    return this;
  }])
  ;
