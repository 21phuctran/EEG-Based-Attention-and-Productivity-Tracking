# Import necessary libraries
import time
import random
import numpy as np
import datetime
import os
from psychopy import visual, core, event, sound
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# EEG Setup (BrainFlow)
params = BrainFlowInputParams()
params.serial_port = "COM3"  # Adjust as needed for your system
board_id = BoardIds.CYTON_BOARD.value  # OpenBCI Cyton Board
board = BoardShim(board_id, params)

# Retrieve EEG channels
eeg_channels = BoardShim.get_eeg_channels(board_id)

# Define selected channels (8 channels)
selected_channels = {
    "Fp1": eeg_channels[0],  # Frontal - attention
    "Fp2": eeg_channels[1],  # Frontal - attention
    "F3": eeg_channels[2],   # Frontal - cognitive work
    "F4": eeg_channels[3],   # Frontal - cognitive work
    "C3": eeg_channels[4],   # Central - task engagement
    "C4": eeg_channels[5],   # Central - task engagement
    "Cz": eeg_channels[6],   # Central midline - cognitive control
    "Pz": eeg_channels[7]    # Parietal - fatigue detection
}

# Define ground and reference channels
ground_channel = "O1"  #GND
reference_channel = "O2" #REF

# Start EEG session
board.prepare_session()
board.start_stream()
print("EEG Data Streaming Started!")

# Experiment Setup (PsychoPy)
window = visual.Window(size=(1920, 1080), color="black", fullscr=False, allowGUI=False, units="norm")

# Function to display a message
def display_message(text, duration=3):
    message = visual.TextStim(window, text=text, color="white", height=0.08)
    message.draw()
    window.flip()
    core.wait(duration)

# Function to get EEG data from selected channels
def get_eeg_data():
    data = board.get_board_data()
    return {channel: data[selected_channels[channel]] for channel in selected_channels}

# Baseline Recording (Resting State)
def run_baseline():
    print("Running Baseline Recording (30s)...")
    display_message("+", duration=30)  # Fixation cross for 30s
    return get_eeg_data()

# Pre-trial EEG Recording (Capturing Preparatory Activity)
def run_pre_trial():
    print("Running Pre-Trial EEG (10s)...")
    display_message("Get ready...", duration=10)  # 10-second pre-trial wait
    return get_eeg_data()

# Self-Report Validation
def run_self_report():
    display_message("How focused were you? (1 = Distracted, 5 = Focused)", duration=2)
    response = event.waitKeys(maxWait=10, keyList=['1', '2', '3', '4', '5'])
    return response[0] if response else "No Response"

# High Attention Task: Reading a Scientific Article
def run_high_attention():
    print("Running High Attention Task...")
    run_pre_trial()

    article_text = (
        "Cognitive research shows that decision speed affects moral evaluations. Quick decisions suggest confidence, "
        "leading to more extreme moral character judgments..."
    )
    
    article_stim = visual.TextStim(window, text=article_text, color="white", height=0.06, wrapWidth=1.5, alignText="left")
    article_stim.draw()
    window.flip()
    core.wait(60)  # Display article for 60 seconds
    
    return get_eeg_data()

# Low Attention Task: Listening to Music
def run_low_attention():
    print("Running Low Attention Task...")
    run_pre_trial()

    music = sound.Sound("lofi_jazz_background_music.wav")
    music.play()

    display_message("+", duration=60)  # Fixation cross while listening
    
    music.stop()
    return get_eeg_data()

# Fatigue Task: Continuous Arithmetic
def run_fatigue():
    print("Running Fatigue Task...")
    run_pre_trial()

    start_time = core.getTime()
    while core.getTime() - start_time < 60:
        problem_text = f"{random.randint(10, 99)} + {random.randint(10, 99)} = ?"
        problem_stim = visual.TextStim(window, text=problem_text, color="white", height=0.1)
        problem_stim.draw()
        window.flip()
        core.wait(5)

    return get_eeg_data()

# Generate Unique Filename (Timestamped)
def generate_unique_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"eeg_experiment_{timestamp}.npy"

# Experiment Loop
def run_experiment():
    conditions = ['HighAttention', 'LowAttention', 'Fatigue']
    random.shuffle(conditions)  # Randomize condition order
    all_data = {}

    for condition in conditions:
        print(f"Starting Condition: {condition}")

        # Baseline Recording
        baseline_data = run_baseline()

        # Run the selected condition
        if condition == 'HighAttention':
            task_data = run_high_attention()
        elif condition == 'LowAttention':
            task_data = run_low_attention()
        elif condition == 'Fatigue':
            task_data = run_fatigue()

        # Self-report validation
        focus_rating = run_self_report()
        
        # Store data
        all_data[condition] = {
            "baseline": baseline_data,
            "trials": task_data,
            "self_reports": focus_rating
        }

        # Break between conditions
        display_message("Take a short break (10s)...", duration=10)

    return all_data

# Run the experiment and collect EEG data
eeg_results = run_experiment()

# Save EEG data with timestamped filename
filename = generate_unique_filename()
board.stop_stream()
board.release_session()
np.save(filename, eeg_results)
print(f"EEG data saved as {filename}!")

# End Experiment
display_message("Thank you for participating!", duration=4)
window.close()
core.quit()
