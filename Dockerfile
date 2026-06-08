# 1. 뼈대: 파이썬 3.9 버전 사용 (오렌지와 호환성 최고)
FROM python:3.9-slim

# 2. 부품: 오렌지3가 계속 칭얼대던 리눅스 화면 부품 강제 설치
RUN apt-get update && apt-get install -y libglib2.0-0 libgl1-mesa-glx libegl1

# 3. 작업 공간 세팅
WORKDIR /app
COPY . .

# 4. 내 파일들(requirements.txt) 설치
RUN pip install -r requirements.txt

# 5. 스트림릿 서버 실행 포트 열기
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
