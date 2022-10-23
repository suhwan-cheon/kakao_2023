from sys import stdin
import requests
import operator as op

### 기본값 설정 ###

BASE_URL = 'https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users'
x_auth_token = '2dd38574d34bb60bdf8cb9c065bcb4a0'
auth_key = None

###############

### API 영역 ###

# Start API
def startAPI(problem):
    return requests.post(BASE_URL+'/start', headers={'X-Auth-Token':x_auth_token}, json={'problem': problem}).json()["auth_key"]

# Locations API
def locationsAPI(auth_key):
    return requests.get(BASE_URL+'/locations', headers={'Authorization': auth_key}).json()["locations"]

# Trucks API
def trucksAPI(auth_key):
    return requests.get(BASE_URL+'/trucks', headers={'Authorization': auth_key}).json()["trucks"]

# simulate API
def simulateAPI(auth_key, commands):
    return requests.put(BASE_URL+'/simulate', headers={'Authorization': auth_key}, json=commands).json()

# Score API
def scoreAPI(auth_key):
    return requests.get(BASE_URL+'/score', headers={'Authorization': auth_key}).json()

################

### code 영역 ###

# ID -> (y, x) 좌표로 바꾸는 dict
ID_TO_YX = dict()
XY_TO_ID = [[0 for col in range(60)] for row in range(60)]
boards = [[0 for col in range(60)] for row in range(60)]

def startInit(n):

    # 대여소 형식 변경
    id = 0
    for y in range(0, n):
        for x in range(0, n):
            ID_TO_YX[id] = [4 - x, y]
            XY_TO_ID[4 - x][y] = id
            id += 1


