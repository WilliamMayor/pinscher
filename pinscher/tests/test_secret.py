from nose.tools import assert_equal, assert_not_equal

from pinscher.Secret import Secret


def test_lock():
    s = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s.lock(1234)
    assert_equal('\xbb<\xbd\xc3\x1a', s.cipher)


def test_unlock():
    s = Secret(cipher='\xbb<\xbd\xc3\x1a', iv=b'iv' * 8, tags=('t'))
    s.unlock(1234)
    assert_equal('plain', s.plain)


def test_different_tags():
    s1 = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s1.lock(1234)
    s2 = Secret(plain='plain', iv=b'iv' * 8, tags=('u'))
    s2.lock(1234)
    assert_not_equal(s1.cipher, s2.cipher)


def test_tag_order_matters():
    s1 = Secret(plain='plain', iv=b'iv' * 8, tags=('t', 'u'))
    s1.lock(1234)
    s2 = Secret(plain='plain', iv=b'iv' * 8, tags=('u', 't'))
    s2.lock(1234)
    assert_not_equal(s1.cipher, s2.cipher)


def test_different_pins():
    s1 = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s1.lock(1234)
    s2 = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s2.lock(5678)
    assert_not_equal(s1.cipher, s2.cipher)


def test_wrong_pin():
    s1 = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s1.lock(1234)
    s2 = Secret(cipher=s1.cipher, iv=b'iv' * 8, tags=('t'))
    s2.unlock(5678)
    assert_not_equal(s1.plain, s2.plain)


def test_different_ivs():
    s1 = Secret(plain='plain', iv=b'iv' * 8, tags=('t'))
    s1.lock(1234)
    s2 = Secret(plain='plain', iv=b'jw' * 8, tags=('t'))
    s2.lock(1234)
    assert_not_equal(s1.cipher, s2.cipher)


def test_random_ivs():
    s1 = Secret(plain='plain', tags=('t'))
    s1.lock(1234)
    s2 = Secret(plain='plain', tags=('t'))
    s2.lock(1234)
    assert_not_equal(s1.cipher, s2.cipher)
