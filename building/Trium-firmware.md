# Trium Firmware


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

For more information see:
- [Configuring Marlin](http://marlinfw.org/docs/configuration/configuration.html)
- [How to flash](http://marlinfw.org/docs/basics/install.html)
- [Automatic Bed Levelling](http://marlinfw.org/docs/features/auto_bed_levelling.html)
- [Linear Advance extrusion algorithm](http://marlinfw.org/docs/features/lin_advance.html)
- [Marlin development](http://marlinfw.org/meta/development/)
- [List of GCodes understood by Marlin RC8](http://marlinfw.org/meta/gcode/)
- [Printer codes](http://trium3d.proboards.com/thread/7/printer-codes).

