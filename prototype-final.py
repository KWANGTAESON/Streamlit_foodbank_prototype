# 라이브러리
import pandas as pd
import streamlit as st
import numpy as np
# import plotly.express as px
import os
from urllib.parse import quote
from streamlit_folium import st_folium
import folium
from folium import IFrame
import seaborn as sns
import folium
import matplotlib.pyplot as plt
from datetime import date
from streamlit_folium import folium_static
import re
import joblib

# 시각화 한글폰트 설정
plt.rc('font', family='Malgun Gothic')
sns.set(font="Malgun Gothic",#"NanumGothicCoding", 
rc={"axes.unicode_minus":False}, # 마이너스 부호 깨짐 현상 해결
style='darkgrid')


class MyClass:
    def __init__(self):
        pass
    
    # 재고 수량 함수 1
    def inventory(self, code_name):
        test = pd.read_csv('기부물품대분류(가짜데이터).csv', encoding='cp949')
        test.set_index(test.columns[0], inplace=True)
        return test.loc[code_name, '재고수량']

    # 재고 수량 계산 함수 2
    # 계산은 가능하지만 새로운 데이터가 추가되었을 때는 그 파일을 사용하지 못하고 다른 새로운 파일을 사용해야한다.
    # ---> 어떻게 해결해야하나? 방법을 모르겠네
    # 근데 저절로 추가된 것만 빠지네?
    def inventory_cal(self, code_name):
        test = pd.read_csv('기부물품대분류(가짜데이터).csv', encoding='cp949')
        user_data = pd.read_excel('output3.xlsx')

        user_data_group = user_data.groupby('기부물품대분류코드', as_index=False)['수량'].sum()
        # 사용자 데이터에서 기부 품목 코드와 수량 추출
        user_data_item_code = user_data_group['기부물품대분류코드']
        user_data_quantity = user_data_group['수량']

        # 테스트 데이터에서 기부 품목 코드와 수량 추출
        test_item_code = test['기부물품대분류코드']
        test_quantity = test['재고수량']

        # 기부 품목 코드가 일치하는 경우에만 수량 뺄셈 연산 수행
        result = test_quantity.copy()
        for i in range(len(user_data_quantity)):
            if user_data_item_code[i] in list(test_item_code):
                idx = test_item_code[test_item_code.str.contains(user_data_item_code[i])].index[0]
                result[idx] -= user_data_quantity[i]

        test['재고수량'] = result
        result_test = test.set_index(test.columns[0])
        test_val = result_test.loc[code_name, '재고수량']
        test.drop('장부금액', axis=1, inplace=True)
        test.to_csv('재고 계산된 기부물품대분류(가짜데이터).csv', index=False, encoding='cp949')
        
        return test_val

    # 기부처 찾기 3
    def donate(self, needs):
        donate_info = pd.read_csv('3.부산기부자정보조회(2016~2021년).csv', encoding='cp949')
        if needs == '신선식품':
            matching = '식품 도,소매업'
        elif needs == '일상용품':
            matching = '즉선판매,제조가공업'
        else:
            matching = '기타'
        donater = donate_info[donate_info['기부사업장종류코드'] == matching]
        donater_list = list(donater['기부자명'].unique())
        return donater_list

    # 부산 기부처 목록 4
    def find_busan_donors(self, search):
        busan_donors = pd.read_csv('부산기부처목록.csv', encoding='cp949')
        return busan_donors[busan_donors['기부자명'].str.contains(search)]

    # 기부처 발굴 5
    def find_new_donors(self, selected_gugun, selected_comp_name):
        find_new = new[(new['표준산업분류명'] == selected_comp_name) & (new['시군구명'] == selected_gugun)][['상호명', '표준산업분류명', '시군구명', '도로명주소','위도', '경도']]
        find_new = find_new.reset_index(drop=True)
        return find_new

#     # 지도 함수 6
#     def find_new_donors_location(self, df):
#         # 라이브러리
#         import folium
#         import webbrowser
#         from folium import IFrame
#         import urllib.parse

#         # 맵 생성
#         map = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=11)

#             # 데이터프레임의 각 위치에 마커 추가
#         for i in df.index:
#             name = df.loc[i, '상호명']
#             gugun = df.loc[i, '시군구명']
#             location = df.loc[i, '도로명주소']
#             cls1 = df.loc[i, '표준산업분류명']

