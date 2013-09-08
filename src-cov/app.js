if (typeof _$jscoverage === 'undefined') _$jscoverage = {};
if (typeof _$jscoverage['src/app.js'] === 'undefined'){_$jscoverage['src/app.js']=[];
_$jscoverage['src/app.js'].source=['(function() {',
'  define([\'underscore\', \'gamecore\'], function(_, gamecore) {',
'    var Game;',
'    Game = gamecore.Base.extend(\'Game\', {}, {',
'      fps: 60,',
'      lastStart: 0,',
'      lastEnd: 0,',
'      init: function() {',
'        this.entities = [];',
'        return this.startLoop();',
'      },',
'      frameRate: function() {',
'        var ms;',
'        ms = this.lastEnd - this.lastStart;',
'        return console.log(ms * this.fps);',
'      },',
'      startLoop: function() {',
'        this.lastStart = (new Date()).getTime();',
'        return setTimeout(_.bind(function() {',
'          this.update();',
'          this.lastEnd = (new Date()).getTime();',
'          return this.startLoop();',
'        }, this), 1000 / this.fps);',
'      },',
'      update: function() {',
'        return _.invoke(this.entities, \'update\');',
'      }',
'    });',
'    return Game;',
'  });',
'',
'}).call(this);',
''];
_$jscoverage['src/app.js'][21]=0;
_$jscoverage['src/app.js'][1]=0;
_$jscoverage['src/app.js'][22]=0;
_$jscoverage['src/app.js'][3]=0;
_$jscoverage['src/app.js'][2]=0;
_$jscoverage['src/app.js'][19]=0;
_$jscoverage['src/app.js'][10]=0;
_$jscoverage['src/app.js'][4]=0;
_$jscoverage['src/app.js'][9]=0;
_$jscoverage['src/app.js'][13]=0;
_$jscoverage['src/app.js'][14]=0;
_$jscoverage['src/app.js'][15]=0;
_$jscoverage['src/app.js'][18]=0;
_$jscoverage['src/app.js'][20]=0;
_$jscoverage['src/app.js'][26]=0;
_$jscoverage['src/app.js'][29]=0;
}_$jscoverage['src/app.js'][1]++;
(function() {
  _$jscoverage['src/app.js'][2]++;
define(['underscore', 'gamecore'], function(_, gamecore) {
    _$jscoverage['src/app.js'][3]++;
var Game;
    _$jscoverage['src/app.js'][4]++;
Game = gamecore.Base.extend('Game', {}, {
      fps: 60,
      lastStart: 0,
      lastEnd: 0,
      init: function() {
        _$jscoverage['src/app.js'][9]++;
this.entities = [];
        _$jscoverage['src/app.js'][10]++;
return this.startLoop();
      },
      frameRate: function() {
        _$jscoverage['src/app.js'][13]++;
var ms;
        _$jscoverage['src/app.js'][14]++;
ms = this.lastEnd - this.lastStart;
        _$jscoverage['src/app.js'][15]++;
return console.log(ms * this.fps);
      },
      startLoop: function() {
        _$jscoverage['src/app.js'][18]++;
this.lastStart = (new Date()).getTime();
        _$jscoverage['src/app.js'][19]++;
return setTimeout(_.bind(function() {
          _$jscoverage['src/app.js'][20]++;
this.update();
          _$jscoverage['src/app.js'][21]++;
this.lastEnd = (new Date()).getTime();
          _$jscoverage['src/app.js'][22]++;
return this.startLoop();
        }, this), 1000 / this.fps);
      },
      update: function() {
        _$jscoverage['src/app.js'][26]++;
return _.invoke(this.entities, 'update');
      }
    });
    _$jscoverage['src/app.js'][29]++;
return Game;
  });

}).call(this);
