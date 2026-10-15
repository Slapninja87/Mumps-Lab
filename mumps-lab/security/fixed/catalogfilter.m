catalogfilter ;
 ; Library catalog "custom filter" feature.
 ; FIXED: parses the condition into an operator and a number from an
 ; allowlist instead of executing any part of the input as code.
 do seed
 read !,"Filter condition on year, e.g. ""year>2000"": ",cond,!
 new op,val
 if "year"'=$extract(cond,1,4) write "Rejected: must start with ""year""",! quit
 set op=$extract(cond,5,5)
 set val=$extract(cond,6,$length(cond))
 if op'=">",op'="<",op'="=" write "Rejected: operator must be > < or =",! quit
 if '(val?1.N) write "Rejected: value must be numeric",! quit
 for id=1:1:3 do
 . if '$data(^book(id)) quit
 . new year,keep
 . set year=$piece(^book(id),"^",3)
 . set keep=0
 . if op=">" set keep=(year>val)
 . if op="<" set keep=(year<val)
 . if op="=" set keep=(year=val)
 . if keep write $piece(^book(id),"^",1),!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real staff record.
 set ^book(1)="The Pragmatic Programmer^Hunt^1999"
 set ^book(2)="Clean Code^Martin^2008"
 set ^book(3)="The Mythical Man-Month^Brooks^1975"
 set ^staff("admin","password")="hunter2-not-real"
 quit
