from macimu import IMU
from playsound3 import playsound
import csv
import time

DELTA_THRESHOLD = 0.06 
SAMPLES_TO_COLLECT = 40  
COOLDOWN = 0.5           
FILENAME = "data2.csv"


label = input("Enter label for this session (e.g., left, right, trackpad): ").strip()
print(f"\n🎧 Starting collection for '{label}'.")
print(f"Waiting for a sudden Z-axis shift of {DELTA_THRESHOLD}g... SLAP when ready!\n")


def main():
    with IMU() as imu:
        prev_z = -1.0 # Initialize roughly at gravity
    
        while True:
            samples = imu.read_accel()
            
            for s in samples:
                # STATE 0: Check the DELTA (the sudden change)
                jump = abs(s.z - prev_z)
                
                if jump > DELTA_THRESHOLD:
                    print(f"💥 SLAP DETECTED! (Jump of {jump:.3f}g) Recording...")
                    # playsound("Overworld.mp3")

                    capture = [[s.x,s.y,s.z]]

                    while len(capture) < SAMPLES_TO_COLLECT:
                        more_samples = imu.read_accel()
                        for ms in more_samples:
                            if len(capture) < SAMPLES_TO_COLLECT:
                                capture.append([ms.x, ms.y, ms.z])
                            else:
                                break
                    
                    flat_data =[]
                    for sublist in capture:
                        for val in sublist:
                            flat_data.append(val)
                    flat_data.append(label)

                    with open(FILENAME, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(flat_data)

                    print(f"Data Saved to csv {FILENAME}")
                    # After cooling down, reset prev_z so we don't instantly re-trigger
                    time.sleep(COOLDOWN)
                    prev_z = s.z 
                    break 
                
                # Update prev_z for the next loop if we didn't trigger
                prev_z = s.z

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Session ended. Data saved. IMU connection closed.")
    except Exception as e:
        print(f"\n\n❌ An unexpected error occurred: {e}")