# 시나리오 1 (v1)
def scene1():
    auth_key = startAPI(1)
    startInit(5)

    # simulate flow
    for i in range(720):

        # simulate api에 보낼 payload
        simulate_payload = dict()

        # location 호출
        locations = locationsAPI(auth_key)
        for location in locations:
            locY = ID_TO_YX[location["id"]][0]
            locX = ID_TO_YX[location["id"]][0]
            boards[locY][locX] = location["located_bikes_count"]

        # trucks 호출
        trucks = trucksAPI(auth_key)

        # 이미 사용한 트럭인지 파악하기
        usedTruck = [False for _ in range(5)]

        # 알맞은 트럭이 하나라도 있으면 true
        truckFlag = False
        

        # 1개 이하로 저장하고 있는 location 파악
        for y in range(5):
            for x in range(5):
                if boards[y][x] <= 1:

                    # (y, x) 좌표에 두어야 할 자전거의 개수
                    needBikeCnt = 2 - boards[y][x]

                    # 조건에 만족하는 트럭이 한 개라도 있다면 true
                    isTruckCanDo = False
                    # 가장 효율적인 트럭, 중간다리의 좌표와 거리
                    bestTruck_Y = -1
                    bestTruck_X = -1
                    bestBridge_Y = -1
                    bestBridge_X = -1
                    bestDist = 999
                    bestTruckID = -1

                    # 트럭과 비교
                    for truck in trucks:

                        truckID = truck["id"]

                        # 이미 이 턴에 움직였던 트럭이라면
                        if usedTruck[truckID] == True:
                            continue

                        truckY, truckX = ID_TO_YX[truck["location_id"]]
                        truckCanHasBikes = 20 - truck["loaded_bikes_count"]


                        # 만약 트럭이 2개도 담지 못한다면
                        if truckCanHasBikes < 2:
                            continue

                        # (y, x) ~ (truckY, truckX) 범위 파악
                        # 반복문 탈출 flag
                        iterFlag = False


                        for iterY in range(min(y, truckY), max(y, truckY) + 1):
                            for iterX in range(min(x, truckX), max(x, truckX) + 1):

                                # 만약 이 범위 내에 하나라도 필요한 바이크 개수를 채울 수 있다면
                                if boards[iterY][iterX] - 2 >= needBikeCnt:
                                    iterFlag = True

                                    # 이 곳으로 이동할 수 있다
                                    isTruckCanDo = True

                                    # 거리는 맨해튼 거리로 파악
                                    thisTruckDist = abs(y - truckY) + abs(x - truckX)

                                    if bestDist > thisTruckDist:
                                        bestDist = thisTruckDist
                                        bestTruckID = truckID
                                        bestTruck_Y = truckY
                                        bestTruck_X = truckX
                                        bestBridge_Y = iterY
                                        bestBridge_X = iterX
                                    
                                    break

                            if iterFlag == True:
                                break



                    ## 트럭 비교가 끝난 부분

                    # 만약 만족하는 트럭이 없다면
                    if isTruckCanDo == False:
                        continue

                    # 만족하는 트럭이 존재한다면
                    usedTruck[bestTruckID] = True


                    truck_cmds = []

                    # 트럭에서 중간 다리까지 (truck ~ bridge)
                    for _ in range(abs(bestTruck_Y - bestBridge_Y)):
                        # 위로 올라가야 한다면
                        if bestTruck_Y > bestBridge_Y:
                            truck_cmds.append(1)
                        else:
                            truck_cmds.append(3)
                    
                    for _ in range(abs(bestTruck_X - bestBridge_X)):
                        # 왼쪽으로 이동해야 한다면
                        if bestTruck_X > bestBridge_X:
                            truck_cmds.append(4)
                        else:
                            truck_cmds.append(2)

                    # 자전거 상차
                    for _ in range(needBikeCnt):
                        truck_cmds.append(5)

                    # 중간 다리에서 목표 지점까지 (bridge ~ (y, x))
                    for _ in range(abs(y - bestBridge_Y)):
                        # 위로 올라가야 한다면
                        if bestBridge_Y > y:
                            truck_cmds.append(1)
                        else:
                            truck_cmds.append(3)
                    
                    for _ in range(abs(x - bestBridge_X)):
                        # 왼쪽으로 이동해야 한다면
                        if bestBridge_X > x:
                            truck_cmds.append(4)
                        else:
                            truck_cmds.append(2)

                    # 자전거 하차
                    for _ in range(needBikeCnt):
                        truck_cmds.append(6)

                    # simulate payload에 저장
                    truck_move = dict()
                    truck_move["truck_id"] = bestTruckID
                    truck_move["command"] = truck_cmds

                    # print(truck_move)

                    truckFlag = True

                    commands_payload = []
                    commands_payload.append(truck_move)

                    simulate_payload["commands"] = commands_payload

        # 움직일 트럭이 없다면
        if truckFlag == False:
            simulate_payload["commands"] = []

        # 모든 트럭을 움직였다면 simulate 함수 호출
        simulate_response = simulateAPI(auth_key, simulate_payload)
        # print(simulate_response)
        # print("실패한 요청 수 : " + simulate_response["failed_requests_count"])
        # print("이동한 거리의 총합 : " + simulate_response["distance"])
        print("simulate 횟수 : " + str(i))



    print(scoreAPI(auth_key))


