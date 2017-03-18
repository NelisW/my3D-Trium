// small part that fits over the slider top to provide
// a better seating area for the end-stop switch

length = 8; // total length
basewidth = 8.;
baseheight = 9.;
overhang = 6.;
overdepth = 1.5;
slotwidth = 3.2;
slotdepth = 8;

rotate([0,-90,0]){
difference(){
union(){
    difference(){
        translate([0,-basewidth/2.,0])
            cube([length,basewidth,baseheight]);
        translate([0,-slotwidth/2.,1.5])
            cube([length,slotwidth,slotdepth]);
    }
 
    translate([0,-overhang-basewidth/2.,0])
        cube([length,basewidth+overhang,overdepth]);
 }
        translate([0,basewidth/2.,0])
            rotate([5,0,0])
                cube([length,2,10]);
   translate([0,-basewidth/2,overdepth])
        rotate([-5,0,0])
            translate([0,-2,0])
                cube([length,2,10]);

}
}
