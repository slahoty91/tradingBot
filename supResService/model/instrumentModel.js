const mongoose = require('mongoose')

const instrumentNSEtokens = new mongoose.Schema({
    "instrument_token" : Number,
	"exchange_token" : String,
	"tradingsymbol" : String,
	"name" : String,
	"last_price" : Number,
	"expiry" : String,
	"strike" : Number,
	"tick_size" : Number,
	"lot_size" : Number,
	"instrument_type" : String,
	"segment" : String,
	"exchange" : String
})

let instrumentNSE = mongoose.model('instrumentNSE',instrumentNSEtokens,'instrumentNSE')
module.exports = instrumentNSE