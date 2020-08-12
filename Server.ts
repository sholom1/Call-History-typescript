import express = require('express');
import formidable = require('formidable');
import unzipper = require('unzipper');
import io = require('socket.io');
import path = require('path');
import fs = require('fs');
import jsdom = require('jsdom');
// Create a new express app instance
const app: express.Application = express();
const PORT: string = process.env.PORT || '3000';

app.get('/', (req, res) => {
	res.sendFile(path.join(__dirname, 'public', 'index.html'));
});
app.post('/fileupload', (req, res) => {
	var form = new formidable.IncomingForm();
	form.maxFileSize = 300 * 1024 * 1024;
	form.parse(req, async (err, fields, files) => {
		try {
			if (err) console.log(err);
			var zip = fs.createReadStream(files.filetoupload.path).pipe(unzipper.Parse({ forceStream: true }));

			let entry: unzipper.Entry;
			let paths: String = ``;
			for await (entry of zip) {
				if (entry.path.match(/\/Calls\/.+\.html+/)) {
					fs.readFile(entry.path, (err, data) => {
						console.log(`<p>${entry.path}</p>`);
						var doc: HTMLDocument = new jsdom.JSDOM(data, {
							contentType: 'text/html',
							includeNodeLocations: true,
						}).window.document;
						let detailsElement: Node = doc.evaluate('/html/body/div/span.fn', doc, null, 9, null)
							.singleNodeValue;
						console.log(detailsElement);
						paths += detailsElement.textContent;
						paths += `<p>${entry.path}</p>`;
						entry.autodrain();
					});
				} else entry.autodrain();
			}
			res.send(paths);
			//res.write(`oldpath: ${oldpath}`);
			res.end();
		} catch (e) {
			console.error(e);
		} finally {
			fs.unlinkSync(files.filetoupload.path);
		}
	});
});
app.listen(PORT, function () {
	console.log(`App is listening on port: ${PORT}!`);
});
