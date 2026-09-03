

#first step
#%matplotlib qt
# %% for loop to make of all combination of the simulation cases
origR11  =  'R11=40k'# the initial variable in original-file


# %% Format array from value of the risistance from 100 to 1m by step 1 db and then into strings 
import numpy as np
import re
import pandas as pd
import time

file_names = [] 
resistance_strings = []
resistances = [] 
magnitudes=[]
# Frequency in Hz
f = 5000  # Hz
w = 2 * np.pi * f


start = 40000        # Starting value
stop = 950000 # Ending value
step_db = 0.5  # Step size in decibels

# Convert start and stop to dB scale
start_db = 10 * np.log10(start)
stop_db = 10 * np.log10(stop)

# Create values in dB scale
db_values = np.arange(start_db, stop_db + step_db, step_db)

# Convert back to linear scale
#linear_values = 10 ** (db_values / 10)
linear_values = [50000, 60000, 700000, 80000, 90000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000, 550000, 600000, 650000, 700000, 750000, 800000, 850000, 900000, 950000, 1000000]
# Round to nearest integer and remove duplicates
linear_values_int = np.unique(np.round(linear_values).astype(int))

# Format into strings 
def format_resistor(val):
    if val >= 1_000_000:
        return f"R11={val//1_000_000}MEG"
    elif val >= 1_000:
        return f"R11={val//1_000}k"
    else:
        return f"R11={val}"

resistance_strings = [format_resistor(val) for val in linear_values_int]









listR11= resistance_strings
#listR11 = ['R11=50k']


resistances = linear_values_int


# %% create the subdirectory
import os
cwd = os.getcwd() # current working directory of LTspice .osc file
# create.a subfolder to save all the variations of LTspice simulation files

try:
    os.mkdir('SimFolder') # no whitespoce
except:
    print("The folder already exists!")

#orig  = "try" # without extension
#origTxt = orig + '.txt' # To run .cir, the file name must have no whitespaces

origTxt = "C:\\Users\\aboal\\Desktop\\zpc_project\\final tasks\\06-zpc_R11withLinear Chirp Signal 1\LCS with res.txt"

#print(os.getcwd())


# %% Create new .txt.files.and run-in.LTspice
start = time.time()
print("begin ... ")

dir_XVIIx64 = "C:\\Users\\aboal\\AppData\\Local\\Programs\\ADI\\LTspice"
#ltspice_path = "C:\\Users\\aboal\\AppData\\Local\\Programs\\ADI\\LTspice\\LTspice.exe"



import subprocess


iter = 0 # iteration
listALL = [] # All .txt file names, dimension=len(X)*Len(Y) ... e.g.,=3^4=81
for idx, r11 in enumerate(listR11):
  
    newFileName = f"{iter+1}-{r11}"  # Include both R11 and C11 in the file name
    newFileTxt = newFileName + '.txt'
    listALL.append(newFileName)  # Save each file name into listALL
    with open(origTxt, 'rb') as file:
        origData = file.read()
        tempData = origData.replace(origR11.encode('ascii'), r11.encode('ascii')) 
                        
    with open('SimFolder/' + newFileTxt, 'wb') as file:
        file.write(tempData)
    iter += 1
    print('To run txt files # : ', iter, ' over total has a file name: ', newFileName)
    subprocess.call(dir_XVIIx64+'/LTspice.exe  -b ' + 'SimFolder/' + newFileTxt)
  
    file_names.append(newFileName)
  
end = time.time()
print("Done!")
print('~~~~~~~~~~~~~~Time elapsed is: ', end - start, '~~~~~~~~~~~~~~~~')


# %% 

import sys
sys.path.append("C:\\Users\\aboal\\Desktop\\zpc_project\\zpc_first_step\\ltspy3.py.txt")  # Use your actual path

import ltspy3
# https://matplotlib.org/tutorials/introductory/pyplot.html

import matplotlib.pyplot as plt

try:
    os.mkdir('FigFolder')# no whitespace
except:
    print("The folder already exists!")


import time
start = time.time()
print("begin ... ")


#~~~~~~~~~~~~~~~~~ read data into python ide ~~~~~~~~~~~~~~~~~~~~~~~~~~~

iter = 0 # iteration
Resistors_M = []
iters = []
Rref = 100000  # in ohms
amp_values = []
Rmn_sims = []
deviations = []
real_resistance_all = []
deviations_res= []
Am_values=[]
Amn_values=[]
# Frequencies to analyze
frequenciesfft = list(range(500, 11000, 500))

