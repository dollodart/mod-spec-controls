# Overview

The directory contents were made for a project to control pumps and gas flow controllers for modulation spectroscopy studies. I worked remotely and did not have the opportunity to test this on real equipment, instead using virtual ports made by the socat program, but the scripts were otherwise tested. Because the application, in an academic lab, did not require high reliability and low time latency, it was feasible and ideal to make a solution in Python rather than a dedicated controls program like LabView. Where LabView has complicated solutions to the problem of spawning subprocesses due to its data flow paradigm, reading and writing from common files by parallel executing scripts with whatever the OS has for resource control was sufficient for the application. 

# Usage
1. Adjust the parameters for each instrument in the `user-inputs.yaml` file using a program like Notepad. Keep this open as it will enable you to change set points while the pumps are running.
2. Do one of the two:
  1. For n instruments to be controlled, open up n+2 anaconda prompts. Do `python slave-1.py` through `python slave-<n>.py` (or whatever they've been named), one in each prompt. You should see the pumps start with the last settings used. This is the disadvantage of not executing in parallel from a batch file. Do `python master.py` in another prompt, and the setpoints for each pump should update. In the last available terminal run `python plot.py`. A pop-up plot should open displaying the times and setpoints. It updates with any changes in the set point.
  2. In the Anaconda power shell prompt, type `./exec.bat` and enter. This should run the master loop, slave loop(s), and plot loop. Note if the slave loop file names change, this file must be updated.
4. Update setpoints by saving to the user-inputs.yaml.

# Description of files
exec.bat: A command line executable which runs all scripts in parallel. The Anaconda power shell has to be used, since this can run both powershell commands and the python interpreter. Untested, as all development was done on a Linux box.
master.py: A script which reads user inputs and sends the slave loops messages to update their setpoints.
user-inputs.yaml: Text file in which users input the parameters for each pump for its setpoints and communication.
general-settings.yaml: Text file for parameters which are not particular to a pump but determine operation of the control loops.
slave-template.py: Template for slave loop. This template is repeated for the total number of slave devices. The template can be applied without changes to all devices since the `find_instrument` function returns the correct class to communicate with the instrument, but for different devices still some customization may be desired.
funcs.py: Defines functions used by master and slave loops.
classes.py: Defines classes used for instruments by the slave loops.
comm-settings.yaml: Text file containing 

# Description of program
The Pyserial package is used to communicate with devices, here for examples of the Legato syringe pump, Parker-Hannifen gas flow controller, and Alicat mass flow controller. See existing Alicat package at https://github.com/numat/alicat.

Using the general pyserial interface, which works for most new devices (which will be assigned /dev/USBn or /dev/ACMn as ports), it takes only 3 lines to begin communication

```
dev = serial.Serial('/dev/devname',timeout=1.)
message = 'abc\r'.encode('ascii')
dev.write(message)
```

All of the files have only one script which can write to them, all other scripts reading from it, so I don't think there can be a collision--if two scripts read something at the same time, or read something while it is being written, by the fact that it is "read-only" and the file contents don't change, I don't think collisions are possible.

Like the alicat package, the connection attribute of the relevant instrument class instance is actually the serial object, and using the write method just writes to this object. 

Here parallel operation is achieved just by executing the scripts (calling the python interpreter) from the command line parallelly (achieved with the & symbol). The "message passing interface" is just reading and writing to files, where there is only one script which may write to any file. The issues of resource conflict (I have seen file contents disappear when there is simultaneous read and write, though in principle with view copying there should only be collisions between two or more writes) and possible double reading of parameters can be dealt with, for the required time resolutions, just by offsetting the read and write times to thousands of the loop iteration times (writing a pickle file takes 0.21 milliseconds, for example).

As reference in reading the communication files which are python binary (pickle) encoded, <80>^C<88> is True and <80>^C<89> is False.

Better solutions exist to the problem of synchronous control. If the slave loops are operating independently there can be a message passing interface (MPI) between them and the master. 

# Description of Science

By controlling the phase, frequency, and shape of modulation of several sources of reactants, it can be possible to infer properties of catalysts and the reactions they catalyze by the spectroscopic response. Note that while atomic relaxation times are on the order of picoseconds, these bulk changes in fluid concentration can be order miliseconds to seconds and still show significant inertial effects, which is usually resulting in phase shift for first-order like systems. The assumption of an ideal mixed fluid which is in equilibrium with the catalyst surface is required.
