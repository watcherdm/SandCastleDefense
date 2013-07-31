(function() {
  define(['gamecore'], function(gamecore) {
    var Game;
    console.log(gamecore);
    Game = gamecore.Base.extend({
      initialize: function() {
        return console.log('initialize');
      },
      update: function() {
        return console.log('update');
      }
    });
    return Game;
  });

}).call(this);
