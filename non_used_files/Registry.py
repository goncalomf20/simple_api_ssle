from flask import Flask, jsonify,request,abort
import json

app = Flask(__name__)

port = 5020

services_dict = {}

@app.route('/services', methods=['POST'])
def register():
    data = request.form.to_dict()

    services_dict[len(services_dict.keys()) + 1] = data


    print(services_dict)
    
    return "Success",201



@app.route('/services', methods=['GET'])
def get_services():
    return jsonify(services_dict)




@app.route('/services/<int:id>', methods=['GET'])
def get_one_service(id):
    service = services_dict.get(id)  # Safely get the service by id
    if service is None:  # Check if the service exists
        return jsonify({"Error": "No service found with the given ID"}), 404
    return jsonify(service)


if __name__ == '__main__':
    app.run(debug=True, port=port)