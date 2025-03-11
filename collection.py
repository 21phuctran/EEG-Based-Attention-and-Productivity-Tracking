import time
import numpy as np
import matplotlib.pyplot as plt
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# BrainFlow Setup for OpenBCI Synthetic Board
params = BrainFlowInputParams()
board_id = BoardIds.SYNTHETIC_BOARD.value  # Use Synthetic Board for testing

# Define EEG Electrodes
attention_channels = [1, 2, 3, 4]  # Fp1, Fp2, F3, F4 (Frontal)
task_engagement_channels = [5, 6]  # C3, C4 (Central)
eeg_channels = attention_channels + task_engagement_channels

# Sampling Rate
sampling_rate = BoardShim.get_sampling_rate(board_id)

# Initialize EEG Board
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()
print("BrainFlow Synthetic Board started. Streaming EEG data!")

# Experiment Parameters
num_seconds = 10  # Collect 10 seconds of data
collected_data = {ch: [] for ch in eeg_channels}

# Live Plot Setup
plt.ion()
fig, ax = plt.subplots(len(eeg_channels), 1, figsize=(10, 6), sharex=True)
lines = []
for i, ch in enumerate(eeg_channels):
    lines.append(ax[i].plot([], [], label=f"EEG {ch}")[0])
    ax[i].set_xlim(0, num_seconds * sampling_rate)  # Set x-axis for time
    ax[i].set_ylim(-100, 100)  # Adjust signal range
    ax[i].legend(loc="upper right")

# EEG Data Collection Loop
start_time = time.time()
time_series = np.arange(0, num_seconds * sampling_rate)  # Time axis
buffer_size = num_seconds * sampling_rate  # Storage buffer

while time.time() - start_time < num_seconds:
    data = board.get_board_data()
    
    if data.shape[1] > 0:
        eeg_data = data[eeg_channels, -sampling_rate:]  # Get latest samples
        
        # Append to each channel's data buffer
        for i, ch in enumerate(eeg_channels):
            collected_data[ch].extend(eeg_data[i, :].tolist())
            collected_data[ch] = collected_data[ch][-buffer_size:]  # Keep only last buffer_size points

            # Update Plot Data
            lines[i].set_xdata(time_series[:len(collected_data[ch])])
            lines[i].set_ydata(collected_data[ch])
    
        plt.pause(0.01)

# Stop EEG stream
board.stop_stream()
board.release_session()

# Save collected data
eeg_data_array = np.array([collected_data[ch] for ch in eeg_channels])
np.save("eeg_data.npy", eeg_data_array)
print("EEG data saved to eeg_data.npy")

# Show final plot
plt.ioff()
plt.show()

print("EEG data collection completed successfully!")
