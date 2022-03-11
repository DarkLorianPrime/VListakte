def up():
    return """ALTER TABLE Account ADD Phone_mom CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'; ALTER TABLE Account ADD Phone CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'"""


def down():
    return """ALTER TABLE Account DROP Phone; ALTER TABLE Account DROP Phone_mom"""
