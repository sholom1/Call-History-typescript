import express = require('express');
// Create a new express app instance
const app: express.Application = express();
const PORT: string = process.env.PORT || '3000';

app.get('/', function (req, res) {
	res.send('<button>');
});
app.listen(PORT, function () {
	console.log('App is listening on port 3000!');
});