#             # 네이버 검색 결과 링크 생성
#             encoded_name = urllib.parse.quote(name)
#             naver_search_link = f'https://search.naver.com/search.naver?query={encoded_name}&sm=top_hty&fbm=1&ie=utf8'

#             # 팝업 내용 생성
#             popup_content = f'<div style="font-family: Arial, sans-serif; font-size: 14px;"> \
#             상호명 : <a href="{naver_search_link}" target="_blank"> {name}</a><br>{location}</div>'
#             popup = folium.Popup(popup_content, max_width=250)

#             # IFrame을 사용하여 수평으로 표시되도록 팝업 설정
#             popup = folium.Popup(IFrame(html=popup_content, width=200, height=80))

#             # 마커 생성 및 팝업 추가
#             marker = folium.Marker(
#                     location=[df.loc[i, '위도'], df.loc[i, '경도']],
#                     icon=folium.Icon(icon='home', color='red'),
#                     popup=popup
#             )
#             marker.add_to(map)


#         # 출력 화면에 맵 열기
#         return folium_static(map)
    # 지도 함수 6
    def find_new_donors_location(self, df):
        # 라이브러리
        import folium
        import webbrowser
        from folium import IFrame
        import urllib.parse

        # 지도 객체 생성
        map = folium.Map(location=[map_df[(map_df['구군명'] == selected_gugun) & (map_df['구분'] == '푸드마켓')]['위도'], 
                                   map_df[(map_df['구군명'] == selected_gugun) & (map_df['구분'] == '푸드마켓')]['경도']], 
                                   zoom_start=13)
        
        popup_content2 = f'부산 {selected_gugun} 푸드마켓'
        # 시작 좌표 아이콘 추가
        folium.Marker(location=[map_df[(map_df['구군명'] == selected_gugun) & (map_df['구분'] == '푸드마켓')]['위도'], 
                                map_df[(map_df['구군명'] == selected_gugun) & (map_df['구분'] == '푸드마켓')]['경도']], 
                                icon=folium.Icon(color='blue'),
                                popup= folium.Popup(popup_content2, max_width=250)).add_to(map)

            # 데이터프레임의 각 위치에 마커 추가
        for i in df.index:
            name = df.loc[i, '상호명']
            gugun = df.loc[i, '시군구명']
            location = df.loc[i, '도로명주소']
            cls1 = df.loc[i, '표준산업분류명']

            # 네이버 검색 결과 링크 생성
            encoded_name = urllib.parse.quote(name)
            naver_search_link = f'https://search.naver.com/search.naver?query={encoded_name}&sm=top_hty&fbm=1&ie=utf8'

            # 팝업 내용 생성
            popup_content = f'<div style="font-family: Arial, sans-serif; font-size: 14px;"> \
            상호명 : <a href="{naver_search_link}" target="_blank"> {name}</a><br>{location}</div>'
            popup = folium.Popup(popup_content, max_width=250)

            # IFrame을 사용하여 수평으로 표시되도록 팝업 설정
            popup = folium.Popup(IFrame(html=popup_content, width=200, height=80))

            # 마커 생성 및 팝업 추가
            marker = folium.Marker(
                    location=[df.loc[i, '위도'], df.loc[i, '경도']],
                    icon=folium.Icon(icon='home', color='red'),
                    popup=popup
            )
            marker.add_to(map)


        # 출력 화면에 맵 열기
        return folium_static(map)

    # 구 별 최다 기부처 그래프 Top20 함수 7
    def grouping_gugun_graph20(self, gu):


        top20 = group_gugun_data1[group_gugun_data1['통합시군구코드'] == gu].sort_values('기부건수', ascending=False).head(20)
        fig = plt.figure()
        fig.set_dpi(300) # DPI 값을 조정하여 레티나 품질로 설정
        sns.barplot(data=top20, x='기부건수', y='기부자명')
        plt.title('기부건수 별')
        plt.show()

        return st.pyplot(fig)


    # 금액 별 그래프 함수 8
    def grouping_gugun_money_graph20(self, gu):

        top20 = group_gugun_data2[group_gugun_data2['통합시군구코드'] == gu].sort_values('기부금액', ascending=False).head(20)
        fig = plt.figure()
        fig.set_dpi(300) # DPI 값을 조정하여 레티나 품질로 설정
        sns.barplot(data=top20, x='기부금액', y='기부자명')
        plt.title('기부금액 별')
        plt.show()

        return st.pyplot(fig)
    
    # 리턴 변수 : X, Y
    def preprocessing(self, data):
        target = '사업장유형'
        feature = ['제공금액','장부수량','이관금액','기부자수']
        Y = data[target]
        X = data[feature]

        return X, Y


    def predict_bussiness(self, data):

        sym_list = ['임의', '당연']
        test_df = pd.DataFrame(data)
        test_x, test_y = p.preprocessing(test_df)
        model_lgb = joblib.load('lgb_pca2_model.pkl')
        pred = model_lgb.predict(test_x)
        return sym_list[pred[0]]

