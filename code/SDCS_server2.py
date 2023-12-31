import flask
from flask import request,json
from concurrent import futures
import grpc
import SDCS_pb2
import SDCS_pb2_grpc
import threading
import hashlib
server = flask.Flask(__name__)#实例化Flask服务器
cache = {'muli':114,'momuli':514}#预先为内存写入数据，便于检测
selfnum = 2  # 本节点的序号
#####################服务器内部的rpc操作(基于gRPC)####################
###rpc的服务器端：从SDCS_pb2_grpc的SDCSServicer中创建一个子类，重写其方法。###
class SDCSServicer(SDCS_pb2_grpc.SDCSServicer):
    '''
    响应其他的节点的查找请求
    函数输入（请求）是SDCS_pb2中的Key类型，和未用到的 unused_context
    函数输出（回复）是SDCS_pb2中的Data类型
    '''
    def finddata(self, request: SDCS_pb2.Key, unused_context
                 )-> SDCS_pb2.Data:
        key = request.key
        if key in cache:#当前节点有
            value = cache[key]
            Data = SDCS_pb2.Data(data = str(value))
            return Data
        else:#当前节点没有
            Data = SDCS_pb2.Data(data ='')
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
        cache.update(json.loads(data))
        State = SDCS_pb2.State(state = 1)
        return State
###开启rpc服务器###
def grpc_serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SDCS_pb2_grpc.add_SDCSServicer_to_server(SDCSServicer(), server)
    server.add_insecure_port("sdcs_server2:5000")#本节点的grpc服务器地址和端口号
    server.start()
    server.wait_for_termination()
###rpc的客户端：从SDCS_pb2_grpc的SDCSStub中实例化一个stub。###
channel0 = grpc.insecure_channel('sdcs_server0:5000')#节点0存根
stub0 = SDCS_pb2_grpc.SDCSStub(channel0)
channel1 = grpc.insecure_channel('sdcs_server1:5000')#节点1存根
stub1 = SDCS_pb2_grpc.SDCSStub(channel1)
channel2 = grpc.insecure_channel('sdcs_server2:5000')#节点2存根
stub2 = SDCS_pb2_grpc.SDCSStub(channel2)
stub = [stub0, stub1, stub2]#存根列表

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
        hash = hashlib.md5()
        hash.update(key.encode("utf-8"))
        res = hash.hexdigest()
        res = int(res,16)
        node_num = res%3
        print(node_num)
    if node_num == selfnum:
        cache.update(data)
        return ''
    Data = SDCS_pb2.Data(data = json.dumps(data))
    if node_num == 0:
        State = stub[0].writedata(Data)
    if node_num == 1:
        State = stub[1].writedata(Data)
    if node_num == 2:
        State = stub[2].writedata(Data)
    state = State.state
    return ''
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
        for i in range(0,3):
            if i == selfnum:
                continue
            _stub = stub[i]
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
        for i in range(0, 3):
            if i == selfnum:
                continue
            _stub = stub[i]
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
#开启flask服务器
def flask_serve():
    server.run(host='0.0.0.0', port='8000')
    # 127.0.0.1只接受容器内的本地访问，使用0.0.0.0向容器外开放8000端口
    # 访问时，最终实现的是从宿主机的IP地址的9527端口访问，由容器实现映射
if __name__ == "__main__":
    # 创建两个线程对象
    grpc_server_thread = threading.Thread(target=grpc_serve)
    flask_server_thread = threading.Thread(target=flask_serve)
    # 启动两个线程
    grpc_server_thread.start()  # 开启grpc服务器
    flask_server_thread.start()  # 开启flask服务器
    # 等待线程结束
    grpc_server_thread.join()
    flask_server_thread.join()




