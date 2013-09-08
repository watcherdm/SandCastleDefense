define ['underscore','gamecore'], (_, gamecore)->
  Game = gamecore.Base.extend 'Game', {},
    fps: 60
    lastStart: 0
    lastEnd: 0
    init: ->
      @entities = []
      @startLoop()
    frameRate: ->
      ms = @lastEnd - @lastStart
    startLoop: ->
      @lastStart = (new Date()).getTime()
      setTimeout(_.bind(->
          @update()
          @lastEnd = (new Date()).getTime()
          @startLoop()
        , this)
      , 1000 / @fps)
    update: ->
      _.invoke @entities, 'update'
  return Game