#     def predict_map(self):
#         map_df = pd.read_csv('부산광역시_푸드뱅크 및 푸드마켓 현황_20230201.csv', encoding='cp949')

#         # 맵 생성
#         map = folium.Map(location=[map_df['위도'].mean(), map_df['경도'].mean()], zoom_start=11)

#         # 데이터프레임의 각 위치에 마커 추가
#         for i in map_df.index:
#             name =map_df.loc[i, '구분']
#             gugun = map_df.loc[i, '구군명']
#             location = map_df.loc[i, '소재지']
#             tel = map_df.loc[i, '연락처']
#             team = map_df.loc[i, '운영단체명']

#             # 팝업 내용 지정(폰트 설정 등..)
#             popup_content = f'<div style="font-family: Arial, sans-serif; font-size: 14px;"> \
#             [{gugun} {name}]<br>{location}<br>Tel. {tel}</div>'

#             # IFrame을 사용하여 수평으로 표시되도록 팝업 설정
#             popup = folium.Popup(IFrame(html=popup_content, width=200, height=80))

#             # 'bank'와 'market'에 대한 아이콘 정의
#             bank_icon = folium.CustomIcon(icon_image='이미지파일모음/bank.png', icon_size=(25, 25))
#             market_icon = folium.CustomIcon(icon_image='이미지파일모음/market.png', icon_size=(15, 15))
#             center_icon = folium.CustomIcon(icon_image='이미지파일모음/distribution-center.png', icon_size=(15, 15))


#             if bs_name[:2] in gugun:
#                 bank_icon = folium.CustomIcon(icon_image='이미지파일모음/bank.png', icon_size=(45, 45))
#                 market_icon = folium.CustomIcon(icon_image='이미지파일모음/market.png', icon_size=(45, 45))
#                 center_icon = folium.CustomIcon(icon_image='이미지파일모음/distribution-center.png', icon_size=(45, 45))

#             # 이름에 따라 해당하는 아이콘 선택
#             if '광역푸드뱅크' in team:
#                 icon = bank_icon

#                 # 마커 생성 및 팝업 추가
#                 marker = folium.Marker(
#                     location=[map_df.loc[i, '위도'], map_df.loc[i, '경도']],
#                     icon=icon,
#                     popup=popup
#                 )
#                 marker.add_to(map)
#                 continue

#             if '뱅크' in name:
#                 icon = center_icon
#             elif '마켓' in name:
#                 icon = market_icon
#             else:
#                 icon = None



#             # 마커 생성 및 팝업 추가
#             marker = folium.Marker(
#                 location=[map_df.loc[i, '위도'], map_df.loc[i, '경도']],
#                 icon=icon,
#                 popup=popup
#             )
#             marker.add_to(map)


#         # Streamlit 앱에서 지도 표시
#         folium_static(map)
# -------------------- ▲ 필요 변수 생성 코딩 End ▲ --------------------


# -------------------- ▼ Streamlit 웹 화면 구성 START ▼ --------------------
# 웹 페이지 기본 구성
st.set_page_config(
    page_icon="🖥",
    page_title="기부 관리 시스템",
    layout="wide"
)

@st.cache_data
def read_data():
    proto = MyClass()
    return proto

p = read_data()

# 데이터 불러오기
test = pd.read_csv('기부물품대분류(가짜데이터).csv', encoding='cp949')

