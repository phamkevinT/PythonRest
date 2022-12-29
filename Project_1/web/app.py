from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]


class Register(Resource):
    def post(self):
        # Get posted data by the user
        postedData = request.get_json()

        # Get the data
        username = postedData["username"]
        password = postedData["password"]

        # Hashing and Salting the password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Store username and password into the database
        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(retJson)


def verifyPassword(username, password):
    """
    Verify if password matches the password of username stored in database
    """

    hashed_pw = users.find({
        "Username": username,
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf-8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    """
    Get the amount of tokens a user has left
    """
    
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


class Store(Resource):
    def post(self):
        # Step 1 - Get posted fata
        postedData = request.get_json()

        # Step 2 - Read the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        # Step 3 - Verify username and password
        correct_password = verifyPassword(username, password)

        if not correct_password:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        # Step 4 - Verify if user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0: 
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        # Step 5 - Store user's sentence and return status code 200 OK
        users.update_one({
            "Username": username
        }, {
            "$set":{
                "Sentence": sentence,
                "Token": num_tokens - 1
            }
        })

        retJson = {
            "status": 200,
            "msg": "Sentence saved succesfully"
        }
        return jsonify(retJson)


class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        # Verify username and password
        correct_password = verifyPassword(username, password)
        if not correct_password:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)
        
        # Check if user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)
        
        # User pay 1 token from total
        users.update_one({
            "Username": username
        }, {
            "$set":{
                "Token": num_tokens - 1
            }
        })

        # Return user's sentence
        sentence = users.find({
            "Username": username
        })[0]["Sentence"]
        retJson = {
            "status": 200,
            "sentence": str(sentence)
        }

        return jsonify(retJson)



api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')

if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)



# ======================================== OLD PRACTICE CODE =====================================================

""" 

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.aNewDB
UserNum = db["UserNum"]

UserNum.insert_one({
    "num_of_users": 0
})


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]["num_of_users"]
        new_num = prev_num + 1
        UserNum.update_one({}, {"$set":{"num_of_users":new_num}})
        return str("Hello user " + str(new_num))


def checkPostedData(postedData, functionName):
    if (functionName == "add" or functionName == "subtract" or functionName == "multiply"):
        if "x" not in postedData or "y" not in postedData:
            return 301 #Missing parameter
        else:
            return 200
    elif (functionName == "division"):
        if "x" not in postedData or "y" not in postedData:
            return 301
        elif int(postedData["y"])==0:
            return 302
        else:
            return 200

class Add(Resource):
    def post(self):
        #If I am here, then the resouce Add was requested using the method POST

        #Step 1: Get posted data:
        postedData = request.get_json()

        #Steb 1b: Verify validity of posted data
        status_code = checkPostedData(postedData, "add")
        if (status_code!=200):
            retJson = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(retJson)

        #If i am here, then status_code == 200
        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)

        #Step 2: Add the posted data
        ret = x+y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retMap)

class Subtract(Resource):
    def post(self):
        #If I am here, then the resouce Subtract was requested using the method POST

        #Step 1: Get posted data:
        postedData = request.get_json()

        #Steb 1b: Verify validity of posted data
        status_code = checkPostedData(postedData, "subtract")


        if (status_code!=200):
            retJson = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(retJson)

        #If i am here, then status_code == 200
        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)

        #Step 2: Subtract the posted data
        ret = x-y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retMap)


class Multiply(Resource):
    def post(self):
        #If I am here, then the resouce Multiply was requested using the method POST

        #Step 1: Get posted data:
        postedData = request.get_json()

        #Steb 1b: Verify validity of posted data
        status_code = checkPostedData(postedData, "multiply")


        if (status_code!=200):
            retJson = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(retJson)

        #If i am here, then status_code == 200
        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)

        #Step 2: Multiply the posted data
        ret = x*y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retMap)

class Divide(Resource):
    def post(self):
        #If I am here, then the resouce Divide was requested using the method POST

        #Step 1: Get posted data:
        postedData = request.get_json()

        #Steb 1b: Verify validity of posted data
        status_code = checkPostedData(postedData, "division")


        if (status_code!=200):
            retJson = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(retJson)

        #If i am here, then status_code == 200
        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)

        #Step 2: Multiply the posted data
        ret = (x*1.0)/y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retMap)



api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/division")
api.add_resource(Visit, "/hello")

@app.route('/')
def hello_world():
    return "Hello World!"


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)

"""