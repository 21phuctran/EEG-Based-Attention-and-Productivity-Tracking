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
board_id = BoardIds.SYNTHETIC_BOARD.value  # Change this to your actual board ID
board = BoardShim(board_id, params)
sampling_rate = BoardShim.get_sampling_rate(board_id)  # EEG Sampling rate
eeg_channels = BoardShim.get_eeg_channels(board_id)  # EEG Channels list

# Prepare EEG session
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

# Baseline Recording (Resting State)
def run_baseline():
    print("Running Baseline Recording (30s)...")
    display_message("+", duration=30)  # Fixation cross for 30s
    return board.get_board_data()  # Collect EEG data

# Pre-trial EEG Recording (Capturing Preparatory Activity)
def run_pre_trial():
    print("Running Pre-Trial EEG (10s)...")
    display_message("Get ready...", duration=10)  # 10-second pre-trial wait
    return board.get_board_data()  # Collect EEG data

# Self-Report Validation
def run_self_report():
    display_message("How focused were you? (1 = Distracted, 5 = Focused)", duration=2)
    response = event.waitKeys(maxWait=10, keyList=['1', '2', '3', '4', '5'])
    return response[0] if response else "No Response"

# Task Conditions
def run_high_attention():
    print("Running High Attention Task...")
    run_pre_trial()

    article_text = (
        "It has been suggested that people attend to others’ actions in the service of forming impressions of their "
        "underlying dispositions. If so, it follows that in considering others’ morally relevant actions, social perceivers "
        "should be responsive to accompanying cues that help illuminate actors’ underlying moral character. This article "
        "examines one relevant cue that can characterize any decision process: the speed with which the decision is made. "
        "Two experiments show that actors who make an immoral decision quickly (vs. slowly) are evaluated more negatively. "
        "In contrast, actors who arrive at a moral decision quickly (vs. slowly) receive particularly positive moral character "
        "evaluations. Quick decisions carry this signal value because they are assumed to reflect certainty in the decision, "
        "which in turn signals that more unambiguous motives drove the behavior, explaining the more polarized moral character "
        "evaluations."
    )
    
    article_stim = visual.TextStim(window, text=article_text, color="white", height=0.06, wrapWidth=1.5, alignText="left")
    article_stim.draw()
    window.flip()
    core.wait(60)  # Display article for 60 seconds
    
    return board.get_board_data()

# Condition 2: Low Attention (Listening to Music)
def run_low_attention():
    print("Running Low Attention Task...")
    run_pre_trial()

    music = sound.Sound("lofi_jazz_background_music.wav")
    music.play()

    display_message("+", duration=60)  # Fixation cross while listening
    
    music.stop()
    return board.get_board_data()

# Condition 3: Fatigue (Continuous Arithmetic)
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

    return board.get_board_data()

# Generate Unique Filename (Timestamped)
def generate_unique_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"eeg_experiment_{timestamp}.npy"

# Generate Unique Filename (Trial Numbering)
def generate_trial_filename():
    existing_files = [f for f in os.listdir() if f.startswith("eeg_experiment_trial_") and f.endswith(".npy")]
    trial_numbers = [int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()]
    next_trial = max(trial_numbers) + 1 if trial_numbers else 1  # Start at 1 if no files exist
    return f"eeg_experiment_trial_{next_trial:03d}.npy"

# Experiment Loop
def run_experiment():
    conditions = ['HighAttention', 'LowAttention', 'Fatigue']
    random.shuffle(conditions)  # Randomize condition order
    all_data = {}  # Store EEG data

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
        
        # Save data
        if condition not in all_data:
            all_data[condition] = {"baseline": [], "trials": [], "self_reports": []}

        all_data[condition]["baseline"].append(baseline_data)
        all_data[condition]["trials"].append(task_data)
        all_data[condition]["self_reports"].append(focus_rating)

        # Break between conditions
        display_message("Take a short break (10s)...", duration=10)

    return all_data

# Run the experiment and collect EEG data
eeg_results = run_experiment()

# Choose how to save: Timestamped or Numbered
use_timestamps = True  # Set to False to use trial numbering

if use_timestamps:
    filename = generate_unique_filename()
else:
    filename = generate_trial_filename()

# Stop EEG streaming and save data
board.stop_stream()
board.release_session()
np.save(filename, eeg_results)
print(f"EEG data saved as {filename}!")

# End Experiment
display_message("Thank you for participating!", duration=4)
window.close()
core.quit()



