$fn = 30;

bx = 6.18;
by = 6.18;
bz = 3.5;
bgap = 3.75;
btab = 1.2; // height of button above body
wall = 4;
bezel = 3;
flangez = 1;
bheight = 2;
grid = 2.54;
pcbthk = 1.6;

braceheight = 5; // calculated to 4.7, but needs verification

rowx = bx+bgap+wall*2+4;
rowy = 4*(by+bgap)+2*grid+4;
row3y = 3*(by+bgap)+4;
echo(rowx);
echo(rowy);

*button_housing();
*row();
*for (i=[-1, 1, 0], j=[-1, 1])
    translate([i*15, j*10, 0])
        button_pad();
*xypad(); 

*xyback();
*zpad();
*row3();
*zpad2();
*zpad3();
*z3back();

*z2back();
*resetpad();

*xbutton_pad();
*translate([0, -10, 0]) ybutton_pad();
*translate([0, -20, 0]) zbutton_pad();

*resetback();

*translate([-13, 18, -40])
fullback();
*resettunnel();
*translate([-70, 0, 0])ztunnel();
*backbox();
*lid();
*backplate();
backbox2();


module backbox2() {
    union() {
        translate([0, 0, 40/2])
        difference() {
            union() {
                cube([98.5, 56, 40], true);
            }
            translate([0, 56/2, 40/2])
                rotate([45, 0, 0])
                    cube([200, 10, 40], true);
             translate([0, -56/2, 40/2])
                rotate([-45, 0, 0])
                    cube([200, 10, 40], true);
            
            translate([0, 0, -1.01])
                backboxvoid();
            
            for (i=[-1, 1]) {
                translate([i*101/2+1, 29, 0])
                    cylinder(r=3, h=200, center=true);
                translate([i*67.8/2+1, -29, 0])
                    cylinder(r=3, h=200, center=true);
            }

            
         }
         mounttabs();
         translate([32.5, -3, 38.115])
            color("red") cube([30, 30, 0.25], true);
     }
}

module mounttabs() {
    translate([1, 0, 1])
    difference() {
        for(i=[-1, 1]) {
            translate([0, i*58/2, 0])
                hull() {
                    for (j=[-1, 1])
                        translate([j*101/2, 0, 0])
                            cylinder(r=4, h=2, center=true);
                }
        }
        for (i=[-1, 1]) {
            translate([i*101/2, 29, 0])
                cylinder(r=2, h=20, center=true);
            translate([i*67.8/2, -29, 0])
                cylinder(r=2, h=20, center=true);
        }
    }
}

module backboxvoid() {
    difference() {
        union() {
            cube([92.5, 50, 38], true);
            translate([92.5/2-26/2+3, -50/2+14/2+13.5, 38/2-10/2+3])
                cube([30, 14, 14], true);
        }
        translate([0, 50/2+1, 38/2+1])
            rotate([45, 0, 0])
                cube([200, 10, 40], true);
         translate([0, -50/2-1, 38/2+1])
            rotate([-45, 0, 0])
                cube([200, 10, 40], true);
    }
}

module lid() {
    mirror([0, 0, 0])
     union() {
        difference() {
            union() {
                hull() for(i=[-1, 1], j=[-1, 1])
                    translate([i*(93/2+4), j*(50/2+4), 0])
                        cylinder(r=4, h=8, center=true);
               translate([-13, 18, 0])
                    cylinder(r=30, h=8, center=true);
            }
            translate([0, 0, 2])
                cube([93, 50, 8], true);
            translate([-13, 18, 2]) 
                cylinder(r=27, h=8, center=true);
            
   
            translate([93/2, -(50/2+4)-4+2.5+37, 8/2-4/2])
                cube([20, 5, 4.01], true);
             
             
            for(i=[-1, 1], j=[-1, 1])
                translate([i*(93/2+4), j*(50/2+4), 0])
                    cylinder(r=2, h=10, center=true);

         }
     }
}

