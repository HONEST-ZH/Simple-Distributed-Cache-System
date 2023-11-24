FROM ubuntu:20.04
WORKDIR /sdcs
#复制镜像所需的文件：SDCS.proto、SDCS_server0.py、SDCS_server1.py、SDCS_server2.pyrequirements.txt
COPY /code  ./

#更新apt,下载python,更新pip,换pip的镜像源
#安装virtualenv,创建虚拟环境,激活虚拟环境
#从requirements.txt下载依赖
#从SDCS.proto文件生成SDCS_pb2.py和SDCS_pb2_grpc.py
#运行SDCS_server0.py、SDCS_server1.py、SDCS_server2.py
RUN apt update \
&& apt install python3.9 \
&& python -m pip install --upgrade pip \
&& python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
&& python -m pip install virtualenv \
RUN virtualenv venv \
&& source venv/bin/activate \
&& python -m pip install -r requirements.txt \
&& python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. SDCS.proto \
&& python SDCS_server0.py \
&& python SDCS_server1.py \
&& python SDCS_server2.py

# 暴露5000端口
EXPOSE 9527 9528 9529