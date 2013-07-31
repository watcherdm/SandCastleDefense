module.exports = (grunt)->
  grunt.initConfig
    pkg: grunt.file.readJSON 'package.json'
    connect: 
      test: 
        port : 8000
    watch:
      coffee:
        files: ['**/*.coffee']
        tasks: ['coffee']
      scripts:
        files: ['src/**/*.js', 'spec/**/*.js']
        tasks: ['jshint', 'blanket']
      coverage:
        files: ['src-cov/**/*.js']
        tasks: ['jasmine']

    coffee:
      src:
        expand: true
        flatten: false
        cwd: 'coffee/'
        src: ['**/*.coffee']
        dest: 'src/'
        ext: '.js'
      specs:
        expand: true
        flatten: false
        cwd: 'spec_cs/'
        src: ['**/*.coffee']
        dest: 'spec/'
        ext: '.js'
    jshint: 
      all: ['src/**/*.js']
    blanket:
      all:
        files:
          "src-cov/": ['src/']
    jasmine:
      all:
        src: 'src-cov/**/*.js'
        options:
          outfile: 'index.html'
          keepRunner: true
          host: 'http://127.0.0.1:8000/'
          specs: 'spec/**/*Spec.js'
          helpers: 'spec/**/*Helper.js'
          template: require('grunt-template-jasmine-requirejs')
          templateOptions:
            requireConfigFile: 'src-cov/main.js'
  grunt.loadNpmTasks 'grunt-contrib-jshint'
  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-blanket'
  grunt.loadNpmTasks 'grunt-contrib-jasmine'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-connect'

  grunt.registerTask 'default', ['connect','coffee','jshint','blanket','jasmine','watch']