# Containers for components
components_vin = []
components_vout = []




def calculate_Rmn_Cmn(R_ref_n, Amn, Am, beta_mn, phi_m, omega_m):
    """
    Calculate Rmn and Cmn from the given parameters.

    Parameters:
    R_ref_n : float
        Reference resistance.
    Amn : float
        Amplitude Amn.
    Am : float
        Amplitude Am.
    beta_mn : float
        Beta angle in radians.
    phi_m : float
        Phi angle in radians.
    omega_m : float
        Angular frequency.

    Returns:
    Rmn, Cmn : tuple of floats
    """
    angle_diff = beta_mn - phi_m
    tan_sq = np.tan(angle_diff)**2
    sqrt_term = np.sqrt(1 + tan_sq)

    Rmn = (R_ref_n / (Amn / Am)) * sqrt_term
    Cmn = (np.tan(angle_diff) * (Amn / Am)) / (omega_m * R_ref_n * sqrt_term)

    return Rmn, Cmn


def extract_resistance_value(file_name):
    # Extract the R11=... portion from the filename using regex
    match = re.search(r'R11=([\d.]+)([kKmM]?[eE]?[gG]?)', file_name)
    if not match:
        raise ValueError(f"Could not find a valid R11 value in filename: {file_name}")
    
    value_str, suffix = match.groups()
    value = float(value_str)

    # Convert suffix to numeric multiplier
    suffix = suffix.lower()
    if suffix == 'k':
        return value * 1e3
    elif suffix in ['meg', 'm']:
        return value * 1e6
    else:
        return value  # No suffix = ohms



def find_fourier_component_and_phase(log_text, frequency):
    # Convert frequency to scientific notation as in LTspice log
    freq_sci = f"{frequency:.3e}".replace("e+0", "e+").replace("e+00", "e+0")

    # Match a line like: 4   	 5.000e+3	 1.250e-1	 8.965e+3	   90.01°	  266.13°
    pattern = rf"^\s*\d+\s+{re.escape(freq_sci)}\s+([-\d\.e\+]+)\s+[-\d\.e\+]+\s+([-]?\d+\.\d+)°"
    match = re.search(pattern, log_text, re.MULTILINE)
    if match:
        fourier_component = float(match.group(1))
        phase_deg = float(match.group(2))
        return fourier_component, phase_deg
    return None, None

def extract_section(log_text, signal_name):
    # Extract the block that starts with 'Fourier components of V(signal_name)' until the next such block or end of file
    pattern = rf"Fourier components of V\({re.escape(signal_name)}\)(.*?)(?=Fourier components of V\(|\Z)"
    match = re.search(pattern, log_text, re.DOTALL)
    return match.group(1) if match else ""

