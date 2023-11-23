import flask
from flask import request
from concurrent import futures
import grpc
import SDCS_pb2
import SDCS_pb2_grpc
server = flask.Flask(__name__)#实例化Flask服务器
cache = {'hello':114,'bye':514}#预先为内存写入数据，便于检测

#####################服务器内部的rpc操作(基于gRPC)####################
###rpc的服务器端：从SDCS_pb2_grpc的SDCSServicer中创建一个子类，重写其方法。###
class SDCSServicer(SDCS_pb2_grpc.SDCSServicer):
    '''
    响应其他的节点的查找请求
    函数输入（请求）是SDCS_pb2中的Key类型，和未用到的 unused_context
    函数输出（回复）是SDCS_pb2中的Data类型
    '''
    def finddata(self, request:SDCS_pb2.Key, unused_context
                 )->SDCS_pb2.Data:
        key = request.key
        if key in cache:#当前节点有
            value = cache[key]
            dict = {key,value}
            Data = SDCS_pb2.Data(data = str(dict))
            return Data
        else:#当前节点没有
            Data = SDCS_pb2.Data(data = '')
            return Data
    '''
    响应其他的节点的删除请求
    函数输入（请求）是SDCS_pb2中的Key类型，和未用到的 unused_context
    函数输出（回复）是SDCS_pb2中的State类型
    '''
    def deletedata(self, request: SDCS_pb2.Key, unused_context
                 ) -> SDCS_pb2.State:
        key = request.key
        if key in cache:#当前节点有
            cache.pop(key)
            State = SDCS_pb2.State(state = 1)
            return State
        else:#当前节点没有
            State = SDCS_pb2.State(state = 0)
            return State
    '''
        响应其他的节点的写入请求
        函数输入（请求）是SDCS_pb2中的Data类型，和未用到的 unused_context
        函数输出（回复）是SDCS_pb2中的State类型
    '''
    def writedata(self, request: SDCS_pb2.Data, unused_context
                   ) -> SDCS_pb2.State:
        data = request.data
        cache.update(data)
        State = SDCS_pb2.State(state = 1)
        return State
###开启rpc服务器###
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SDCS_pb2_grpc.add_SDCSServicer_to_server(SDCSServicer(), server)
    server.add_insecure_port("127.0.0.1:5000")#本节点的grpc服务器地址和端口号
    server.start()
    server.wait_for_termination()

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
    data = request.get_json()
    for key in data:
        res = hash(key)
        node_num = res%3
    if node_num == 0:
        cache.update(data)
        return ''
    Data = SDCS_pb2.Data(data = data)
    if node_num == 1:
        stub[1].writedata(Data)
    if node_num == 2:
        stub[2].writedata(Data)
#客户端从服务器获得数据
@server.get("/<key>")
def server_read(key):
    n_kv = {}
    if key in cache:#本地查找
        content = cache[key]
        n_kv[key] = content
        return n_kv, 200
    else:#其他节点查找，调用rpc
        Key = SDCS_pb2.Key(key = key)
        for i in (0,3):
            if i == selfnum:
                continue
            _stub = stub(i)
            Data = _stub.finddata(Key)
            data = Data.data
            if data != '':#找到一个其他节点拥有key的数据
                n_kv[key] = data
                return n_kv, 200
            else:#当前节点没有，找下一个
                continue
        return '', 404#都没有返回空
#客户端从服务器删除数据
@server.delete("/<key>")
def server_delete(key):
    if key in cache:#本地删除
        cache.pop(key)
        return '1', 200
    else:
        Key = SDCS_pb2.Key(key=key)
        for i in (0, 3):
            if i == selfnum:
                continue
            _stub = stub(i)
            State = _stub.deletedata(Key)
            state = State.state
            if state:#找到一个删除了的节点
                return '1', 200
            else:#当前节点没有，找下一个
                continue
        return '0', 200#都没有返回0个删除
#客户端从服务器获得所有数据目录
@server.route("/all")
def server_see_all():
    return cache

if __name__ == "__main__":
    #开启flask服务器
    server.run(host ='127.0.0.1',port = '9527')
    #开启grpc服务器
    server()
    ###rpc的客户端：从SDCS_pb2_grpc的SDCSStub中实例化一个stub。###
    channel0 = grpc.insecure_channel('127.0.0.1:5001')#节点0存根
    stub0 = SDCS_pb2_grpc.SDCSStub(channel0)
    channel1 = grpc.insecure_channel('127.0.0.1:5001')#节点1存根
    stub1 = SDCS_pb2_grpc.SDCSStub(channel1)
    channel2 = grpc.insecure_channel('127.0.0.1:5002')#节点2存根
    stub2 = SDCS_pb2_grpc.SDCSStub(channel2)
    stub = [stub0, stub1, stub2]#存根列表
    selfnum = 0#本节点的序号

