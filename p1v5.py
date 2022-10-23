### 1번 시나리오 ver 5
# 제출 의도
# amount 값에 제한을 걸어 길이 3 이상인 것들은 바로바로 잡아준다 (ready)
# 그 외의 것들은 따로 리스트에 담아두기 (pause)
# 만약 아직 리스트에 담겨져있는 예약 요청 기한이 다 되었다면, 예약 매칭 시켜주기

# 당일만 매칭한 결괏값
# {'accuracy_score': 80.0, 'efficiency_score': 6.310756972111554, 'penalty_score': 203.09527543179732, 'score': 383.2154815403143}
# 길이 2 이하인 예약들을 이전 날짜 -3 까지 모두 매칭한 결괏값
# {'accuracy_score': 80.0, 'efficiency_score': 7.266932270916334, 'penalty_score': 186.88030645847803, 'score': 400.3866258124383}
# 길이 1인 것들만 뺄까
# {'accuracy_score': 80.0, 'efficiency_score': 8.637450199203187, 'penalty_score': 176.01312753421897, 'score': 412.6243226649842}


from apis import *

BASE_URL = "https://68ecj67379.execute-api.ap-northeast-2.amazonaws.com/api"

def solve(problem_num, h, w, day):
    auth_key = startAPI(BASE_URL, problem_num)

    # [height][width][date] 체크 배열 초기화
    check = [[[False for day in range(day + 1)] for col in range(w + 1)] for row in range(h + 1)]
    checkIn = [[] for _ in range(day + 1)]
    expires = [[] for _ in range(day + 1)]

    pauses = []

    for cnt in range(1, day + 1):

        # reply API를 위한 딕셔너리
        reply = dict()
        reply["replies"] = []

        requests = newRequestAPI(BASE_URL, auth_key)

        ready = []

        # 예약 기한별로 먼저 담아둔다.
        for request in requests:
            reserveID = request["id"] # 예약 ID
            amount = request["amount"] # 연속 구간
            checkInDate = request["check_in_date"]
            checkOutDate = request["check_out_date"]

            expireDate = min(cnt + 14, checkInDate - 1)
            if amount >= 2:
                ready.append((reserveID, amount, checkInDate, checkOutDate))
            else:
                pauses.append((expireDate, reserveID, amount, checkInDate, checkOutDate))

        tmp_pauses = []
        # 만약 오늘내일하는 친구라면
        for pause in pauses:
            if pause[0] < cnt + 2:
                ready.append((pause[1], pause[2], pause[3], pause[4]))
            else:
                tmp_pauses.append(pause)
        pauses = tmp_pauses

        # 오늘 처리할 예약 정보들을 담는다.
        ready.sort(key = lambda element: element[1])

        for request in ready:
            
            reserveID = request[0] # 예약 ID
            amount = request[1] # 연속 구간
            checkInDate = request[2]
            checkOutDate = request[3]


            # 해당 요청에 대한 예약이 가능하면 true
            wholeReserveFlag = False
            

            # (checkIn ~ checkOut - 1) 날짜 구간에 예약된 것이 없으면 된다.
            for height in range(1, h + 1):

                # (1 ~ w - amount + 1) 까지만 탐색해도 된다. (연속 구간 처리)
                for width in range(1, w - amount + 2):


                    # (height, width) 를 기점으로 한 예약이 가능하면 true
                    reserveFlag = True

                    # (height, width) 를 기점으로 (height, width + amount - 1) 객실을 확인한다.
                    for cont in range(amount):

                        # 해당 구간의 날짜를 모두 탐색해서 되는지 확인한다.
                        for date in range(checkInDate, checkOutDate):
                            # 만약 이미 예약되어있는 날짜라면
                            if check[height][width + cont][date] == True:
                                reserveFlag = False
                                break
                        
                        # 더 볼 필요 없다
                        if reserveFlag == False:
                            break

                    # 만약 예약이 가능했다면
                    if reserveFlag == True:
                        wholeReserveFlag = True
                        roomNumber = str(height)
                        widthNum = str(width)
                        if len(widthNum) == 1:
                            roomNumber += "00"
                        elif len(widthNum) == 2:
                            roomNumber += "0"
                        
                        roomNumber += widthNum

                        # 미리 checkIn에 기록해둔다 (id, room_number)
                        checkIn[checkInDate].append({"id": reserveID, "room_number": int(roomNumber)})

                        # 예약처리해둔다
                        for cont in range(amount):

                            # 해당 구간의 날짜를 모두 탐색해서 되는지 확인한다.
                            for date in range(checkInDate, checkOutDate):
                                check[height][width + cont][date] = True
                    
                    if wholeReserveFlag == True:
                        break

                if wholeReserveFlag == True:
                    break

                    
            # 만약 예약이 가능했다면
            if wholeReserveFlag == True:
                
                # reply에 담는다
                reply["replies"].append({"id": reserveID, "reply": "accepted"})
            
            # 불가능했다면
            else:
                reply["replies"].append({"id": reserveID, "reply": "refused"})

        # 오늘의 예약 답변
        replyAPI(BASE_URL, auth_key, reply)
        
        # 오늘의 시뮬레이션 기록
        roomAssign = dict()
        roomAssign["room_assign"] = checkIn[cnt]

        ret = simulateAPI(BASE_URL, auth_key, roomAssign)

        if cnt % 10 == 0:
            print(ret)

    print(scoreAPI(BASE_URL, auth_key))





# 시작 지점
if __name__ == "__main__":
    solve(1, 3, 20, 200)