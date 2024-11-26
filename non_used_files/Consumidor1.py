import requests, json


def get_temp(url):
    response = requests.get(url)


    if response.status_code == 200:

        temp_dict = response.json()  
        temp_value = temp_dict['key']

        print("Temperature is {}".format(temp_value))
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")



def get_all_services():
    response = requests.get("http://127.0.0.1:5020/services")

    print(response.json())

def get_one_service(id):
    try:
        response = requests.get(f"http://127.0.0.1:5020/services/{id}")

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("url", "URL not found")
        else:
            # Handle cases where the service does not exist (e.g., 404)
            return {"Error": "Service not found"}, response.status_code
    except requests.exceptions.RequestException as e:
        # Handle any other exceptions (like connection errors)
        return {"Error": str(e)}, 500

get_all_services()

url = get_one_service(1)

get_temp(url)