# Example inside your loop
for indx, eachFile in enumerate(listALL):
    
    if '' in eachFile:
        print(eachFile)
        sd = ltspy3.SimData('SimFolder/' + eachFile + '.raw') # .raw file in a string
        name = sd.variables # variable names from .raw data
        time_trace = sd.values # time and traces from .raw data
        time_Axis = sd.values[0] # The first element is the time as a matrix
        trace_Axis = sd.values[1:6] # The rest.elements.are traces as in matrices
        
        # Read the log file
        with open('SimFolder/' + eachFile + '.log', "r") as f:
            log_text = f.read()
        
        # Extract sections
        section_row_in1 = extract_section(log_text, "row_in1")
        section_v_out_1 = extract_section(log_text, "v_out_1")

        # Extract component and phase for each section at 5000 Hz
        component_rowin1, phase_rowin1 = find_fourier_component_and_phase(section_row_in1, 5000)
        component_vout1, phase_vout1 = find_fourier_component_and_phase(section_v_out_1, 5000)
        # Extract Fourier components for each frequency
        for freq in frequenciesfft:
            component_vin, _ = find_fourier_component_and_phase(section_row_in1, freq)
            component_vout, _ = find_fourier_component_and_phase(section_v_out_1, freq)
            
            components_vin.append(component_vin)
            components_vout.append(component_vout)

                # Invert the phase sign if needed
        phase_rowin1 *= -1
        phase_vout1 *= -1

        print(f"row_in1 @ 5kHz: Component = {component_rowin1}, Phase = {phase_rowin1}°")
        print(f"v_out_1 @ 5kHz: Component = {component_vout1}, Phase = {phase_vout1}°")




    if component_rowin1 is not None and component_vout1 is not None:
          
        
        Am = component_rowin1 # Amplitude of sin signal at row1
        Amn  = component_vout1
        Am_values.append(Am)
        Amn_values.append(Amn)
        rmn = Rref * (Am / Amn)                         # Apply formula
        amp_values.append(Amn)
        iters.append(iter)
        Rmn_sims.append(rmn)
        deviation_percent = ((rmn - resistances[indx] ) / resistances[indx] ) * 100
        deviations.append(deviation_percent)

        print('figures #: ', iter, ' - file name: ', newFileName, f"- f = 200 kHz magnitude in DB: {Amn }")
       
 # print(f"figures #: {indx} - file name: {eachFile} - f = 200 Hz | measured resistance: Rmn = {Rmn:.4f} Ohms | capacitor: Cmn = {Cmn*1e12:.6e} pF")

    else:
        magnitudes.append(None)  # Append None if not found
        iters.append(iter)
        print('Could not find 200 Hz harmonic in log file #: ', iter)
            
    # Time-domain plots
    plt.figure(figsize=(12, 10))

    # 1. Vin time-domain
    plt.subplot(2, 2, 1)
    plt.plot(time_Axis, trace_Axis[0], 'g-', linewidth=2, label='Vin')
    plt.legend(loc='upper right', fontsize=10)
    plt.xlabel('Time (sec)', fontsize=12)
    plt.ylabel('Voltage (V)', fontsize=12)
    plt.title('Input Voltage - Time Domain')
    plt.grid(True)

    # 2. Vout time-domain
    plt.subplot(2, 2, 3)
    plt.plot(time_Axis, trace_Axis[1], 'b-', linewidth=2, label='Vout')
    plt.legend(loc='upper right', fontsize=10)
    plt.xlabel('Time (sec)', fontsize=12)
    plt.ylabel('Voltage (V)', fontsize=12)
    plt.title('Output Voltage - Time Domain')
    plt.grid(True)

    # 3. Vin frequency-domain
    plt.subplot(2, 2, 2)
    plt.plot(frequenciesfft, components_vin, color='green', label='Vin FFT Magnitudes')
    plt.legend(loc='upper left', fontsize=5)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Magnitude', fontsize=12)
    plt.title('Input Voltage - Frequency Domain')
    plt.grid(True)

    # 4. Vout frequency-domain
    plt.subplot(2, 2, 4)
    plt.plot(frequenciesfft, components_vout, color='orange', label='Vout FFT Magnitudes')
    plt.legend(loc='upper left', fontsize=5)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Magnitude', fontsize=12)
    plt.title('Output Voltage - Frequency Domain')
    plt.grid(True)


    plt.tight_layout()
    plt.show()

# Save as a seperate figure

    plt.savefig('FigFolder/' + eachFile + '.png', dpi=150)    
    
    plt.show()
    plt.close("all") # close all figures
    iter += 1  # print out the current iteration
    print('To plot figures #: ', iter, 'over total  has a file name: ', newFileName)
    components_vin = []
    components_vout = []
# === Plotting ===
import matplotlib.pyplot as plt

plt.figure(figsize=(7, 5))
plt.plot(resistances, deviations, marker='o', linestyle='-', color='blue')
plt.xlabel('Reference Resistance [Ohms]')
plt.ylabel('Deviation [%]')
plt.title('Deviation vs Reference Resistance')
plt.grid(True)
plt.tight_layout()
plt.savefig('FigFolder/deviation_vs_resistance.png', dpi=300)
plt.show()




data = {
    'Iteration': iters,
    'Reference R (Ohms)': resistances,
    'Extracted Rmn (Ohms)': Rmn_sims,
    'Deviation (%)': deviations,
    'Am (row_in1)': Am_values,
    'Amn (v_out_1)': Amn_values
}

df = pd.DataFrame(data)
df.to_csv('SimFolder/extracted_impedance_analysis.csv', index=False)
print("✅ CSV file saved as 'SimFolder/extracted_impedance_analysis.csv'")






end = time.time()
print("Done!")
print('~~~~~~~~~~  Time elapsed is: ',end-start,'~~~~~~~~~~~~')

