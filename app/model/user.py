import mongoengine_goodjson as gj
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
from mongoengine import StringField, ListField, ReferenceField, FileField, BooleanField, DateTimeField
import uuid
import pylcs

from app.model.post import Post
from app.model.userEmbedd import UserEmbedd


class User(gj.Document):
    phonenumber = StringField(required=True, unique=True)
    password = StringField(required=True, min_length=6)
    firstname = StringField(required=True)
    lastname = StringField(required=True)
    username = StringField(required=True)
    birthday = StringField(required=True)
    blocks = ListField(ReferenceField('User'))
    avatar = FileField(default=None)
    uuid = StringField(required=True)
    verify = BooleanField()
    creation_date = DateTimeField()
    modified_date = DateTimeField(default=datetime.datetime.now)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def default(self):
        self.username = self.firstname + " " + self.lastname
        self.uuid = str(uuid.uuid4())
        self.verify = False
        with open('app/model/default.jpg', 'rb') as fd:
            self.avatar.put(fd, content_type='image/jpeg')
        # self.blocks = []

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_uuid(self, uuid):
        return self.uuid == uuid

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now()
        self.modified_date = datetime.datetime.now()
        return super(User, self).save(*args, **kwargs)
    
    def update_username(self, firstname="", lastname = ""):
        if firstname == "":
            firstname = self.firstname
        if lastname == "":
            lastname = self.lastname
        self.username = firstname + " " + lastname


    def compare_password(self, password, new_password):
        lcs = pylcs.lcs(password, new_password)
        if (lcs/len(new_password)) < 0.8:
            return True
        return False

    def get_user_dic(self):
        res = {
            "user": self.id,
            "username": self.username
        }
        return res

    def get_user_embedded(self):
        res = UserEmbedd()
        res.user = self.id
        res.username = self.username
        return res
