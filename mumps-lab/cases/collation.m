collation ;
 ;@title Subscripts sort numbers first, and canonical numeric strings are the same node as numbers
 ;@kind breaks
 ;@naive subscripts iterate in insertion or plain string order, and s("10") is a different node from s(10)
 ;@why A subscript that is a canonical number (no leading zeros, no trailing zeros after the decimal point) is stored as that number, so s(10) and s("10") are one node and the second SET overwrites the first. Numbers collate before strings, in numeric order. "010" and "1.50" are not canonical, so they are strings and sort after every number.
 ;@verified GT.M V7.0-005
 new key
 set s(10)="num"
 set s("10")="str"
 set s("010")=""
 set s("1.50")=""
 set s("abc")=""
 set s("a")=""
 set s("B")=""
 set s(2)=""
 set s(1)=""
 set s(-1)=""
 set s(1.5)=""
 write s(10),!
 set key=""
 for  set key=$order(s(key)) quit:key=""  write key,!
 quit
