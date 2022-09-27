# TCP Over UDP
a project for Computer Networks at BIU using Python

## Introduction
Implementing some of TCP features over UDP:

    connection using 3-way handshaking
    pipelined reliable data transfer using Selective repeat.
    congestion control similar to TCP Tahoe

## Algorithm
This algorithm attempts to forward 100 bytes of information in each package from the client to the server.

The information is forwarded through the router 'foo' that simulates an internet connection.
The algorithm resembles a pipeline connection; each package sent and received is marked with an appropriate flag, allowing the lost package to be retransmitted.

 ### Client-Side
 
#### Connection initialization:
The client is being initialized; the file is loaded into the `data` variable, then the variable is split into 97-byte chunks of data.
The client then connects with the server by sending the SYN flag and the desired number of packages (chunks).
The client awaits the SYN + ACK from the server and transmits the final ACK + first chunk of data.

#### Package Transmission:
Using the iterator defined in the class, the client sends the packages to the server; for each package sent, the client awaits the acknowledgment message; if the message does not arrive within the default timeout window, the client retransmits the package.

#### End of connection:
After the client has received all the acknowledgment messages for the packages transmitted, it sends a FIN message to the server; after receiving a follow-up FIN message, the client is convinced the server has received the data in full and disconnects the connection.

 ### Server-Side
 
 #### Connection initialization:
The server iterates over an endless loop awaiting connections. (`SYN_FLG`) as a new connection arrives, 
the server initializes a boolean array for tracking the order of the received packages.
 
  #### Package Transmission:
As a connection has been initialized, the server receives new packages; for each package received, the server sends a corresponding ack message using the recv_pkg method.
  
 #### End of connection:
After filling the boolean array, the server transmits a FIN message to the client resulting in its closing; if by the time of a timeout, no additional information was sent, the server closes the connection.
 
A complete running example with a Hebrew explanation can be found here.
