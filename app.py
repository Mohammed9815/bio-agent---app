import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from zipfile import ZipFile
import base64

# --- استيراد المكتبات الجديدة لمعالجة اللغة العربية ---
import arabic_reshaper
from bidi.algorithm import get_display

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="الوكيل الذكي لمادة الأحياء", layout="centered", page_icon="🧬")

# -- تم تصحيح الخطأ هنا --
# استخدام علامات اقتباس فردية من الخارج ومزدوجة من الداخل لتجنب الخطأ
st.markdown('<h1 style="text-align: center; color: #4CAF50;">🧬 الوكيل الذكي لمادة الأحياء</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">🎯 توليد أنشطة مخصصة للطلاب حسب درجاتهم</h4>', unsafe_allow_html=True)
st.markdown("---")

# --- تسجيل الخط العربي المستخدم في ملفات PDF ---
# تأكد من أن ملف الخط Amiri-Regular.ttf موجود في نفس مجلد المشروع
try:
    pdfmetrics.registerFont(TTFont("Arabic", "Amiri-Regular.ttf"))
except Exception as e:
    st.error(f"خطأ في تحميل الخط: لم يتم العثور على ملف Amiri-Regular.ttf. تأكد من وجوده في المستودع. الخطأ: {e}")


# --- واجهة المستخدم لاستقبال بيانات الطلاب ---
st.subheader("📥 أولاً: بيانات الطلاب")
method = st.radio("طريقة الإدخال:", ["📄 رفع ملف Excel", "✍️ إدخال يدوي"], horizontal=True)
df = pd.DataFrame()

if method == "📄 رفع ملف Excel":
    excel_file = st.file_uploader("🔼 ارفع ملف Excel فيه عمودين: الاسم - الدرجة", type=["xlsx"])
    if excel_file:
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            st.error(f"حدث خطأ في قراءة ملف Excel: {e}")
else:
    count = st.number_input("📌 عدد الطلاب:", min_value=1, max_value=100, value=1, step=1)
    data = {'الاسم': [], 'الدرجة': []}
    for i in range(count):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input(f"اسم الطالب {i+1}", key=f"n{i}")
        with col2:
            score = st.number_input("الدرجة", 0.0, 10.0, 0.0, step=0.1, key=f"s{i}")
        data['الاسم'].append(name)
        data['الدرجة'].append(score)
    
    if st.button("إضافة الطلاب", key="add_students"):
        df = pd.DataFrame(data)
        df = df[df['الاسم'] != ""] # تجاهل الطلاب بدون اسم


# --- اختيار الدرس ---
st.subheader("📚 ثانياً: اختر الدرس")
lessons = [
    "الأغشية الخلوية والنقل عبرها", "الإنتشار والنقل النشط", "الخاصية الأسموزية وجهد الماء",
    "النقل في النباتات", "النقل في الثدييات", "تبادل الغازات", "الجهاز الدوري", 
    "الدورة القلبية", "الأوعية الدموية", "مكونات الدم", "التنفس الخلوي", "الجهاز التنفسي"
]
selected_lesson = st.selectbox("اختر الدرس:", lessons)

# --- دالة توليد الأنشطة بناءً على الدرجة ---
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

# --- دالة إنشاء ملف PDF (النسخة المعدلة) ---
def create_pdf(name, level, content):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- معالجة جميع النصوص العربية قبل كتابتها ---
    reshaped_title = arabic_reshaper.reshape("الوكيل الذكي لمادة الأحياء 🧬")
    bidi_title = get_display(reshaped_title)
    
    reshaped_name = arabic_reshaper.reshape(f"الاسم: {name}")
    bidi_name = get_display(reshaped_name)

    reshaped_level = arabic_reshaper.reshape(f"التصنيف: {level}")
    bidi_level = get_display(reshaped_level)

    c.setFont("Arabic", 14)
    c.drawRightString(width - 50, height - 50, bidi_title)
    
    c.setFont("Arabic", 12)
    c.drawRightString(width - 50, height - 80, bidi_name)
    c.drawRightString(width - 50, height - 100, bidi_level)

    # إعداد كائن النص للكتابة من اليمين لليسار
    text = c.beginText(width - 50, height - 140)
    text.setFont("Arabic", 12)
    text.setLeading(20) # المسافة بين الأسطر

    # معالجة كل سطر من المحتوى على حدة
    for line in content.split("\n"):
        reshaped_line = arabic_reshaper.reshape(line)
        bidi_line = get_display(reshaped_line)
        # كتابة السطر المعالج بدون عكسه
        text.textLine(bidi_line)

    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- المنطق الرئيسي لعرض الأنشطة وتوليد الملفات ---
if not df.empty and 'الاسم' in df.columns and 'الدرجة' in df.columns and selected_lesson:
    st.subheader("✨ الأنشطة المقترحة")
    st.write("---")
    
    files_to_zip = []
    
    for index, row in df.iterrows():
        name, score = row['الاسم'], row['الدرجة']
        
        # التحقق من أن الاسم ليس فارغاً وأن الدرجة رقمية
        if pd.notna(name) and name.strip() != "" and pd.notna(score):
            level, content = generate_activity(name, float(score), selected_lesson)
            st.markdown(f"**👤 {name} — {level}**")
            st.code(content)
            
            try:
                pdf_buffer = create_pdf(name, level, content)
                files_to_zip.append((f"{name}.pdf", pdf_buffer.getvalue()))
            except Exception as e:
                st.warning(f"لم يتمكن من إنشاء ملف PDF للطالب {name}. الخطأ: {e}")
            st.write("---")

    if files_to_zip:
        zip_buf = BytesIO()
        with ZipFile(zip_buf, "w") as zipf:
            for filename, data in files_to_zip:
                zipf.writestr(filename, data)
        
        zip_buf.seek(0)
        
        b64 = base64.b64encode(zip_buf.read()).decode()
        download_filename = f"أنشطة_{selected_lesson.replace(' ', '_')}.zip"
        href = f'<a href="data:application/zip;base64,{b64}" download="{download_filename}" style="text-align: center; display: block; background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; text-decoration: none;">📥 تحميل جميع ملفات PDF كملف مضغوط</a>'
        st.markdown(href, unsafe_allow_html=True)
elif not df.empty:
    st.warning("يرجى التأكد من أن ملف الإكسل يحتوي على عمودين بالاسمين 'الاسم' و 'الدرجة' تماماً.")


