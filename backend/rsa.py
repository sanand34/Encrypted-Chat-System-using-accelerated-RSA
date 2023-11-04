import random
import fractions


def coPrime(x):
    """
    Finds a random co-prime of the given number
    """
    n = x * 2 + 100000  # Upper limit for the range of random integers
    y = random.randint(x * 2, n)
    if fractions.gcd(x, y) != 1:
        return coPrime(x)
    else:
        return y


def mod_inverse(base, m):
    """
    Calculates modular multiplicative inverse
    """
    g, x, y = mod_inverse_iterative(base, m)
    if g != 1:
        return None
    else:
        return x % m


def mod_inverse_iterative(a, b):
    """
    Helps mod_inverse work
    """
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return b, x, y


def modulo(a, b, c):
    """
    Calculates modulo
    """
    return ((int(a) ** int(b)) % int(c))


def totient(n):
    """
    Calculates Euler's totient
    """
    count = 0
    for i in range(1, n):
        if fractions.gcd(n, i) == 1:
            count += 1
    return count


def gen_prime(n):
    """
    Generates random prime numbers between 2 and n
    """
    if n == 2:
        return [2]
    elif n < 2:
        return []
    s = list(range(3, n + 1, 2))
    mroot = n ** 0.5
    half = (n + 1) // 2
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m * m - 3) // 2
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i += 1
        m = 2 * i + 3
    primes = [2] + [x for x in s if x]
    return primes[random.randint(1, len(primes) - 1)]


def prime_factors(n):
    """
    Factorizes the given prime number
    """
    factors = []
    last_result = n
    c = 2
    while last_result != 1:
        if last_result % c == 0 and c % 2 > 0:
            factors.append(c)
        last_result //= c
        c += 1
    return factors[0], factors[1]


def endecrypt(x, e, c):
    """
    Encrypts/decrypts the given ASCII character value using the RSA crypto algorithm
    """
    return modulo(x, e, c)


def decode(x):
    """
    Decodes the given ASCII character value into an ASCII character
    """
    try:
        return str(chr(x).encode('ascii', 'replace'))  # Make sure data is encoded properly
    except ValueError as err:
        print(err)
        print("** ERROR - Decoded character is unrecognized **")


def key_cracker(e, c):
    """
    RSA Key Cracker
    """
    print("Public Key: (%0d, %0d)" % (e, c))
    a, b = prime_factors(c)
    print("[a, b]: [%0d, %0d]" % (a, b))
    m = (a - 1) * (b - 1)
    print("Totient: %0d" % (totient(m)))
    d = mod_inverse(e, m)
    return d


def keygen():
    """
    Generates random RSA keys
    """
    a = gen_prime(100)
    b = gen_prime(100)
    if a == b:
        keygen()
    c = a * b
    m = (a - 1) * (b - 1)
    e = coPrime(m)
    d = mod_inverse(e, m)
    return e, d, c


def test_helpers():
    """
    Test function for utility functions
    """
    print("GCD of 8 and 12 is %0d" % fractions.gcd(8, 12))
    print("%0d and %0d are co-prime" % (2, coPrime(2)))
    print("%0d and %0d are co-prime" % (6, coPrime(6)))
    mod_inverse(11, 60)
    modulo(2, 3, 4)
    totient(24)


def test_encryption(e, c):
    """
    Test function for encryption
    """
    e = int(input("\nEnter e from public key\n"))
    c = int(input("\nEnter c from public key\n"))
    string = input("\nEnter word to encrypt\n")
    for i in range(0, len(string)):
        endecrypt(ord(string[i]), e, c)


def test_decryption(d, c):
    """
    Test function for decryption
    """
    d = int(input("\nEnter d from public key\n"))
    c = int(input("\nEnter c from public key\n"))
    x = int(input("\nEnter number to decrypt\n"))
    decode(endecrypt(x, d, c))


if __name__ == "__main__":
    e, d, c = keygen()
    test_encryption(e, c)
    test_decryption(d, c)
    key_cracker(e, c)
