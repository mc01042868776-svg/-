import streamlit as st
import pickle
import os
import pandas as pd
import numpy as np
import Orange
from Orange.data import Table

# 웹앱 기본 설정
st.set_page_config(page_title="학과 vs 계열 취업률 비교 시스템", page_icon="📊", layout="centered")

st.title("📊 학과 vs 계열 취업률 상대 비교 시스템")
st.markdown("오렌지3(Orange3)에서 저장한 `major_model.pkcls`와 `field_model.pkcls` 모듈 파일을 직접 읽어와 깃허브(Streamlit Cloud) 서버에서 실시간으로 작동시키는 전용 코드입니다.")

# 1. 2개의 오렌지 모델 로드 (캐싱 적용)
@st.cache_resource
def load_orange_models():
    major_path = "major_model.pkcls"
    field_path = "field_model.pkcls"
    
    if not os.path.exists(major_path) or not os.path.exists(field_path):
        return None, None
        
    with open(major_path, "rb") as f1:
        model_major = pickle.load(f1)
    with open(field_path, "rb") as f2:
        model_field = pickle.load(f2)
        
    return model_major, model_field

model_major, model_field = load_orange_models()

# 파일 누락 시 안내문
if model_major is None or model_field is None:
    st.error("🚨 **모델 파일(.pkcls)을 찾을 수 없습니다!**")
    st.warning("깃허브 저장소(Repository)에 `app.py`와 함께 오렌지에서 추출한 `major_model.pkcls` 및 `field_model.pkcls` 파일이 같은 위치에 업로드되어 있는지 확인해주세요.")
    st.stop()

# 2. 학과 및 계열 매핑 데이터 테이블 세팅 (본인의 데이터셋에 맞게 자유롭게 수정)
major_mapping = {
    "국어국문학과": "인문계열",
    "영어영문학과": "인문계열",
    "경영학과": "사회계열",
    "경제학과": "사회계열",
    "컴퓨터공학과": "공학계열",
    "기계공학과": "공학계열",
    "전자공학과": "공학계열",
    "간호학과": "자연계열",
    "물리학과": "자연계열"
}

st.subheader("⚙️ 예측 조건 입력")

# 사용자 입력 UI
year = st.number_input("공시연도 선택", min_value=2020, max_value=2060, value=2026, step=1)
selected_major = st.selectbox("전공(학과) 선택", list(major_mapping.keys()))
selected_field = major_mapping[selected_major]

st.info(f"💡 **선택된 분석 대상:** {year}년도 | 계열: {selected_field} ➔ 학과: {selected_major}")
st.markdown("---")

# 3. 예측 실행 버튼 클릭 시
if st.button("🎯 깃허브 서버에서 예측 및 상대 비교 실행", use_container_width=True):
    try:
        # 오렌지 데이터 규격 변환 및 예측
        raw_major_data = [[year, selected_major]]
        major_table = Table(model_major.domain, raw_major_data)
        pred_major = model_major(major_table)[0]
        
        raw_field_data = [[year, selected_field]]
        field_table = Table(model_field.domain, raw_field_data)
        pred_field = model_field(field_table)[0]
        
        diff = pred_major - pred_field
        
        # 4. 결과 시각화 메트릭 카드 출력
        st.subheader("📈 실시간 예측 분석 결과")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"🎯 {selected_major} 예상 취업률", value=f"{pred_major:.2f}%")
        with col2:
            st.metric(label=f"🏢 {selected_field} 전체 평균 취업률", value=f"{pred_field:.2f}%", 
                      delta=f"차이: {diff:+.2f}%p", delta_color="inverse" if diff < 0 else "normal")
        
        st.markdown("---")
        
        # 5. 예측 결과 비교 분석 인사이트 제공
        if diff > 0:
            st.success(f"🔥 **상대적 우위:** {selected_major}의 예측 취업률이 소속 계열({selected_field})의 전체 평균보다 **{diff:.2f}%p** 높게 아웃퍼폼할 것으로 예측됩니다. 해당 계열 내에서 취업 경쟁력이 강력한 전공입니다.")
        elif diff < 0:
            st.warning(f"📉 **상대적 열위:** {selected_major}의 예측 취업률이 소속 계열({selected_field})의 전체 평균 대비 **{abs(diff):.2f}%p** 낮을 것으로 예측됩니다. 취업 인프라 보완전략이 요구됩니다.")
        else:
            st.info(f"⚖️ **평균 수렴:** {selected_major}의 예측 취업률이 소속 계열의 평균 통계치와 정확히 일치하는 수준으로 계산되었습니다.")
            
    except Exception as e:
        st.error("🚨 **오렌지 도메인 매핑 에러 발생!**")
        st.markdown(f"**원인:** 오렌지3에서 모델을 학습시킬 당시 `Select Columns` 위젯의 `Features`에 지정했던 변수의 개수나 순서가 현재 코드 내부의 입력 형태와 맞지 않습니다.")
        st.caption(f"시스템 상세 오류 메세지: {e}")
