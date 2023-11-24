FROM ubuntu:20.04
WORKDIR /sdcs
#复制镜像所需的文件：SDCS.proto、SDCS_server0.py、SDCS_server1.py、SDCS_server2.pyrequirements.txt
COPY SDCS.proto /sdcs/ && requirements.txt /sdcs/
COPY SDCS_server0.py /sdcs/
COPY SDCS_server1.py /sdcs/
COPY SDCS_server2.py /sdcs/

RUN apt updata
    #更新apt
  &&apt install python3.9
    #下载python
  &&python -m pip install --upgrade pip
    #更新pip
  &&python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    #换pip的镜像源
  &&python -m pip install virtualenv
    #安装virtualenv
  &&virtualenv venv
    #创建虚拟环境
  &&source venv/bin/activate
    #激活虚拟环境
  &&python -m pip install -r requirements.txt
    #从requirements.txt下载依赖
  &&python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. SDCS.proto
    #从SDCS.proto文件生成SDCS_pb2.py和SDCS_pb2_grpc.py
  &&python SDCS_server0.py
  &&python SDCS_server1.py
  &&python SDCS_server2.py
    #运行SDCS_server0.py、SDCS_server1.py、SDCS_server2.py

# 暴露5000端口
EXPOSE 9527 && 9528 && 9529