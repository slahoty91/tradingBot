const { addSuppRes, updateStatus, getLevels } = require("../services/service");

class suResontroller {
    
    async addSupportResistance(req, res){
        try{
            let result = await addSuppRes(req.body)
            // console.log(result,'result from controller')
            console.log(result,'resultttttt')
            res.status(200).send(result)
        }catch(err){
            console.log(err,"err catch")
            
            res.status(500).send(err)
        }
    }

    async updatateStatus(req, res){
        console.log("update status called")
        try{
            let obj = req.body
            console.log(obj,"object",obj.interchange)
            if (obj.interchange == undefined){
                return res.send("NEED INTERCHANGE FLAGE")
            }
            let result = await updateStatus(obj)
            res.send(result)
        }catch(err){
            res.status(400).send(err)
        }
    }

    async getLevels(req, res){
        try{
            console.log("get levels called")
            let object = req.query
            
            let result = await getLevels(object)
            res.send(result)
        }catch(err){
            res.send(500).send(err)
        }
    }

}

module.exports = suResontroller