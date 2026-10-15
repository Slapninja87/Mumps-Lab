killall ;
 ;@title Argumentless KILL deletes every local variable, including the caller's
 ;@kind breaks
 ;@naive cleanup only removes variables it created, so keep survives
 ;@why Argumentless KILL has no notion of ownership. It removes every local variable the process can see, including ones the caller set. Give KILL an explicit list of names to remove only your own.
 ;@verified GT.M V7.0-005
 set keep="important"
 do cleanup
 write $data(keep),!
 quit
cleanup ;
 kill
 quit
