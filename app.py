import streamlit as st
import json
import os
import fitz
from PIL import Image
from datetime import datetime
import random
import requests

# ===============================
# CONFIGURATION
# ===============================

st.set_page_config(
    page_title="Ramadan Quran Reader",
    layout="wide"
)


PDF_PATH = "quran.pdf"
PROGRESS_FILE = "progress.json"
TOTAL_PAGES = 607

# ===============================
# AUTO DOWNLOAD PDF FROM GOOGLE DRIVE
# ===============================

FILE_ID = "1UHV6e8GvwgbNm80cff0E6_skKJRN0X1a"
PDF_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

if not os.path.exists(PDF_PATH):
    with st.spinner("📥 Downloading Quran PDF... Please wait"):
        try:
            response = requests.get(PDF_URL)
            response.raise_for_status()
            with open(PDF_PATH, "wb") as f:
                f.write(response.content)
        except Exception as e:
            st.error(f"❌ Failed to download Quran PDF: {e}")
# ===============================
# SESSION STATE
# ===============================

if "page" not in st.session_state:
    st.session_state.page = 1

if "days" not in st.session_state:
    st.session_state.days = 30

if "start_day" not in st.session_state:
    st.session_state.start_day = datetime.now().date()

# Game state
if "game_progress" not in st.session_state:
    st.session_state.game_progress = {}

# ===============================
# PDF IMAGE FUNCTION
# ===============================

def get_pdf_page_image(pdf_path, page_number):

    doc = fitz.open(pdf_path)

    page_number = max(1, min(page_number, TOTAL_PAGES))

    page = doc[page_number - 1]

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# ===============================
# DESIGN STYLE
# ===============================

