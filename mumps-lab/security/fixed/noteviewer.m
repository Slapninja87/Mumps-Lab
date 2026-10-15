noteviewer ;
 ; Library "view a book's cover note" feature. Notes live as flat files
 ; under notes/, one per book id, e.g. notes/1.txt.
 ; FIXED: id is checked against a numeric-only pattern before it ever
 ; becomes part of a path, so no "../" sequence or absolute path can reach
 ; it in the first place.
 new notesdir set notesdir="notes/"
 do seed
 read !,"Book id: ",id,!
 if '(id?1.N) write "Rejected: book id must be numeric",! quit
 new path set path=notesdir_id_".txt"
 open path:(READONLY) use path
 new line read line use 0 close path
 write line,!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real secret.
 zsystem "mkdir -p notes secret && echo 'Great read, dog-eared pages.' > notes/1.txt && echo 'topsecret-not-real' > secret/credentials.txt"
 quit
