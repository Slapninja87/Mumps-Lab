catalogexport ;
 ; Library "export catalog to a file" feature.
 ; VULNERABLE: splices an attacker-influenced filename straight into a shell
 ; command via ZSYSTEM (a GT.M/YottaDB extension, not standard M), and opens
 ; whatever path the input names with no containment to one directory.
 do seed
 read !,"Export filename (no extension): ",fname,!
 new path set path=fname_".txt"
 open path:(NEWVERSION)
 use path
 for id=1:1:2 if $data(^book(id)) write $piece(^book(id),"^",1),!
 use 0
 close path
 zsystem "gzip -f "_path
 write "Exported to "_path_".gz",!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real staff record.
 set ^book(1)="The Pragmatic Programmer^Hunt^1999"
 set ^book(2)="Clean Code^Martin^2008"
 quit
