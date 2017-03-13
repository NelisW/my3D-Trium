; probe three points to tower and centre
M119 ; print a clearly visible separator in the log file
G21  ; set units to mm
G90  ; absolute positioning
G28  ; home: reset coord sys by reading MAX endstops
G0 X-39. Y-39. Z10. F3000 ; move to X tower 10 mm above bed
G30  ; do a single z probe at current (x,y)
G30
G30
G30
G30
G28 ; home: reset coord sys by reading MAX endstops
G0 X106. Y-39. Z10. F3000 ; move to Y tower 10 mm above bed
G30
G30
G30
G30
G30
G28 ; home: reset coord sys by reading MAX endstops
G0 X33.5 Y92. Z10. F3000
G30
G30
G30
G30
G30
G28 ; home: reset coord sys by reading MAX endstops
G0 X33.5 Y5. Z10. F3000 ; move to centre 10 mm above bed
G30
G30
G30
G30
G30
G28 ; home: reset coord sys by reading MAX endstops