import streamlit as st
import hashlib
import sqlite3
from datetime import datetime

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls
        (id TEXT PRIMARY KEY,
         original_url TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

# URL 단축 함수
def shorten_url(url):
    # URL의 해시값을 생성하여 첫 8자리만 사용
    hash_object = hashlib.sha256(url.encode())
    short_id = hash_object.hexdigest()[:8]
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    try:
        # 데이터베이스에 저장
        c.execute('INSERT INTO urls (id, original_url) VALUES (?, ?)',
                 (short_id, url))
        conn.commit()
    except sqlite3.IntegrityError:
        # 이미 존재하는 경우 기존 URL 반환
        pass
    finally:
        conn.close()
    
    return short_id

# URL 조회 함수
def get_original_url(short_id):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT original_url FROM urls WHERE id = ?', (short_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Streamlit 앱 UI
def main():
    st.title('URL 단축기')
    st.write('긴 URL을 짧게 줄여보세요!')

    # 데이터베이스 초기화
    init_db()

    # URL 입력
    url = st.text_input('단축할 URL을 입력하세요:')

    if st.button('URL 단축하기'):
        if url:
            # URL 유효성 검사 (간단한 버전)
            if not url.startswith(('http://', 'https://')):
                st.error('유효한 URL을 입력해주세요. (http:// 또는 https://로 시작)')
            else:
                short_id = shorten_url(url)
                shortened_url = f"http://ICT4TH.com/{short_id}"
                
                st.success('URL이 성공적으로 단축되었습니다!')
                st.write('원본 URL:', url)
                st.write('단축된 URL:', shortened_url)
                
                # 단축된 URL을 클립보드에 복사할 수 있는 버튼
                st.code(shortened_url)
                st.caption('위의 URL을 클릭하여 복사할 수 있습니다.')
        else:
            st.warning('URL을 입력해주세요.')

    # URL 조회 기능
    st.subheader('단축된 URL 조회')
    short_id = st.text_input('단축된 URL의 ID를 입력하세요:')
    
    if st.button('원본 URL 조회'):
        if short_id:
            original_url = get_original_url(short_id)
            if original_url:
                st.write('원본 URL:', original_url)
            else:
                st.error('해당하는 URL을 찾을 수 없습니다.')
        else:
            st.warning('단축된 URL의 ID를 입력해주세요.')

if __name__ == '__main__':
    main()
