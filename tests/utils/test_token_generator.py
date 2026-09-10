from apps.API.utils.token_generator import generate_token_value


def test_generate_token_value_is_unique_across_calls():
    tokens = {generate_token_value() for _ in range(50)}

    assert len(tokens) == 50


def test_generate_token_value_is_url_safe_and_long_enough():
    token = generate_token_value()

    assert len(token) >= 32
    assert all(char.isalnum() or char in "-_" for char in token)
