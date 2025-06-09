import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import base64

# --- استيراد المكتبات الجديدة ---
# مكتبة لإنشاء ملفات وورد
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
# مكتبات معالجة اللغة العربية
import arabic_reshaper
from bidi.algorithm import get_display

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الوكيل الذكي لمادة الأحياء", layout="wide", page_icon="🧬")

# --- CSS مخصص لإعادة تصميم الواجهة بالكامل ---
def load_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
            
            /* ---- الخلفية والخط العام ---- */
            html, body, [class*="st-"] {
                font-family: 'Cairo', sans-serif;
            }
            
            .stApp {
                background-image: linear-gradient(to bottom right, #e0f2f1, #d4eaf7);
                background-attachment: fixed;
            }

            /* إخفاء رأس ستريملت الافتراضي */
            .stApp > header {
                background-color: transparent;
            }

            /* ---- تصميم البطاقات ---- */
            .card {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                border: 1px solid rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(5px);
            }

            /* ---- تصميم العناصر ---- */
            .stButton > button {
                border-radius: 10px;
                background-color: #00897B; /* Teal */
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                transition: all 0.3s;
            }
            .stButton > button:hover {
                background-color: #00695C;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            .stSelectbox div[data-baseweb="select"] > div {
                border-radius: 10px;
                background-color: #FFFFFF;
            }
            .stFileUploader {
                border: 2px dashed #00897B;
                border-radius: 10px;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.5);
            }
        </style>
    """, unsafe_allow_html=True)

# --- تحميل التصميم ---
load_css()

# --- العنوان الرئيسي ---
st.markdown('<h1 style="text-align: center; color: #004D40;">🧬 الوكيل الذكي لمادة الأحياء 🧬</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center; color: #00695C;">أداة ذكية لتوليد أنشطة علاجية، داعمة وإثرائية للطلاب</h4>', unsafe_allow_html=True)
st.markdown("---")


# --- دالة إنشاء ملف Word (النسخة النهائية والمصححة) ---
def create_word_doc(name, level, content):
    document = Document()
    # Set document direction to RTL for all sections
    for section in document.sections:
        section.right_to_left = True

    # Helper function to add RTL text correctly
    def add_rtl_text(paragraph, text, size=12, bold=False):
        # Reshape and apply bidi algorithm
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        # Add run and set text
        run = paragraph.add_run(bidi_text)
        
        # Set font properties for the run
        font = run.font
        font.name = 'Arial' # Using a common font
        font.size = Pt(size)
        font.bold = bold
        font.rtl = True # This is crucial for Word to render correctly

    # Add Title
    title_p = document.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rtl_text(title_p, "الوكيل الذكي لمادة الأحياء", size=16, bold=True)

    # Add student info
    name_p = document.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_rtl_text(name_p, f"اسم الطالب: {name}")

    level_p = document.add_paragraph()
    level_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_rtl_text(level_p, f"التصنيف: {level}")

    # Add separator
    document.add_paragraph("------------------")

    # Add activity content line by line
    for line in content.split('\n'):
        content_p = document.add_paragraph()
        content_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_rtl_text(content_p, line)

    # Save to buffer
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


# --- دالة توليد الأنشطة (بدون تغيير) ---
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

# --- واجهة المستخدم ---
df = None
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 الخطوة 1: أدخل بيانات الطلاب")
    method = st.radio("اختر طريقة الإدخال:", ["📄 رفع ملف Excel", "✍️ إدخال يدوي"], horizontal=True)
    
    if method == "📄 رفع ملف Excel":
        excel_file = st.file_uploader("ارفع ملف Excel (يحتوي على عمودي 'الاسم' و 'الدرجة')", type=["xlsx"])
        if excel_file:
            df = pd.read_excel(excel_file)
    else:
        count = st.number_input("حدد عدد الطلاب:", min_value=1, max_value=50, value=1, step=1)
        data = {'الاسم': [], 'الدرجة': []}
        for i in range(count):
            c1, c2 = st.columns([3, 1])
            with c1:
                name = st.text_input(f"اسم الطالب {i+1}", key=f"n{i}")
            with c2:
                score = st.number_input("الدرجة", 0.0, 10.0, 0.0, step=0.1, key=f"s{i}")
            data['الاسم'].append(name)
            data['الدرجة'].append(score)
        
        if st.button("تأكيد الطلاب", key="add_students"):
            df = pd.DataFrame(data)
            df = df[df['الاسم'].str.strip() != ""]
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📚 الخطوة 2: اختر الدرس")
    lessons = [
        "الأغشية الخلوية والنقل عبرها", "الإنتشار والنقل النشط", "الخاصية الأسموزية وجهد الماء",
        "النقل في النباتات", "النقل في الثدييات", "تبادل الغازات", "الجهاز الدوري", 
        "الدورة القلبية", "الأوعية الدموية", "مكونات الدم", "التنفس الخلوي", "الجهاز التنفسي"
    ]
    selected_lesson = st.selectbox("اختر الدرس من القائمة:", lessons)
    st.markdown('</div>', unsafe_allow_html=True)

# --- المنطق الرئيسي لعرض النتائج وتوليد الملفات ---
if df is not None and not df.empty and 'الاسم' in df.columns and 'الدرجة' in df.columns and selected_lesson:
    st.markdown("---")
    st.markdown('<h2 style="text-align: center; color: #004D40;">✨ الأنشطة المقترحة للطلاب</h2>', unsafe_allow_html=True)

    files_to_zip = []
    
    for index, row in df.iterrows():
        name, score = row['الاسم'], row['الدرجة']
        
        if pd.notna(name) and name.strip() != "" and pd.notna(score):
            level, content = generate_activity(name, float(score), selected_lesson)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<h4>👤 {name} <span style='color:#00897B;'>— {level}</span></h4>", unsafe_allow_html=True)
            st.text_area("النشاط المقترح:", content, height=150)
            
            # إنشاء ملف وورد في الذاكرة
            word_buffer = create_word_doc(name, level, content)
            files_to_zip.append((f"{name}.docx", word_buffer.getvalue()))
            st.markdown('</div>', unsafe_allow_html=True)

    if files_to_zip:
        zip_buf = BytesIO()
        with ZipFile(zip_buf, "w") as zipf:
            for filename, data in files_to_zip:
                zipf.writestr(filename, data)
        zip_buf.seek(0)
        
        b64 = base64.b64encode(zip_buf.read()).decode()
        download_filename = f"أنشطة_{selected_lesson.replace(' ', '_')}.zip"
        # زر التحميل بتصميم جديد
        st.markdown(f"""
            <div style="text-align: center; margin-top: 20px;">
                <a href="data:application/zip;base64,{b64}" download="{download_filename}" 
                   style="background-color: #F4511E; color: white; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 18px;">
                   📥 تحميل جميع الأنشطة (ملفات Word)
                </a>
            </div>
        """, unsafe_allow_html=True)

elif df is not None:
    st.warning("يرجى التأكد من إدخال بيانات الطلاب وأن ملف الإكسل يحتوي على عمودين بالاسمين 'الاسم' و 'الدرجة'.")

