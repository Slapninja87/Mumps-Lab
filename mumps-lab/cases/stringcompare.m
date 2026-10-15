stringcompare ;
 ;@title < and > are numeric, = is string equality, ] is string order
 ;@kind breaks
 ;@naive "A"<"B" is 1, "10"<"9" is 0, "abc"=0 is 0 but "abc"<1 is false
 ;@why < and > coerce both operands to numbers by their leading numeric prefix, so non-numeric text becomes 0 and "A"<"B" is 0<0. = never coerces: it compares text, so "1.0"=1 is false while 1.0=1 is true because the literal 1.0 becomes the number 1 before the comparison. Alphabetical order needs the follows operator ].
 ;@verified GT.M V7.0-005
 write "A"<"B",!
 write "B"]"A",!
 write "10"<"9",!
 write "10"]"9",!
 write "abc"=0,!
 write "abc"<1,!
 write 1.0=1,!
 write "1.0"=1,!
 write "3 apples"+4,!
 quit
