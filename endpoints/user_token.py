from flask import Flask, json
from flask_restful import reqparse, abort, Api, Resource, inputs
from database import db
from models import UserTokens
from loguru import logger

import sys
sys.path.insert(0, "..")

class UserTokenJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UserTokens):
            json_str = {
                    "token": obj.token,
                    "user_id": obj.user_id
                    }
            return json_str

         # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class UserTokenEndpoint(Resource):
    """
    request endpoint for ULTRA to handle requesting oresat passes.
    """

    def get(self):
        # type: () -> str
        """
        Return associated user to the request token.

        request_token : str
            Request unique token.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("request_token", type=inputs.regex('^\w{1,25}$'), required=True, location="json") #length(user_uid) shouldn't > 25 chars
        args = parser.parse_args()
        requests = []

        try:
            requests = db.session.query(UserTokens)\
                        .with_lockmode('read') \
                        .filter(UserTokens.token == args["request_token"])\
                        .all()
        except Exception as e:
            logger.error(e)
            logger.error("Error fetching token '{}'".format(args["request_token"]))
            return {"Error" : "No user token or invalid request token "}, 400

        return json.dumps(requests, cls=UserTokenJsonEncoder)

    def post(self):
        # type: () -> str, int
        """
        Makes a new request token for a user.

        Returns
        -------
        str
            New UserToken data as a JSON or a error message.
        int
            error code
        """

        parser = reqparse.RequestParser()
        parser.add_argument("request_token", type=inputs.regex('^\w{1,25}$'), required=True, location="json")
        parser.add_argument("user_id", type=inputs.regex('^\w{1,35}$'), required=True, location="json")
        args = parser.parse_args()

        try:
            new_user_token = UserTokens(
                    token = args["request_token"],
                    user_id = args["user_id"]
            )

            db.session.add(new_user_token)
            db.session.commit()

        except:
            db.session.rollback()
        return {
                "message": "New UserToken submitted.",
                "user_id": args["user_id"]
                }
