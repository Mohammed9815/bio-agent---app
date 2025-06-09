import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from zipfile import ZipFile
import base64

st.set_page_config(page_title="الوكيل الذكي لمادة الأحياء", layout="centered", page_icon="🧬")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🧬 الوكيل الذكي لمادة الأحياء</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>🎯 توليد أنشطة مخصصة للطلاب حسب درجاتهم</h4>", unsafe_allow_html=True)
st.markdown("---")

pdfmetrics.registerFont(TTFont("Arabic", "Amiri-Regular.ttf"))

st.subheader("📥 أولاً: بيانات الطلاب")
method = st.radio("طريقة الإدخال:", ["📄 رفع ملف Excel", "✍️ إدخال يدوي"], horizontal=True)
df = pd.DataFrame()

if method == "📄 رفع ملف Excel":
    excel_file = st.file_uploader("🔼 ارفع ملف Excel فيه عمودين: الاسم - الدرجة", type=["xlsx"])
    if excel_file:
        df = pd.read_excel(excel_file)
else:
    count = st.number_input("📌 عدد الطلاب:", min_value=1, max_value=100, step=1)
    names, scores = [], []
    for i in range(count):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input(f"اسم الطالب {i+1}")
        with col2:
            score = st.number_input("الدرجة", 0.0, 10.0, step=0.1, key=f"s{i}")
        if name:
            names.append(name)
            scores.append(score)
    if names:
        df = pd.DataFrame({"الاسم": names, "الدرجة": scores})

st.subheader("📚 ثانياً: اختر الدرس")
lessons = [
    "الأغشية الخلوية والنقل عبرها", "الإنتشار والنقل النشط", "الخاصية الأسموزية وجهد الماء",
    "النقل في النباتات", "النقل في الثدييات", "تبادل الغازات", "الجهاز الدوري", 
    "الدورة القلبية", "الأوعية الدموية", "مكونات الدم", "التنفس الخلوي", "الجهاز التنفسي"
]
selected_lesson = st.selectbox("اختر الدرس:", lessons)

def generate_activity(name, score, lesson):
    if score < 5:
        level = "علاجي 😕"
        text = f"🔹 عزيزي {name}، تحتاج إلى دعم في هذا الدرس.\n1. ما المقصود بـ {lesson}؟\n2. لماذا هو مهم؟\n3. مثال عليه."
    elif score < 8:
        level = "دعم 💪"
        text = f"🔸 مرحبًا {name}، راجع المهارات التالية:\n1. لخص {lesson}.\n2. اشرح لزميلك.\n3. مثال عملي."
    else:
        level = "إثرائي 😃"
        text = f"🌟 ممتاز {name}!\n1. ابحث عن تطبيق لـ {lesson}.\n2. ناقش فائدته.\n3. صمم سؤالاً إبداعياً."
    return level, text

def create_pdf(name, level, content):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Arabic", 14)
    c.drawRightString(width - 50, height - 50, "الوكيل الذكي لمادة الأحياء 🧬")
    c.setFont("Arabic", 12)
    c.drawRightString(width - 50, height - 80, f"الاسم: {name}")
    c.drawRightString(width - 50, height - 100, f"التصنيف: {level}")
    text = c.beginText(width - 50, height - 140)
    text.setFont("Arabic", 12)
    text.setTextOrigin(width - 50, height - 140)
    text.setLeading(20)
    for line in content.split("\n"):
        text.textLine(line[::-1])
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

if not df.empty and selected_lesson:
    st.subheader("✨ الأنشطة المقترحة")
    files = []
    for i, row in df.iterrows():
        name, score = row['الاسم'], row['الدرجة']
        level, content = generate_activity(name, score, selected_lesson)
        st.markdown(f"**👤 {name} — {level}**")
        st.code(content)
        pdf = create_pdf(name, level, content)
        files.append((name, pdf))

    if st.button("📥 تحميل ملفات PDF"):
        zip_buf = BytesIO()
        with ZipFile(zip_buf, "w") as zipf:
            for name, pdf in files:
                zipf.writestr(f"{name}.pdf", pdf.read())
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="أنشطة_{selected_lesson}.zip">📎 اضغط هنا للتنزيل</a>'
        st.markdown(href, unsafe_allow_html=True)