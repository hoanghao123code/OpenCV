
import cv2
import pytesseract
import streamlit as st
import numpy as np
import pandas as pd
import re
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="🎈Hoang Hao's Applications",
    # page_icon=Image.open("./images/Logo/logo_welcome.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🎈Ứng dụng đọc thông tin từ thẻ sinh viên")



# # Cấu hình đường dẫn Tesseract OCR nếu cần
pytesseract.pytesseract.tesseract_cmd =  r'./services/Tesseract-OCR/tesseract'

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

def extract_portrait(image):
    h, w = image.shape[:2]
    portrait = image[int(h * 0.48):h, 0:int(w * 0.3)]  
    return portrait

def extract_text(image):
    text = pytesseract.image_to_string(image, lang='vie')
    return text

def parse_student_info(text):
    info = {}
    lines = text.split('\n')
    for line in lines:
        if "Họ & tên" in line or "tên" in line:
            info['Họ tên'] = line.split(":")[-1].strip()  
        elif "Ngày sinh" in line or "sinh" in line:
            info['Ngày sinh'] = line.split(":")[-1].strip()
        elif "Lớp" in line:
            info['Lớp'] = line.split(":")[-1].strip()
        elif "Khóa học" in line or "học" in line:
            info['Khóa học'] = line.split(":")[-1].strip()
        elif "Mã SV" in line or "SV" in line:
            info['Mã SV'] = line.split(":")[-1].strip()
    return info

def validate_student_info(info):
    """Kiểm tra định dạng thông tin hợp lệ."""
    if 'Mã SV' in info:
        info['Mã SV hợp lệ'] = bool(re.match(r'^\d{2}[A-Z]\d{7}$', info['Mã SV']))

    if 'Ngày sinh' in info:
        info['Ngày sinh hợp lệ'] = bool(re.match(r'^\d{2}/\d{2}/\d{4}$', info['Ngày sinh']))

    if 'Khóa học' in info:
        info['Khóa học hợp lệ'] = bool(re.match(r'^\d{4}-\d{4}$', info['Khóa học']))

    return info

def save_to_file(data, file_name="student_info.csv"):
    """Lưu thông tin vào file CSV hoặc Excel."""
    df = pd.DataFrame([data])
    df.to_csv(file_name, index=False)

def main():

    # st.title("Trích Xuất Thông Tin Từ Ảnh Thẻ Sinh Viên")
    st.header("1. Sơ đồ minh họa luồng xử lí")
    image = cv2.imread("./images/pipeline.png")
    st.image(image, caption="Sơ đồ minh họa luồng xử lí")
    st.header("2. Ứng dụng trích xuất thông tin")
    uploaded_file = st.file_uploader("Tải lên ảnh thẻ sinh viên", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = np.array(Image.open(uploaded_file))

        st.subheader("Ảnh Gốc")
        st.image(image, channels="RGB")

        # Tiền xử lý ảnh
        processed_image = preprocess_image(image)
        # st.subheader("Ảnh Sau Tiền Xử Lý")
        # st.image(processed_image, channels="GRAY")

        # Trích xuất ảnh chân dung
        portrait = extract_portrait(image)
        st.subheader("Ảnh Chân Dung")
        st.image(portrait, channels="RGB")

        # OCR để trích xuất văn bản
        text = extract_text(processed_image)
        # st.subheader("Văn Bản Trích Xuất")
        # st.text(text)

        # Phân tích thông tin sinh viên
        student_info = parse_student_info(text)
            
        # Kiểm tra định dạng thông tin hợp lệ
        student_info = validate_student_info(student_info)
        if student_info['Mã SV hợp lệ'] == False:
            st.warning("Mã sinh viên không hợp lệ")
        if student_info['Ngày sinh hợp lệ'] == False:
            st.warning("Ngày sinh không hợp lệ")
        if student_info['Khóa học hợp lệ'] == False:
            st.warning("Khóa học không hợp lệ")

        # Hiển thị thông tin sinh viên dưới dạng bảng
        st.subheader("Thông Tin Sinh Viên")
        student_df = pd.DataFrame([student_info])
        st.dataframe(student_df)

        # Lưu kết quả vào file CSV
        if st.button("Lưu vào file CSV"):
            save_to_file(student_info)
            st.success("Thông tin đã được lưu vào file student_info.csv")

if __name__ == "__main__":
    main()