module backplate() {
    mirror([0, 1, 0])
     union() {
        difference() {
            union() {
                hull() for(i=[-1, 1], j=[-1, 1])
                    translate([i*(93/2+4), j*(50/2+4), 0])
                        cylinder(r=4, h=5, center=true);
                translate([46, 0, 0])
                    hull() for (i=[-1, 1])
                        translate([0, i*15-30, 0])
                            cylinder(r=8, h=5, center=true);
                translate([-50, -20, 0])
                    cylinder(r=15, h=5, center=true);
                translate([-13, 18, 0])
                    cylinder(r=30, h=5, center=true);
            }
            translate([0, 0, 2])
                cube([93, 50, 5], true);
            translate([46, 0, 0])
                hull() for (i=[-1, 1])
                    translate([0, i*15-30, -1.9])
                        cylinder(r=6, h=5, center=true);
            translate([-50, -20, -1.9])
                cylinder(r=13, h=5, center=true);
            translate([-13, 18, 2]) {
                cylinder(r=8, h=50, center=true);
                for(i=[-1, 1], j=[-1, 1])
                    translate([i*15, j*15, 0]) {
                        cylinder(r=1.9, h=50, center=true);
                    }
                for(i=[-1, 1])
                    translate([i*15, 15, 0]) {
                        cylinder(r=3.4, h=5, center=true);
                    }
            }
             
             
             
            for(i=[-1, 1])
                translate([i*(93/2+4), (50/2+4), 0]) {
                   translate([0, 0, 3.25])
                        cylinder(r=1.9, h=5, center=true);
                   translate([0, 0, -2])
                        cylinder(r=3.2, h=5, center=true, $fn=6);
                }
                
            for(i=[-1, 1])
                translate([i*(60/2+4), -(50/2+4), 0]) {
                   translate([0, 0, 3.25])
                        cylinder(r=1.9, h=5, center=true);
                   translate([0, 0, -2])
                        cylinder(r=3.2, h=5, center=true, $fn=6);
                }

         }
         translate([41.5, 14.75, 1.5])
            difference() {
                cylinder(r=4, h=8, center=true);
                cylinder(r=2.6, h=11, center=true);
            }
         translate([-37.5, -14., 1.5])
            difference() {
                cylinder(r=4, h=8, center=true);
                translate([0, 0, 2])
                    cylinder(r=2.6, h=10, center=true);
            }
     }
}

module backbox() {
    mirror([0, 1, 0])
     union() {
        difference() {
            union() {
                hull() for(i=[-1, 1], j=[-1, 1])
                    translate([i*(93/2+4), j*(50/2+4), 0])
                        cylinder(r=4, h=40, center=true);
                translate([46, 0, 0])
                    hull() for (i=[-1, 1])
                        translate([0, i*15-30, -40/2+10/2])
                            cylinder(r=8, h=10, center=true);
                translate([-50, -20, -40/2+10/2])
                    cylinder(r=15, h=10, center=true);
                translate([-13, 18, 0])
                    cylinder(r=30, h=40, center=true);
            }
            translate([0, 0, 2])
                cube([93, 50, 40], true);
            translate([46, 0, 0])
                hull() for (i=[-1, 1])
                    translate([0, i*15-30, -40/2+10/2-2])
                        cylinder(r=6, h=10, center=true);
            translate([-50, -20, -40/2+10/2-2])
                cylinder(r=13, h=10, center=true);
            translate([-13, 18, 2]) {
                cylinder(r=27, h=40, center=true);
                cylinder(r=8, h=50, center=true);
                for(i=[-1, 1], j=[-1, 1])
                    translate([i*15, j*15, 0]) {
                        cylinder(r=1.9, h=50, center=true);
                    }
            }
             
             
             
            for(i=[-1, 1], j=[-1, 1])
                translate([i*(93/2+4), j*(50/2+4), 40/2-5+0.01])
                    cylinder(r=2.6, h=10, center=true);

         }
         translate([41.5, 14.75, -40/2+10/2])
            difference() {
                cylinder(r=4, h=10, center=true);
                cylinder(r=2.6, h=11, center=true);
            }
         translate([-37.5, -14., -40/2+10/2])
            difference() {
                cylinder(r=4, h=10, center=true);
                translate([0, 0, 2])
                    cylinder(r=2.6, h=10, center=true);
            }
     }
}

module resettunnel() {
    translate([-38, -38, 0]) {
        difference() {
            union() {
                translate([0, 0, -4])
                    cylinder(r=14, h=2, center=true);
                cylinder(r=8, h=10, center=true);
                translate([0, 15, 0])
                    cube([16, 30, 10], true);
            }
            translate([0, 0, -1])
                cylinder(r=5, h=8.01, center=true);
            translate([0, 15, -1])
                cube([10.02, 30.01, 8.01], true);
            rotate([0, 0, -17.7]) {
                translate([0, -10, 0]) {
                    translate([0, 0, 2])
                        cylinder(r=3, center=true, h=10);
                    cylinder(r=2, center=true, h=30);
                }
            }
        }
    }

}