# tabs 만들기 
tab1, tab2, tab3 = st.tabs(["이용 관리", "재고 확인", "기부처 발굴"])

### ------------------------------ tab1 내용 구성하기 ---------------------------------------------
with tab1:
    # 사업장정보 넣기
    st.image('ktlogo.png')
    st.markdown('### 📃 이용자 관리')
    today = date.today()
    st.info(today)
    
    # 엑셀파일 열기
    user_data = pd.read_excel('output3.xlsx')
    if st.button('이용자 목록 확인'):
        st.dataframe(user_data)
        # 당일 이용자 뽑기
        today_object = today.strftime('%Y-%m-%d')
        count = user_data['날짜'].str.replace('.', '-')
        cnt = 0
        for i in count:
            if i == today_object:
                cnt += 1

        st.write(f'**당일 총 이용자는 {cnt}명 입니다.**')
    
    
    st.info('**이용자 추가 입력**')
    
    # 컬럼을 정의합니다.
    col1, col2, col3,col4,col5 = st.columns(5)

    # 각 컬럼에 텍스트를 추가합니다.
    with col1:
        st.info("이름")
    with col2:
        st.info("날짜")
    with col3:
        st.info("기부물품대분류코드")
    with col4:
        st.info("내용")
    with col5:
        st.info("수량")


    big_classfy = ['스포츠용품', '신선식품', '일상용품', '의류/패션잡화', '가정용품', '의약품/의료용품', '문화용품', '내구소비재', '기타상품']    

    # 새로운 입력을 받습니다.
    cols = st.columns(5)
    
    new_name = cols[0].text_input('이름', label_visibility="collapsed")
    new_date = cols[1].text_input('날짜', label_visibility="collapsed")
    new_category = cols[2].selectbox('기부물품대분류코드', big_classfy, label_visibility="collapsed")
    new_content = cols[3].text_input('내용', value='', label_visibility="collapsed")
    new_quantity = cols[4].text_input('수량', value='', label_visibility="collapsed")
    

    valid = True

    # 이름과 내용이 문자로만 구성되어 있는지 확인합니다.
    if not new_name.isalpha() or not new_content.isalpha():
        st.warning("이름과 내용은 문자로만 입력해야 합니다.")
        valid = False

    # 수량이 숫자로만 구성되어 있는지 확인합니다.
    elif not new_quantity.isdigit():
        st.warning("수량은 숫자로만 입력해야 합니다.")
        valid = False

    # 날짜가 0000-00-00 형식인지 확인합니다.
    elif not re.match(r'\d{4}.\d{2}.\d{2}', new_date):
        st.warning("날짜는 'YYYY.MM.DD' 형식으로 입력해야 합니다.")
        valid = False

    # 모든 입력이 유효하다면, new_input 딕셔너리를 만들고 Excel 파일에 저장합니다.   
    if valid:
        new_input = {
            "이름": new_name,
            "날짜": new_date,
            "기부물품대분류코드": new_category,
            "내용": new_content,
            "수량": new_quantity
        }
    
        
    # 입력을 완료하고 저장할 수 있는 버튼을 추가합니다.
   
    if st.button('Save to excel'):
        # DataFrame을 엑셀 파일로 저장합니다.
        if os.path.exists('output3.xlsx'):
            df_input = pd.read_excel('output3.xlsx')
            new_df = pd.DataFrame([new_input])
            df_input = pd.concat([df_input, new_df], ignore_index=True)
            
                
        else:
            df_input = pd.DataFrame([new_input])

        df_input.to_excel('output3.xlsx', index=False)
        st.success("Data saved successfully!")
        st.experimental_rerun()
        
        
        

    
