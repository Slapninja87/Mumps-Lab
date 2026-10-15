scopeleak ;
 ;@title A subroutine that reuses a variable name without NEW can make the caller's loop run forever
 ;@kind breaks
 ;@naive the FOR loop runs three times because the subroutine's i is its own
 ;@why M has no local scope by default, so every routine called from here sees and changes the same i. The subroutine's own FOR leaves i at 2, the outer FOR adds 1 and runs again with i at 3, and that repeats forever. The pass counter stops it after 4 passes only so the demonstration ends. NEW stacks the variable and the subroutine gets its own copy.
 ;@verified GT.M V7.0-005
 new i,passes
 set passes=0
 for i=1:1:3 do audit set passes=passes+1 write "i=",i," pass ",passes,! quit:passes=4
 write "stopped after ",passes," passes",!
 write "--- with NEW",!
 set passes=0
 for i=1:1:3 do auditsafe set passes=passes+1 write "i=",i," pass ",passes,! quit:passes=4
 write "finished after ",passes," passes",!
 quit
audit ;
 for i=1:1:2 write "audit ",i,!
 quit
auditsafe ;
 new i
 for i=1:1:2 write "audit ",i,!
 quit
