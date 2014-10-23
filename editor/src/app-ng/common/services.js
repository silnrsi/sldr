'use strict';

// Services
angular.module('ldmlEdit.service', [ ])
  .service('DomService', [ function() {
    var dom = null;
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
        if (!dom) return null;
        return dom.evaluate(path, dom.documentElement, nsResolver, XPathResult.ANY_TYPE, null);
    };
    this.getXPath = function(path, element) {
        if (!dom) return null;
        return dom.evaluate(path, element, nsResolve, XPathResult.ANY_TYPE, null);
    };
    this.asElementTree = function(element) {
        if (!element) return null;
        var res = {
            attributes: {},
            children: [],
            text: null };
        var lastElement = null;

        res.tag = element.tagName;
        for (var i = element.attributes.length - 1; i >= 0; i--) {
            var a = element.attributes.item(i);
            res.attributes[a.name] = a.value;
        }

        for (var n = element.firstChild; n; n = n.nextSibling)
        {
            if (n.nodeType == Node.ELEMENT_NODE)
            {
                lastElement = this.asElementTree(n);
                res.children.push(lastElement);
            }
            else if (n.nodeType == Node.TEXT_NODE)
            {
                if (lastElement)
                    lastElement.tail = n.wholeText;
                else if (!res.text)
                    res.text = n.wholeText;
            }
            else if (n.nodeType == Node.COMMENT_NODE)
            {
                // need to do something good here.
            }
        }
        return res;
    };
    return this;
  }])
  ;
