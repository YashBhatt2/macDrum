# macDrum
Turn Your Macbook Into A Drum

One day I was scrolling on reels when I saw this reel:        
[Reel](https://www.instagram.com/reel/DWO4jpYEwh6/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ==)

While watching this reel I was tapping my table like Its a drum, and then I decided to make My laptop detect where I am tapping it, using the Inbuilt accelerometer that this reel's app [slapmac](https://slapmac.com/) uses, (I am guessing)

So, I reversed-engineered the concept and built **macDrum**—a tiny, low-latency, machine-learning-powered drum kit that turns different zones of your MacBook chassis into live MIDI/audio triggers.

## How it Works
Instead of using the microphone or camera, `macDrum` intercepts raw physical vibrations traveling through the aluminum unibody of the Mac. Here is the engineering breakdown of the pipeline:

### 1. Telemetry & Data Ingestion
MacBooks have an internal **IMU (Inertial Measurement Unit)** to detect sudden drops (historically to park hard drive heads). Using the `macimu` bridge, this project hooks directly into Apple's internal **Shared Memory (SHM)** segment. This bypasses high-overhead OS layers to read raw, high-frequency linear acceleration across three spatial dimensions: $X$, $Y$, and $Z$.

### 2. Signal Thresholding & Edge Triggering
The system idle-polls gravity (resting at roughly $-1.0g$ on the Z-axis). When an impact occurs, the sudden shockwave causes an acute spike in amplitude. The script uses an **asymmetric delta threshold mechanism** to catch this spike. The moment $\Delta Z > 0.06g$, an edge-trigger fires, and the script instantly captures a rolling spatial-temporal window of the next 40 hardware clock ticks.

### 3. Spatial Matrix Flattening
A single slap yields a 2D matrix of shape `(40, 3)`—representing 40 sequential moments in time, each with 3 spatial axes. To feed this into a classical classifier, the matrix is programmatically linearized into a **1D Feature Vector** of 120 dimensions:

$$[X_1, Y_1, Z_1, X_2, Y_2, Z_2, \dots, X_{40}, Y_{40}, Z_{40}]$$

### 4. Machine Learning Inference (The Brain)
The core classification is handled by a **Supervised Random Forest Classifier** (`scikit-learn`). 
* Rather than relying on rigid mathematical formulas, the model uses an ensemble of **100 independent Decision Trees**. 
* During training, trees evaluate splits using **Gini Impurity** to discover exactly how a shockwave dissipates through the chassis.
* When you hit a zone, the 100 trees run parallel evaluations and hold a **majority vote** to instantly classify the vibration signature into one of five categories: `top_left`, `top_right`, `bottom_left`, `bottom_right`, or `none`.

### 5. Asynchronous, Non-Blocking Audio Execution
Using typical python audio players freezes the execution thread during playback, causing massive input lag. `macDrum` achieves near **zero-latency audio rendering** by utilizing an asynchronous runtime pattern. It spins up concurrent child processes via macOS’s native `afplay` binary engine (`subprocess.Popen`), allowing rapid overlapping hits (like a real drum roll) without blocking the primary telemetry thread.
---
## Repo Blueprint

* **`collect_data.py`**: The data acquisition script. It prompts you for a label, registers your slaps, flattens the vectors, and appends them to your training set.
* **`train_model.py`**: The training engine. It ingests your raw data, splits it into an 80/20 train/test distribution, prints an evaluation report, and serializes the model.
* **`play_drums.py`**: The real-time live engine. It loads the compiled brain, continuously polls the IMU, runs real-time inference, and triggers local audio files.
* **`drum_data.csv`**: The local dataset containing your raw, flattened 120-feature vibration fingerprints.
* **`drum_model.pkl`**: The compiled, pickled binary representation of your trained Random Forest model.

---
## Next Steps

* [ ] **Virtual MIDI Loopback**: Replace native `afplay` execution with a virtual MIDI port driver (`mido`), allowing `macDrum` to drive professional DAWs like Logic Pro, Ableton Live, or GarageBand as a physical hardware controller.
* [ ] **CoreML Compilation**: Export the trained Random Forest directly into Apple's native `.mlmodel` format to leverage the Apple Neural Engine (ANE) for hardware-accelerated inference.
* [ ] **Dynamic Calibration Loop**: Implement a 5-second automatic threshold calibration routine upon script startup to read ambient environment noise and adjust `DELTA_THRESHOLD` algorithmically.

---