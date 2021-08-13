from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import pandas as pd
import ast
from test import get_album_info
import json

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

class Individual(Resource):
    def get(self, album_id):
        with open('collection.json', 'r') as myfile:
            read_file = myfile.read()
        data = [i for i in json.loads(read_file) if i["album_id"] == album_id]
        if not data:
            with open('wishlist.json', 'r') as myfile:
                read_file = myfile.read()
            data = [i for i in json.loads(read_file) if i["album_id"] == album_id]
            if not data:
                return {'message': "No album found"}, 404
        print(data)
        return {'data': data}, 200
        
class Albums(Resource):
    def get(self):
        with open('collection.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)
        print(data)
        return {'data': data}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('album_id', required=True)
        parser.add_argument('artist', required=True)
        parser.add_argument('title', required=True)
        parser.add_argument('year', required=True)
        parser.add_argument('genre', required=True, action='append')
        parser.add_argument('tracklist', required=True, action='append')
        parser.add_argument('imageLink', required=True)

        args = parser.parse_args()

        with open('collection.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)

        tracklist_array = [ast.literal_eval(i) for i in args["tracklist"]]

        if args['album_id'] in [i['album_id'] for i in data]:
            return {
                'message': f"'{args['album_id']}' already exists."
            }, 401
        else:
            new_album = {'album_id': args['album_id'], 'artist': args['artist'], 'title': args['title'], 'year': args['year'], 'genre': args['genre'], 'tracklist': tracklist_array, 'imageLink': args['imageLink'], 'isWishlist': 'false'}
            data.append(new_album)
            with open('collection.json', 'w') as collection:
                json.dump(data, collection)
            return {'data': data}, 200

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('album_id', required=True)
        args = parser.parse_args()
        print(args["album_id"])
        with open('collection.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)

        if args['album_id'] in [i['album_id'] for i in data]:
            new_data = [i for i in data if i["album_id"] != args['album_id']]
            with open('collection.json', 'w') as collection:
                json.dump(new_data, collection)
            return {'data': new_data}, 200
        else:
            return {
                'message': f"'{args['album_id']}' does not exist."
            }, 404

class Search(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        args = parser.parse_args()

        full_album_list = get_album_info(args['query'])

        #data.tracklist = [[[i.position, i.title, i.duration] for i in j.tracklist.songs] for j in full_album_list]
        for data in full_album_list:
           data.tracklist = [[i.position, i.title, i.duration] for i in data.tracklist.songs]
        new_albums = [{'album_id': data.album_id, 'artist': data.artist, 'title': data.title, 'year': data.year, 'genre': data.genre, 'tracklist': data.tracklist, 'imageLink': data.imageLink} for data in full_album_list]
        return {'data': new_albums}, 200
        
class Wishlist(Resource):
    def get(self):
        with open('wishlist.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)
        print(data)
        return {'data': data}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('album_id', required=True)
        parser.add_argument('artist', required=True)
        parser.add_argument('title', required=True)
        parser.add_argument('year', required=True)
        parser.add_argument('genre', required=True, action='append')
        parser.add_argument('tracklist', required=True, action='append')
        parser.add_argument('imageLink', required=True)

        args = parser.parse_args()

        with open('wishlist.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)

        tracklist_array = [ast.literal_eval(i) for i in args["tracklist"]]

        if args['album_id'] in [i['album_id'] for i in data]:
            return {
                'message': f"'{args['album_id']}' already exists."
            }, 401
        else:
            new_album = {'album_id': args['album_id'], 'artist': args['artist'], 'title': args['title'], 'year': args['year'], 'genre': args['genre'], 'tracklist': tracklist_array, 'imageLink': args['imageLink'], 'isWishlist': 'true'}
            data.append(new_album)
            with open('wishlist.json', 'w') as collection:
                json.dump(data, collection)
            return {'data': data}, 200

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('album_id', required=True)
        args = parser.parse_args()
        print(args["album_id"])
        with open('wishlist.json', 'r') as myfile:
            read_file = myfile.read()
        data = json.loads(read_file)

        if args['album_id'] in [i['album_id'] for i in data]:
            new_data = [i for i in data if i["album_id"] != args['album_id']]
            with open('wishlist.json', 'w') as collection:
                json.dump(new_data, collection)
            return {'data': new_data}, 200
        else:
            return {
                'message': f"'{args['album_id']}' does not exist."
            }, 404

api.add_resource(Search, '/search')
api.add_resource(Albums, '/albums')
api.add_resource(Wishlist, '/wishlist')
api.add_resource(Individual, '/individual/<album_id>')

if __name__ == '__main__':
    app.run()