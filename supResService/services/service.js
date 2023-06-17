const instrumentNSE = require("../model/instrumentModel")
const surResModel = require("../model/supResModel")

module.exports.addSuppRes = async (data)=>{
    try{
        ct = []
        ct = await surResModel.find({"levelDetails.level": data.levelDetails.level})
        console.log(ct,"ctttttt")
        if (ct.length > 0){
            return {
                msg: `Level already their with ID ${ct[0].id}`
            }
        }
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
            },
            interchangable: false
        }
        count = await surResModel.count({})
        console.log(count,"counttttttttttttt")
        obj.id = `Level-0${count+1}`
        obj.name = result.name
        obj.status = data.status == "Active"? data.status : "Passive"
        obj.instrument_token = result.instrument_token
        obj.tradingsymbol = result.tradingsymbol
        obj.levelDetails.level = data.levelDetails.level
        obj.levelDetails.type = data.levelDetails.type
        obj.interchangable = data.interchangable ? data.interchangable : false
        console.log(obj,"objjjjjjjjjj")
        const newDoc = new surResModel(obj)
        let doc = await newDoc.save()
        console.log(doc,'doccccccccc')
        return doc

    }catch(err){
        throw new Error(err)
        // return err
    }
}

module.exports.updateStatus = async (data) => {
    try{
        console.log(data)
        let updateFilter = {
            "id": data.id
        }
        let updateObj = {
            "status": data.status,
            "levelDetails": {
                "type": "NA"
            }
        }
        let re = await surResModel.findOne({id:data.id},{"levelDetails.type": 1, "_id":0})
        console.log(re.levelDetails.type,"reeeeeee")
        if (data.interchange == false){
            updateObj.levelDetails.type = re.levelDetails.type
        }
        if (data.interchange == true){
           console.log("from ifffff")
           if(re.levelDetails.type == "resistance"){
            console.log("from ifffff inside iifff")
            updateObj.levelDetails.type = "support"
           }else if(re.levelDetails.type == "support"){
            updateObj.levelDetails.type = "resistance"
           }
        }

        
       
        console.log(updateFilter,updateObj,"<<<<<<<<<<")
        res = await surResModel.updateOne(updateFilter,updateObj)
        console.log(res,"resulttt")
        return res
        
    }catch(err){
        return err
    }

}

module.exports.getLevels = async (data)=>{
    try{
        console.log(data)
        let filterObj = {}
        if(data.status){
            filterObj.status = data.status
        }
        if(data.id){
            filterObj.id = data.id
        }
        console.log(filterObj,"filterObj")
        res = await surResModel.find(filterObj)
        return res
    }catch(err){
        return err
    }
}