### ------------------------------ tab2 내용 구성하기 ---------------------------------------------
with tab2:
    
    # 사업장정보 넣기
    st.image('ktlogo.png')
    st.markdown('### 📋 재고 및 기부처 확인')
    today = date.today()
    st.info(today)
    
     ## -------------------- ▼ 입력창1 ▼ --------------------
        
    col001, col002, col003, col004, col005, col006, col007, col008, col009 = st.columns(9)
    with col001:
        code1 = st.checkbox('스포츠용품', value=True)
        if code1:
            result1 = p.inventory_cal('스포츠용품')
            st.write(f'재고 수량 : {result1}')
            if result1 < 50:
                st.write('보충이 필요합니다.')
                rec_comp1 = st.selectbox('추천 기부처', p.donate('스포츠용품'), key = 0)
    with col002:
        code2 = st.checkbox('신선식품', value=True)
        if code2:
            result2 = p.inventory_cal('신선식품')
            st.write(f'재고 수량 : {result2}')
            if result2 < 50:
                st.write('보충이 필요합니다.')
                rec_comp2 = st.selectbox('추천 기부처', p.donate('신선식품'), key=999)
    with col003:
        code3 = st.checkbox('일상용품', value=True)
        if code3:
            result3 = p.inventory_cal('일상용품')
            st.write(f'재고 수량 : {result3}')
            if result3 < 50:
                st.write('보충이 필요합니다.')
                rec_comp3 = st.selectbox('추천 기부처', p.donate('일상용품'), key = 1)
    with col004:
        code4 = st.checkbox('의류/패션잡화', value=True)
        if code4:
            result4 = p.inventory_cal('의류/패션잡화')
            st.write(f'재고 수량 : {result4}')
            if result4 < 50:
                st.write('보충이 필요합니다.')
                rec_comp4 = st.selectbox('추천 기부처', p.donate('의류/패션잡화'), key = 2)
    with col005:
        code5 = st.checkbox('가정용품', value=True)
        if code5:
            result5 = p.inventory_cal('가정용품')
            st.write(f'재고 수량 : {result5}')
            if result5 < 50:
                st.write('보충이 필요합니다.')
                rec_comp5 = st.selectbox('추천 기부처', p.donate('가정용품'), key = 3)
    with col006:
        code6 = st.checkbox('의약품/의료용품', value=True)
        if code6:
            result6 = p.inventory_cal('의약품/의료용품')
            st.write(f'재고 수량 : {result6}')
            if result6 < 50:
                st.write('보충이 필요합니다.')
                rec_comp6 = st.selectbox('추천 기부처', p.donate('의약품/의료용품'), key = 4)
    with col007:
        code7 = st.checkbox('문화용품', value=True)
        if code7:
            result7 = p.inventory_cal('문화용품')
            st.write(f'재고 수량 : {result7}')
            if result7 < 50:
                st.write('보충이 필요합니다.')
                rec_comp7 = st.selectbox('추천 기부처', p.donate('문화용품'), key = 5)
    with col008:
        code8 = st.checkbox('내구소비재', value=True)
        if code8:
            result8 = p.inventory_cal('내구소비재')
            st.write(f'재고 수량 : {result8}')
            if result8 < 50:
                st.write('보충이 필요합니다.')
                rec_comp8 = st.selectbox('추천 기부처', p.donate('내구소비재'), key = 6)
    with col009:
        code9 = st.checkbox('기타상품', value=True)
        if code9:
            result9 = p.inventory_cal('기타상품')
            st.write(f'재고 수량 : {result9}')
            if result9 < 50:
                st.write('보충이 필요합니다.')
                rec_comp9 = st.selectbox('추천 기부처', p.donate('기타상품'), key = 7)
    
    
    
    ## -------------------- ▼ 입력창2 ▼ --------------------
    
    st.info("모든 기부처 확인 및 검색")
    
    col010, col011 = st.columns(2)
    with col010:
        all_donater = pd.read_csv('부산기부처목록.csv', encoding='cp949')        
        if st.button('모든 기부처 확인'):
            # st.dataframe(all_donater)
            st.session_state['opened_data'] = all_donater
            
        # 세션 상태에 열린 데이터가 있는 경우에만 테이블로 출력
        if 'opened_data' in st.session_state:
            st.write(st.session_state['opened_data'])

    with col011: 
        search = st.text_input('기부처 찾기',  placeholder='찾고 싶은 기부처(물품)를 입력하세요.')
        if search:
            st.dataframe(p.find_busan_donors(search))
            
    ## -------------------- ▼ 입력창3 ▼ --------------------
    
    
    
    st.info("구 별 최다 기부처")
    group_gugun_data1 = pd.read_csv('부산구별기부처.csv', encoding='cp949')
    group_gugun_data2 = pd.read_csv('부산구별기부처(금액).csv', encoding='cp949')
    gu999 = list(group_gugun_data1['통합시군구코드'].unique())
    
    col801, col802 = st.columns([0.1, 0.9])
    
    with col801:
        selected_gu = st.selectbox('**구 선택**', gu999, key='unique1')
    
    col901, col902 = st.columns(2)
    
    with col901:    
        p.grouping_gugun_graph20(selected_gu)
        
    with col902:
        p.grouping_gugun_money_graph20(selected_gu)
        
        
            
