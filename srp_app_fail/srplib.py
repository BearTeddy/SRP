  # N    A large safe prime (N = 2q+1, where q is prime)
  #      All arithmetic is done modulo N.
  # g    A generator modulo N
  # k    Multiplier parameter (k = H(N, g) in SRP-6a, k = 3 for legacy SRP-6)
  # s    User's salt
  # I    Username
  # p    Cleartext Password
  # H()  One-way hash function
  # ^    (Modular) Exponentiation
  # u    Random scrambling parameter
  # a,b  Secret ephemeral values
  # A,B  Public ephemeral values
  # x    Private key (derived from p and s)
  # v    Password verifier

import hashlib
import os
import binascii
import six



SHA1 = hashlib.sha1

NG_1024   = 0


N = '''\
AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC319294\
3DB56050A37329CBB4A099ED8193E0757767A13DD52312AB4B03310D\
CD7F48A9DA04FD50E8083969EDB767B0CF6095179A163AB3661A05FB\
D5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740ADBF4FF74\
7359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A\
436C6481F1D2B9078717461A5B9D32E688F87748544523B524B0D57D\
5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6AF874E73\
03CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6\
94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F\
9E4AFF73'''
g = '2'
k= "5b9e8ef059c6b32ea59fc1d322d37f04aa30bae5aa9003b8321e21ddb04e300"

def bytes_to_long(s):
    n = 0
    for b in six.iterbytes(s):
        n = (n << 8) | b
    return n

def long_to_bytes(n):
    l = list()
    x = 0
    off = 0
    while x != n:
        b = (n >> off) & 0xFF
        l.append( chr(b) )
        x = x | (b << off)
        off += 8
    l.reverse()
    return six.b(''.join(l))

def get_random( nbytes ):
    return bytes_to_long( os.urandom( nbytes ) )

def get_random_of_length( nbytes ):
    offset = (nbytes*8) - 1
    return get_random( nbytes ) | (1 << offset)



def gen_x( hash_class, salt, username, password ):
    username = username.encode() if hasattr(username, 'encode') else username
    password = password.encode() if hasattr(password, 'encode') else password
    if _no_username_in_x:
        username = six.b('')
    return H( hash_class, salt, H( hash_class, username + six.b(':') + password ) )



def create_salted_verification_key( username, password, hash_alg=SHA1, ng_type=NG_2048, n_hex=None, g_hex=None, salt_len=4 ):
    if ng_type == NG_CUSTOM and (n_hex is None or g_hex is None):
        raise ValueError("Both n_hex and g_hex are required when ng_type = NG_CUSTOM")
    hash_class = _hash_map[ hash_alg ]
    N,g = get_ng( ng_type, n_hex, g_hex )
    _s = long_to_bytes( get_random( salt_len ) )
    _v = long_to_bytes( pow(g,  gen_x( hash_class, _s, username, password ), N) )

    return _s, _v



def calculate_M( hash_class, N, g, I, s, A, B, K ):
    I = I.encode() if hasattr(I, 'encode') else I
    h = hash_class()
    h.update( HNxorg( hash_class, N, g ) )
    h.update( hash_class(I).digest() )
    h.update( long_to_bytes(s) )
    h.update( long_to_bytes(A) )
    h.update( long_to_bytes(B) )
    h.update( K )
    return h.digest()


def calculate_H_AMK( hash_class, A, M, K ):
    h = hash_class()
    h.update( long_to_bytes(A) )
    h.update( M )
    h.update( K )
    return h.digest()


