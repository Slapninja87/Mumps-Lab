noteviewer ;
 ; Library "view a book's cover note" feature. Notes live as flat files
 ; under notes/, one per book id, e.g. notes/1.txt.
 ; VULNERABLE: the id is spliced straight into the path with no check, so
 ; "../" sequences and absolute paths both work, reaching any file the OS
 ; user running this process can read.
 new notesdir set notesdir="notes/"
 do seed
 read !,"Book id: ",id,!
 new path set path=notesdir_id_".txt"
 open path:(READONLY) use path
 new line read line use 0 close path
 write line,!
 quit
seed ;
 ; Synthetic demo data. Not a real library, not a real secret.
 zsystem "mkdir -p notes secret && echo 'Great read, dog-eared pages.' > notes/1.txt && echo 'topsecret-not-real' > secret/credentials.txt"
 quit
