from sys import stdin
import requests
import operator as op

### 기본값 설정 ###

BASE_URL = 'https://huqeyhi95c.execute-api.ap-northeast-2.amazonaws.com/prod'
x_auth_token = '904aa7eb39b8f419ee1148d8d03d32e2'
auth_key = None

###############

### API 영역 ###

# Start API
def startAPI(problem):
    resp = requests.post(BASE_URL+'/start', headers={'X-Auth-Token':x_auth_token}, json={'problem': problem}).json()["auth_key"]
    
    return resp

# Locations API
def waitingLineAPI(auth_key):
    resp = requests.get(BASE_URL+'/waiting_line', headers={'Authorization': auth_key}).json()["waiting_line"]
    
    return resp

# Trucks API
def gameResultAPI(auth_key):
    resp = requests.get(BASE_URL+'/game_result', headers={'Authorization': auth_key}).json()["game_result"]
    
    return resp

# simulate API
def userInfoAPI(auth_key):
    resp = requests.get(BASE_URL+'/user_info', headers={'Authorization': auth_key}).json()["user_info"]
    
    return resp

# match API
def matchAPI(auth_key, pairs):
    resp = requests.put(BASE_URL+'/match', headers={'Authorization': auth_key}, json=pairs).json()
    
    return resp

# match API
def changeGradeAPI(auth_key, commands):
    resp = requests.put(BASE_URL+'/change_grade', headers={'Authorization': auth_key}, json=commands).json()
    
    return resp

# Score API
def scoreAPI(auth_key):
    return requests.get(BASE_URL+'/score', headers={'Authorization': auth_key}).json()

################

### code 영역 ###

grade = [0 for col in range(901)]

def startInit(n):

    commands = dict()
    command = []
    
    for i in range(1, n + 1):
        grade[i] = 5000
        idToGrade = dict()
        idToGrade["id"] = i
        idToGrade["grade"] = 5000
        command.append(idToGrade)
    
    commands["commands"] = command
    changeGradeAPI(auth_key, commands)

# 시나리오 1 (v1)
def scene1():
    auth_key = startAPI(2)
    pairs = dict()
    pairs["pairs"] = []
    matchAPI(auth_key, pairs)

    # 등급 초기화
    startInit(900)

    for i in range(595):
        if i % 10 == 0:
            print(i)
        
        # waitingLine, Match API로 매칭을 시킬 수 있는 턴
        if i <= 555:
            waitingLines = waitingLineAPI(auth_key)
            gradeList = []
            for waitingLine in waitingLines:
                userID = waitingLine["id"]
                tup = (userID, grade[userID])
                gradeList.append(tup)
            
            gradeList.sort(key = lambda element: element[1])

            # 순서대로 매칭하기
            matchingList = []
            
            for j in range(1, len(gradeList), 2):
                leftID = gradeList[j-1][0]
                rightID = gradeList[j][0]
                matched = [leftID, rightID]
                matchingList.append(matched)
            

            pairs = dict()
            pairs["pairs"] = matchingList
            matchAPI(auth_key, pairs)
        
        # gameResult, changeGrade로 등급을 바꿀 수 있는 턴
        gameResults = gameResultAPI(auth_key)

        commands = dict()
        command = []

        for gameResult in gameResults:
            winner = gameResult["win"]
            loser = gameResult["lose"]
            timeDist = gameResult["taken"]

            grade[winner] += (40 - timeDist)
            grade[loser] -= (40 - timeDist)

            idToGrade = dict()
            idToGrade["id"] = winner
            idToGrade["grade"] = grade[winner]
            command.append(idToGrade)
            idToGrade = dict()
            idToGrade["id"] = loser
            idToGrade["grade"] = grade[loser]
            command.append(idToGrade)
        
        commands["commands"] = command
        changeGradeAPI(auth_key, commands)

        if i > 555:
            pairs = dict()
            pairs["pairs"] = []
            matchAPI(auth_key, pairs)

    
    print(scoreAPI(auth_key))


if __name__ == "__main__":
    scene1()
    