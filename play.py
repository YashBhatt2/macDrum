import time
import joblib
import subprocess
import warnings
from macimu import IMU

# Ignore the annoying scikit-learn warnings about "feature names"
warnings.filterwarnings("ignore", category=UserWarning)

# --- CONFIGURATION ---
DELTA_THRESHOLD = 0.06 
SAMPLES_TO_COLLECT = 40  
COOLDOWN = 0.2 


SOUNDS = {
    'top_left': 'assets/Snare Small.mp3',
    'top_right': 'assets/Hihat AudioMass.mp3',
    'bottom_left': 'assets/AudioMass Crash.mp3',
    'bottom_right': 'assets/kick_small.mp3',
    'none': None # Important: Don't play anything if it predicts 'none'
}

def play_sound(label):
    sound_file = SOUNDS.get(label)
    if sound_file:
        # We use macOS's native 'afplay' via subprocess instead of playsound.
        # This plays the sound in the background instantly without freezing the script!
        subprocess.Popen(["afplay", sound_file])

def main():
    print("Loading Drum Brain...")
    clf = joblib.load('drum_model.pkl')
    print("### Brain loaded. Start tapping!\n")

    with IMU() as imu:
        prev_z = -1.0
        
        while True:
            samples = imu.read_accel()
            
            for s in samples:
                jump = abs(s.z - prev_z)
                
                if jump > DELTA_THRESHOLD:
                    # 1. Capture the 40 samples
                    capture = [[s.x, s.y, s.z]]
                    
                    while len(capture) < SAMPLES_TO_COLLECT:
                        more_samples = imu.read_accel()
                        for ms in more_samples:
                            if len(capture) < SAMPLES_TO_COLLECT:
                                capture.append([ms.x, ms.y, ms.z])
                            else:
                                break
                    
                    # 2. Flatten the data exactly like we did for training
                    flat_data = [val for sublist in capture for val in sublist]
                    
                    # 3. Predict! (scikit-learn expects a 2D array, so wrap it in brackets)
                    prediction = clf.predict([flat_data])[0]
                    
                    print(f"{prediction.upper()}")
                    
                    # 4. Make noise
                    play_sound(prediction)
                    
                    time.sleep(COOLDOWN)
                    prev_z = s.z
                    break 
                
                prev_z = s.z

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Drum kit powered down.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")