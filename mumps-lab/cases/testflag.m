testflag ;
 ;@title ELSE tests $TEST, which a called routine can change behind your back
 ;@kind breaks
 ;@naive ELSE runs only when the IF condition was false, so only "inner ran" prints
 ;@why ELSE does not look at the IF. It reads the flag $TEST, which every IF sets from its own condition. The called routine's IF sets it to 0, nothing restores it on return, and the ELSE on the next line fires even though the first IF was true.
 ;@verified GT.M V7.0-005
 set x=1
 if x=1 do inner
 else  write "else ran too",!
 quit
inner ;
 write "inner ran",!
 if 0 write "never printed",!
 quit
