from macimu import IMU
import time

# Note: This script must be executed with 'sudo'
with IMU() as imu:
    print("Streaming accelerometer data... Press Ctrl+C to stop.")
    while True:
        # Read all new samples since the last call
        samples = imu.read_accel()
        for s in samples:
            print(f"X: {s.x:.3f}g | Y: {s.y:.3f}g | Z: {s.z:.3f}g")
        time.sleep(0.1)