### ------------------------------ tab3 내용 구성하기 ---------------------------------------------
map_df = pd.read_csv('부산광역시_푸드뱅크 및 푸드마켓 현황_20230201.csv', encoding='cp949')     
new = pd.read_csv('부산도소매업(전처리).csv', encoding='cp949')
new_comp_name = list(new['표준산업분류명'].unique())
new_comp_gugun = list(new['시군구명'].unique())

with tab3:
    
    st.image('ktlogo.png')
    st.markdown('### 🔎 새로운 기부처 찾기')
    today = date.today()
    st.info(today)
    
    col012, col013, col014 = st.columns([1, 1, 3])
    with col012:
        selected_city = st.selectbox('지역 선택', ['부산광역시'], label_visibility="collapsed")

    with col013:
        selected_gugun = st.selectbox('구 선택', new_comp_gugun, label_visibility="collapsed")
        
    with col014:
        selected_comp_name = st.selectbox('산업군 선택', new_comp_name, label_visibility="collapsed")
        
    if selected_gugun and selected_comp_name:
        df = p.find_new_donors(selected_gugun, selected_comp_name)
        mark_df = df[['상호명', '표준산업분류명', '도로명주소']].set_index('상호명')
        st.dataframe(mark_df)
        p.find_new_donors_location(df)
        
        
        
### ------------------------------ tab4 내용 구성하기 ---------------------------------------------

# # tab4 내용 구성하기
# with tab4:
#     data = pd.read_csv('분석전체데이터.csv', encoding="cp949")   
#     bank_name = list(data['지원센터코드'].unique())
    
#     # 사업장정보 널기
#     st.markdown("### 사업장 정보 입력")

#     ## -------------------- ▼ 입력창 ▼ --------------------
#     try: 
#         col1, col2 ,col3= st.columns([0.1, 0.3, 0.5])
#         with col1:
#             st.info("사업장명")
#         with col2:
#             bs_name = st.selectbox('사업장', bank_name, label_visibility="collapsed", key="unique_key_1")

#         col4, col5, col6 = st.columns([0.1, 0.3, 0.5])
#         with col4:
#             st.info("기부자수")
#         with col5:
#             donater = st.text_input("기부자수", label_visibility="collapsed")


#         col7, col8, col9 = st.columns([0.1, 0.3, 0.5])
#         with col7:
#             st.info("제공금액")
#         with col8:
#             money1 = st.text_input("제공금액", value='', label_visibility="collapsed")


#         col10, col11, col12 = st.columns([0.1, 0.3, 0.5])
#         with col10:
#             st.info("이관금액")
#         with col11:
#             money2 = st.text_input("이관금액", value='', label_visibility="collapsed")

#         col13, col14, col15 = st.columns([0.1, 0.3, 0.5])
#         with col13:
#             st.info('장부수량')
#         with col14:
#             remain = st.text_input('장부수량', value='', label_visibility="collapsed")
            
    
    
#     ## -------------------- ▼ 예측 ▼ --------------------
#         dic = {
#         '기부자수':[int(donater)],
#         '제공금액':[int(money1)], 
#         '이관금액':[int(money2)],
#         '장부수량':[int(remain)],
#         '사업장유형':['']
#         }
   
        
#         if st.button('예측하기'):
#             df = pd.DataFrame(dic)
#             st.write(f'{bs_name}는 **{p.predict_bussiness(df)}** 사업장으로 예측됩니다.')
#             if p.predict_bussiness(df) == '임의':
#                 st.image('이미지파일모음/goodbank2.jpg')
    
#     except:
#         st.write('숫자를 입력하세요.')
#     ### ------------------------------지도생성-----------------------------------


#     p.predict_map()
     
