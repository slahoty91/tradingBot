const instrumentNSE = require("../model/instrumentModel")
const surResModel = require("../model/supResModel")

module.exports.addSuppRes = async (data)=>{
    try{
        console.log(data,'data from sup res service')
        let result = await instrumentNSE.findOne({
            "name": data.name
        })
        let obj = {
            id: "",
            name: "",
            instrument_token: 0,
            tradingsymbol: "",
            levelDetails: {
                level: 0,
                type: "notAssigned"
            }
        }
        count = await surResModel.count({})
        console.log(count,"counttttttttttttt")
        obj.id = `Level-0${count+1}`
        obj.name = result.name
        obj.instrument_token = result.instrument_token
        obj.tradingsymbol = result.tradingsymbol
        obj.levelDetails.level = data.levelDetails.level
        obj.levelDetails.type = data.levelDetails.type
        console.log(obj,"objjjjjjjjjj")
        const newDoc = new surResModel(obj)
        newDoc.save()
        .then((doc)=>{
            console.log(doc)
        }).catch(err=>{
            console.log(err)
        })
        return newDoc
    }catch(err){
        console.log(err)
    }
}

module.exports.updateSupRes = async (data) => {
    try{
        
        if(data.type == 'soft'){
            const update = {
                $push:{
                    supportLevel: data.supportLevel,
                    resistanceLevel: data.resistanceLevel
                }
            }
           const result = await surResModel.updateOne({"tradingsymbol": data.tradingsymbol},update)
           console.log(result,'result from servicesss')
           return result
        }
        if(data.type == 'hard'){
            const update = {
                $set:{
                    supportLevel: data.supportLevel,
                    resistanceLevel: data.resistanceLevel
                }
            }
           const result = await surResModel.updateOne({"tradingsymbol": data.tradingsymbol},update)
           console.log(result,'result from servicesss')
           return result
        }
    }catch(err){
        return err
    }
}