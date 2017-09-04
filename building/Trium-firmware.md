# Trium Firmware

## Emergin RC7 Version
The standard Marlin open source firmware source is available [here](github.com/MarlinFirmware/Marlin) or one of the Release Candidate versions [here](http://marlinfw.org/meta/download/).  The E-Mergin web site provides a **modified** version of RC7, but note that the GitHub version has moved beyond RC7 (RC8 has *many* differences with RC7).  Be very careful to replace the TRIUM RC7 firmware with RC8 firmware. Ensure that you understand the differences between RC7 and RC8 as it pertains to the TRIUM.  E-Mergin provided the following [instruction](http://trium3d.proboards.com/thread/68/upgrade-marlin-1-rc8-planned) to upgrade from RC7 to RC8: download RC8, and replace the configuration.h and configuration_adv.h files using the the previous version files.

At least the following files are modified in the Trium hot end version of RC7 (relative to the Marlin standard RC7):
-  `_Bootscreen.h`: a new file not present in the standard Marlin distribution (possibly showing the Trium or E-Mergin logo?)
-  `Configuration.h`: a heavily modified file, for TRIUM printer info.
-  `Configuration_adv.h`: slightly modified for TRIUM printer info.
-  `Marlin.ino`: no significant changes, only TRIUMs weak attempt to time stamp.
-  `pins.h`: modified to only include the `pin_RAMPS.h` file, other file includes are removed
-  `pin_RAMPS.h`: slightly modified for TRIUM printer info.
-  `pins_xxxxx.h` a large number of pin definition files are removed, only `RAMPS.h` is retained.
-  `ultralcd.cpp`: slightly modified for TRIUM printer info.
-  `ultralcd.h`: slightly modified for TRIUM printer info.
-  `Version.h`: modified with TRIUM web site info.
-  `fonts/*.*` is a new folder containing some font info (possibly for the LCD).

The two TRIUM firmware versions (standard/DH and E3D) differ in the following file:
-  `Configuration.h`: different temperature sensor `TEMP_SENSOR_0`.
	-  The E3D uses sensor 5: "100K / 4.7k - ATC Semitec 104GT-2 (Used in ParCan & J-Head)"
	-  The standard hot end uses sensor 11: "100k / 4.7k beta 3950 1%".

## JohanV Marlin 1.1.5

[JohanV posted](http://trium3d.proboards.com/thread/144/marlin-1-5) a detailed description for preparing 1.1.5 for the standard Trium V1 with a single extruder.  He enabled thermal protection and adjusted the PID loop controller.

 Three files are affected: major changes to `Configuration.h`, minor changes to `Configuration_adv.h` and the entire `pins_RAMPS.h`.
And here they are: [Marlin115Trium3Dsingle.zip (43.86 KB)](http://trium3d.proboards.com/attachment/download/280).


Enable thermal protection (which hitherto was disabled) - you find this in lines 441 and 442 of `Configuration.h`:  

    #define THERMAL_PROTECTION_HOTENDS // Enable thermal protection for all extruders
    #define THERMAL_PROTECTION_BED // Enable thermal protection for the heated bed

1.  Download a  fresh [Marlin 1.1.5](https://github.com/MarlinFirmware/Marlin/archive/1.1.5.zip)  from github, and 
2.  Download [JohanV's zip file](http://trium3d.proboards.com/attachment/download/280)
3.  Copy the three files listed above from  [JohanV's zip file](http://trium3d.proboards.com/attachment/download/280) over the same files in the downloaded github folder.
4.  Make a note of the  Z probe offset by issuing the M851 command to your printer.
4. Compile and download to your Trium. 
6.  On Trium LCD  confirm that it reports Marlin 1.1.5 during start up.
7. Restore hard-coded defaults:    M502
8. Restore the Z probe offset M851 Z-1.7    //use the z probe offset for your printer.
9.  G33: Auto-calibrate 
10. M500:  to save the results, or you can hard-code the numbers that G33 came up with into 'Configuration.h' and then repeat the above, with the exception of the auto-calibration, of course.

JohanV [changed the following](http://trium3d.proboards.com/thread/144/marlin-1-5):

**Thermal Protection**   
If you use a damp cloth to clean hairspray from the heated bed, the newly-activated thermal protection declares a failure. To prevent these false alarms JohanV increased the time constant and allowable hysteresis on the bed (in `Configuration_adv.h`). If a thermistor should really fail the protection should activate. 

**PID Loop Calibration**  
Previously, the bed heating used bang-bang control.  JohanV activated the PID loop controller for the bed temperature control.  The bed (ID -1) PID optimisation  is similar to PID optimisation for the extruder.  
Marlin attempts to characterise the first extruder hardware (ID E0) by issuing 
M303 E0 S200 C8 telling it to heat, at full power until it hits 200 °C, and then letting it coast (for it overshoots significantly) until it falls back below the target temperature, and to repeat this for 8 cycles, observing its behaviour all the while. Then it calculates from these observations the Proportional, Integral and Derivative parameters for the control loop, which you can save using M500 (or copy back into `Configuration.h`, as was done here).

http://reprap.org/wiki/PID_Tuning  
https://www.youtube.com/watch?v=APzJfYAgFkQ  
https://forum.e3d-online.com/index.php?threads/pid-tuning.731/  
https://toms3d.org/2014/04/01/3d-printing-guides-using-marlins-pid-autotune/  
[https://oxi.ch](https://oxi.ch/2017/03/28/prusa-i3-and-all-marlin-based-3d-printers-pid-tuning-with-octoprint-slic3r-and-simplify3d/)  
https://en.wikipedia.org/wiki/PID_controller  



## More information

- [Configuring Marlin](http://marlinfw.org/docs/configuration/configuration.html)
- [How to flash](http://marlinfw.org/docs/basics/install.html)
- [Automatic Bed Levelling](http://marlinfw.org/docs/features/auto_bed_levelling.html)
- [Linear Advance extrusion algorithm](http://marlinfw.org/docs/features/lin_advance.html)
- [Marlin development](http://marlinfw.org/meta/development/)
- [List of GCodes understood by Marlin RC8](http://marlinfw.org/meta/gcode/)
- [Printer codes](http://trium3d.proboards.com/thread/7/printer-codes).

