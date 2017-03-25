# Introduction

The commercial world is a cruel and ruthless environment. There is little room for kindness and tolerance.  As a supplier, you are indeed aggressively working to take market share away from your competition; so can you really  expect kindness and tolerance?   In my open source endeavours I offer the fruits of my labour for free, and even there I find little kindness and tolerance. I agree that this situation is not commendable, but this is the way it is.  This is the world we live and compete in.

This document is not an attack on the E-Mergin company or team members. It is my evaluation of the Trium 1 printer as a commercial offering.  If your offering is not overall better than the competition, why should someone buy it?   Given the time I spent trying to get my Trium 1 printing, could have bought two built-up Original Josef Prusa i3 MK2 printers. They simply work.

I write this from considerable experience in aerospace engineering, software design and system engineering. I do not have prior 3D printing experience, but read extensively on the topic while waiting for the Trium.

# General notes

A prototype is not a product.  Many people can build prototypes. Few succeed in turning these prototypes into successful products.  A relatively small portion of the budget for new product development is spent on product design. Most of the resources are spent on documentation, quality assurance, produceability, debugging and improving reliability.  It appears that Trium 1 received mostly delta frame design attention with relatively little of remaining product development activities.  Trium 1 is not yet a smoothed out product - it should be regarded as a prototype basis for further experimentation.

The documentation is grossly incomplete and poor.  Exploded-view drawings are not assembly instructions.  I do not expect a 1000-page document, but some of the essential building topics are not  even mentioned.  There is not even a wiring diagram! Agreed, you do not have to tell the user how to develop a 3D STL model or how to operate Repetier, but at least give him some references to the many good books and resources on the internet. Unless a user has built hot-ends before, just throwing the parts at him with no instruction except an exploded view diagram is not acceptable.  Another example is the tape in the slider - shown briefly in the (poor) videos but no mention as to what, why or how.

Videos are no substitute for written documentation, but can be very useful additions to the written notes. But open your mouth and explain what you are doing and why it must be done.  Remember that the viewer must see, understand and internalise: the video should give sufficient time for this.  I found myself reversing and replaying most of the time, and even then not really understanding what I am supposed to do.

The performance of a delta printer depends critically on its mechanical integrity (alignment, mounting, firmware setup, etc) -- much more so than for a cartesian printer. Yet there is no mention of this, or even instructions on where to take special care.

Most of my issues are around maintenance and rework. Almost always, such work requires the disassembly of the printer, or at the very least turning it upside down.  The printer is definitely not maintenance friendly.

# Metal Frame

The Trium metal frame is indeed a beautiful work of art. It is very sturdy and has the potential to provide a stable printer mechanics.  The designers focussed so strongly on the stable metal frame that they lost perspective on the balance of the design. Compromises were made to other design considerations.

- The current design has high mechanical stability but not very good mechanical integrity. 
  - The extrusions slide into bent plates will ill-defined mechanical dimensions. Not all towers slide in to the same depth.
  - The endstop positions are left to change on PCB tolerance.  There is no mechanism to adjust the endstop position. Why is this important? The the endstop heights determines the z=0 plane. This plane must be perpendicular to all three towers. 

- Mechanical maintenance or rework is almost impossible, and almost always requires disassembly of the frame.  Once the top plate has been removed the mechanical integrity is lost.
  -  There is very limited access to the stepper motors once the Top Plate is in place. You have to take off the top plate to gain access or to change the stepper motors.
  - If you use a mechanical damper on the stepper motor, you have to disassemble the printer to get to the screws.
 -  There is severely limited access to the slider mechanics. Most screw heads are not accessible and requires removal of the Top Plate to take out the sliders for any rework or even tightening.
  - There is no instruction on how to align the slider such that the two balls are horizontal. It is surprisingly hard to align, and keep alingment, of this horizontal datum.

# Endstops and stepper motors

As described above, the endstops don't just stop the slider motion, the actually define the coordinate system.

