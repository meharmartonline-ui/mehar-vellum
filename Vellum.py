import streamlit as st
import io, base64
import urllib.parse
import requests

st.set_page_config(page_title="MEHAR VELLUM", layout="centered")
st.title("🌍 MEHAR VELLUM")
st.caption("Photo dalo -> Kahani banegi -> Awaz banegi")

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")

# NEW: API Choice - Maine khud add kiya
api_choice = st.sidebar.selectbox("Konsa AI use karna hai?", ["Gemini - Free Vision ✅", "Groq - Paid Vision"])

gemini_key = st.secrets.get("GEMINI_API_KEY", "")
if not gemini_key:
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

groq_key = st.secrets.get("GROQ_API_KEY", "")
if not groq_key:
    groq_key = st.sidebar.text_input("Groq API Key", type="password")

groq_model = st.sidebar.text_input("Groq Model", value="meta-llama/llama-4-scout-17b-16e-instruct")
gemini_model = "gemini-2.5-flash"

# Voice Speed
speed_choice = st.sidebar.selectbox("🎙️ Awaz ki Speed", ["Slow", "Normal", "Fast"])
slow_val = True if speed_choice == "Slow" else False

# History
if "history" not in st.session_state:
    st.session_state.history = []
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Pichli Kahaniyan")
if st.session_state.history:
    for i, h in enumerate(st.session_state.history[-5:]):
        if st.sidebar.button(f"{i+1}. {h[:30]}...", key=f"hist_{i}"):
            st.session_state["story"] = h
else:
    st.sidebar.caption("Abhi koi kahani nahi bani")

# --- Language ---
lang_map = {
    "Urdu (اردو)": "ur",
    "Sindhi (سنڌي)": "ur",
    "Hindi (हिन्दी)": "hi",
    "Arabic (العربية)": "ar",
    "English": "en",
    "Punjabi (پنجابی)": "pa",
}
lang_choice = st.selectbox("👉 Kis Language me kahani chahiye?", list(lang_map.keys()))
lang_name = lang_choice.split(" ")[0]
lang_code = lang_map[lang_choice]

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("🎭 Genre", ["Noir Mystery", "Literary Fiction", "Gothic", "Speculative", "Intimate Memoir", "Horror", "Love Story", "Village Story"])
with col2:
    length_choice = st.selectbox("📏 Kahani ki Lambai", ["Choti (150 words)", "Medium (300 words)", "Lambi (600 words)"])
    length_words = "150-200" if "Choti" in length_choice else "300-400" if "Medium" in length_choice else "600-700"

uploaded = st.file_uploader("📸 Photo Upload karo", type=["jpg","png","jpeg"])
if uploaded:
    st.image(uploaded, caption="Aap ki Photo", use_container_width=True)

author_dir = st.text_input("✍️ Author Direction (Optional)", placeholder="e.g. First-person narrator, darawani kahani")

with st.expander("💡 Kahani ke Ideas"):
    st.write("• Is photo me jo larka hai, wo 10 saal baad wapas aaya hai...")
    st.write("• Baarish wali raat, aur ye purana ghar...")
    st.write("• Is larki ko ek purana khat milta hai...")

if st.button("✨ Kahani Banao", use_container_width=True):
    # Check Key
    active_key = gemini_key if "Gemini" in api_choice else groq_key
    if not active_key:
        st.error("Pehle Sidebar ya Secrets me API Key dalo")
    elif not uploaded:
        st.error("Pehle Photo Upload karo")
    else:
        with st.spinner("Kahani likhi ja rahi hai..."):
            img_bytes = uploaded.getvalue()
            b64 = base64.b64encode(img_bytes).decode()
            prompt = f"""You are a master storyteller like Vellum.
            Look at this image carefully.
            Write a beautiful, emotional, cinematic story in {lang_name} language ONLY.
            Genre: {genre}
            Author Direction: {author_dir}
            Story Length: {length_words} words.
            Rules:
            - Full story must be in {lang_name} language, not English.
            - Start with a strong hook.
            - Use sensory details: rain, light, smell, sound.
            - Give a title at top.
            - Return ONLY story, no English explanation.
            """

            # ===== GEMINI - Maine khud add kiya =====
            if "Gemini" in api_choice:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={active_key}"
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": prompt},
                                {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
                            ]
                        }]
                    }
                    r = requests.post(url, json=payload, timeout=120)
                    if r.status_code == 200:
                        story = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        st.session_state["story"] = story
                        st.session_state.history.append(story)
                        st.success(f"✅ Kahani {lang_name} me ban gayi!")
                    else:
                        st.error("Gemini Fail: " + r.text[:500])
                except Exception as e:
                    st.error(f"Error: {e}")

            # ===== GROQ =====
            else:
                headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}
                payload = {
                    "model": groq_model,
                    "temperature": 0.8,
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}
                    ]
                }
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=120)
                if r.status_code == 200:
                    story = r.json()["choices"][0]["message"]["content"].strip()
                    st.session_state["story"] = story
                    st.session_state.history.append(story)
                    st.success(f"✅ Kahani {lang_name} me ban gayi!")
                else:
                    st.error("Groq Fail: " + r.text[:500])

if "story" in st.session_state:
    story = st.session_state["story"]
    words = len(story.split())
    st.caption(f"📊 Words: {words} | Reading Time: {max(1, words//150)} min | Language: {lang_name}")

    story = st.text_area("📖 Aap ki Kahani", st.session_state["story"], height=350)
    st.session_state["story"] = story

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🎙️ Awaz Banao", use_container_width=True):
            with st.spinner("Awaz ban rahi hai..."):
                try:
                    from gtts import gTTS
                    tts = gTTS(text=story[:4000], lang=lang_code, slow=slow_val)
                    buf = io.BytesIO()
                    tts.write_to_fp(buf)
                    buf.seek(0)
                    st.audio(buf, format="audio/mp3")
                    st.download_button("⬇️ MP3 Download", buf, file_name="mehar_vellum.mp3")
                except Exception as e:
                    st.error(f"Awaz me masla: {e}")
                    st.info("Sindhi ke liye Urdu select karke try karo.")
    with c2:
        st.download_button("📄 Kahani Download (TXT)", story, file_name="mehar_vellum_kahani.txt", use_container_width=True)
    with c3:
        wa_msg = urllib.parse.quote(story[:1000])
        st.markdown(f"[📲 WhatsApp par Bhejo](https://wa.me/?text={wa_msg})")

    if st.button("🗑️ Kahani Saaf Karo"):
        del st.session_state["story"]
        st.rerun()
