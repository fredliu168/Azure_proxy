
# Azure OpenAi 接口代理开发

[Azure_proxy](https://github.com/fredliu168/Azure_proxy)项目是一个代理，用于将ChatGPT请求转发到Azure OpenAi。

如果直接使用[ChatGPT-Next-Web](https://github.com/Yidadaa/ChatGPT-Next-Web),直接配置azure相关信息到ChatGPT-Next-Web就可以使用了。

如果需要自己开发Chat对接Azure OpenAi接口，可以参考本仓库。

## 一、开发

用Conda设置虚拟环境azure_proxy：

```
conda create -y -n azure_proxy  python=3.10

conda activate azure_proxy

pip install -r requirements.txt # 安装依赖

```

## 二、接口部署发布

###（1）使用python环境运行

gunicorn 是一个用于运行 WSGI（Web Server Gateway Interface）应用程序的HTTP服务器。WSGI是Python Web应用程序和Web服务器之间的标准接口，允许你使用不同的Web服务器来运行你的Python Web应用程序。

以下是 gunicorn 的一些主要特点和优势：

> 高性能： gunicorn 是一个高性能的HTTP服务器，设计用于处理高并发的请求。它使用异步的工作模型，允许同时处理多个请求。

> 支持多种工作模型： gunicorn 支持多种工作模型，包括预派（preforking）、异步（async）、gevent、tornado等。你可以根据应用程序的特性选择最适合的工作模型。

>  易于使用： gunicorn 非常易于使用，只需简单的命令就可以启动你的Web应用程序。它还提供了丰富的命令行选项和配置选项，以满足不同需求。

>  自动处理工作进程： gunicorn 可以自动处理工作进程的生成和管理。你只需指定要运行的工作进程数，gunicorn 将自动为你生成并管理这些进程。

>  支持热重载： gunicorn 支持热重载，允许你在不停止服务的情况下重新加载应用程序代码。这对于部署新版本的应用程序时非常有用。

>  集成性良好： 由于 gunicorn 符合WSGI标准，因此它能够与大多数符合WSGI标准的Python Web框架（如Flask、Django等）良好集成。

```
pip install -r requirements.txt # 安装依赖

pip install gunicorn

gunicorn -w 4 -b 0.0.0.0 'azure_openai:app'

```
### （2）用Docker部署安装

#### 镜像打包：

##### 2.1、使用Docker打包运行

使用**python:3.10.13-slim**作为基础镜像，它是一个基于 Python 3.10 的官方 Docker 镜像，使用的是 Debian 的 Slim 版本。这个镜像旨在提供一个相对轻量级的 Python 运行环境，适用于构建小型和精简的 Docker 镜像，大小仅有普通python镜像的10%，大约一百多M。

详细可以看Dockerfile.tmp文件,把Dockerfile.tmp文件放到azure_proxy目录下，改成把Dockerfile：


```
docker build -t azure_openai_proxy .

```
运行接口

```

docker run  -p 8000:8000 azure_openai_proxy
```

##### 2.2、使用docker-compose 打包运行

创建**docker-compose.yml**文件，内容如下，把仓库中的**docker-compose.yml.tmp**改成docker-compose.yml：

```yml
version: '3.1'

services:
  azure_proxy:
    build:
      context: ./
    ports:
      - "8000:8000" # 端口映射
    volumes:
      - ./:/var/azure_openai/workspace/ # 映射程序文件到宿主机
    environment:
      AZURE_OPENAI_API_KEY: <AZURE_KEY>
      AZURE_ENDPOINT: <AZURE_ENDPOINT>
      AZURE_OPENAI_API_VERSION: <AZURE_API_VERSION>
      AUTH_KEY: <AUTH_KEY> # 自定义授权Key

```

> AZURE_OPENAI_API_KEY: 微软dev的API密钥，可以在微软开发者中心申请
> AZURE_ENDPOINT: 微软的API地址，可以在微软开发者中心申请
> AZURE_OPENAI_API_VERSION: 微软的API版本，可以在微软开发者中心申请
> AUTH_KEY: 自己设置的访问密钥，避免被别人访问

```cmd

docker-compose up

docker-compose up --build #强制重新生成 

```
 
##### 2.3、部署

导出azure_openai_proxy镜像文件azure_openai_proxy.tar

```
docker save -o azure_openai_proxy.tar azure_openai_proxy

```

服务器上传azure_openai_proxy.tar，加载镜像

```
docker load -i ./azure_openai_proxy.tar
```

启动接口容器：

```
docker run -p 8088:8000 azure_openai_proxy 
```
或者
```
docker-compose up -d
```

### 三、接口测试

使用Postman测试接口
```
/POST http://192.168.50.108:8088/v1/chat/completions
```
header: 
```
Authorization Bearer <AUTH_KEY> # 自定义授权Key
Proxy-src azure
```
Body:
```
{
    "model":"gpt-35-turbo",
    "temperature":0.7,
    "stream":true, # 是否使用流输出
    "messages":[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你是谁？"}
]
}

```

### 四、Nginx配置

配合ChatWeb使用，需要配置Nginx，在/etc/nginx/nginx.conf中添加如下配置：

azure_proxy.conf

```conf

server {
    listen 8001;
    server_name localhost;
    location / {
       root /home/www/chatgpt-web;
       index  index.html index.htm;  
    }

    location /api/azure_api/{
                proxy_pass http://127.0.0.1:8088/;
	            proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
    }
}
```

配置后执行

```
nginx -t

```
如果没有显示错误，执行如下命令，重新加载nginx配置文件

```
nginx -s reload
```

### 五、可能遇到的错误

（1）、执行docker compose 时提示：http: invalid Host header 错误

原因：

服务器使用snap安装的docker。

解决办法：

```
sudo snap refresh docker --channel=latest/edge
```
安装新版本docker后解决该问题
