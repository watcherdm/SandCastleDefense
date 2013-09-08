(function() {
  require(['app'], function(app) {
    return describe('App', function() {
      return it('should exist', function() {
        return expect(new app()).toBeDefined();
      });
    });
  });

}).call(this);
