catalogexport ;
 ; Library "export catalog to a file" feature.
 ; FIXED: the filename is checked against a strict allowlist pattern before
 ; it touches a file path or a shell command. No path separators, spaces,
 ; quotes, or shell metacharacters survive the check, so splicing it into
 ; ZSYSTEM or OPEN afterward cannot name a path outside EXPORT_DIR or run
 ; a second shell command.
 new exportdir set exportdir="exports/"
 zsystem "mkdir -p "_exportdir
 do seed
 read !,"Export filename (no extension): ",fname,!
 if fname="" write "Rejected: filename required",! quit
 if '(fname?1.(1A,1L,1N,1"_")) write "Rejected: filename may contain only letters, digits, and underscore",! quit
 new path set path=exportdir_fname_".txt"
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