class Verifier (object):

    def __init__(self, username, bytes_s, bytes_v, bytes_A, hash_alg=SHA1, ng_type=NG_2048, n_hex=None, g_hex=None, bytes_b=None):
        if ng_type == NG_CUSTOM and (n_hex is None or g_hex is None):
            raise ValueError("Both n_hex and g_hex are required when ng_type = NG_CUSTOM")
        if bytes_b and len(bytes_b) != 32:
            raise ValueError("32 bytes required for bytes_b")
        self.s = bytes_to_long(bytes_s)
        self.v = bytes_to_long(bytes_v)
        self.I = username
        self.K = None
        self._authenticated = False

        N,g        = get_ng( ng_type, n_hex, g_hex )
        hash_class = _hash_map[ hash_alg ]
        k          = H( hash_class, N, g, width=len(long_to_bytes(N)) )

        self.hash_class = hash_class
        self.N          = N
        self.g          = g
        self.k          = k

        self.A = bytes_to_long(bytes_A)

        # SRP-6a safety check
        self.safety_failed = self.A % N == 0

        if not self.safety_failed:

            if bytes_b:
                self.b = bytes_to_long(bytes_b)
            else:
                self.b = get_random_of_length( 32 )
            self.B = (k*self.v + pow(g, self.b, N)) % N
            self.u = H(hash_class, self.A, self.B, width=len(long_to_bytes(N)))
            self.S = pow(self.A*pow(self.v, self.u, N ), self.b, N)
            self.K = hash_class( long_to_bytes(self.S) ).digest()
            self.M = calculate_M( hash_class, N, g, self.I, self.s, self.A, self.B, self.K )
            self.H_AMK = calculate_H_AMK( hash_class, self.A, self.M, self.K )


    def authenticated(self):
        return self._authenticated


    def get_username(self):
        return self.I


    def get_ephemeral_secret(self):
        return long_to_bytes(self.b)


    def get_session_key(self):
        return self.K if self._authenticated else None

    # returns (bytes_s, bytes_B) on success, (None,None) if SRP-6a safety check fails
    def get_challenge(self):
        if self.safety_failed:
            return None,None
        else:
            return (long_to_bytes(self.s), long_to_bytes(self.B))

    # returns H_AMK on success, None on failure
    def verify_session(self, user_M):
        if not self.safety_failed and user_M == self.M:
            self._authenticated = True
            return self.H_AMK


class User (object):
    def __init__(self, username, password, hash_alg=SHA1, ng_type=NG_2048, n_hex=None, g_hex=None, bytes_a=None, bytes_A=None):
        if ng_type == NG_CUSTOM and (n_hex is None or g_hex is None):
            raise ValueError("Both n_hex and g_hex are required when ng_type = NG_CUSTOM")
        if bytes_a and len(bytes_a) != 32:
            raise ValueError("32 bytes required for bytes_a")
        N,g        = get_ng( ng_type, n_hex, g_hex )
        hash_class = _hash_map[ hash_alg ]
        # k          = H( hash_class, N, g, width=len(long_to_bytes(N)) )
        k = normalH(N)

        self.I     = username
        self.p     = password
        if bytes_a:
            self.a = bytes_to_long(bytes_a)
        else:
            self.a = get_random_of_length( 32 )
        if bytes_A:
            self.A = bytes_to_long(bytes_A)
        else:
            self.A = pow(g, self.a, N)
        self.v     = None
        self.M     = None
        self.K     = None
        self.H_AMK = None
        self._authenticated = False

        self.hash_class = hash_class
        self.N          = N
        self.g          = g
        self.k          = k


    def authenticated(self):
        return self._authenticated


    def get_username(self):
        return self.I


    def get_ephemeral_secret(self):
        return long_to_bytes(self.a)


    def get_session_key(self):
        return self.K if self._authenticated else None


    def start_authentication(self):
        return (self.I, long_to_bytes(self.A))


    # Returns M or None if SRP-6a safety check is violated
    def process_challenge(self, bytes_s, bytes_B):

        self.s = bytes_to_long( bytes_s )
        self.B = bytes_to_long( bytes_B )

        N = self.N
        g = self.g
        k = self.k

        hash_class = self.hash_class

        # SRP-6a safety check
        if (self.B % N) == 0:
            return None

        self.u = H( hash_class, self.A, self.B, width=len(long_to_bytes(N)) )

        # SRP-6a safety check
        if self.u == 0:
            return None

        self.x = gen_x( hash_class, self.s, self.I, self.p )

        self.v = pow(g, self.x, N)

        self.S = pow((self.B - k*self.v), (self.a + self.u*self.x), N)

        self.K     = hash_class( long_to_bytes(self.S) ).digest()
        self.M     = calculate_M( hash_class, N, g, self.I, self.s, self.A, self.B, self.K )
        self.H_AMK = calculate_H_AMK(hash_class, self.A, self.M, self.K)

        return self.M


    def verify_session(self, host_HAMK):
        if self.H_AMK == host_HAMK:
            self._authenticated = True