module ztunnel() {
    translate([58.5, -45-17, 0]) {
        difference() {
            union() {
                cylinder(r=8, h=10, center=true);
                translate([0, 27, 0])
                    cube([16, 54, 10], true);
            }
            translate([0, 33, -1])
                cube([10, 54.01, 8.01], true);
            cylinder(r=2, h=20, center=true);
            translate([0, 0, 6])
                cylinder(r=4, h=10, center=true);
        }
    }

}

module fullback() {
    union() {
        xyback();
        translate([-38, -38, 0])
            resetback();
        translate([-41, -20, 1.5])
            rotate([0, 0, 72.3])
                cube([10, 50, 3], true);
        translate([-20, -40, 1.5])
            rotate([0, 0, 17.7])
                cube([10, 50, 3], true);
        translate([58.5, -45, 0])
            z3back();
        translate([52, -20, 1.5])
           rotate([0, 0, -72.3])
            cube([10, 35, 3], true);
    }
}

module body() {
    difference() {
       linear_extrude(height = 15) scale([1.1, 1.1, 1])
            import (file = "xypad.dxf");
       translate([0, 0, bezel])
            linear_extrude(height = 15-bezel) scale([0.9, 0.9, 1])
            import (file = "xypad.dxf");
    }
}

module xyback() {
    difference() {
        union() {
            linear_extrude(height = 5) scale([1.1, 1.1, 1])
                import (file = "xypad.dxf");
            for(i=[0, 1, 2, 3])
                rotate([0, 0, i*90])
                    translate([0, (rowx+rowy)/2, braceheight/2+5])
                        for(j=[-1, 1])
                            translate([j*(bx+bgap+wall)/2, 0, 0])
                                cube([wall-1, rowy, braceheight], true);
        }
        cylinder(r=8, h=12, center=true);
        
        for(i=[-1, 1], j=[-1, 1])
            translate([i*15, j*15, 0]) {
                cylinder(r=1.9, h=10, center=true);
                translate([0, 0, 2])
                    cylinder(r=3.2, h=4, $fn=6);
            }
            
        for(i=[-1, 1]) {
            translate([i*(rowy+rowx), 0, 0])
                cylinder(r=2, h=15, center=true);
            translate([0, i*(rowy+rowx), 0])
                cylinder(r=2, h=15, center=true);
        }

    }
}
    
module xypad() {
    union() {
        difference() {
            body();
            for(i=[0, 1, 2, 3])
                rotate([0, 0, i*90])
                    translate([0, rowy/2+bx+bgap, 0])
                        cube([rowx, rowy, bezel*3], true);;
            for(i=[-1, 1]) {
                translate([i*(rowy+rowx), 0, bezel])
                    cylinder(r=2.6, h=15);
                translate([0, i*(rowy+rowx), bezel])
                    cylinder(r=2.6, h=15);
            }
       }
        for(i=[0, 1, 2, 3])
            rotate([0, 0, i*90])
                translate([0, bx+bgap, 0])
                    row();
    }
    
}

module zpad() {
    union() {
        difference() {
            hull() {
                for (i=[-1, 1])
                    translate([0, i*(row3y-rowx+rowx/2+20)/2, 0])
                        cylinder(r=rowx/2+2, h=15);
            }
            translate([0, 0, 15/2+bezel])
                cube([rowx-4, row3y, 15], true);
            translate([0, 0, 0])
                cube([bx+bgap, row3y, 15], true);
            for (i=[-1, 1]) {
                translate([0, i*(row3y-rowx+rowx/2+20)/2, bezel])
                    cylinder(r=2.6, h=20);
           }
         }
        row3();
    }
}

module zpad2() {
    union() {
        difference() {
            hull() {
                for (i=[-1, 1])
                    translate([0, i*(row3y*2-rowx+rowx/2+24)/2, 0])
                        cylinder(r=rowx/2+2, h=15);
            }
            for (i=[-1, 1]) {
                translate([0, i*(row3y/2+2), 15/2+bezel])
                    cube([rowx-4, row3y, 15], true);
                translate([0, i*(row3y/2+2), 0])
                    cube([bx+bgap, row3y, 15], true);
            }
            for (i=[-1, 1]) {
                translate([0, i*(row3y*2-rowx+rowx/2+24)/2, bezel])
                    cylinder(r=2.6, h=20);
           }
         }
         for (i=[-1, 1])
             translate([0, i*(row3y/2+2), 0])
                 if (i == -1) {
                     rotate([0, 0, 180])
                        row3();
                 }
                 else {
                     row3();
                 }
    }
}

