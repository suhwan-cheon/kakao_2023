import requests

def startAPI(BASE_URL, problem):
    header = {'X-Auth-Token': 'a53c370f23fe75b80a5cb24efe92c419', 
            'Content-Type': 'application/json'}
    data = {"problem": problem}

    response = requests.post(BASE_URL+'/start', headers = header, json=data).json()
    return response["auth_key"]

def newRequestAPI(BASE_URL, auth_key):
    header = {'Authorization': auth_key, 
            'Content-Type': 'application/json'}

    response = requests.get(BASE_URL+'/new_requests', headers = header).json()
    return response["reservations_info"]

def replyAPI(BASE_URL, auth_key, replies):
    header = {'Authorization': auth_key, 
            'Content-Type': 'application/json'}

    response = requests.put(BASE_URL+'/reply', headers = header, json=replies).json()
    
    return

def simulateAPI(BASE_URL, auth_key, roomAssign):
    header = {'Authorization': auth_key, 
            'Content-Type': 'application/json'}

    response = requests.put(BASE_URL+'/simulate', headers = header, json=roomAssign).json()
    return response

def scoreAPI(BASE_URL, auth_key):
    header = {'Authorization': auth_key, 
            'Content-Type': 'application/json'}

    response = requests.get(BASE_URL+'/score', headers = header).json()
    # 점수 확인
    print(response)
    return