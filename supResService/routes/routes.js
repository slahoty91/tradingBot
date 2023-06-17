const route = require('express')
const Router = route.Router()
const contClass =  require('../controller/controller')

let contObj = new contClass()
Router.route('/addSupportRes')
    .post(contObj.addSupportResistance)

Router.route('/updateStatus')
    .post(contObj.updatateStatus)

Router.route('/getLevels')
    .get(contObj.getLevels)
    

module.exports = Router