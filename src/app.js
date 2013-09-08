(function() {
  define(['underscore', 'gamecore'], function(_, gamecore) {
    var Game;
    Game = gamecore.Base.extend('Game', {}, {
      fps: 60,
      lastStart: 0,
      lastEnd: 0,
      init: function() {
        this.entities = [];
        return this.startLoop();
      },
      frameRate: function() {
        var ms;
        ms = this.lastEnd - this.lastStart;
        return console.log(ms * this.fps);
      },
      startLoop: function() {
        this.lastStart = (new Date()).getTime();
        return setTimeout(_.bind(function() {
          this.update();
          this.lastEnd = (new Date()).getTime();
          return this.startLoop();
        }, this), 1000 / this.fps);
      },
      update: function() {
        return _.invoke(this.entities, 'update');
      }
    });
    return Game;
  });

}).call(this);
