borrowbook ;
 ; Library "borrow a book" feature: check the copy is available, then mark
 ; it checked out.
 ; FIXED: LOCK makes the check and the set one atomic step. A second process
 ; blocks until the first releases the lock, so it always sees the result
 ; of the first process's write, never the stale value from before it.
 do seed
 lock +^book(1):5
 if '$test write "Could not get the lock (job ",$job,")",! quit
 new available set available=$get(^book(1,"available"),1)
 hang .3
 if available do
 . set ^book(1,"available")=0
 . write "Borrowed by job ",$job,!
 else  write "Already checked out (job ",$job,")",!
 lock -^book(1)
 quit
seed ;
 ; Synthetic demo data.
 if '$data(^book(1,"available")) set ^book(1,"available")=1
 quit
