# Readme

This is my assignment submission for COMP 3010, assignment 1.

Name: Lyle Arcinas
Student number: 7891806

## Instructions for use
Run server.py with the following command: ``python3 server.py clientport workerport``.
Run worker.py with the following command: ``python3 worker.py serverport multicastport syslogport``. Note serverport and workerport should be the same.
Also note that I have NOT included default values for any ports; please provide ports or the programs will give you an error.

I have also included my listener.py for posterity. Use ``python3 listener.py multicastport`` to run this program.
All of my files should have detailed instructions for use.

## Why multicast makes sense
Multicast makes sense for this application as we need to send the results of our work to multiple locations. If we did not use a multicast server, only one active connection would be able to see updates that our worker provides. If this were a real application doing real work, this might be multiple machines that need to know exactly when, say, an image file is done being processed.

Multicast also makes sense because we talked about it during class and when else are we going to bring it up?

### Cat

|\---/|
| o_o |
 \_^_/
