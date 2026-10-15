borrowbook ;
 ; Library "borrow a book" feature: check the copy is available, then mark
 ; it checked out.
 ; VULNERABLE: the check and the set are two separate operations with
 ; nothing holding the global between them. Two processes that both read
 ; "available" before either writes "checked out" both proceed: a classic
 ; check-then-act race, not an injection bug. HANG makes the window wide
 ; enough to hit reliably in a test; on a busy real system the same window
 ; exists, just narrower and harder to reproduce on purpose.
 do seed
 new available set available=$get(^book(1,"available"),1)
 hang .3
 if available do
 . set ^book(1,"available")=0
 . write "Borrowed by job ",$job,!
 else  write "Already checked out (job ",$job,")",!
 quit
seed ;
 ; Synthetic demo data.
 if '$data(^book(1,"available")) set ^book(1,"available")=1
 quit
