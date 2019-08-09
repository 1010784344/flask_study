# -*- coding: UTF-8 -*-


class User(object):
    def __init__(self,name=None,pwd=None,email=None,age=None,birthday=None,face=None):
        self.name = name
        self.pwd = pwd
        self.email = email
        self.age = age
        self.birthday = birthday
        self.face = face
    def to_list(self):
        return [self.name, self.pwd, self.email, self.age, self.birthday, self.face]

    def from_list(self,userinfo):
        self.name = userinfo[0]
        self.pwd = userinfo[1]
        self.email = userinfo[2]
        self.age = userinfo[3]
        self.birthday = userinfo[4]
        self.face = userinfo[5]

























