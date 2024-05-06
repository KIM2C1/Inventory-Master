import json

class Sensor:
    def __init__(self, 이름, 갯수, 링크, 태그, 이미지주소=None):
        self.이름 = 이름
        self.갯수 = 갯수
        self.링크 = 링크
        self.태그 = 태그
        self.이미지주소 = 이미지주소

# 센서 데이터 생성
sensors = [
    Sensor("센서1", 5, "https://www.youtube.com/watch?v=fy-SkZj5wlQ&t=127s", ["태그1", "A", "B", "C", "D", "E", "F"], "https://www.devicemart.co.kr/data/collect_img/kind_0/goods/large/200802281050350.jpg"),
    Sensor("센서2", 3, "https://chat.openai.com/auth/login", ["태그2"]),
    Sensor("센서3", 7, "링크3", ["태그3"]),
    Sensor("센서4", 2, "링크4", ["태그4"]),
    Sensor("센서5", 1, "링크5", ["태그5"]),
    Sensor("센서6", 99, "http", ["asd"])
]
print(sensors)
# JSON 파일로 저장
data = [vars(sensor) for sensor in sensors]  # 클래스의 각 인스턴스를 딕셔너리로 변환

with open("data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("JSON 파일이 생성되었습니다.")