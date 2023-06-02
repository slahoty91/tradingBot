const mongoose = require('mongoose')

module.exports.connectDB = ()=>{
    
    let cs = "mongodb://localhost:27017/algoTrading"
    mongoose.connect(cs,{
        useUnifiedTopology: true})
    .then(()=>{
        console.log('DB connected')
    })
        
}