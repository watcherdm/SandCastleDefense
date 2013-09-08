require.config
  baseUrl: 'src-cov'
  paths:
    gamecore: '../lib/gamecore'
    underscore: '../lib/underscore'
  shim:
    underscore:
      exports: '_'