from apps.API.security.password import hash_password, verify_password


def test_hash_password_returns_argon2_hash():
    hashed = hash_password("my_secret")

    assert hashed.startswith("$argon2")


def test_verify_password_returns_true_for_correct_password():
    hashed = hash_password("correct_password")

    assert verify_password("correct_password", hashed) is True


def test_verify_password_returns_false_for_wrong_password():
    hashed = hash_password("correct_password")

    assert verify_password("wrong_password", hashed) is False


def test_hash_password_produces_different_hashes_for_same_input():
    h1 = hash_password("same")
    h2 = hash_password("same")

    assert h1 != h2


def test_verify_password_works_with_different_hashes_of_same_input():
    h1 = hash_password("same")
    h2 = hash_password("same")

    assert verify_password("same", h1) is True
    assert verify_password("same", h2) is True
