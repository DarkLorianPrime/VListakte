def up():
    return """ALTER TABLE users ADD token uuid"""


def down():
    return """ALTER TABLE user DROP token"""
