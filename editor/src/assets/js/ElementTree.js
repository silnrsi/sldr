
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
    var getFrag = function(e, indent) {
        // e.comments go here
        res = new String(indent + "<" + e.tag);
        for (var k in res.attributes) {
            if (e.attributes.hasOwnProperty(k)) {
                res = res + " " + k + "='" + e.attributes[k] + "'";
            }
        }
        if (e.text.length > 0 || e.children.length > 0)
        {
            res = res + ">";
            indent = indent + "  ";
            if (e.text.length > 0) {
                res = res + e.text
            }
            if (e.children.length > 0)
            {
                res = res + "\n";
                for (c in e.children) {
                    res = res + indent + getFrag(c, indent);
                }
                res = res + indent;
            }
            res = res + "</" + e.tag + ">\n";
            // commentsAfter
        }
        else
        {
            res = res + "/>\n";
        }
        return res;
    };
    res = res + getFrag(this, '');
    return res;
};



