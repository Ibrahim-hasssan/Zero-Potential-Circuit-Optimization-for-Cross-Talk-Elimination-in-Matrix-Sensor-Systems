
# import matplotlib.pyplot as plt
# import pandas as pd
# data = pd.read_csv("C:\\Users\\aboal\\Desktop\\zpc_project\\sin_wave.txt.txt", delimiter= '\t')
# print (data)
# plt.plot(data['time'], data['V(n001)'])
# plt.xlabel("time (s)")
# plt.ylabel("voltage (v)")
# plt.show()
# import sys
# sys.path.append("C:\\Users\\aboal\\Desktop\\zpc_project\\python\\ltspy3.py.txt")  # Use your actual path
# import ltspy3
# print(dir(ltspy3))

#first step
#%matplotlib qt
# %% for loop to make of all combination of the simulation cases
origR11  =  'R11=1meg'# the initial variable in original-file

# %% Format array from value of the risistance from 100 to 1m by step 1 db and then into strings 
import numpy as np

start = 10        # Starting value
stop = 100000000 # Ending value
step_db = 1     # Step size in decibels

# Convert start and stop to dB scale
start_db = 10 * np.log10(start)
stop_db = 10 * np.log10(stop)

# Create values in dB scale
db_values = np.arange(start_db, stop_db + step_db, step_db)

# Convert back to linear scale
linear_values = 10 ** (db_values / 10)

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

#listR11 = [format_resistor(val) for val in linear_values_int]
listR11 = ['R11=50k']
# Optional: print the list
#print(listR1)
# %% 


listALL  =listR11 # Total number of:cases .=. 0 t0 40 value = 41 


# %% create the subdirectory
import os
cwd = os.getcwd() # current working directory of LTspice .osc file
# create.a subfolder to save all the variations of LTspice simulation files

try:
    os.mkdir('SimFolder-ac-R11Res') # no whitespoce
except:
    print("The folder already exists!")

#orig  = "try" # without extension
#origTxt = orig + '.txt' # To run .cir, the file name must have no whitespaces

origTxt = "C:\\Users\\aboal\\Desktop\\zpc_project\\final tasks\\01-ZPC-ac-R11Res\\Draft1-ac-R11Res.txt"

#print(os.getcwd())

# %% Create new .txt.files.and run-in.LTspice

import time
start = time.time()
print("begin ... ")

dir_XVIIx64 = "C:\\Users\\aboal\\AppData\\Local\\Programs\\ADI\\LTspice"
#ltspice_path = "C:\\Users\\aboal\\AppData\\Local\\Programs\\ADI\\LTspice\\LTspice.exe"



import subprocess

iter = 0 # iteration
listALL = [] # All .txt file names, dimension=len(X)*Len(Y) ... e.g.,=3^4=81
for r11 in listR11:
    newFileName = f"{iter+1}-{r11}"
    newFileTxt = newFileName + '.txt'
    listALL.append(newFileName)#.save.each.file.name. into.ListALL
    with open(origTxt, 'rb') as file:#.Read.in.the.file
        origData = file.read()
        tempData = origData.replace(origR11.encode('ascii'), r11.encode('ascii'))
    with open('SimFolder-ac-R11Res/' + newFileTxt, 'wb') as file:
        file.write(tempData)
    iter += 1#.print.out.the.current.iteration
    print('To run txt files # : ', iter, ' over total 61 has a file name: ', newFileName)
                #.run. LTspice. in.the for. loop
    subprocess.call(dir_XVIIx64+'/LTspice.exe  -b ' + 'SimFolder-ac-R11Res/' + newFileTxt)

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
    os.mkdir('FigFolder-ac-R11Res')# no whitespace
except:
    print("The folder already exists!")


import time
start = time.time()
print("begin ... ")


#~~~~~~~~~~~~~~~~~ read data into python ide ~~~~~~~~~~~~~~~~~~~~~~~~~~~

iter = 0 # iteration

iters = []


for eachFile in listALL:
   
    if '' in eachFile: # run the cases containing specific parameters
        print(eachFile)
        sd = ltspy3.SimData(f'SimFolder-ac-R11Res/{eachFile}.raw') # .raw file in a string
        name = sd.variables # variable names from .raw data
        time_trace = sd.values # time and traces from .raw data
        time_Axis = sd.values[0] # The first element is the time as a matrix
        trace_Axis = sd.values[1:6] # The rest.elements.are traces as in matrices
        



# plot
# %matplotlib qt
# when you want graphs.in a-separate window and.be able to save it as a figure

# %matplotlib
#when you want an inline plot


        # Extract data
        complex_data = trace_Axis[1]
        magnitude = np.abs(complex_data)
        phase = np.angle(complex_data, deg=True)
        frequency = time_Axis  # In AC analysis, this is frequency

        # Create the plot with two Y axes
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot magnitude on the left Y-axis
        color_mag = 'tab:blue'
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Magnitude (V)', color=color_mag)
        ax1.semilogx(frequency, magnitude, color=color_mag, label='Magnitude')
        ax1.tick_params(axis='y', labelcolor=color_mag)
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Create second Y-axis for phase
        ax2 = ax1.twinx()
        color_phase = 'tab:red'
        ax2.set_ylabel('Phase (degrees)', color=color_phase)
        ax2.semilogx(frequency, phase, color=color_phase, linestyle='--', label='Phase')
        ax2.tick_params(axis='y', labelcolor=color_phase)

        # Title and layout
        plt.title(f"AC Analysis - {eachFile}")

        fig.tight_layout()

        plt.savefig(f'FigFolder-ac-R11Res/{eachFile}.png', dpi=150)

            
        plt.show()
     
        plt.close("all") # close all figures
        iter += 1  # print out the current iteration
        print('To plot figures #: ', iter, 'over total 61 has a file name: ', newFileName)


end = time.time()
print("Done!")
print('~~~~~~~~~~  Time elapsed is: ',end-start,'~~~~~~~~~~~~')
