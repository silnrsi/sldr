'use strict';

// Services
angular.module('ldmlEdit.service', [ ])
  .service('DomService', [ function() {
    var dom;
    var nsResolver;

    this.loadFromFile = function(file, cb) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var dat = reader.result;
            var parser = new DOMParser();
            dom = parser.parseFromString(dat,"text/xml");
            nsResolver = dom.createNSResolver(dom.documentElement)
            cb(dat);
        };
        reader.readAsBinaryString(file);
    };
    this.getXPathFromRoot = function(path) {
        return dom.evaluate(path, dom.documentElement, nsResolver, XPathResult.ANY_TYPE, null);
    };
    this.getXPath = function(path, element) {
        return dom.evaluate(path, element, nsResolve, XPathResult.ANY_TYPE, null);
    };
    this.asElementTree = function(element) {
    };
    return this;
  }])
  ;
