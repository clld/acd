import time


def test_ui(selenium):
    selenium.browser.get(selenium.url('/'))

    time.sleep(1)
    selenium.browser.get(selenium.url('/languages'))
    time.sleep(3)
    selenium.browser.get(selenium.url('/sources'))

    time.sleep(3)
