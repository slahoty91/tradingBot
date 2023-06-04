const { addSuppRes, updateSupRes } = require("../services/service");

class suResontroller {
    
    async addSupportResistance(req, res){
        try{
            let result = await addSuppRes(req.body)
            // console.log(result,'result from controller')
            console.log(result,'resultttttt')
            res.status(200).send(result)
        }catch(err){
            let errorObj = {
                msg: "Duplicate Entry"
            }
            res.status(500).send(errorObj)
        }
    }

    async updatateSupRes(req, res){
        try{
            let obj = req.body
            obj.type = req.query.type
            let result = await updateSupRes(obj)
            res.send(result)
        }catch(err){
            res.status(400).send(err)
        }
    }

}

module.exports = suResontroller