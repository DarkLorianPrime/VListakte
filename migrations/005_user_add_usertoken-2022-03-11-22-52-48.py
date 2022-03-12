def up():
    return """ALTER TABLE UserAccount ADD token uuid"""


def down():
    return """ALTER TABLE UserAccount DROP token"""
