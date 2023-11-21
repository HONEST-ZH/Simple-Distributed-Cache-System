import flask
server = flask.Flask(__name__)
cache = {'hello':114,'bye':514}
'''
@server.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
'''
@server.route("/sever1/see_all")
def server_see_all():
    return cache
@server.post("/server1/")
def server_write():
    kv = flask.request.json()
    global cache
    cache.update(kv)
@server.get("/server1/<key>")
def server_read(key):
    if key in cache:
        content = cache[key]
        n_kv = {}
        n_kv[key] = content
        return n_kv, 200
    else:
        return '', 404
@server.delete("/server1/<key>")
def server_delete(key):
    global cache
    if key in cache:
        del cache[key]
        return 1,200
    else:
        return 0,200
