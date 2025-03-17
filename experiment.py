#import libraries
from psychopy import visual, core, event
import time
import random
from psychopy import sound
import os
import numpy as np
from scipy.io.wavfile import read
from psychopy import prefs

#creates a window to display everything
window = visual.Window(monitor = "testMonitor", fullscr = False, color="black")

message = visual.TextStim(window, text = "Hello and welcome! Thank you for participating in our experiment today")
message.draw()
window.flip()

core.wait(4)

#Baseline Recording (resting state)
def run_baseline():
    baseline_message = visual.TextStim(window, text = "+", color = "white")
    #Fixation cross
    baseline_message.draw()
    window.flip()
    core.wait(15) # 15-second baseline recording

#pre-trial EEG Start
def run_pre_trial():
    pre_trial_message = visual.TextStim(window, text = "Pre-trial Period. Please wait.", color = "white")
    pre_trial_message.draw()
    window.flip()
    core.wait(5) #5-second pre trial period

# Self-report validation
def run_self_report():
    self_report_message = visual.TextStim(window, text="How focused were you? (1 = Very Distracted, 5 = Highly Focused)", color="white", height=0.1)
    self_report_message.draw()
    window.flip()
    response = event.waitKeys(maxWait=10, keyList=['1', '2', '3', '4', '5'])  # Wait for key press
    if response:
        print(f"Self-report rating: {response[0]}")
    else:
        print("No response recorded.")

#Condition 1: High Attention
def run_high_attention():
    # Define the article text directly in the script
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

    # Display instructions
    instruction_text = (
        "Please read the excerpt carefully and focus on understanding it.\n\n"
        "Keep your eyes open, fixating on the neutral point, and remain as still as possible.\n\n"
        "Avoid distractions or looking away from the screen. You will have 90 seconds to read.\n\n"
        "Stay still until further instructions are given."
    )

    instruction_stim = visual.TextStim(window, text=instruction_text, color="white", height=0.08, wrapWidth=1.8)
    instruction_stim.draw()
    window.flip()
    core.wait(15)  # Display instructions for 15 seconds

    # Pre-trial EEG wait time
    run_pre_trial()

    # Display the article
    article_stim = visual.TextStim(
        window,
        text=article_text,
        color="white",
        height=0.06,  # Adjust font size
        wrapWidth=1.5,  # Adjust wrap width to control line length
        alignText="left",  # Align text to the left for better readability
        font="Arial",  # font
    )
    article_stim.draw()
    window.flip()
    core.wait(90)  # Display article for 90 seconds

    # Clear screen after the task
    window.flip()

    # Pre-trial EEG wait time
    run_pre_trial()

    # Clear screen after the task
    window.flip()

# Condition 2: Low Attention
def run_low_attention():
    # Set the audio file path
    mySound = sound.Sound("lofi_jazz_background_music.wav")
    # Display Instructions
    instruction_text = (
        "Please listen to the music.\n\n"
        "Keep your eyes open, fixating on the neutral point, and remain as still as possible.\n\n"
        "Avoid distractions or looking away from the screen. You will have 90 seconds to listen.\n\n"
        "Stay still until further instructions are given."
    )

    # Display instruction text
    instruction_stim = visual.TextStim(window, text=instruction_text, color="white", height=0.08, wrapWidth=1.8)
    instruction_stim.draw()
    window.flip()
    core.wait(5)  # Display instructions for 5 seconds

    # Display fixation cross while the song is playing
    fixation_stim = visual.TextStim(window, text="+", color="white")
    fixation_stim.draw()
    window.flip()

    # Play the audio and wait for 90 seconds
    mySound.play()
    core.wait(90)

    # Stop
    mySound.stop()

    # Pre-trial EEG wait time
    run_pre_trial()
    
    # Clear screen
    window.flip()
 
# Function to generate arithmetic problems
def generate_problem():
    operations = ['+', '-', '*', '/']
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    op1 = random.choice(operations)

    # Ensure division results in whole numbers
    if op1 == '/':
        num1 = num1 * num2  # Make num1 a multiple of num2 to avoid decimals

    # 50% chance to add a second operation for increased difficulty
    if random.random() < 0.5:
        num3 = random.randint(10, 99)
        op2 = random.choice(operations)
        if op2 == '/':
            num3 = max(1, num3 // 2)  # Avoid small denominators
        problem_text = f"({num1} {op1} {num2}) {op2} {num3} = ?"
    else:
        problem_text = f"{num1} {op1} {num2} = ?"

    return problem_text
 
# Condition 3: Fatigue
def run_fatigue():
    instructions_text = (
        "Please solve the arithmetic problems as quickly and accurately as possible.\n\n"
        "Keep your eyes open, fixating on the neutral point, and remain as still as possible.\n\n"
        "Avoid distractions or looking away from the screen. You will have 90 seconds to solve problems.\n\n"
        "Stay still until further instructions are given."
    )
    
    instruction_stim = visual.TextStim(window, text=instructions_text, color="white", height=0.07, wrapWidth=1.5)
    instruction_stim.draw()
    window.flip()
    core.wait(5)  # Display instructions for 5 seconds

    run_pre_trial()

    # Display arithmetic problems
    start_time = core.getTime()
    while core.getTime() - start_time < 90:  # Run for 90 seconds
        problem_text = generate_problem()
        problem_stim = visual.TextStim(window, text=problem_text, color="white", height=0.1)
        problem_stim.draw()
        window.flip()
        core.wait(5)  # Display each problem for 5 seconds
    #Clear screen after task
    window.flip()

# Experiment loop
def run_experiment():
    conditions = ['HighAttention', 'LowAttention', 'Fatigue']
    random.shuffle(conditions)  # Randomize the order of conditions

    for condition in conditions:
        # Baseline recording before each condition
        run_baseline()
        # Pre-trial EEG start
        run_pre_trial()

        # Run the condition
        if condition == 'HighAttention':
            run_high_attention()
        elif condition == 'LowAttention':
            run_low_attention()
        elif condition == 'Fatigue':
            run_fatigue()
            
        # Self-report after each trial
        run_self_report()
        
        # Add a short break between conditions
        break_message = visual.TextStim(window, text="Take a short break. The next condition will start soon.", color="white", height=0.1)
        break_message.draw()
        window.flip()
        core.wait(10) 

# Run the experiment
run_experiment()

# End of experiment
end_message = visual.TextStim(window, text="Thank you for participating! The experiment is now over.", color="white", height=0.1)
end_message.draw()
window.flip()
core.wait(4)  # Display the end message for 4 seconds

# Close the window
window.close()
core.quit()