(function() {
  require.config({
    baseUrl: 'src-cov',
    paths: {
      gamecore: '../lib/gamecore'
    },
    shims: {
      gamecore: {
        "export": 'gamecore'
      }
    }
  });

}).call(this);
