catalogfilter ;
 ; Library catalog "custom filter" feature.
 ; VULNERABLE: builds M code from unsanitized input and XECUTEs it.
 do seed
 read !,"Filter condition on year, e.g. ""year>2000"": ",cond,!
 for id=1:1:3 do
 . if '$data(^book(id)) quit
 . new year,keep
 . set year=$piece(^book(id),"^",3)
 . set keep=0
 . xecute "set keep=("_cond_")"
 . if keep write $piece(^book(id),"^",1),!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real staff record.
 set ^book(1)="The Pragmatic Programmer^Hunt^1999"
 set ^book(2)="Clean Code^Martin^2008"
 set ^book(3)="The Mythical Man-Month^Brooks^1975"
 set ^staff("admin","password")="hunter2-not-real"
 quit
