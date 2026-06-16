import time
import audio
import head_pose

# place holders 
GLOBAL_CHEAT = 0
PERCENTAGE_CHEAT = 0
CHEAT_THRESH = 0.6

def avg(current, previous):
    if previous > 1:
        return 0.65
    if current == 0:
        if previous < 0.01:
            return 0.01
        return previous / 1.01
    if previous == 0:
        return current
    return 1 * previous + 0.1 * current

def process():
    global GLOBAL_CHEAT, PERCENTAGE_CHEAT, CHEAT_THRESH
    
    # Count how many suspicious indicators are active
    suspicious_count = 0
    suspicious_count += head_pose.X_AXIS_CHEAT
    suspicious_count += head_pose.Y_AXIS_CHEAT
    suspicious_count += audio.AUDIO_CHEAT
    suspicious_count += head_pose.LIP_MOVEMENT_CHEAT
    
    # Calculate cheat probability based on number of indicators
    # 0 indicators = 0% (relax slightly)
    # 1 indicator = 10-20%
    # 2 indicators = 35-50%
    # 3 indicators = 65-80%
    # 4 indicators = 95%
    if suspicious_count == 0:
        PERCENTAGE_CHEAT = avg(0, PERCENTAGE_CHEAT)
    elif suspicious_count == 1:
        PERCENTAGE_CHEAT = avg(0.15, PERCENTAGE_CHEAT)
    elif suspicious_count == 2:
        PERCENTAGE_CHEAT = avg(0.45, PERCENTAGE_CHEAT)
    elif suspicious_count == 3:
        PERCENTAGE_CHEAT = avg(0.75, PERCENTAGE_CHEAT)
    else:  # 4 indicators
        PERCENTAGE_CHEAT = avg(0.95, PERCENTAGE_CHEAT)
    
    if PERCENTAGE_CHEAT > CHEAT_THRESH:
        GLOBAL_CHEAT = 1
    else:
        GLOBAL_CHEAT = 0
    
    # Debug output
    print(f"Indicators: X={head_pose.X_AXIS_CHEAT} Y={head_pose.Y_AXIS_CHEAT} Audio={audio.AUDIO_CHEAT} Lips={head_pose.LIP_MOVEMENT_CHEAT} | Cheat: {PERCENTAGE_CHEAT:.2%}")

def run_detection():
    while True:
        process()
        time.sleep(0.2)  # Process 5 times per second
