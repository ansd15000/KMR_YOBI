FROM python:3.8.9
WORKDIR /root/server
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        nginx \
        apt-utils \
        ca-certificates \
        software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# ============ pip install ============
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install flask flask_restx boto3 simplejson networkx==2.3 gevent gunicorn -i https://opentuna.cn/pypi/web/simple

# ============ aws-cli 2 ============
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm -rf aws
RUN rm -rf awscliv2.zip

ARG AWS_DEFAULT_REGION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_ACCESS_KEY_ID ${AWS_ACCESS_KEY_ID}
ENV AWS_DEFAULT_REGION ${AWS_DEFAULT_REGION}
ENV AWS_SECRET_ACCESS_KEY ${AWS_SECRET_ACCESS_KEY}
RUN echo ${AWS_DEFAULT_REGION}
RUN echo ${AWS_ACCESS_KEY_ID}
RUN echo ${AWS_SECRET_ACCESS_KEY}

# ============ for flask server ============
RUN mkdir /root/server/models
RUN mkdir /root/server/work

COPY utils.py     /root/server/
COPY predictor.py /root/server/
COPY serve.py     /root/server/
COPY wsgi.py      /root/server/
COPY container_ingredient.py     /root/server/models/

# ============ for nginx ============
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log
COPY nginx.conf /etc/nginx/

ENTRYPOINT cp -R `ls . | grep -v work` work && cp /etc/nginx/nginx.conf ./work && python serve.py
EXPOSE 5000

# 우분투 패키지 설명
# apt-utils 
#     - 리눅스 기반 os에서 패키지 구성 관련설정을 저장해두어 인스톨 시간을 단축하는 기능을하는 debconf를 사용시 필요

# ca-certificates
#     - 기본적으로 Curl은 https의 ssl 인증서를 검증하는데, 인증기관의 인증서가 목록에 없거나 모르는 기관의 검증시 에러를 반환한다.
#     - 확인 불가능한 ssl 인증서를 수동으로 인증시키기 위해 우분투에서 사용하는 패키지

# libgl1-mesa-glx
#     - openGL 과 유사한 그래픽 렌더링 가속화 라이브러리. 해당 서비스엔 사용하지 않는다.

# software-properties-common
#     - 기본 우분투 패키지 리포지터리에 없는 패키지 설치를 위해 저장소를 추가하는 명령어가 에러날때 적용함

# flask_restx : RestAPI 요청 클래스화
# apscheduler : 특정시간에 따라 로직수행을 위한 스케줄러 라이브러리
# simplejson : Decimal 타입 반환값 인코딩을 위함
# boto3 : aws 서비스 활용을 위한 라이브러리
# gevent : 비동기 관련 라이브러리
# networkx==2.3 : 네트워크 구조 시각화
# soynlp pandas numpy norm : 코사인 유사도를 위해 사용하는 라이브러리
# gunicorn -i https://opentuna.cn/pypi/web/simple : WSGI 서버 운영을 위한 라이브러리