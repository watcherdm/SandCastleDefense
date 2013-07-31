define ['gamecore'], (gamecore)->
  console.log(gamecore)
  Game = gamecore.Base.extend
    initialize: ->
      console.log 'initialize'
    update: ->
      console.log 'update'
  return Game