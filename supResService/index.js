const express = require('express')
const bodyParse = require('body-parser')
const routes = require('./routes/routes')
const DB = require('./database/connect')

const app = express()

DB.connectDB()
const port = 3000
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
app.use(bodyParse.urlencoded({ extended: false }))
app.use(bodyParse.json())
app.use('/api/v1/',routes)
