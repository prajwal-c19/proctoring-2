import sounddevice as sd
import numpy as np

# Placeholders and global variables
SOUND_AMPLITUDE = 0
AUDIO_CHEAT = 0

# Sound variables
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CALLBACKS_PER_SECOND = SAMPLE_RATE // BLOCK_SIZE  # ~21 callbacks per second
SUS_FINDING_FREQUENCY = 2                         # Checks 2 times per second
SOUND_AMPLITUDE_THRESHOLD = 0.001                 # Very low threshold for testing

# Packing *n* frames to calculate SUS
FRAMES_COUNT = max(1, int(CALLBACKS_PER_SECOND / SUS_FINDING_FREQUENCY))
AMPLITUDE_LIST = [0] * FRAMES_COUNT
SUS_COUNT = 0
count = 0
callback_count = 0

def calculate_rms(indata):
    """Calculate the RMS value of the audio data (normalized to 0-1 range)."""
    return np.sqrt(np.mean(indata**2))

def print_sound(indata, outdata, frames, time, status):
    global SOUND_AMPLITUDE, SUS_COUNT, count, SOUND_AMPLITUDE_THRESHOLD, AUDIO_CHEAT, callback_count
    
    callback_count += 1
    
    try:
        if status:
            print(f"Audio stream warning: {status}")
        
        rms_amplitude = calculate_rms(indata)
        AMPLITUDE_LIST.append(rms_amplitude)
        count += 1
        AMPLITUDE_LIST.pop(0)
        
        if count == FRAMES_COUNT:
            avg_amp = sum(AMPLITUDE_LIST) / FRAMES_COUNT
            SOUND_AMPLITUDE = avg_amp
            
            # Debug: Print current amplitude
            print(f"[{callback_count}] RMS: {avg_amp:.6f} | Threshold: {SOUND_AMPLITUDE_THRESHOLD} | SUS: {SUS_COUNT} | AUDIO_CHEAT: {AUDIO_CHEAT}")
            
            if SUS_COUNT >= 2:
                AUDIO_CHEAT = 1
                print("*** AUDIO CHEAT DETECTED ***")
                SUS_COUNT = 0
            
            if avg_amp > SOUND_AMPLITUDE_THRESHOLD:
                SUS_COUNT += 1
            else:
                SUS_COUNT = 0
                AUDIO_CHEAT = 0
            
            count = 0
    except Exception as e:
        print(f"Error in callback: {e}")

def sound():
    global callback_count
    try:
        print("Starting audio stream...")
        print(f"Sample rate: {SAMPLE_RATE}, Block size: {BLOCK_SIZE}, Frames count: {FRAMES_COUNT}")
        print(f"Current threshold: {SOUND_AMPLITUDE_THRESHOLD}")
        
        # List available audio devices
        devices = sd.query_devices()
        print(f"Available audio devices:")
        for i, device in enumerate(devices):
            print(f"  [{i}] {device['name']}")
        
        # Try to find input device
        try:
            default_device = sd.default.device
            print(f"Using default device: {default_device}")
        except:
            default_device = None
        
        # Configure audio stream with proper settings
        with sd.Stream(samplerate=SAMPLE_RATE, 
                       channels=1, 
                       blocksize=BLOCK_SIZE,
                       callback=print_sound,
                       latency='low',
                       device=default_device):
            print("✓ Audio stream started. Listening for sounds...")
            sd.sleep(-1)
            
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        print("Make sure you have a microphone connected and audio permissions enabled.")

def sound_analysis():
    global AMPLITUDE_LIST, FRAMES_COUNT, SOUND_AMPLITUDE
    while True:
        AMPLITUDE_LIST.append(SOUND_AMPLITUDE)
        AMPLITUDE_LIST.pop(0)

        avg_amp = sum(AMPLITUDE_LIST) / FRAMES_COUNT

        if avg_amp > 10:
            print("Sus...")

if __name__ == "__main__":
    sound()
