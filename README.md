### CreateTable.py
테이블 이름, 파티션키, 정렬키 (선택) 으로 DynamoDB 테이블 생성

### add_SecondaryKey.py
세컨더리 인덱스를 추가하여 테이블의 쿼리 기능 강화.

### local add recipe.py
크롤링하여 json 파일로 저장된 요리 레시피 디렉토리의 데이터를 DynamoDB에 추가하는 로직

### restful_API 요청정보 정리 최종.xlsx
프론트에서 백엔드로 요청할 주소 정보와 반환 데이터 정보 정리  

---
### 도커파일 빌드 및 이미지 실행 예시

Dockerfile 빌드시 서비스하려는 aws의 계정정보를 활용하기위한 세가지의 인자값을 추가로 선언해주어야 한다.  
docker build -t user:latest --build-arg AWS_DEFAULT_REGION=ap-northeast-2 --build-arg AWS_ACCESS_KEY_ID=^ㅍ^ --build-arg AWS_SECRET_ACCESS_KEY=^ㅠ^ .  


컨테이너 실행시 아래와 같은 형태로 볼륨 마운드를 진행하여 코드 수정사항을 수시로 적용할 수 있도록 한다. 포트는 Dockerfile에 명시하였기에 -P 옵션으로 랜덤으로 주어도 좋다.  
docker run --name user -p 5002:5002 -v $(pwd)/work:/root/server/work user:latest

---
## 선택사항
각 컨테이너마다 빌드하는것이 번거롭고 귀찮다면 docker-compose.yml 을 활용하여도 괜찮다.  
만약 docker-compose 로 빌드시 aws 계정정보는 꼭 편집해서 추가 해주어야 한다!  

---
# 재료 테이블
BaseImage: python 3.8.9  
Back-end : Docker, Gunicorn을 활용한 WSGI 서버 (Flask + Nginx)  
Service : 재료의 유통기한 정보를 조회, 저장, 수정, 삭제.  
사용자가 보유한 재료의 유통기한과 신선도 정보를 저장, 조회, 수정, 삭제  
PORT : 5000

---
# 레시피 테이블
BaseImage: python 3.8.9  
Back-end : Docker, Gunicorn을 활용한 WSGI 서버 (Flask + Nginx)  
Service : 이미지 분석 후 인식된 재료들로 추천 알고리즘 진행.  
가장 유사도가 높은 음식 이름들로 DynamoDB에서 다시 검색하여 클라이언트로 전달  
PORT : 5001

---
# 사용자 테이블
BaseImage: python 3.8.9  
Back-end : Docker, Gunicorn을 활용한 WSGI 서버 (Flask + Nginx)  
Service : 사용자 정보를 조회, 저장, 수정, 삭제, 회원가입, 아이디 중복확인  
PORT : 5002
