import flask
from flask import request
import grpc
import SDCS_pb2
import SDCS_pb2_grpc

server = flask.Flask(__name__)#实例化Flask服务器
cache = {'hello':114,'bye':514}#预先为内存写入数据，便于检测

#####################服务器内部的rpc操作(基于gRPC)####################
#rpc的服务器端：从SDCS_pb2_grpc的SDCSServicer中创建一个子类，重写其方法。
class SDCSServicer(SDCS_pb2_grpc.SDCSServicer):
    '''
    响应其他的节点的查找请求
    函数输入（请求）是SDCS_pb2中的Key类型，和未用到的 unused_context
    函数输出（回复）是SDCS_pb2中的Data类型
    '''
    def finddata(self, request:SDCS_pb2.Key, unused_context
                 )->SDCS_pb2.Data:
        key = request.key
        if key in cache:
            value = cache[key]
            dict = {key,value}
            Data = SDCS_pb2.Data(data = str(dict))
            return Data
        else:
            Data = SDCS_pb2.Data(data = '')
            return Data
    '''
    响应其他的节点的查找请求
    函数输入（请求）是SDCS_pb2中的Key类型，和未用到的 unused_context
    函数输出（回复）是SDCS_pb2中的State类型
    '''
    def deletedata(self, request: SDCS_pb2.Key, unused_context
                 ) -> SDCS_pb2.State:
        global cache
        key = request.key
        if key in cache:
            del cache[key]
            State = SDCS_pb2.State(stete = 1)
            return State
        else:
            State = SDCS_pb2.State(stete=0)
            return State
#rpc的客户端：从SDCS_pb2_grpc的SDCSStub中实例化一个stub。
channel = grpc.insecure_channel('127.0.0.1:9527')
stub = SDCS_pb2_grpc.SDCSStub(channel)

#####################面向客户端的HTTP操作（基于flask）####################
#默认显示
@server.get("/")
def hello_world():
    return "<p>Hello, It is simple distributed cache system!</p>"
#客户端向服务器写入数据
@server.post("/")
def server_write():
    '''
    #读取URL成功的检验
    if request.is_json:
        #错误判断，windows,cmd的curl指令有问题导致 request.get_json()获得数据不正确
        try:
            data = request.get_json()
        except Exception as e:
            print('error during parsing')
            return '-1'
        #都正确进行以下步骤
    else:
        print("not json")
        return '-2'
    '''
    global cache
    #TODO：哈希判定写入哪个服务器
    #TODO：向选好的服务器写入KV对
    data = request.get_json()
    print(data)
    cache.update(data)
    return ''

#客户端从服务器获得数据
@server.get("/<key>")
def server_read(key):
    if key in cache:#本地查找
        content = cache[key]
        n_kv = {}
        n_kv[key] = content
        return n_kv, 200
    else:#其他节点查找，调用rpc
        Key = SDCS_pb2.Key(key = key)
        Data = stub.finddata(Key)
        data = Data.data
        if data != '':
            n_kv = {}
            n_kv[key] = data
            return n_kv, 200
        else:
            return '', 404
#客户端从服务器删除数据
@server.delete("/<key>")
def server_delete(key):
    global cache
    if key in cache:
        del cache[key]
        return '1', 200
    else:
        Key = SDCS_pb2.Key(key=key)
        State = stub.deletedata(Key)
        state = State.state
        if state:
            return '1', 200
        else:
            return '0', 200
#客户端从服务器获得所有数据目录
@server.route("/all")
def server_see_all():
    return cache
