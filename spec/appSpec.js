(function() {
  require(['app'], function(app) {
    return describe('App', function() {
      return it('should exist', function() {
        return expect(app).toBeDefined();
      });
    });
  });

}).call(this);
