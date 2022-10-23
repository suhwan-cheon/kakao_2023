from sys import stdin
import requests
import operator as op

BASE_URL = 'https://huqeyhi95c.execute-api.ap-northeast-2.amazonaws.com/prod'
x_auth_token = '904aa7eb39b8f419ee1148d8d03d32e2'
auth_key = None

# start API
def start(problem):
    return requests.post(BASE_URL+'/start', headers={'X-Auth-Token':x_auth_token}, json={'problem': problem}).json()["auth_key"]

# Waiting Line API
def waitLine(auth_key):
    return requests.get(BASE_URL+'/waiting_line', headers={'Authorization': auth_key}).json()["waiting_line"]

# Game Result API
def gameResult(auth_key):
    return requests.get(BASE_URL+'/game_result', headers={'Authorization': auth_key}).json()["game_result"]

# User Info API
def userInfo(auth_key):
    return requests.get(BASE_URL+'/user_info', headers={'Authorization': auth_key}).json()

# Match API
def match(auth_key, matchPair):
    return requests.put(BASE_URL+'/match', headers={'Authorization': auth_key}, json=matchPair).json()

# Change Grade API
def changeGrade(auth_key, cmds):
    return requests.put(BASE_URL+'/change_grade', headers={'Authorization': auth_key}, json=cmds).json()

# Score API
def score(auth_key):
    return requests.get(BASE_URL+'/score', headers={'Authorization': auth_key}).json()

# # API 작동 테스트 함수
# def test():
#     # start API
#     auth_key = start(1)
#     print(auth_key)

#     # Waiting Line API
#     print(waitLine(auth_key))
    

#     # Game Result API
#     result = gameResult(auth_key)
#     print(result)

#     # User Info API
#     info = userInfo(auth_key)
#     print(info)

#     # Match API
#     games = dict()
#     games["pairs"] = []
#     games["pairs"].append([1, 2])
#     games["pairs"].append([3, 4])
#     print(match(auth_key, games))

#     # Change Grade API
#     change_cmds = dict()
#     change_cmds["commands"] = []
#     change_cmds["commands"].append({ "id": 1, "grade": 1900 })
#     print(changeGrade(auth_key, change_cmds))
    
#     # Score API
#     print(score(auth_key))

# main 부분

# API test
#test()

# get auth key
auth_key = start(2)
ranking = [0 for _ in range(901)]

win_cnt = [0 for _ in range(901)]
lose_cnt = [0 for _ in range(901)]

# game start (0 ~ 595 + 1턴 진행)
for i in range(597):
    # 현재 등급 확인
    uInfo = userInfo(auth_key)
    for user in uInfo["user_info"]:
        uId = user["id"]
        uGrade = user["grade"]
        ranking[uId] = uGrade

    # match game
    games = dict()
    games["pairs"] = []

    # 0턴 처리
    if i == 0:
        match(auth_key, games) # 의미 없는 match API
        # 현재 등급 -> 평균 값에 맞출 필요가 있다.
        ranking = [0 for _ in range(901)]
        change_cmds = dict()
        change_cmds["commands"] = []
        for j in range(1, 901):
            change_cmds["commands"].append({ "id": j, "grade": 0 })
        changeGrade(auth_key, change_cmds)
        continue
    # waiting line, match API를 사용할 수 있는 턴 (직접적으로 게임 매칭을 할 수 있는 턴)
    elif i <= 555:
        # {id, from}
        lines = waitLine(auth_key)

        for j in range(len(lines)):
            lines[j]["rating"] = ranking[lines[j]["id"]]
        
        lines.sort(key=op.itemgetter("rating"))

        #print(lines)
        for j in range(0, len(lines), 2):
            if j + 1 < len(lines):
            #if j + 1 < len(lines) and abs(lines[j]["rating"] - lines[j + 1]["rating"]) < 100 : 
                games["pairs"].append([lines[j]["id"], lines[j + 1]["id"]])
        #print(games)
        match(auth_key, games)

    # game result, change grade API를 사용할 수 있는 턴
    else:
        match(auth_key, games) # 의미 없는 match API
    
    change_cmds = dict()
    change_cmds["commands"] = []

    # 게임 결과 받아오기
    game_ret = gameResult(auth_key)
    # print(game_ret)
    if len(game_ret) > 0:
        for game in game_ret:
            winner = game["win"]
            loser = game["lose"]
            minute = game["taken"]
            
            #if minute < 11 : continue
            change_cmds["commands"].append({ "id": winner, "grade": (ranking[winner] + (40 - minute) ) })
            #change_cmds["commands"].append({ "id": loser, "grade": (ranking[loser] - (minute) ) })


        # 등급 수정하기
        changeGrade(auth_key, change_cmds)

        
        # print(len(change_cmds["commands"]))
        print(userInfo(auth_key))
    
print(score(auth_key))

# # 어뷰저 판단
# check = [True for _ in range(999)]
# # 3-10 값 체크
# # 10번이상 했을 때 패배 확률이 80% 넘어가는경우 -> 다음 3-10 격차에서 해당 id가 들어오면 continue 
# win_cnt = [0 for _ in range(999)]
# lose_cnt = [0 for _ in range(999)]