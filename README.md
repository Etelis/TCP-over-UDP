# TCP Over UDP
a project for Computer Networks at BIU using Python

## Introduction
Implementing some of TCP features over UDP:

    connection using 3-way handshaking
    pipelined reliable data transfer using Selective repeat.
    congestion control similar to TCP Tahoe

## Algorithm
This algorithm attemps to forward 100 bytes of information in each package.
the information is being forwarded thrue the router 'foo' that simulates an interner connection.

the algorithm resembles a pipeline connection, each package sent and received is marked with appropriate flag, allowing for lost package to be retransmitted.

 ### Client-Side
 
 #### Connection initialization:
 The client is being initialised, the file is loaded into `data` variable, then the variable is being split into 97 byte chunks of data.
 
 The client then forms a connection with the server by sending the SYN flag and the desired number of packages (chunks).
 
 the client awaits the SYN + ACK from the server, and transmittes the final ACK + first chunk of data.
 
 #### Package Transmittion:
 using the iterator defined in the class, the client sends the packges to the server, for each package sent the client awaits the acknolagment message, if was not received withen the defualut timeout window the package is transmitted again.

#### End of connection:
After the client has received all the acknolagment messages for the packages transmitted it sends an FIN message to the server, after receiving a followup FIN message the client is convinced the sever has received the data in full and disconnects the connection.


 ### Server-Side
 
 #### Connection initialization:
 The server itterates over an endless loop awaiting connections. (`SYN_FLG`)
 as a new connection arrives the server initialises a boolean array for tracking the order of the received packages.
 
  #### Package Transmittion:
  as a connection has been initialised the server receives new packages, for each package received the server sends a corresponding ack message using the `recv_pkg` method.
  
 #### End of connection:
 After filling the boolean array the server transmittes a FIN message to the client resulting it to close, if by the time of a timeout no additional information was sent the server closes the connection.
 
 
 
 
 A full running example with hebrew explanation could be found here.
 

