# 1. 뼈대: 도구함이 꽉 찬 파이썬 3.9 정식 버전 사용 (slim 아님!)
FROM python:3.9

# 2. 부품: 리눅스 최신 버전에 맞는 정확한 화면 부품 설치
RUN apt-get update && apt-get install -y libglib2.0-0 libgl1 libsm6 libxrender1 libxext6

# 3. 작업 공간 세팅
WORKDIR /app
COPY . .

# 4. 파이썬 설치 도구 최신화 및 라이브러리 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. 스트림릿 서버 실행
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