module zpad3() {
    mirror([1, 0,0])
    union() {
        //translate([0, 30, 0]) rotate([0, 0, 17.7]) cube([100, 4, 4], true);
        difference() {
            hull() {
                for (i=[-1, 1], j=[-1, 1])
                    translate([j*rowx, i*row3y/2+j*7, 0])
                        cylinder(r=10, h=15);
            }
            translate([0, 0, 5+bz+btab+bezel+flangez+pcbthk]) cube([30, row3y, 10], true);
            for (i=[-1, 1]) {
                translate([i*(rowx/2+2), i*4, 15/2+bezel])
                    cube([rowx-4, row3y, 15], true);
                translate([i*(rowx/2+2), i*4, 0])
                    cube([bx+bgap, row3y, 15], true);
            }
            translate([rowx, row3y/2+7, bezel])
                cylinder(r=2.6, h=20);
            translate([-rowx, -(row3y/2+7), bezel])
                cylinder(r=2.6, h=20);
    
         }
         for (i=[-1, 1])
             translate([i*(rowx/2+2), i*4, 0])
                 if (i == -1) {
                     rotate([0, 0, 180])
                        row3();
                 }
                 else {
                     row3();
                 }
    }
}

module z3back() {
    union() {
        //translate([0, 30, 0]) rotate([0, 0, 17.7]) cube([100, 4, 4], true);
        difference() {
            hull() {
                for (i=[-1, 1], j=[-1, 1])
                    translate([j*rowx, i*row3y/2+j*7, 0])
                        cylinder(r=10, h=3);
            }
            
            translate([rowx, row3y/2+7, bezel])
                cylinder(r=2, h=20, center=true);
            translate([-rowx, -(row3y/2+7), bezel])
                cylinder(r=2, h=20, center=true);
            
            hull() for (i=[-1, 1])
                translate([0, i*8, 0])
                    cylinder(r=4, h=20, center=true);
            
            translate([0, -17, 0]) {
                cylinder(r=2, h=20, center=true);
                translate([0, 0, 1.5])
                    cylinder(r=3.2, h=3, $fn=6);
            }
    
         }
         for (i=[-1, 1])
             translate([i*(rowx/2+2), i*4, braceheight/2+3])
                difference() {
                    cube([rowx-6, 15, braceheight], true);
                    cube([bx+bgap+1, 16, braceheight+1], true);
                }
   }
}

module z2back() {
    union() {
        difference() {
            hull() {
                for (i=[-1, 1])
                    translate([0, i*(row3y*2-rowx+rowx/2+24)/2, 0])
                        cylinder(r=rowx/2+2, h=3);
            }
            cylinder(r=5, h=10, center=true);
            for (i=[-1, 1]) {
                translate([0, i*(row3y*2-rowx+rowx/2+24)/2, 0])
                    cylinder(r=2, h=20, center=true);
                translate([0, i*10, 0]) {
                    cylinder(r=2, h=20, center=true);
                    translate([0, 0, 1.5])
                        cylinder(r=3.2, h=3, $fn=6);
                }
           }
         }
        for(i=[0, 1])
            rotate([0, 0, i*180])
                translate([0, (row3y/2+2), braceheight/2+3])
                    for(j=[-1, 1])
                        translate([j*(bx+bgap+wall)/2, 0, 0])
                            cube([wall-1, row3y-1, braceheight], true);
    }
}


