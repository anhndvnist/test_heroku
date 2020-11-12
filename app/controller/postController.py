from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
import json

from app.model.post import Post, Images
from app.model.user import User
from app.model.like import Like
from app.model.comment import Comment
import app.controller.responseController as resCon
import app.util.response as response


def get_user_name(user):
    res = {
        "user": user["id"],
        "username": user["username"]
    }
    return res


def list_return(res, friend_anything):
    """
    docstring
    """
    data = []
    for i in friend_anything:
        data.append(resCon.convert_object_to_dict(i))
    res = response.sucess()
    res["data"] = data
    res["total"] = len(data)
    return res

# def is_like(post, like):


class PostsApi(Resource):
    res = {}

    @jwt_required
    def get(self):
        try:
            # Init
            user_id = get_jwt_identity()
            posts = Post.objects().to_json()
            posts = json.loads(posts)
            # check is_like
            for index, post in enumerate(posts):
                like = Like.objects.get(post=post["id"])
                is_like = like.is_like(user_id)
                posts[index]["is_like"] = is_like
            # return lastest
            return jsonify(posts[::-1])
        except Exception:
            raise Exception
            self.res = response.internal_server()
        return jsonify(self.res)

    @jwt_required
    def post(self):
        try:
            # init
            user_id = get_jwt_identity()
            form = request.form
            files = request.files
            user = User.objects(id=user_id).only('username').first()
            owner = get_user_name(user)
            post = Post(described=form["described"], owner=owner)
            images = Images()
            # add file video and images
            for name_file in files:
                file = request.files.get(name_file)
                content_type = file.content_type
                if "video" in content_type:
                    post.video.replace(file, content_type=content_type)
                elif "image" in content_type:
                    images[name_file].replace(file, content_type=content_type)
            # save Like, comment
            post.images = images
            post.save()
            Comment(post=post).save()
            Like(post=post).save()
            return Response(post.to_json(), mimetype="application/json", status=200)
        except DoesNotExist:
            self.res = response.user_is_not_validated()
        except Exception:
            raise Exception
            self.res = response.internal_server()
        return jsonify(self.res)


class PostApi(Resource):
    res = {}

    @jwt_required
    def put(self, id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=id)
            body = request.get_json()
            post.update(**body)
            self.res = response.sucess()
            self.res = resCon.response_value(self.res, body)
        except DoesNotExist:
            self.res = response.post_is_not_exit()
        except Exception as e:
            raise e
            self.res = response.internal_server()
        return jsonify(self.res)

    @jwt_required
    def delete(self, id):
        try:
            post = Post.objects(id=id).first()
            post.delete()
            self.res = response.sucess()
        except DoesNotExist:
            self.res = response.post_is_not_exit()
        return jsonify(self.res)

    @jwt_required
    def get(self, id):
        try:
            user_id = get_jwt_identity()
            post = Post.objects.get(id=id)
            post = json.loads(post)

            like = Like.objects.get(post=post["id"])
            is_like = like.is_like(user_id)
            post["is_like"] = is_like

            self.res = response.sucess()
            self.res["data"] = post
        except DoesNotExist:
            self.res = response.post_is_not_exit()
        except Exception:
            raise Exception
            self.res = response.internal_server()
        return jsonify(self.res)


class UserPostsApi(Resource):
    res = {}

    @jwt_required
    def get(self, user_id):
        try:
            posts = Post.objects()
            data = []
            for post in posts:
                if str(post.owner.user) == str(user_id):
                    data.append(resCon.convert_object_to_dict(post))
            return jsonify(data)
        except Exception:
            self.res = response.internal_server()
        return jsonify(self.res)


class ImagesRetrievalApi(Resource):
    res = {}

    def get(self, post_id, image_id):
        try:
            post = Post.objects.get(id=post_id)
            image = post.images[image_id]
            image_read = image.read()
            content_type = image.content_type
            return Response(image_read, content_type=content_type)
        except Exception:
            raise Exception
            self.res = response.internal_server()
        return jsonify(self.res)


class VideoRetrievalApi(Resource):
    res = {}

    def get(self, post_id):
        try:
            post = Post.objects.get(id=post_id)
            video = post.video.read()
            content_type = post.video.content_type
            return Response(video, content_type=content_type)
        except Exception:
            self.res = response.internal_server()
        return jsonify(self.res)


class ReportPostApi(Resource):
    pass


class GetNewItemApi(Resource):
    pass
