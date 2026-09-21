from machine import Pin, ADC
from neopixel import NeoPixel
import time
import random

# =========================
# 설정
# =========================

# MQ-2
sensor = ADC(Pin(27))   # GP27

# WS2813
TIMING = (280, 515, 515, 745)
LED_COUNT = 60
led = NeoPixel(Pin(16), LED_COUNT, timing=TIMING)

# 게임 설정
GAME_TIME = 10

# 네 MQ-2 평소 측정값에 맞춤
TARGET_MIN = 9500
TARGET_MAX = 11000

# 목표값과 200 이내면 성공
SUCCESS_RANGE = 300


# =========================
# LED 함수
# =========================

def clear_led():
    for i in range(LED_COUNT):
        led[i] = (0, 0, 0)
    led.write()


def show_bar(distance):

    # 목표값과의 최대 차이
    max_distance = 1500

    count = int((distance / max_distance) * LED_COUNT)

    if count < 0:
        count = 0

    if count > LED_COUNT:
        count = LED_COUNT

    # 가까울수록 초록
    # 멀수록 빨강
    ratio = distance / max_distance

    if ratio > 1:
        ratio = 1

    red = int(255 * ratio)
    green = int(255 * (1 - ratio))

    for i in range(LED_COUNT):

        if i < count:
            led[i] = (red, green, 0)
        else:
            led[i] = (0, 0, 0)

    led.write()


def success_effect():

    for n in range(3):

        for i in range(LED_COUNT):
            led[i] = (0, 255, 0)

        led.write()
        time.sleep(0.3)

        clear_led()
        time.sleep(0.3)


def fail_effect():

    for n in range(3):

        for i in range(LED_COUNT):
            led[i] = (255, 0, 0)

        led.write()
        time.sleep(0.2)

        clear_led()
        time.sleep(0.2)


# =========================
# 센서값 읽기
# =========================

def read_sensor():
    return sensor.read_u16()


# =========================
# 게임
# =========================

clear_led()

print("==============================")
print("     MQ-2 센서 맞추기 게임")
print("==============================")
print("Shell에 '다시'를 입력하면")
print("새로운 게임을 시작합니다.")
print()


# 게임을 계속 반복
while True:

    # -------------------------
    # 새로운 게임 시작
    # -------------------------

    # 게임 시작 전 현재 MQ-2 값 측정
    current_value = read_sensor()
    
    # 현재 값보다 높은 목표값 생성
    target_min = current_value + 300
    target_max = current_value + 1500
    
    target = random.randint(target_min, target_max)
    
    print()
    print("📟 현재 MQ-2 값:", current_value)
    print("🎯 목표값:", target)
    print()
    print("==============================")
    print("🎮 새로운 게임!")
    print("🎯 목표값:", target)
    print("센서값을 목표값에 가깝게 만들어 보세요!")
    print("⏱️ 제한시간:", GAME_TIME, "초")
    print("==============================")
    print()

    start_time = time.ticks_ms()

    best_distance = 65535
    best_value = 0
    success = False

    # -------------------------
    # 게임 진행
    # -------------------------

    while True:

        value = read_sensor()

        # 목표값과의 차이
        distance = abs(value - target)

        # 최고 기록 저장
        if distance < best_distance:
            best_distance = distance
            best_value = value

        # LED 표시
        show_bar(distance)

        # 시간 계산
        elapsed = time.ticks_diff(
            time.ticks_ms(),
            start_time
        ) / 1000

        remaining = GAME_TIME - elapsed

        if remaining < 0:
            remaining = 0

        # 현재 상황 출력
        print(
            "목표:",
            target,
            "| 현재:",
            value,
            "| 차이:",
            distance,
            "| 남은 시간:",
            round(remaining, 1),
            "초"
        )

        # 성공 확인
        if distance <= SUCCESS_RANGE:
            success = True
            break

        # 시간 종료
        if elapsed >= GAME_TIME:
            break

        time.sleep(0.1)


    # -------------------------
    # 게임 결과
    # -------------------------

    clear_led()

    print()
    print("==============================")

    if success:

        print("🎉 성공!")
        print("🎯 목표값:", target)
        print("📟 성공한 값:", value)
        print("📏 차이:", distance)

        # 점수 계산
        score = 1000 - int(distance / 10)

        if score < 0:
            score = 0

        print("🏆 점수:", score)

        success_effect()

    else:

        print("⏰ 시간 종료!")
        print("🎯 목표값:", target)
        print("📟 가장 가까웠던 값:", best_value)
        print("📏 차이:", best_distance)

        # 점수 계산
        score = 1000 - int(best_distance / 10)

        if score < 0:
            score = 0

        print("🏆 점수:", score)

        fail_effect()


    print("==============================")
    print("게임이 끝났습니다.")
    print()
    print("다시 하려면 Shell에 '다시'를 입력하세요.")
    print("끝내려면 '끝'을 입력하세요.")
    print()

    # -------------------------
    # 다시 하기
    # -------------------------

    command = input("> ")

    if command == "다시":
        print()
        print("🔄 새로운 게임을 시작합니다!")
        time.sleep(1)
        continue

    elif command == "끝":
        print()
        print("👋 게임을 종료합니다.")
        clear_led()
        break

    else:
        print()
        print("입력이 잘못되었습니다.")
        print("'다시'를 입력하면 게임을 계속할 수 있습니다.")
        print()

        # 잘못 입력해도 다시 게임 시작
        time.sleep(1)
        continue
