recordbrowser ;
 ; Library "browse by record type" feature: book or review, by id.
 ; VULNERABLE: builds a global reference from unsanitized input via naked
 ; indirection, so neither the global name nor the subscript is checked.
 do seed
 read !,"Record type (book/review): ",rtype,!
 read "Id: ",id,!
 write @("^"_rtype_"("_id_")"),!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real staff record.
 set ^book(1)="The Pragmatic Programmer^Hunt^1999"
 set ^review(1)="Still relevant today."
 set ^staff("admin","password")="hunter2-not-real"
 quit
