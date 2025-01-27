import json


class User(object):
    username = ""
    pwd = ""
    access = 0

    def __init__(self, username, pwd, access):
        self.username = username
        self.pwd = pwd
        self.access = access

    def login(self, pwd):
        return self.pwd == pwd

    def toJSON(self):
        ans = dict()
        ans["pwd"] = self.pwd
        ans["username"] = self.username
        ans["access"] = str(self.access)
        return ans


def fromJSONtoUser(js):
    return User(js["username"], js["pwd"], int(js["access"]))


class AuthManager(object):
    users = []
    sessions = []

    def __init__(self):
        self.loadUserData()
        return

    def getBySID(self, sid):
        if (self.sessions[sid] == -1):
            raise NameError("Invalid session")
        return self.users[self.sessions[sid]]

    def addUser(self, user):
        for tuser in self.users:
            if (tuser.username == user.username):
                raise NameError("Username already in use")
        self.users.append(user)
        self.saveUserData()

    def saveUserData(self):
        data = [el.toJSON() for el in self.users]
        with open('users.json', 'w') as f:
            f.write(json.dumps(data))

    def loadUserData(self):
        with open('users.json', 'r') as f:
            try:
                self.users = json.load(f)
            except json.JSONDecodeError:
                self.users = []
        for i in range(len(self.users)):
            self.users[i] = fromJSONtoUser(self.users[i])

    def checkSID(self, sid):
        return self.sessions[sid] != -1

    def login(self, user, pwd):
        id = 0
        for tuser in self.users:
            # print(tuser.username, user, tuser.pwd, pwd)
            if (tuser.username == user):
                if (tuser.login(pwd)):
                    self.sessions.append(id)
                    return len(self.sessions) - 1
                else:
                    raise NameError("Wrong username or password")
            id += 1
        raise NameError("Wrong username or password")

    def terminateSID(self, sid):
        self.sessions[sid] = -1
