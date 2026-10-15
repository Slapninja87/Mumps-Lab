piecerecords ;
 ;@title Delimiter characters inside field data silently shift every later field
 ;@kind breaks
 ;@naive storing "JO^HN" in field 2 keeps it as one field, and reading a missing field is an error
 ;@why A record is one string with an in-band delimiter. $PIECE splits on every delimiter it finds, so data that contains the delimiter creates an extra field with no error. Out-of-range fields read as empty, and setting one pads with delimiters.
 ;@verified GT.M V7.0-005
 new rec
 set rec="SMITH^JOHN^1970"
 write $piece(rec,"^",2),!
 write $piece(rec,"^",9)="",!
 set $piece(rec,"^",5)="X"
 write rec,!
 write $length(rec,"^"),!
 set $piece(rec,"^",2)="JO^HN"
 write rec,!
 write $piece(rec,"^",3),!
 write $length(rec,"^"),!
 quit
