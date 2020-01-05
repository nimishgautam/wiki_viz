# wiki_viz

Wikipedia clickstream visualization

This is a set of files I initially created to showcase a novel visualization tool, and to play around with CouchDB.

The frontend is a standalone file which expects a particular data structure to be returned inside the `/wikiviz/db/wiki_stream/{Title}` path, or a 404 if nothing is found.  The example is set up with the articles "Wikipedia" and "Pizza" but the original design was set up to have CouchDB running and returning the generated record for any given article.

The files inside the `util` directory are the orignal python files used for preprocessing, checked in as-is. There's a bit of work needed to get it up and running. I haven't fixed it because if I were to redo this, I would use a graph database instead of NoSQL. If/when I get around to rewriting the backend in a graph db, I'll update it here

