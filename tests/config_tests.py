def test_1():
    """
    Tests for the function 'user_input'
    """

    from utils import user_input
    from aiogram import types

    message = types.Message()

    message.text = "/ban user123"
    assert user_input(message, "/ban") == "user123"

    message.text = "/rm"
    assert user_input(message, "/rm") == ""

    message.text = "/remove_this_user_please "
    assert user_input(message, "/remove_this_user_please") == ""


def test_2():
    """
    Defautl test for get_content from the config file
    """

    from config.cfg import get_content
    assert get_content('tests/test.json')["value"] == 'test value'


test_1()
test_2()
