from apis import *

URL = "https://huqeyhi95c.execute-api.ap-northeast-2.amazonaws.com/prod"
USER_NUM = 30

if __name__ == "__main__":
    auth_key = start_api(URL, 1)

    pairs = []
    cmd = []
    for i in range(1, USER_NUM + 1):
        cmd.append({"id": i, "grade": 5000})
    