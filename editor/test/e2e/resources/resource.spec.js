'use strict';

var ResourcePage  = require('./page/resource.page.js');

describe('resource page:', function () {

  beforeEach(function () {
//    browser.driver.manage().timeouts().implicitlyWait(20);
  });

  it('works', function () {
    var page = new ResourcePage();
    expect(page.getTitle()).toEqual('Something');
  });
  it('reads back', function () {
    var pageReadBack = new ResourcePage();
    expect(pageReadBack.getTitle()).toEqual('Journal Inquiry');
    pageReadBack.search(reference, 'Funds Transfer', '1/2/2013', '1/2/2013', null);
    var items = pageReadBack.getResultRow(0);
    items.then(function(actualItems) {
      trans_no = parseInt(actualItems[2].text, 10);
      expect(items).toEqual([
        {column: 0, text: '01/02/2013'},
        {column: 1, text: 'Funds Transfer'},
        {column: 2, text: trans_no.toString()},
        {column: 3, text: reference},
        {column: 4, text: '11.00'},
        {column: 5, text: 'Some memo'},
        {column: 6, text: 'test'},
        {column: 7, text: ''},
        {column: 8, text: ''}
      ]);
    });
  });



});
