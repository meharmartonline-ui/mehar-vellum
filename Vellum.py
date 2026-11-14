import streamlit as st
import io, base64
from gtts import gTTS

st.set_page_config(page_title="MEHAR VELLUM", layout="centered")
st.title("🌍 MEHAR VELLUM")
st.caption("Photo dalo -> Kahani banegi -> Awaz banegi")

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
groq_key = st.sidebar.text_input("Groq API Key", type="password")
groq_model = st.sidebar.text_input("Groq Model", value="meta-llama/llama-4-scout-17b-16e-instruct")

# --- Language ---
lang_map = {
    "Urdu (اردو)": "ur",
    "Sindhi (سنڌي)": "ur", # gTTS me Sindhi nahi, is liye Urdu awaz use hogi
    "Hindi (हिन्दी)": "hi",
    "Arabic (العربية)": "ar",
    "English": "en",
    "Punjabi (پنجابی)": "pa",
}
lang_choice = st.selectbox("👉 Kis Language me kahani chahiye?", list(lang_map.keys()))
lang_name = lang_choice.split(" ")[0]
lang_code = lang_map[lang_choice]

genre = st.selectbox("🎭 Genre", ["Noir Mystery", "Literary Fiction", "Gothic", "Speculative", "Intimate Memoir", "Horror", "Love Story", "Village Story"])

uploaded = st.file_uploader("📸 Photo Upload karo", type=["jpg","png","jpeg"])
if uploaded:
    st.image(uploaded, caption="Aap ki Photo", use_container_width=True)

author_dir = st.text_input("✍️ Author Direction (Optional)", placeholder="e.g. First-person narrator, darawani kahani")

if st.button("✨ Kahani Banao", use_container_width=True):
    if not groq_key:
        st.error("Pehle Sidebar me Groq API Key dalo")
    elif not uploaded:
        st.error("Pehle Photo Upload karo")
    else:
        with st.spinner("Kahani likhi ja rahi hai..."):
            import requests
            img_bytes = uploaded.getvalue()
            b64 = base64.b64encode(img_bytes).decode()
            prompt = f"""You are a master storyteller like Vellum.
            Look at this image carefully.
            Write a beautiful, emotional, cinematic story in {lang_name} language ONLY.
            Genre: {genre}
            Author Direction: {author_dir}
            Rules:
            - Full story must be in {lang_name} language, not English.
            - Start with a strong hook.
            - Use sensory details: rain, light, smell, sound.
            - Story should be 300-400 words.
            - Give a title at top.
            - Return ONLY story, no English explanation.
            """
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
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
                st.success(f"✅ Kahani {lang_name} me ban gayi!")
            else:
                st.error("Groq Fail: " + r.text[:500])

if "story" in st.session_state:
    story = st.text_area("📖 Aap ki Kahani", st.session_state["story"], height=350)
    st.session_state["story"] = story
    if st.button("🎙️ Awaz Banao", use_container_width=True):
        with st.spinner("Awaz ban rahi hai..."):
            try:
                # gTTS lambi kahani ko tukron me karega
                tts = gTTS(text=story[:4000], lang=lang_code, slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                st.audio(buf, format="audio/mp3")
                st.download_button("⬇️ MP3 Download", buf, file_name="mehar_vellum.mp3")
            except Exception as e:
                st.error(f"Awaz me masla: {e}")
                st.info("Sindhi ke liye Urdu select karke try karo.")
