import numpy as np
import matplotlib.pyplot as plt

# Load the EEG data
filename = r"C:\Users\pct001\EEG-Based-Attention-and-Productivity-Tracking\eeg_experiment_data.npy" # Replace with your actual file name
eeg_data = np.load(filename, allow_pickle=True).item()

# Print the data structure
print("EEG Data Structure:", eeg_data.keys())

# Plot EEG data for one condition and trial
condition = list(eeg_data.keys())[0]  # Select the first condition
trial_idx = 0  # Select the first trial

# Convert to numpy array for plotting
eeg_trial_data = np.array(eeg_data[condition]["trials"][trial_idx])

# Plot EEG signals (assuming channels are along the first axis)
plt.figure(figsize=(12, 6))
for i in range(eeg_trial_data.shape[0]):  # Iterate over channels
    plt.plot(eeg_trial_data[i, :], label=f"Channel {i+1}")

plt.xlabel("Time (samples)")
plt.ylabel("EEG Signal (µV)")
plt.title(f"EEG Data - {condition} (Trial {trial_idx+1})")
plt.legend()
plt.show()



