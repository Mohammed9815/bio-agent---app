
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64

st.set_page_config(page_title="الوكيل الذكي لمادة الأحياء", layout="centered", page_icon="🧬")

# ------------------ واجهة المستخدم ------------------ #
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🧬 الوكيل الذكي لمادة الأحياء</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>🎯 توليد أنشطة مخصصة للطلاب حسب درجاتهم</h4>", unsafe_allow_html=True)
st.markdown("---")

# ------------------ تحميل بيانات الطلاب ------------------ #
st.subheader("📥 أولاً: بيانات الطلاب")
input_method = st.radio("كيف تود إدخال بيانات الطلاب؟", ["📄 رفع ملف Excel", "✍️ إدخال يدوي"], horizontal=True)

df = pd.DataFrame()

if input_method == "📄 رفع ملف Excel":
    uploaded_file = st.file_uploader("🔼 ارفع ملف Excel يحتوي على عمودين: الاسم - الدرجة", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
else:
    num_students = st.number_input("📌 كم عدد الطلاب؟", min_value=1, max_value=100, step=1)
    names = []
    scores = []
    for i in range(num_students):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input(f"اسم الطالب رقم {i+1}")
        with col2:
            score = st.number_input(f"درجة {name or f'طالب {i+1}'}", min_value=0.0, max_value=10.0, step=0.1, key=f"score_{i}")
        if name:
            names.append(name)
            scores.append(score)
    if names:
        df = pd.DataFrame({"الاسم": names, "الدرجة": scores})

# ------------------ اختيار الدرس ------------------ #
st.subheader("📚 ثانياً: اختر الدرس")
lessons = [
    "الأغشية الخلوية والنقل عبرها", "الإنتشار والنقل النشط", "الخاصية الأسموزية وجهد الماء",
    "النقل في النباتات", "النقل في الثدييات", "تبادل الغازات", "الجهاز الدوري", 
    "الدورة القلبية", "الأوعية الدموية", "مكونات الدم", "التنفس الخلوي", "الجهاز التنفسي"
]
selected_lesson = st.selectbox("اختر أحد الدروس:", lessons)

# ------------------ توليد النشاط حسب التصنيف ------------------ #
def generate_activity(name, score, lesson):
    if score < 5:
        level = "علاجي 😕"
        activity = f"🔹 عزيزي {name}، تحتاج إلى دعم في هذا الدرس.\nابدأ بالإجابة على:\n1. ما المقصود بـ {lesson}؟\n2. لماذا هذا المفهوم مهم؟\n3. أعطني مثالاً بسيطاً عليه."
    elif 5 <= score < 8:
        level = "دعم 💪"
        activity = f"🔸 مرحبًا {name}!\nراجع المهارات التالية:\n1. لخص النقاط الأساسية في {lesson}.\n2. اشرحها لزميلك.\n3. اذكر تطبيقاً عملياً."
    else:
        level = "إثرائي 😃"
        activity = f"🌟 ممتاز يا {name}!\nنشاط إثرائي:\n1. ابحث عن تطبيق واقعي لـ {lesson}.\n2. ناقش فائدته.\n3. صمم سؤالاً إبداعياً حوله."
    return level, activity

# ------------------ توليد PDF ------------------ #
def create_pdf(name, level, activity):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 80, f"الوكيل الذكي لمادة الأحياء 🧬")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 120, f"اسم الطالب: {name}")
    c.drawString(100, height - 140, f"التصنيف: {level}")
    text = c.beginText(100, height - 180)
    for line in activity.split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ------------------ زر توليد الأنشطة ------------------ #
if not df.empty and selected_lesson:
    st.subheader("✨ الأنشطة المقترحة:")
    all_pdfs = []
    for i, row in df.iterrows():
        name = row['الاسم']
        score = row['الدرجة']
        level, activity = generate_activity(name, score, selected_lesson)
        st.markdown(f"**👤 {name}** — {level}")
        st.code(activity, language="markdown")
        pdf_file = create_pdf(name, level, activity)
        all_pdfs.append((name, pdf_file))

    # تحميل الملفات بشكل مضغوط
    st.markdown("---")
    if st.button("📥 تحميل ملفات PDF لجميع الطلاب"):
        zip_buffer = BytesIO()
        from zipfile import ZipFile
        with ZipFile(zip_buffer, "w") as zipf:
            for name, pdf in all_pdfs:
                zipf.writestr(f"{name}.pdf", pdf.read())
        zip_buffer.seek(0)
        b64 = base64.b64encode(zip_buffer.read()).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="أنشطة_{selected_lesson}.zip">📎 اضغط هنا لتنزيل جميع الأنشطة بصيغة ZIP</a>'
        st.markdown(href, unsafe_allow_html=True)