# 시나리오 2 (v1)
def scene2():
    auth_key = startAPI(2)
    startInit(60)

    # simulate flow
    for i in range(720):

        # simulate api에 보낼 payload
        simulate_payload = dict()

        # location 호출
        locations = locationsAPI(auth_key)
        for location in locations:
            locY = ID_TO_YX[location["id"]][0]
            locX = ID_TO_YX[location["id"]][0]
            boards[locY][locX] = location["located_bikes_count"]

        # trucks 호출
        trucks = trucksAPI(auth_key)

        # 이미 사용한 트럭인지 파악하기
        usedTruck = [False for _ in range(60)]

        # 1개 이하로 저장하고 있는 location 파악
        for y in range(60):
            for x in range(60):
                if boards[y][x] <= 1:

                    # (y, x) 좌표에 두어야 할 자전거의 개수
                    needBikeCnt = 2 - boards[y][x]

                    # 조건에 만족하는 트럭이 한 개라도 있다면 true
                    isTruckCanDo = False
                    # 가장 효율적인 트럭, 중간다리의 좌표와 거리
                    bestTruck_Y = -1
                    bestTruck_X = -1
                    bestBridge_Y = -1
                    bestBridge_X = -1
                    bestDist = 999
                    bestTruckID = -1

                    # 트럭과 비교
                    for truck in trucks:

                        truckID = truck["id"]

                        # 이미 이 턴에 움직였던 트럭이라면
                        if usedTruck[truckID] == True:
                            continue

                        truckY, truckX = ID_TO_YX[truck["location_id"]]
                        truckCanHasBikes = 20 - truck["loaded_bikes_count"]


                        # 만약 트럭이 2개도 담지 못한다면
                        if truckCanHasBikes < 2:
                            continue

                        # (y, x) ~ (truckY, truckX) 범위 파악
                        # 반복문 탈출 flag
                        iterFlag = False


                        for iterY in range(min(y, truckY), max(y, truckY) + 1):
                            for iterX in range(min(x, truckX), max(x, truckX) + 1):

                                # 만약 이 범위 내에 하나라도 필요한 바이크 개수를 채울 수 있다면
                                if boards[iterY][iterX] - 2 >= needBikeCnt:
                                    iterFlag = True

                                    # 이 곳으로 이동할 수 있다
                                    isTruckCanDo = True

                                    # 거리는 맨해튼 거리로 파악
                                    thisTruckDist = abs(y - truckY) + abs(x - truckX)

                                    if bestDist > thisTruckDist:
                                        bestDist = thisTruckDist
                                        bestTruckID = truckID
                                        bestTruck_Y = truckY
                                        bestTruck_X = truckX
                                        bestBridge_Y = iterY
                                        bestBridge_X = iterX
                                    
                                    break

                            if iterFlag == True:
                                break



                    ## 트럭 비교가 끝난 부분

                    # 만약 만족하는 트럭이 없다면
                    if isTruckCanDo == False:
                        continue

                    # 만족하는 트럭이 존재한다면
                    usedTruck[bestTruckID] = True

                    print(1)

                    truck_cmds = []

                    # 트럭에서 중간 다리까지 (truck ~ bridge)
                    for _ in range(abs(bestTruck_Y - bestBridge_Y)):
                        # 위로 올라가야 한다면
                        if bestTruck_Y > bestBridge_Y:
                            truck_cmds.append(1)
                        else:
                            truck_cmds.append(3)
                    
                    for _ in range(abs(bestTruck_X - bestBridge_X)):
                        # 왼쪽으로 이동해야 한다면
                        if bestTruck_X > bestBridge_X:
                            truck_cmds.append(4)
                        else:
                            truck_cmds.append(2)

                    # 자전거 상차
                    for _ in range(needBikeCnt):
                        truck_cmds.append(5)

                    # 중간 다리에서 목표 지점까지 (bridge ~ (y, x))
                    for _ in range(abs(y - bestBridge_Y)):
                        # 위로 올라가야 한다면
                        if bestBridge_Y > y:
                            truck_cmds.append(1)
                        else:
                            truck_cmds.append(3)
                    
                    for _ in range(abs(x - bestBridge_X)):
                        # 왼쪽으로 이동해야 한다면
                        if bestBridge_X > x:
                            truck_cmds.append(4)
                        else:
                            truck_cmds.append(2)

                    # 자전거 하차
                    for _ in range(needBikeCnt):
                        truck_cmds.append(6)

                    # simulate payload에 저장
                    truck_move = dict()
                    truck_move["truck_id"] = bestTruckID
                    truck_move["command"] = truck_cmds

                    print(truck_move)

                    commands_payload = []
                    commands_payload.append(truck_move)

                    simulate_payload["commands"] = commands_payload

        # 움직일 트럭이 없다면
        simulate_payload["commands"] = []

        # 모든 트럭을 움직였다면 simulate 함수 호출
        simulate_response = simulateAPI(auth_key, simulate_payload)
        print(simulate_response)
        # print("실패한 요청 수 : " + simulate_response["failed_requests_count"])
        # print("이동한 거리의 총합 : " + simulate_response["distance"])
        print("simulate 횟수 : " + str(i))



    print(scoreAPI(auth_key))

if __name__ == "__main__":
    scene1()
    