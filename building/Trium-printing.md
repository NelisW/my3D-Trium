
# Bed Preparation

## Hairspray

For bed preparation I use hairspray (Perfect Touch, Firm Hold) - this is a non-aerosol, you pump with your finger.  There are some conflicting advice on the internet: some say a thin coat, some say a liberal coat.   First I made a plastic sheet apron around the bed to prevent spray off the bed. I clean the table with water first, then a dab of cotton and surgical spririts/alcohol to remove grease (if necessary). Then apply a [liberal coat](https://www.youtube.com/watch?v=wzCcTCXGiDU) of hairspray up to the bed edges (two to three layers). You must clearly see the layer on the bed. Try to spray evenly over the bed, avoid forming a bump in the middle. I find it easier to go around the edges first and then just touch up in the centre. Let it dry for ten minutes.  After removing the apron, I set the bed temperature to 70 C for some 10-20 minutes (use Repetier or by LCD  `Prepare-> Preheat PLA -> Preheat PLA bed` and afterwards `Prepare-> Cooldown`).  The prints are done at 230 C for the first layer, then dropping to 200 C for the rest.  After printing let the bed cool to room temperature.  The prints do not quite jump of the bed, but it is not to hard to remove with a sharp knife. Removing the hairspray is easy: simply wash off with a little water. Joe Larson believes the hairspray preparation should last for ten to fifteen prints, but I tend to remove and reapply after five or so prints.  I often find that the skirt lines are broken and spotty, but normally the brim and part print adheres well to the hairspray bed.

<img src="images/bed-hairspray-apron.jpg" width=300>


# First prints 
## Calibration prints
Then I printed [this](http://www.thingiverse.com/thing:745523) which tests the geometry of the delta printer.   The first Print1 failed on the small towers but had a good base. The second Print2 was only somewhat better on the towers, but still not acceptable. Both prints provided very good base detail.   Verbatim PLA translucent in regular Trium hot-end. Feedrate: 100. Flowrate:100. Fan: layer 0: 0%,  layer 1: 24%,  layer 2: 40%,  layer 6: 100%.  Bed: 75 C all the time. Hot-end: 230 C. Nozzle: 0.5


It turned out that the TRIUM towers are exactly 120 degrees displaced (which is why we invested in the superb frame!)  The Print1 scale (from leg length=59.88 measured in Blender) was (X:59.58, Y:59.65, Z:59.75)/59.88 =  (X:0.9950, Y:0.9962, Z:0.9978) avg=0.9963. Print2 scale (from tower to tower) was (X:60.14, Y:60.17, Z:60.14)/60 =  (X:1.0023, Y:1.0028, Z:1.0023) avg=1.0025.  The average of the two is 0.9994.  This average implies to 0.12 mm over 220 mm. 

As a result of this finding I decided that 
- The towers are well placed and accurate.
- The scale is  virtually symmetrical in x and y axes (z axis not yet tested)  and very close to unity, but some more investigation is required if dimensionally accurate prints are required.
- The printing of fine detail definately requires more work 230 C seems too high a temperature.
