require ['app'], (app)->
  describe 'App', ->
    it 'should exist', ->
      expect(new app()).toBeDefined()