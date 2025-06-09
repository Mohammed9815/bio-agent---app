import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import base64
import random # لاستيراد مكتبة الاختيار العشوائي

# --- استيراد المكتبات ---
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import arabic_reshaper
from bidi.algorithm import get_display

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الوكيل الذكي لمادة الأحياء", layout="wide", page_icon="🧬")

# --- CSS مخصص للتصميم ---
def load_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
            html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; }
            .stApp {
                background-image: linear-gradient(to bottom right, #e0f2f1, #d4eaf7);
                background-attachment: fixed;
            }
            .stApp > header { background-color: transparent; }
            .card {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 15px; padding: 25px; margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                border: 1px solid rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(5px);
            }
            .stButton > button, .stDownloadButton > a {
                border-radius: 10px; background-color: #00897B; color: white;
                font-weight: bold; border: none; padding: 10px 20px; transition: all 0.3s;
                text-decoration: none; display: inline-block;
            }
            .stButton > button:hover { background-color: #00695C; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
            .stSelectbox div[data-baseweb="select"] > div { border-radius: 10px; background-color: #FFFFFF; }
            .stFileUploader { border: 2px dashed #00897B; border-radius: 10px; padding: 20px; background-color: rgba(255, 255, 255, 0.5); }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- العناوين ---
st.markdown('<h1 style="text-align: center; color: #004D40;">🧬 الوكيل الذكي 2.0 🧬</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center; color: #00695C;">مساعدك الشخصي لتوليد أنشطة طلابية فريدة ومبتكرة</h4>', unsafe_allow_html=True)
st.markdown("---")


# ==============================================================================
#  المرحلة الأولى: بناء العقل الذكي (بنك الأنشطة)
# ==============================================================================
ACTIVITY_BANK = {
    "علاجي": [
        "اكتب تعريفاً مبسطاً لمفهوم '{lesson}'.",
        "صل بين المصطلحات التالية وما يناسبها من تعاريف بخصوص درس '{lesson}'. (سيقوم المعلم بتوفير المصطلحات)",
        "أكمل الفراغ: من أهم أجزاء '{lesson}' هي ______ و ______. (مثال توضيحي)",
        "ارسم شكلاً مبسطاً يوضح فكرة '{lesson}' مع كتابة البيانات الأساسية.",
        "اذكر وظيفة واحدة رئيسية لـ '{lesson}' في جسم الكائن الحي."
    ],
    "دعم": [
        "لخص في ثلاث نقاط أهم الأفكار في درس '{lesson}'.",
        "قارن بين مفهومين مرتبطين بدرس '{lesson}' (مثلاً: الانتشار البسيط والانتشار المسهل).",
        "اشرح لزميل لك كيف تعمل الآلية الخاصة بـ '{lesson}'.",
        "حلل الرسم البياني أو الشكل الموجود في الكتاب المدرسي صفحة (X) المتعلق بدرس '{lesson}'.",
        "صمم خريطة مفاهيمية بسيطة توضح العلاقات بين المكونات الرئيسية لـ '{lesson}'."
    ],
    "إثرائي": [
        "ابحث عن مرض أو حالة طبية ترتبط بخلل في آلية '{lesson}' واكتب فقرة موجزة عنها.",
        "اقترح طريقة مبتكرة لشرح مفهوم '{lesson}' باستخدام مواد بسيطة من الحياة اليومية.",
        "ماذا سيحدث لو لم تكن عملية '{lesson}' موجودة؟ صف التأثيرات المحتملة.",
        "ابحث عن أحدث الاكتشافات العلمية المتعلقة بـ '{lesson}' خلال السنوات الخمس الماضية.",
        "صمم سؤالاً واحداً بمستوى تفكير عليا (تحليل، تركيب، تقويم) حول درس '{lesson}' مع نموذج إجابته."
    ]
}

# ==============================================================================
#  المرحلة الثانية: إصلاح منطق التصنيف وتوليد الأنشطة الديناميكية
# ==============================================================================
def generate_smart_activity(score):
    # تصحيح منطق التصنيف
    if score < 5:
        level = "علاجي"
        level_emoji = "😕"
    elif 5 <= score <= 7:
        level = "دعم"
        level_emoji = "💪"
    else: # أكبر من 7
        level = "إثرائي"
        level_emoji = "😃"
    
    # اختيار قالب نشاط عشوائي من البنك
    activity_template = random.choice(ACTIVITY_BANK[level])
    
    return f"{level} {level_emoji}", activity_template


# --- دالة إنشاء ملف Word (النسخة النهائية) ---
def create_word_doc(name, level, content):
    document = Document()
    for section in document.sections:
        section.right_to_left = True

    def add_rtl_paragraph(text, alignment=WD_ALIGN_PARAGRAPH.RIGHT, size=12, bold=False):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        p = document.add_paragraph()
        p.alignment = alignment
        run = p.add_run(bidi_text)
        font = run.font
        font.name = 'Times New Roman'
        font.size = Pt(size)
        font.bold = bold
        p_format = p.paragraph_format
        p_format.right_to_left = True
        
    add_rtl_paragraph("الوكيل الذكي لمادة الأحياء", alignment=WD_ALIGN_PARAGRAPH.CENTER, size=16, bold=True)
    add_rtl_paragraph(f"اسم الطالب: {name}", size=14)
    add_rtl_paragraph(f"التصنيف: {level}", size=14)
    document.add_paragraph("--------------------------------------------------")

    for line in content.split('\n'):
        add_rtl_paragraph(line)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


# ==============================================================================
#  المرحلة الثالثة: تصميم جديد لتجربة المستخدم
# ==============================================================================

# --- الجزء الأول: إدخال البيانات ---
df = None
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 الخطوة 1: أدخل بيانات الطلاب واختر الدرس")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
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
            df = pd.DataFrame(data)
            df = df[df['الاسم'].str.strip() != ""] if not df.empty else df

    with col2:
        lessons = [
            "الأغشية الخلوية والنقل عبرها", "الإنتشار والنقل النشط", "الخاصية الأسموزية وجهد الماء",
            "النقل في النباتات", "النقل في الثدييات", "تبادل الغازات", "الجهاز الدوري", 
            "الدورة القلبية", "الأوعية الدموية", "مكونات الدم", "التنفس الخلوي", "الجهاز التنفسي"
        ]
        selected_lesson = st.selectbox("اختر الدرس من القائمة:", lessons)
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- الجزء الثاني: زر التوليد وعرض النتائج ---
if df is not None and not df.empty and 'الاسم' in df.columns and 'الدرجة' in df.columns and selected_lesson:
    
    if st.button("✨ توليد الأنشطة الذكية", use_container_width=True):
        
        with st.spinner('الوكيل الذكي يفكر... 🧠 لطفاً، انتظر قليلاً.'):
            files_to_zip = []
            
            st.markdown("---")
            st.markdown('<h2 style="text-align: center; color: #004D40;">📋 النتائج والأنشطة المخصصة</h2>', unsafe_allow_html=True)

            for index, row in df.iterrows():
                name, score = row['الاسم'], row['الدرجة']
                
                if pd.notna(name) and name.strip() != "" and pd.notna(score):
                    level, activity_template = generate_smart_activity(float(score))
                    final_activity = activity_template.format(lesson=selected_lesson)
                    
                    # عرض النتائج في بطاقات قابلة للتوسيع
                    with st.expander(f"👤 {name}  |  الدرجة: {score}  |  المستوى المقترح: {level}"):
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.text_area("النشاط المولد:", final_activity, height=150)
                        
                        word_buffer = create_word_doc(name, level, final_activity)
                        files_to_zip.append((f"{name}.docx", word_buffer.getvalue()))
                        
                        st.markdown('</div>', unsafe_allow_html=True)

            # --- الجزء الرابع: الحفاظ على الميزات الناجحة (زر التحميل) ---
            if files_to_zip:
                zip_buf = BytesIO()
                with ZipFile(zip_buf, "w") as zipf:
                    for filename, data in files_to_zip:
                        zipf.writestr(filename, data)
                zip_buf.seek(0)
                
                b64 = base64.b64encode(zip_buf.read()).decode()
                download_filename = f"أنشطة_{selected_lesson.replace(' ', '_')}.zip"
                
                st.markdown("---")
                st.markdown(f"""
                    <div style="text-align: center; margin: 20px;">
                        <a href="data:application/zip;base64,{b64}" download="{download_filename}" 
                           style="background-color: #F4511E; color: white; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 18px;">
                           📥 تحميل جميع الأنشطة (ملفات Word)
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        
        st.success("🎉 تم توليد الأنشطة بنجاح!")
        st.balloons()

