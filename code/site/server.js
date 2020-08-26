/* server script for nodejs docker image */
'use strict';

const express = require('express');

// Constants
const PORT = 80;
const HOST = '0.0.0.0';

// App
const app = express();
app.use('/cdli-accounting-viz',
  express.static(__dirname + ''));

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
