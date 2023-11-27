# SDCS
这是一个简单的分布式缓存系统（Simple Distributed Cache System, SDCS）。
本项目是电子科技大学分布式系统的项目作业，仅用于参考。
以下是课程测试脚本的连接，来自于[薛瑞尼老师](https://github.com/ruini-classes/sdcs-testsuit)。

This is a simple distributed cache system(SDCS). This project is a term project for the distributed
system of UESCT and is for reference only. The following is a link to the course test script, 
from teacher [Xue Ruini](https://github.com/ruini-classes/sdcs-testsuit).  

本项目通过python的Flask框架和gRPC方法实现了一个简单的分布式缓存系统。
利用Flask提供的Web接口和gRPC提供的RPC接口，实现了缓存的存储、查询和删除功能。 
最后通过Docker在ubantu 20.04虚拟机中进行了容器化部署。

This project implements a simple distributed cache system through python's Flask 
framework and gRPC method. The cache storage, query and deletion functions are 
implemented using the Web interface provided by Flask and the RPC interface provided by gRPC.
Finally, containerization was deployed in the ubantu 20.04 virtual machine through Docker.
# How to build it
首先进行docker容器的构建。在文件夹/sdcs中打开Linux终端,运行docker compose
建立容器和其所需的镜像。

First build the docker container. Open the Linux terminal in the folder /sdcs and run docker compose
Create the container and its required images.

    sudo docker-compose up

接下来是使用脚本实现SDCS的功能测试。在同一目录下打开另一个linux终端，运行sdcs-test.sh脚本。

The next step is to use scripts to implement functional testing of SDCS. Open another Linux terminal in the same directory and run the sdcs-test.sh script

    ./sdcs-test.sh 3