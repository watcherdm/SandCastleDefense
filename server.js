var connect = require('connect'),
  app = connect(),
	port = parseInt(process.env.PORT, 10) || 4827;

app.use(connect.static('public'))
  .listen(port);

console.log('Sand Castle Defense Server Started on port ' + port);