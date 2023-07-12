const instrumentNSE = require("../model/instrumentModel")
const surResModel = require("../model/supResModel")

module.exports.addSuppRes = async (data)=>{
    try{
        ct = []
        ct = await surResModel.find(
            {
                "status":{$ne:"Closed"},
                "levelDetails.level": data.levelDetails.level,
            })
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
        console.log("resultInstrument",result)
        if(result == null){
            throw new Error("Instrument dosn't exist")
        }
        let obj = {
            id: "",
            name: "",
            instrument_token: 0,
            tradingsymbol: "",
            levelDetails: {
                level: 0,
                type: "notAssigned"
            },
            interchangable: false,

        }
        count = await surResModel.count({})
        console.log(count,"counttttttttttttt")
        obj.id = `Level-0${count+1}`
        obj.sno = count + 1
        obj.name = result.name
        obj.status = data.status == "Active"? data.status : "Passive"
        obj.instrument_token = result.instrument_token
        obj.tradingsymbol = result.tradingsymbol
        obj.levelDetails.level = data.levelDetails.level
        obj.levelDetails.type = data.levelDetails.type
        obj.interchangable = data.interchangable ? data.interchangable : false
        obj.forDevPurpuouse = data.forDevPurpuouse ? data.forDevPurpuouse: false
        console.log(obj,"objjjjjjjjjj")
        const newDoc = new surResModel(obj)
        let doc = await newDoc.save()
        console.log(doc,'doccccccccc')
        return doc
        // return obj

    }catch(err){
        console.log("errorrrr")
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
                "level":0,
                "type": "NA",
                "testCount":0,
                "interChanged": false
            }
        }
        let re = await surResModel.findOne({id:data.id},{"levelDetails": 1, "_id":0})
        console.log(re,"reeeeeee")
        updateObj.levelDetails.level = re.levelDetails.level
        updateObj.levelDetails.testCount = re.levelDetails.testCount
        updateObj.levelDetails.interChanged = re.levelDetails.interChanged
        if (data.interchange == false){
            console.log(re.levelDetails.type,"reeeeeee","from false")
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