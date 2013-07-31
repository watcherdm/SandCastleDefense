if (typeof _$jscoverage === 'undefined') _$jscoverage = {};
if (typeof _$jscoverage['src/app.js'] === 'undefined'){_$jscoverage['src/app.js']=[];
_$jscoverage['src/app.js'].source=['(function() {',
'  define([\'gamecore\'], function(gamecore) {',
'    var Game;',
'    console.log(gamecore);',
'    Game = gamecore.Base.extend({',
'      initialize: function() {',
'        return console.log(\'initialize\');',
'      },',
'      update: function() {',
'        return console.log(\'update\');',
'      }',
'    });',
'    return Game;',
'  });',
'',
'}).call(this);',
''];
_$jscoverage['src/app.js'][1]=0;
_$jscoverage['src/app.js'][2]=0;
_$jscoverage['src/app.js'][3]=0;
_$jscoverage['src/app.js'][4]=0;
_$jscoverage['src/app.js'][5]=0;
_$jscoverage['src/app.js'][7]=0;
_$jscoverage['src/app.js'][10]=0;
_$jscoverage['src/app.js'][13]=0;
}_$jscoverage['src/app.js'][1]++;
(function() {
  _$jscoverage['src/app.js'][2]++;
define(['gamecore'], function(gamecore) {
    _$jscoverage['src/app.js'][3]++;
var Game;
    _$jscoverage['src/app.js'][4]++;
console.log(gamecore);
    _$jscoverage['src/app.js'][5]++;
Game = gamecore.Base.extend({
      initialize: function() {
        _$jscoverage['src/app.js'][7]++;
return console.log('initialize');
      },
      update: function() {
        _$jscoverage['src/app.js'][10]++;
return console.log('update');
      }
    });
    _$jscoverage['src/app.js'][13]++;
return Game;
  });

}).call(this);