st.markdown("""
<style>
.block-container{
    background: linear-gradient(135deg,#0f3d2e,#14532d);
    color:white;
    padding:30px;
    border-radius:25px;
}

.stButton>button{
    background:#1b5e20;
    color:white;
    border-radius:20px;
    padding:6px 18px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================

st.markdown("""
<h1 style="
text-align:center;
font-size:80px;
margin-top:40px;
margin-bottom:40px;
">
🌙 Ramadan Kareem
</h1>
""", unsafe_allow_html=True)
# ===============================
# DAYS INPUT
# ===============================
st.title("🕋 ختم القرآن الكريم")

days = st.number_input(
    "📅 How many days to finish Quran?",
    min_value=1,
    step=1,
    value=st.session_state.days
)

st.session_state.days = days

# ===============================
# SEQUENTIAL SCHEDULING LOGIC
# ===============================

pages_per_day = TOTAL_PAGES / days if days > 0 else TOTAL_PAGES

days_since_start = (datetime.now().date() - st.session_state.start_day).days

current_day_index = min(days_since_start + 1, days)

day_start = int((current_day_index - 1) * pages_per_day) + 1
day_end = int(current_day_index * pages_per_day)

day_start = max(1, day_start)
day_end = min(TOTAL_PAGES, day_end)

st.info(f"📖 Today read pages {day_start} → {day_end}")

# ===============================
# NAVIGATION BUTTONS
# ===============================

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("⬅ Previous"):
        if st.session_state.page > day_start:
            st.session_state.page -= 2

with col3:
    if st.button("Next ➡"):
        if st.session_state.page < day_end:
            st.session_state.page += 2

# Clamp page inside block
st.session_state.page = max(day_start, st.session_state.page)
st.session_state.page = min(day_end, st.session_state.page)

# ===============================
# DAILY COMPLETION MESSAGE
# ===============================

pages_read_today = st.session_state.page - day_start + 2

if pages_read_today >= pages_per_day:
    st.success("🎉 You finished your daily Quran reading! Come back tomorrow 🌙")

# ===============================
# DISPLAY MERGED BOOK VIEW
# ===============================

st.markdown(f"### 📖 Page {st.session_state.page} & {st.session_state.page + 1}")

if os.path.exists(PDF_PATH):

    try:
        img1 = get_pdf_page_image(PDF_PATH, st.session_state.page)

        if st.session_state.page + 1 <= TOTAL_PAGES:
            img2 = get_pdf_page_image(PDF_PATH, st.session_state.page + 1)

            total_width = img1.width + img2.width
            max_height = max(img1.height, img2.height)

            merged_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))

            merged_img.paste(img1, (0, 0))
            merged_img.paste(img2, (img1.width, 0))
        else:
            merged_img = img1

        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            st.image(merged_img, width=700)

    except Exception as e:
        st.error(f"PDF Rendering Error: {e}")

else:
    st.error("❌ Quran PDF file not found!")

# ===============================
# TASBIH POP STAR GAME
# ===============================

st.markdown("---")
st.title("📿 تسبيحاتي")

tasbih_items = {
    "سبحان الله": 33,
    "الحمد لله": 33,
    "الله أكبر": 34,
    "لا إله إلا الله": 100
}

selected_tasbih = st.selectbox(
    "",
    list(tasbih_items.keys())
)

target = tasbih_items[selected_tasbih]

# Initialize game state
if selected_tasbih not in st.session_state.game_progress:
    st.session_state.game_progress[selected_tasbih] = [False] * target

balloons = st.session_state.game_progress[selected_tasbih]

st.write(f"🎯 الهدف: {target}")

# Grid layout
cols = st.columns(18)

for i in range(target):

    col = cols[i % 18]

    with col:

        if balloons[i]:
            st.write("✨")

        else:
            if st.button("⭐", key=f"{selected_tasbih}_{i}"):

                balloons[i] = True
                st.session_state.game_progress[selected_tasbih] = balloons
                st.rerun()

# ===============================
# DUAA OF THE DAY (STABLE RANDOM)
# ===============================

st.markdown("---")

st.title("🤲 دعاء اليوم")

duas = [
    ("اللهم بلغنا رمضان", "دعاء لطلب بلوغ شهر رمضان والبركة فيه."),
    ("اللهم أعنا على ذكرك وشكرك وحسن عبادتك", "دعاء لطلب العون على الطاعة والعبادة."),
    ("ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار", "دعاء شامل لخير الدنيا والآخرة."),
    ("اللهم اغفر لي ذنبي كله دقه وجله", "دعاء لطلب المغفرة من الله."),
    ("اللهم اهدني وسددني", "دعاء لطلب الهداية والاستقامة."),
    ("اللهم إني أسألك علماً نافعاً", "دعاء لطلب العلم النافع."),
    ("اللهم أصلح لي ديني الذي هو عصمة أمري", "دعاء إصلاح الدين والدنيا."),
    ("اللهم اجعل القرآن ربيع قلبي", "دعاء لطلب حب القرآن والأنس به."),
    ("اللهم ارزقني توبة نصوحاً", "دعاء للتوبة الصادقة."),
    ("اللهم ارحمني برحمتك يا أرحم الراحمين", "دعاء لطلب رحمة الله."),
    ("اللهم قني عذابك يوم تبعث عبادك", "دعاء للنجاة يوم القيامة."),
    ("اللهم زدني علماً", "دعاء لطلب زيادة العلم."),
    ("اللهم ثبت قلبي على دينك", "دعاء لثبات القلب على الإيمان."),
    ("اللهم بارك لي في وقتي", "دعاء للبركة في الوقت والعمل."),
    ("اللهم تقبل مني صلاتي وصيامي", "دعاء لقبول الطاعات.")
]

# Choose random duaa once per session
if "duaa_today" not in st.session_state:
    st.session_state.duaa_today = random.choice(duas)

duaa_title, duaa_desc = st.session_state.duaa_today

# Card UI
st.markdown(f"""
<div style="
    background: linear-gradient(135deg,#1b5e20,#14532d);
    padding:30px;
    border-radius:25px;
    text-align:center;
    color:white;
    box-shadow:0 0 15px rgba(255,255,255,0.1);
">


<h1 style="margin:20px 0;">🤲 {duaa_title}</h1>

<p style="font-size:18px; opacity:0.9;">
{duaa_desc}
</p>

</div>
""", unsafe_allow_html=True)
# ===============================
# SAVE PROGRESS
# ===============================

progress = {"last_page": st.session_state.page}

with open(PROGRESS_FILE, "w") as f:
    json.dump(progress, f)