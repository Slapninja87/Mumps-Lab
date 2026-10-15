errortrap ;
 ;@title An error trap unwinds the frame that set it and does not resume the failing line
 ;@kind breaks
 ;@naive after the handler runs, execution continues on the next line after the error
 ;@why When the handler finishes with $ECODE cleared it behaves like QUIT from the frame that set $ETRAP, so the caller carries on and the rest of that frame never runs. Only the standard code (M6 undefined variable, M9 divide by zero) is printed because GT.M appends an engine-specific Z code after it (observed ,M6,Z150373850,). $GET avoids the error for a variable that may not exist.
 ;@verified GT.M V7.0-005
 do undefinedread
 write "caller continues",!
 do dividebyzero
 write "caller continues again",!
 write $get(neverset,"default"),!
 quit
undefinedread ;
 new $etrap
 set $etrap="do handler"
 write neverset,!
 write "not reached in undefinedread",!
 quit
dividebyzero ;
 new $etrap
 set $etrap="do handler"
 write 1/0,!
 write "not reached in dividebyzero",!
 quit
handler ;
 write "caught ",$piece($ecode,",",2),!
 set $ecode=""
 quit
