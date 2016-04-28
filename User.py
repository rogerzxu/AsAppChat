from flask.ext.login import UserMixin


class User(UserMixin):

    def __init__(self, username, id):
        self.user_name = username
        self.user_id = id