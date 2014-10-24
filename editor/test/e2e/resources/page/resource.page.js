'use strict';

var ResourcePage = function() {
//  browser.ignoreSynchronization = true;
  browser.get('');

//  this.reference = element(by.name('Ref'));

  this.search = function(reference, type, from, to, showClosed) {
    if (reference) this.reference.sendKeys(reference);
    this.type.element(by.cssContainingText('option', type)).click();
    this.dateFrom.clear();
    this.dateFrom.sendKeys(from);
    this.dateTo.clear();
    this.dateTo.sendKeys(to);
    if (showClosed) this.showClosed.click();
    this.submit.click();
  };

  this.getTitle = function() {
    return browser.getTitle();
  };

  this.getResultRow = function(row) {
    var items = element.all(by.css('div#_journal_tbl_span tr'))
    .get(row + 1)
    .all(by.tagName('td'))
    .map(function(cellElement, cellIndex) {
      return {
        column: cellIndex,
        text: cellElement.getText()
      };
    });
    return items;
  };

}

module.exports = ResourcePage;
