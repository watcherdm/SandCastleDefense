(function() {
  require(['core/Sprite'], function(Sprite) {
    return describe('Sprite', function() {
      return it('should exist', function() {
        return expect(Sprite).toBeDefined();
      });
    });
  });

}).call(this);
