lefttoright ;
 ;@title Operators have no precedence and evaluate strictly left to right
 ;@kind works
 ;@naive 2+3*4 is 14, 1<2+3 is 1, '1=2 is 1, -2**2 is -4
 ;@why M evaluates binary operators left to right and only parentheses change the order. Unary operators bind to the operand beside them, so '1=2 is ('1)=2 and -2**2 is (-2)**2.
 ;@verified GT.M V7.0-005
 write 2+3*4,!
 write 2+(3*4),!
 write 1<2+3,!
 write '1=2,!
 write '(1=2),!
 write -2**2,!
 quit
