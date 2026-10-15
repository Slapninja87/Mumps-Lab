recordbrowser ;
 ; Library "browse by record type" feature: book or review, by id.
 ; FIXED: rtype is checked against an allowlist and id against a numeric
 ; pattern before either is used, and no global reference is ever built
 ; from attacker-controlled text. There is no indirection left at all.
 do seed
 read !,"Record type (book/review): ",rtype,!
 read "Id: ",id,!
 if rtype'="book",rtype'="review" write "Rejected: unknown record type",! quit
 if '(id?1.N) write "Rejected: id must be numeric",! quit
 if rtype="book" write ^book(id),!
 if rtype="review" write ^review(id),!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real staff record.
 set ^book(1)="The Pragmatic Programmer^Hunt^1999"
 set ^review(1)="Still relevant today."
 set ^staff("admin","password")="hunter2-not-real"
 quit
