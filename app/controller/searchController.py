from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
import json

from app.model.search import Search
from app.model.post import Post
from app.model.user import User
from app.model.like import Like
from app.model.friends import Friend
import app.controller.responseController as resCon
import app.util.response as response


class SearchApi(Resource):
    res = {}

    @jwt_required
    def get(self):
        result = []
        try:
            user_id = get_jwt_identity()
            search = Search.objects.get(owner=user_id)
            result = search.history_search
            len_result = len(result)
            if len_result >= 10:
                result = result[len_result - 10: len_result]
        except DoesNotExist:
            print("not search")
        except Exception:
            self.res = response.internal_server()
        return jsonify(result[::-1])

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            search_all = Search.objects(owner=user_id).first()
            if search_all == None:
                search_all = Search(owner=user_id).save()
            Search.objects(owner=user_id).update_one(
                push__history_search=body["keyword"])
            users = json.loads(User.objects(
                username__icontains=body["keyword"]).to_json())
            posts = json.loads(Post.objects(
                described__icontains=body["keyword"]).to_json())
            for index, post in enumerate(posts):
                like = Like.objects.get(post=post["id"])
                is_liked = like.is_liked(user_id)
                posts[index]["is_liked"] = is_liked
            data = []

            for index, user in enumerate(users):
                if str(user["id"]) == str(user_id):
                    del users[index]
                items = {}
                items["username"] = user["username"]
                items["id"] = user["id"]
                friend = Friend.objects.get(owner=user["id"])
                if friend.is_friend(user_id):
                    items["is_friend"] = True
                else:
                    items["is_friend"] = False
                data.append(items)

            self.res["user"] = data
            self.res["posts"] = posts[::-1]
        except DoesNotExist:
            self.res = response.user_is_invalid
        except Exception:
            self.res = response.internal_server()
            raise Exception
        return jsonify(self.res)


class ListSearchApi(Resource):
    pass
