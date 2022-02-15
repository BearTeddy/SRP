'''
    Author - Htun Htet Myat, Jarrett
    Description - Login system using SRP Protocol ( Zero Knowledge Password Proof )
    Refrences - pysrp
'''
"""
N 	A large, safe prime (N = 2q+1, where q is a Sophie Germain prime) All arithmetic is performed in the field of integers modulo N
g 	A generator modulo N
s 	Small salt for the verification key
I 	Username
p 	Cleartext password
H() 	One-way hash function
a,b 	Secret, random values
K 	Session key
k = H(N,g) 	Multiplier Parameter
A = g^a 	Public ephemeral value
B = kv + g^b 	Public ephemeral value
x = H(s, H( I | ‘:’ | p )) 	Private key (as defined by RFC 5054)
v = g^x 	Password verifier
u = H(A,B) 	Random scrambling parameter
M = H(H(N) xor H(g), H(I), s, A, B, K) 	Session key verifier
[--## Protocol Description ##--]

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
"""
import logging
logging.basicConfig(
    format='%(process)d- %(lineno)d - %(levelname)s-%(message)s',level=logging.INFO)
import srp


# The salt and verifier returned from srp.create_salted_verification_key() should be
# stored on the server or send to database.
# hash_alg is for Hashing Algorithm Default is SHA1 160 bits
# ngtype is the prime number size in terms of bits default is 2048 bits
salt, vkey = srp.create_salted_verification_key( 'testuser', 'testpassword')
logging.info("\nSalt -> {}\nvKey -> {}".format(str(salt.hex()),str(vkey.hex())))

def auth():
    # Being authentication
    
    #create SRP User Object Provided by client
    
    #correct Testing
    usr      = srp.User( 'testuser', 'testpassword')
    #Failed Testing
    # usr      = srp.User( 'testuser', '123Password')
    
    #'''
    #start_authentication()
    #Return (username, bytes_A). These should be passed to the constructor of the remote Verifer
    #uname and A is generated from client side and passed to server.
    #'''
    uname, A = usr.start_authentication()
    logging.info("\nuname -> {}\nA -> {}".format(str(uname),str(A.hex())))
    #If got exception or failure at any point, should abort on first failure.
    # Client => Server: username, A
    
    svr = srp.Verifier( uname, salt, vkey, A)
    s,B      = svr.get_challenge()
    if s is None or B is None:
        logging.error ("Auth Failed.")
        return
    logging.info("\nuname -> {}\nA -> {}".format(str(s.hex()),str(B.hex())))
    
    #server challange back to client
    #process_challenge(bytes_s, bytes_B)
    # Processe the challenge returned by Verifier.get_challenge() on success this method returns bytes_M that should be sent to Verifier.verify_session() if authentication failed, it returns None.
    M        = usr.process_challenge( s, B )
    #if M success send it back to server to as session key
    if M is None:
        logging.error ("Auth Failed.")
        return
    
    # Client => Server: M
    # verify_session(user_M)  
    # Complete the Verifier side of the authentication process. If the authentication succeded the return result, bytes_H_AMK should be returned to the remote user. On failure, this method returns None.

    HAMK     = svr.verify_session( M )
    if HAMK is None:
        logging.error ("Auth Failed.")
        return
    
    usr.verify_session( HAMK )
    
    assert usr.authenticated()
    assert svr.authenticated()
    
    print("Both Authentication Success")


def main():
    auth()
    return

if __name__ == "__main__":
    main()