module resetpad() {
    mirror()
    union() {
        difference() {
            union() {
                hull() {
                    cylinder(r=rowx/2+2, h=15);
                    rotate([0, 0, 72.3])
                        translate([0, 33, 0])
                            cylinder(r=rowx/2+2, h=15);
                }
                hull() {
                    cylinder(r=rowx/2+2, h=15);
                    rotate([0, 0, 17.7])
                        translate([0, -33, 0])
                            cylinder(r=rowx/2+2, h=15);
                }
            }
            
            cube([bx+bgap, by+bgap, 10], true);
            rotate([0, 0, 72.3])
                translate([0, 20, 0])
                    rotate([0, 0, -72.3])
                        cube([bx+bgap, by+bgap, 10], true);
            rotate([0, 0, 17.7])
                translate([0, -20, 0])
                    rotate([0, 0, -17.7])
                        cube([bx+bgap, by+bgap, 10], true);
            
            translate([0, 0, bezel]) union() {
                hull() {
                    cylinder(r=rowx/2+2-3, h=15);
                    rotate([0, 0, 72.3])
                        translate([0, 20, 0])
                            cylinder(r=rowx/2+2-3, h=15);
                }
                hull() {
                    cylinder(r=rowx/2+2-3, h=15);
                    rotate([0, 0, 17.7])
                        translate([0, -20, 0])
                            cylinder(r=rowx/2+2-3, h=15);
                }
            }
            rotate([0, 0, 72.3])
                translate([0, 33, bezel])
                cylinder(r=2.6, h=15);
            rotate([0, 0, 17.7])
                translate([0, -33, bezel])
                cylinder(r=2.6, h=15);

        }

        
        translate([0, -(by+bgap)/2, 0]) {
            buttony_housing();
            rotate([0, 0, 72.3])
                translate([0, 20, 0])
                    rotate([0, 0, -72.3])
                        buttonx_housing();
            rotate([0, 0, 17.7])
                translate([0, -20, 0])
                    rotate([0, 0, -17.7])
                        buttonz_housing();
        }
    }
}

module resetback() {
    union() {
        difference() {
            union() {
                hull() {
                    cylinder(r=rowx/2+2, h=3);
                    rotate([0, 0, 72.3])
                        translate([0, 33, 0])
                            cylinder(r=rowx/2+2, h=3);
                }
                hull() {
                    cylinder(r=rowx/2+2, h=3);
                    rotate([0, 0, 17.7])
                        translate([0, -33, 0])
                            cylinder(r=rowx/2+2, h=3);
                }
                rotate([0, 0, 72.3])
                    translate([0, 11, 3+braceheight/2])
                        difference() {
                            cube([19, 8, braceheight], true);
                            cube([8, 10, braceheight+1], true);
                        }
                rotate([0, 0, 17.1])
                    translate([0, -15, 3+braceheight/2])
                        difference() {
                            cube([19, 8, braceheight], true);
                            cube([8, 10, braceheight+1], true);
                        }
            }
        
            cylinder(r=5, h=10, center=true);
            rotate([0, 0, 72.3]) {
                translate([0, 10, 0]) {
                    cylinder(r=2, h=10, center=true);
                    translate([0, 0, 1.5])
                        cylinder(r=3.2, h=10, $fn=6);
                }
                translate([0, 33, 0])
                    cylinder(r=2, h=10, center=true);
            }
            rotate([0, 0, 17.7]) {
                translate([0, -10, 0]) {
                    cylinder(r=2, h=10, center=true);
                    translate([0, 0, 1.5])
                        cylinder(r=3.2, h=10, $fn=6);
                }
                translate([0, -33, 0])
                    cylinder(r=2, h=10, center=true);
            }
       }
    }
}

module row() {    
    translate([0, 2, 0])
    union() {
        for(i=[0, 1, 2])
            translate([0, i*(by+bgap), 0])
                button_housing();
        translate([0, 3*(by+bgap)+2*grid, 0])
            button_housing();
        translate([0, 3*(by+bgap)+grid, bezel/2])
            cube([bx+bgap+wall*2, 2*grid, bezel], true);
   
        for(i=[-1, 1]) {
            translate([i*((bx+bgap+wall*2)/2+1), (4*(by+bgap)+2*grid)/2, (bz+btab+bezel+flangez+pcbthk)/2])
                cube([2, 4*(by+bgap)+2*grid, bz+btab+bezel+flangez+pcbthk], true);
            translate([0, (i+1)*((4*(by+bgap)+2*grid)/2)+i, (bz+btab+bezel+flangez+pcbthk)/2])
                cube([bx+bgap+wall*2+4, 2, bz+btab+bezel+flangez+pcbthk], true);
        }
    }
}

module row3() {    
    union() {
        translate([0, -(by+bgap)/2, 0])
            for (i=[-1, 0, 1]) {
            translate([0, i*(by+bgap), 0])
                button_housing();
            }
   
        for(i=[-1, 1]) {
            translate([i*((bx+bgap+wall*2)/2+1), 0, (bz+btab+bezel+flangez+pcbthk)/2])
                cube([2, 3*(by+bgap), bz+btab+bezel+flangez+pcbthk], true);
            translate([0, i*((3*(by+bgap))/2+1), (bz+btab+bezel+flangez+pcbthk)/2])
                cube([bx+bgap+wall*2+4, 2, bz+btab+bezel+flangez+pcbthk], true);
        }
    }
}

