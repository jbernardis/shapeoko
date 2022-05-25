$fn = 30;
cvt = 25.4;
brad = 3;

width = 5*cvt;
height = 3.5*cvt;
border = 4;

thick = 3;
module standoff() {
    difference() {
        cylinder(r=4, h=thick+6.5);
        cylinder(r=1.3, h=thick+6.5+1);
    }
}

union() {
    translate([-width/2, -height/2, 0]) {
        difference() {
            cube([width, height, thick], false);
            for (i=[1.15, 1.75, 2.35])
                translate([0.2*cvt, i*cvt, -1])
                    cylinder(r=brad, h=10);
            for (i=[0.2, 0.6, 1.0, 1.4, 2.1, 2.5, 2.9, 3.3 ])
                translate([2.45*cvt, i*cvt, -1])
                    cylinder(r=brad, h=10);
            for (i=[1, 1.4, 2.1, 2.5])
                translate([4.75*cvt, i*cvt, -1])
                    cylinder(r=brad, h=10);
            for (i=[0.9, 1.3, 1.7, 2.1, 2.8, 3.2, 3.6, 4])
                translate([i*cvt, 1.75*cvt, -1])
                    cylinder(r=brad, h=10);
        }
    }
    difference() {
        hull() {
            for(i=[-1, 1], j=[-1, 1])
                translate([i*width/2, j*height/2, 0])
                    cylinder(r=border, h=thick);
        }
        cube([width-1, height-1, thick*4], true);
    }
    
    translate([-0.05*cvt, 0, 0]) standoff();
    translate([1.9*cvt, 0, 0]) standoff();
    translate([-1.9*cvt, 0, 0]) standoff();
    
    translate([-0.45*cvt, -1.6*cvt, 0]) standoff();
    translate([0.35*cvt, -1.6*cvt, 0]) standoff();
    
    translate([-0.45*cvt, 1.6*cvt, 0]) standoff();
    translate([0.35*cvt, 1.6*cvt, 0]) standoff();
    
    translate([-2.3*cvt, 1*cvt, 0]) standoff();
    translate([-2.3*cvt, -1*cvt, 0]) standoff();
   
    translate([2.25*cvt, 1.2*cvt, 0]) standoff();
    translate([2.25*cvt, -1.2*cvt, 0]) standoff();

}
    