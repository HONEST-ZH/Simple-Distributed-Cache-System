import flask
from flask import request
server = flask.Flask(__name__)
cache = {'hello':114,'bye':514}
'''
@server.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
'''
@server.route("/all")
def server_see_all():
    return cache
@server.post("/")
def server_write():
    '''
    if request.is_json:
        try:
            data = request.json
            print(data)
        except Exception as e:
            print('error during parsing')
            return '-1'
    else:
        print("not json")
        return '-2'
    '''
    data = request.data
    print(data)
    #cache.update(data)
    return ''
@server.get("/<key>")
def server_read(key):
    if key in cache:
        content = cache[key]
        n_kv = {}
        n_kv[key] = content
        return n_kv, 200
    else:
        return '', 404
@server.delete("/<key>")
def server_delete(key):
    global cache
    if key in cache:
        del cache[key]
        return '1', 200
    else:
        return '0', 200