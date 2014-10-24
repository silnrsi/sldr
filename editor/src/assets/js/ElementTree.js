
function ElementTree(dom) {
    this.root = this.parseDom(dom, null);
}

ElementTree.prototype.parseDom = function(dom, element) {
    if (element == null) {
        element = dom.documentElement;
    }

    var res = {
        attributes: {},
        children: [],
        text: null };
    var lastElement = null;
    var comments = [];

    res.tag = element.tagName;
    for (var i = element.attributes.length - 1; i >= 0; i--) {
        var a = element.attributes.item(i);
        res.attributes[a.name] = a.value;
    }

    for (var n = element.firstChild; n; n = n.nextSibling)
    {
        if (n.nodeType == Node.ELEMENT_NODE)
        {
            lastElement = this.parseDom(dom, n);
            res.children.push(lastElement);
            if (comments.length > 0) {
                lastElement.comments = comments;
                comments = [];
            }
        }
        else if (n.nodeType == Node.TEXT_NODE)
        {
            var text = n.wholeText.trim();
            if (text.length > 0) {
                if (lastElement)
                    lastElement.tail = text;
                else if (!res.text)
                    res.text = text;
            }
        }
        else if (n.nodeType == Node.COMMENT_NODE)
        {
            comments.push(n.textContent)
        }
    }
    if (comments.length > 0 && lastElement != null) {
        lastElement.commentsAfter = comments;
    }
    return res;
};

ElementTree.prototype.asXML = function() {
    var res = "<?xml version='1.0' encoding='utf-8'?>\n";
    var indentshift = "  ";
    var protmap = {
        "<" : "&lt;",
        ">" : "&gt;",
        "&" : "&amp;"
    };
    var protect = function(s) {
        var repl = function(match) { return protmap[match] || match; }
        return s.replace(/([<>&])/, repl);
        };
    var getFrag = function(e, indent) {
        var res = "";
        if (e.comments != null && e.comments.length > 0) {
            res = res + indent + "<!-- ";
            var prefix = "";
            for (var i = 0; i < e.comments.length; i++) {
                res = res + prefix + e.comments[i];
                prefix = "\n" + indent + "     ";
            }
            res = res + " -->\n";
        }
        var res = res + indent + "<" + e.tag;
        for (var k in e.attributes) {
            if (e.attributes.hasOwnProperty(k)) {
                res = res + " " + k + '="' + protect(e.attributes[k]) + '"';
            }
        }
        if ((e.text != null && e.text.length > 0) || e.children.length > 0)
        {
            res = res + ">";
            if (e.text != null && e.text.length > 0) {
                res = res + protect(e.text);
            }
            if (e.children.length > 0)
            {
                res = res + "\n";
                for (var i = 0; i < e.children.length; i++) {
                    res = res + getFrag(e.children[i], indent + indentshift);
                }
                res = res + indent;
            }
            res = res + "</" + e.tag + ">\n";
            if (e.commentsAfter != null && e.commentsAfter.length > 0) {
                res = res + indent + "<!-- ";
                var prefix = "";
                for (var i = 0; i < e.commentsAfter.length; i++) {
                    res = res + prefix + e.commentsAfter[i];
                    prefix = "\n" + indent + "     ";
                }
                res = res + " -->\n";
            }
        }
        else
        {
            res = res + "/>\n";
        }
        return res;
    };
    res = res + getFrag(this.root, '');
    return res;
};