module button_housing() {
    translate([0, (by+bgap)/2, (bz+btab+bezel+flangez)/2])
        difference() {
            cube([bx+bgap+wall*2, by+bgap, bz+btab+bezel+flangez], true);
            translate([0, 0, bezel/2])
                cube([bx+bgap, by+bgap+1, bz+btab+flangez+.001], true);
            translate([0, -1, 0])
                tri_prism(sc=1.55);
        }
}

module buttony_housing() {
    translate([0, (by+bgap)/2, (bz+btab+bezel+flangez)/2])
        difference() {
            cube([bx+bgap+wall*2, by+bgap, bz+btab+bezel+flangez], true);
            translate([0, 0, bezel/2])
                cube([bx+bgap, by+bgap+1, bz+btab+flangez+.001], true);
            translate([0, 0, 0])
                y_prism(sc=1.55);
        }
}

module buttonx_housing() {
    translate([0, (by+bgap)/2, (bz+btab+bezel+flangez)/2])
        difference() {
            cube([bx+bgap+wall*2, by+bgap, bz+btab+bezel+flangez], true);
            translate([0, 0, bezel/2])
                cube([bx+bgap, by+bgap+1, bz+btab+flangez+.001], true);
            translate([0, 0, 0])
                x_prism(sc=1.55);
        }
}

module buttonz_housing() {
    translate([0, (by+bgap)/2, (bz+btab+bezel+flangez)/2])
        difference() {
            cube([bx+bgap+wall*2, by+bgap, bz+btab+bezel+flangez], true);
            translate([0, 0, bezel/2])
                cube([bx+bgap, by+bgap+1, bz+btab+flangez+.001], true);
            translate([0, 0, 0])
                z_prism(sc=1.55);
        }
}

module button_pad() {
    union() {
        translate([0, 0, (bezel+bheight)/2+flangez])
            tri_prism(ht=bezel+bheight, sc=1.2);
        translate([0, 0, flangez/2])
            cube([bx+bgap-1.5, by+bgap-1.5, flangez], true);
    }
}

module xbutton_pad() {
    union() {
        translate([0, 0, (bezel+bheight)/2+flangez])
            x_prism(ht=bezel+bheight, sc=1.2);
        translate([0, 0, flangez/2])
            cube([bx+bgap-1.5, by+bgap-1.5, flangez], true);
    }
}

module ybutton_pad() {
    union() {
        translate([0, 1.5, (bezel+bheight)/2+flangez])
            y_prism(ht=bezel+bheight, sc=1.2);
        translate([0, 0, flangez/2])
            cube([bx+bgap-1.5, by+bgap-1.5, flangez], true);
    }
}

module zbutton_pad() {
    union() {
        translate([0, 0, (bezel+bheight)/2+flangez])
            z_prism(ht=bezel+bheight, sc=1.2);
        translate([0, 0, flangez/2])
            cube([bx+bgap-1.5, by+bgap-1.5, flangez], true);
    }
}


module tri_prism(ht=10, sc=1) {
    translate([0, 0, -ht/2])
        linear_extrude(height=ht)
            scale([sc, sc, 1])
            polygon(points=[ [0, 3.33], [-2.89, -1.67], [2.89, -1.67]]);
}

module y_prism(ht=10, sc=1) {
    translate([0, 0, -ht/2])
        linear_extrude(height=ht)
            scale([sc, sc, 1])
            polygon(points=[ [0, 0], [-0.65, 1.1], [-2.9, 1.1], [-1.125, -1.9], [-1.125, -3.9], [1.125, -3.9], [1.125, -1.9], [2.9, 1.1], [0.65, 1.1] ]);
}

module x_prism(ht=10, sc=1) {
    translate([0, 0, -ht/2])
        linear_extrude(height=ht)
            scale([sc, sc, 1])
            polygon(points=[ [-2.9, 2.5], [-1, 0], [-2.9, -2.5], [-0.9, -2.5], [0, -1.28], [0.9, -2.5], [2.9, -2.5], [1, 0], [2.9, 2.5], [0.9, 2.5], [0, 1.28], [-0.9, 2.5] ]);
}

module z_prism(ht=10, sc=1) {
    translate([0, 0, -ht/2])
        linear_extrude(height=ht)
            scale([sc, sc, 1])
            polygon(points=[ [-2.7, 2.5], [-2.7, 1], [0.16, 1], [-2.7, -1], [-2.7, -2.5], [2.7, -2.5], [2.7, -1], [-0.16, -1], [2.7, 1], [2.7, 2.5] ]);
}