
# This TCL file resets the project and adds the files
# to enable the simulation and synthesis

# Arguments (in order):
#   - Project's name

set PROJ [lindex $argv 0]
open_project -reset $PROJ

add_files explore.cpp
add_files explore.h

add_files -tb testbench.cpp

exit