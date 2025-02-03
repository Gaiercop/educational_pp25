#import json
#
#
#class User(object):
#    username = ""
#    pwd = ""
#    access = 0
#
#    def __init__(self, username, pwd, access):
#        self.username = username
#        self.pwd = pwd
#        self.access = access
#
#    def login(self, pwd):
#        return self.pwd == pwd
#
#    def toJSON(self):
#        ans = dict()
#        ans["pwd"] = self.pwd
#        ans["username"] = self.username
#        ans["access"] = str(self.access)
#        return ans
#
#
#def fromJSONtoUser(js):
#    return User(js["username"], js["pwd"], int(js["access"]))
#
#
#class AuthManager(object):
#    users = []
#    sessions = []
#
#    def __init__(self):
#        self.loadUserData()
#        return
#
#    def getBySID(self, sid):
#        if (self.sessions[sid] == -1):
#            raise NameError("Invalid session")
#        return self.users[self.sessions[sid]]
#
#    def addUser(self, user):
#        for tuser in self.users:
#            if (tuser.username == user.username):
#                raise NameError("Username already in use")
#        self.users.append(user)
#        self.saveUserData()
#
#    def saveUserData(self):
#        data = [el.toJSON() for el in self.users]
#        with open('users.json', 'w') as f:
#            f.write(json.dumps(data))
#
#    def loadUserData(self):
#        with open('users.json', 'r') as f:
#            try:
#                self.users = json.load(f)
#            except json.JSONDecodeError:
#                self.users = []
#        for i in range(len(self.users)):
#            self.users[i] = fromJSONtoUser(self.users[i])
#
#    def checkSID(self, sid):
#        if (sid == -1):
#            return False
#        return self.sessions[sid] != -1
#
#    def login(self, user, pwd):
#        id = 0
#        for tuser in self.users:
#            # print(tuser.username, user, tuser.pwd, pwd)
#            if (tuser.username == user):
#                if (tuser.login(pwd)):
#                    self.sessions.append(id)
#                    return len(self.sessions) - 1
#                else:
#                    raise NameError("Wrong username or password")
#            id += 1
#        raise NameError("Wrong username or password")
#
#    def terminateSID(self, sid):
#        self.sessions[sid] = -1

import json
import uuid
from typing import Dict, Optional

class User:
    def __init__(self, username: str, pwd: str, access: int):
        self.username = username
        self.pwd = pwd
        self.access = access

    def verify_password(self, pwd: str) -> bool:
        return self.pwd == pwd

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "pwd": self.pwd,
            "access": self.access
        }

class AuthManager:
    def __init__(self):
        self.users: list[User] = []
        self.sessions: Dict[str, int] = {}
        self.load_user_data()

    def find_user(self, username: str) -> Optional[User]:
        for user in self.users:
            if user.username == username:
                return user
        return None

    def add_user(self, user: User):
        if self.find_user(user.username):
            raise ValueError("Username already exists")
        self.users.append(user)
        self.save_user_data()

    def create_session(self, user_index: int) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = user_index
        return session_id

    def get_user_by_session(self, session_id: str) -> Optional[User]:
        if not session_id:
            return None
            
        user_index = self.sessions.get(session_id)
        if user_index is not None and 0 <= user_index < len(self.users):
            return self.users[user_index]
        return None

    def terminate_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def login(self, username: str, password: str) -> str:
        user = self.find_user(username)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid credentials")
        
        return self.create_session(self.users.index(user))

    def check_session(self, session_id: str) -> bool:
        return session_id in self.sessions

    # === Data Persistence ===
    def save_user_data(self):
        data = [user.to_dict() for user in self.users]
        with open('users.json', 'w') as f:
            json.dump(data, f, indent=2)

    def load_user_data(self):
        try:
            with open('users.json', 'r') as f:
                data = json.load(f)
                self.users = [
                    User(user['username'], user['pwd'], user['access'])
                    for user in data
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = []

auth = AuthManager()
