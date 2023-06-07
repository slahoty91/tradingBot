const mongoose = require('mongoose')

const supResLevelSchema = new mongoose.Schema({
    level: {
        type: Number,
        required: true,
        unique: true
    },
    type: {
        type: String,
        enum: [
            "breakout",
            "breakdown",
            "support",
            "resistance",
            "fiveMinSup",
            "fiveMinRes",
            "testedSup",
            "testedRes",
            "notAssigned"
        ],
        required: true
    },
    testCount: {
        type: Number,
        default: 0
    },
    interChanged: {
        type: Boolean,
        default: false
    }
})
const tradeResult = new mongoose.Schema({
    orderId: {
        type: String
    },
    result: {
        type: String,
        enum: ["Profit","Loss"]
    }
})
const supResSchema = new mongoose.Schema({
    id: {
        type: String,
        required: true,
        unique: true
    },
    name: {
        type: String,
        required: true,
    },
    tradingsymbol: {
        type: String,
        required: true
    },
    interchangable: {
        type: Boolean,
        default: false
    },
    status: {
        type: String,
        enum: ["Active", "Passive","Intrade","Closed"],
        default: "Passive"
    },
    instrument_token: {
        type: Number,
        required: true
    },
    
    levelDetails: supResLevelSchema,
    dateCreated: {
        type: Date,
        default: Date.now
    },
    tradeResults: [tradeResult],
    dateUpdated: Date
})



let supResModel = mongoose.model('levels',supResSchema)

module.exports = supResModel  