- The endstop position is fixed by the holes in the extrusion and PCBs.  The position of the endstop depends on too many uncontrolled dimensions. There is no means to measure or adjust the height of the endstops.
- The alignment of the endstop switch levers and the slider mechanics is not very good.  The lever is touched on the side (about 10% overlap on my printer).  This led to unreliable contact and variation in the trigger height (up to 150 um on my printer). I had to print three parts to give the slider a wider, flat top surface for touching the endstop lever.
- The position of the three endstops determine the horizontal plane for the printer. If one switch is higher than the rest, the 'horizontal' plane is not perpendicular to the towers: the coordinate system is slanted.
- The presently used stepper motor is currently obtainable from one supplier only: jj-robotics in the UK. I spent many hours on the internet looking for this specific motor and it is only available from Motech (which does not sell in small quantities) and jj-robotics. I could not find it on Ebay, Aliexpress or Banggood.

# Rods and magnetic bearings

A cheap stainless steel (chrome plated?) ball was used.  Stainless steel has low magnetism and this required Emergin to add a spring to assist the magnetic hold force. 

The rod assembly was done by pushing the rod against the ball on one side while using some spacer on the opposite side. This means that rod at the shallow end scraped on the balls, leading to the rods scraping against the balls, thereby destroying the ball surface.  Some users found that after printing only three 1 kg filament rolls, it was necessary to replace the balls. 

I could not measure the rod lengths, but I suspect that the rods are not of equal length.  Unequal rod length can cause all sorts of problems because the delta kinematics depends critically on equality of rod length.

Many of the users I have contact with are moving to Haydn rods and balls as part of their remedial rebuilding. Why would I have to replace these parts after only a few months of operation? 

# Hot bed and z-probe

- The hot-bed height cannot be adjusted in real time with the nozzle moving around on the bed.  If the hot-end is near the screw, it covers the top of the adjustment screw, blocking access. The best you can do is to move the hot end away, do an adjustment and move the hot end back. This process is very time consuming: after you did this twenty times, it is not fun any more.
- The z-probe is a disaster. I received two different types (for my two hot ends), neither of which worked from the box.
- The z-probe is so far from the hot end that its utility is questionable.
- Even during the design phase it was evident that the z-probe was added in must because most modern printers offer it. It was a problem child in the design and was never really designed as an integral part of the system.  E-Mergin's subsequent statements that 'you don't really need it anyway' is just a cheap escape.
- The Marlin mesh bed auto-levelling simply did not work on my bed, the bed was too uneven.  When printing small object it was better to do manual levelling. I could not print large objects because of the poor quality of the bed.

# General layout

- Why do I have to turn the printer upside down (or at the very least lay it on its side) to gain access to the electronics in the Top Plate? Why can't the Top Plate be open at the top?
- Gravity is not working with us on the upside down electronics. Can we really rely on gravity to keep looms and connectors in place? Especially the low quality connectors used in the electronics?
- The fans


# Cheap electronics

- The quality of the mechanical frame is out of balance with the limitations of the supplied electronics  E-Mergin and many users scarcely built the printer but are now looking at new controllers, stepper drivers, printing beds, endstops, z-rpobes, etc.  Why is it necessary to replace the electronics on a newly designed printer? Emergin offered the lame argument that they had to keep the cost down. Granted, it makes sense - but then sell me only the frame and don't charge me for the lower performing electronics.

- The endstop mechanisms are suspect. In the Kickstarter offering E-Mergin offered a (theoretical) 10 micron accuracy. I fail to see how this is possible with the Trium 1 endstop design.  The promised 10 micron is clearly based on inadequate design calculations and without regard to build tolerance and hardware limitations.

- Too many users had to fix faulty electronics. If you buy from China, then at least have some form of quality assurance in your plant to ensure that the parts are working. I buy from an European commercial company with the expectation that the delivered parts will perform their intended function. Why buy from Europe if I can buy for cheaper from China?

# Quality Assurance

The metal parts probably had some form of outgoing inspection at the machine workshops.  The electronic parts were received from China and repacked for shipment.  There were many posts on the fora about inoperative boards, broken PCB tracks, short circuit PCB tracks, etc.

# Conclusion

I can add several more comments and remarks but all of the above are evidence of inadequate product design.  You simply do not put a product out in the user's hands if you have not built and tested at least a few printers in the intended user environment. Get a beta group to do your testing and fault finding for you, before you release to a wider audience.

The mere fact that there are a number of users replacing parts of their printers (EMergin developers were first to do this) with new and improved parts should tell you something of the design quality and maturity of the Trium 1.  Why do I have to pay the full price of a Trium 1 printer, but then replace most of the components to fix the design oversights?

So the lesson in this case study is: Make sure your prototype is a product before you ship large numbers.
