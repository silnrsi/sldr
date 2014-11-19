
function ElementTree(dom) {
    if (dom == null) 
        this.root = {'tag' : 'ldml', 'attributes' : {}, 'children' : []};
    else
        this.root = this.parseDom(dom, null);
}

ElementTree.prototype.parseDom = function(dom, element) {
    var comments = [];
    if (element == null) {
        for (var n = dom.firstChild; n; n = n.nextSibling)
        {
            if (n.nodeType == Node.ELEMENT_NODE) {
                element = n;
                break;
            }
            else if (n.nodeType == Node.COMMENT_NODE) {
                comments.push(n.textContent);
            }
        }
    }

    var res = {
        attributes: {},
        children: [],
        text: null };
    if (comments.length > 0)
    {
        res['comments'] = comments;
        comments = [];
    }
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
            lastElement = this.parseDom(dom, n);
            res.children.push(lastElement);
            if (comments.length > 0) {
                lastElement.comments = comments;
                comments = [];
            }
        }
        else if (n.nodeType == Node.TEXT_NODE || n.nodeType == Node.CDATA_SECTION_NODE)
        {
            var text;
            if (n.nodeType == Node.TEXT_NODE)
                text = n.wholeText.trim();
            else
                text = n.nodeValue.trim();
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
        // else
        //    console.log("Node type: " + n.nodeType);
    }
    if (comments.length > 0 && lastElement != null) {
        lastElement.commentsAfter = comments;
    }
    return res;
};

ElementTree.prototype.asXML = function() {
    var res = "<?xml version='1.0' encoding='utf-8'?>\n";
    console.log(this.root.comments);
    var indentshift = "  ";
    var protmap = {
        "<" : "&lt;",
        ">" : "&gt;",
        "&" : "&amp;"
    };
    var protect = function(s) {
        var repl = function(match) { return protmap[match] || match; }
        if (s == null)
            return "";
        else
            return s.toString().replace(/([<>&])/g, repl);
    };
    var getFrag = function(e, indent) {
        var res = "";
        if (e.comments != null && e.comments.length > 0) {
            for (var i = 0; i < e.comments.length; i++)
                res = res + indent + "<!--" + e.comments[i] + "-->\n";
        }
        var res = res + indent + "<" + e.tag;
        if (e.attributes) {
            for (var k in e.attributes) {
                if (e.attributes.hasOwnProperty(k)) {
                    res = res + " " + k + '="' + protect(e.attributes[k]) + '"';
                }
            }
        }
        if ((e.text != null && e.text.length > 0) || (e.children != null && e.children.length > 0))
        {
            res = res + ">";
            if (e.text != null && e.text.length > 0) {
                res = res + protect(e.text);
            }
            if (e.children != null && e.children.length > 0)
            {
                res = res + "\n";
                for (var i = 0; i < e.children.length; i++) {
                    res = res + getFrag(e.children[i], indent + indentshift);
                }
                res = res + indent;
            }
            res = res + "</" + e.tag + ">\n";
            if (e.commentsAfter != null && e.commentsAfter.length > 0) {
                for (var i = 0; i < e.commentsAfter.length; i++)
                    res = res + indent + "<!--" + e.commentsAfter[i] + "-->\n";
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



