from flask import Response, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
import json
import datetime

from app.model.user import User
from app.model.friends import Friend
from app.model.notification import Notification
from ..model.notification import Notification
from app.util.errors import SchemaValidationError, NumberAlreadyExistsError, UnauthorizedError, \
    InternalServerError
from app.controller.responseController import response_value, remove_password_convert_dict
import app.util.response as response


class SignupApi(Resource):
    res = {}
    """
    [summary]
    Truyền vào body
    phonenumber
    password
    firstname
    lastname
    """

    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.default()
            data = remove_password_convert_dict(user)
            self.res = response.sucess()
            self.res = response_value(self.res, data)
            user.save()
            Friend(owner=user["id"]).save()
            Notification(owner=user["id"]).save()
        except FieldDoesNotExist:
            self.res = response.parameter_not_enough()
        except NotUniqueError:
            self.res = response.user_existed()
        except Exception:
            raise Exception
            self.res = response.internal_server()
        return jsonify(self.res)


class LoginApi(Resource):
    res = {}

    def get(self):
        user = User.objects()
        user_id = []
        for i in user:
            user_id.append(i["id"])
        print(user_id)
        return jsonify(response.sucess())

    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(phonenumber=body.get('phonenumber'))
            authorized = user.check_password(body.get('password'))
            if not authorized:
                raise UnauthorizedError
            expires = datetime.timedelta(days=365)
            access_token = create_access_token(
                identity=str(user.id), expires_delta=expires)

            data = remove_password_convert_dict(user)
            self.res = response.sucess()
            self.res = response_value(self.res, data)
            self.res["data"]["token"] = access_token
        except (UnauthorizedError, DoesNotExist):
            self.res = response.user_is_not_validated()
        except Exception:
            self.res = response.internal_server()
        return jsonify(self.res)


class LogoutApi(Resource):
    res = {}

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            self.res = response.sucess()
        except Exception:
            self.res = response.internal_server()
        return jsonify(self.res)


class ChangePasswordApi(Resource):

    @jwt_required
    def post(self):
        res = {}
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            user = User.objects.get(id=user_id)
            authorized = user.check_password(body.get('password'))
            if not authorized:
                raise UnauthorizedError
            user.password = body.get("new_password")
            if not user.compare_password(body.get('password'), body.get("new_password")):
                raise response.PasswordInvalid
            user.hash_password()
            user.save()
            res = response.sucess()
        except UnauthorizedError:
            res = response.wrong_password()
        except response.PasswordInvalid:
            res = response.password_invalid()
        except Exception:
            raise Exception
            res = response.internal_server()
        return jsonify(res)
    
class Noti(Resource):
    def get(self):
        users = User.objects()
        
        for user in users:
            noti = Notification.objects(owner=user.id).first()
            if noti == None:
                Notification(owner=user.id).save()
        return "ok"

            
