### 2번 시나리오 ver 7
# 제출 의도 (성수기 고려)

# amount 값에 제한을 걸어 길이 3 이상인 것들은 바로바로 잡아준다 (ready)
# 그 외의 것들은 따로 리스트에 담아두기 (pause)
# 만약 아직 리스트에 담겨져있는 예약 요청 기한이 다 되었다면, 예약 매칭 시켜주기

# But, 성수기를 고려해 성수기라고 판단되면 바로바로 잡아준다.

# 결괏값


from apis import *

BASE_URL = "https://68ecj67379.execute-api.ap-northeast-2.amazonaws.com/api"

def solve(problem_num, h, w, day):
    auth_key = startAPI(BASE_URL, problem_num)

    # [height][width][date] 체크 배열 초기화
    check = [[[False for day in range(day + 1)] for col in range(w + 1)] for row in range(h + 1)]
    checkIn = [[] for _ in range(day + 1)]
    expires = [[] for _ in range(day + 1)]

    pauses = []

    # 성수기 (amount >= 13 && (7 ~ 30) 사이 기간 카운트)
    prePeakCount = 10000 # 첫 주부터 성수기로 오해할 수 있어서 큰 값으로 초기화함
    nowPeakCount = 0

    peakCount = 0

    for week in range(1, day + 1, 7):
        nowPeakCount = 0
        for cnt in range(week, week + 7):
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

                # 만약 현재 성수기라면
                if peakCount > 0:
                    ready.append((reserveID, amount, checkInDate, checkOutDate, checkOutDate - checkInDate))

                else:
                    if amount >= 13 and 7 <= checkInDate and checkInDate <= 30:
                        nowPeakCount += 1

                    expireDate = min(cnt + 14, checkInDate - 1)
                    if amount >= 2:
                        ready.append((reserveID, amount, checkInDate, checkOutDate, checkOutDate - checkInDate))
                    else:
                        pauses.append((expireDate, reserveID, amount, checkInDate, checkOutDate))

            tmp_pauses = []
            # 만약 오늘내일하는 친구라면
            for pause in pauses:
                if pause[0] < cnt + 2:
                    ready.append((pause[1], pause[2], pause[3], pause[4], pause[4] - pause[3]))
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
        
        # 만약 이번 주 피크 범위 예약율이 저번보다 50% 이상 증가했다면?
        if peakCount <= 0 and nowPeakCount >= (prePeakCount * 1.5):
            # 해당 주 기준 7주 동안은 성수기로 판단한다.
            peakCount = 8

        prePeakCount = nowPeakCount
        # 만약 성수기가 끝났다면 다시 초기화
        if peakCount == 1:
            prePeakCount = 10000
        peakCount -= 1

        

    print(scoreAPI(BASE_URL, auth_key))





# 시작 지점
if __name__ == "__main__":
    solve(2, 10, 200, 1000)