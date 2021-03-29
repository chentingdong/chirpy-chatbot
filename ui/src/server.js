var path = require('path')
var express = require('express')

var app = express()

function serveWorkflow (req, res) {
  let indx = path.join(__dirname, '/../dist/index.html')
  res.sendFile(indx)
  console.log('Running Illusionist UI on port 2000')
}

app.use(express.static(path.join(__dirname, '/../dist')))

app.get('/', (req, res) => {
  serveWorkflow(req, res)
})

app.get('/simulator/adidas_luke', (req, res) => {
  serveWorkflow(req, res)
})

app.get('/simulator/adidas_luke/:version', (req, res) => {
  serveWorkflow(req, res)
})

// The 404 Route (ALWAYS Keep this as the last route)
app.get('*', (req, res) => {
  res.send('not found', 404)
})

app.listen(2000)