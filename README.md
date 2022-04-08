# SRP
## PROJECT FOR NUS Based from (https://github.com/simbo1905/thinbus-srp-npm) (https://github.com/symeapp/srp-client)
## Thinbus Javascript Secure Remote Password (SRP)

This project is to simulate the SRP [Secure Remote Password](http://srp.stanford.edu/) [SRP-6](http://srp.stanford.edu/doc.html#papers) protocol in user login and session management. It is to implement a web browser and server connection with zero-knowledge proof-of-password to a web server.

This repo contains 4 projects folders.
SRP_APP <Supposedly implementation between Backend Flask and Front End Library.>
SRP_APP_ <Non Working implementation between Backend Flask and Front End Library.>
SRP_APP_Nodejs <Implementation of SRP protocol using Nodejs Backend and FrontEnd>
SRP_APP_Python <Demonstration of pysrp library>

For each individual project, refer to readme.md of each folder.

== Note - There is differences in hashing algorithm used in pysrp and Thisbus. ==

SRP Overview
------------

SRP is a cryptographically strong authentication
protocol for password-based, mutual authentication over an insecure
network connection.

Unlike other common challenge-response autentication protocols, such
as Kerberos and SSL, SRP does not rely on an external infrastructure
of trusted key servers or certificate management. Instead, SRP server
applications use verification keys derived from each user's password
to determine the authenticity of a network connection.

SRP provides mutual-authentication in that successful authentication
requires both sides of the connection to have knowledge of the
user's password. If the client side lacks the user's password or the
server side lacks the proper verification key, the authentication will
fail.

For a full description of the pysrp package and the SRP protocol, please refer
to the [pysrp documentation](http://pythonhosted.org/srp/)

Note: RFC5054 now provides the de-facto standard for the hashing algorithm used

### What is SRP-6a. Below is the latest design of SRP 6, 6a
'''
N =	A large, safe prime (N = 2q+1, where q is a Sophie Germain prime) All arithmetic is performed in the field of integers modulo N
g =	A generator modulo N
s =	Small salt for the verification key
I =	Username
p =	Cleartext password
H() =	One-way hash function
a,b =	Secret, random values
K =	Session key
k = H(N,g) 	Multiplier Parameter
A = g^a 	Public ephemeral value
B = kv + g^b 	Public ephemeral value
x = H(s, H( I | ‘:’ | p )) 	Private key (as defined by RFC 5054)
v = g^x 	Password verifier
u = H(A,B) 	Random scrambling parameter
M = H(H(N) xor H(g), H(I), s, A, B, K) 	Session key verifier
## -- Protocol Description --

The server stores the password verifier v. Authentication begins with a message from the client:
-- client -> server: I, A = g^a
The server replies with the verifier salt and challenge:
-- server -> client: s, B = kv + g^b
At this point, both the client and server calculate the shared session key:
--client & server: u = H(A,B)
--server: K = H( (Av^u) ^ b )
--client: x = H( s, H( I + ':' + p ) )
--client: K = H( (B - kg^x) ^ (a + ux) )
Now both parties have a shared, strong session key K. To complete authentication they need to prove to each other that their keys match:
--client -> server: M = H(H(N) xor H(g), H(I), s, A, B, K)
--server -> client: H(A, M, K)
'''

![Thinbus SRP Login Diagram](http://simonmassey.bitbucket.io/thinbus/login-cache.png "Thinbus SRP Login Diagram")

In pysrp the dataflow expected during authentication is:

    Client -> Server: username, A
    Server -> Client: s, B
    Client - > Server: M
    Server - > Client : H(A,M,K)

While in Thinbus:

    Client -> Server: username
    Server -> Client: s, B
    Client - > Server: M, A
    Server -> Client: H(A,M,K)
