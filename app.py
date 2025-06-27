# LinkedIn Profile Analyzer App

import streamlit as st
from fpdf import FPDF
import re
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


st.set_page_config(page_title="LinkedIn Profile Analyzer", layout="wide")

st.title("🧠 LinkedIn Profile Analyzer - AI Version")
st.sidebar.title("Upload Your Profile Text or Resume")

# ---------------------------------
# 🔰 INPUT SECTION (Always Visible)
# ---------------------------------

input_option = st.sidebar.radio("Choose Input Type", ["Type Text", "Upload Resume"])

if input_option == "Type Text":
    profile_text = st.text_area("✍️ Paste your LinkedIn 'About' section or resume text here", height=300)
else:
    uploaded_file = st.sidebar.file_uploader("Upload a TXT file", type=["txt"])
    if uploaded_file is not None:
        profile_text = uploaded_file.read().decode("utf-8")
    else:
        profile_text = ""

submitted = st.button("Submit")

# ---------------------------------
# 🚀 FEATURES (Run After Submit)
# ---------------------------------

if submitted and profile_text:

    st.subheader("✅ Profile Text Received")
    st.write(profile_text)

    # -------------------------------
    # 💡 SMART PROFILE SUGGESTIONS + SCORING
    # -------------------------------

    st.subheader("💡 Smart Profile Suggestions and Scoring")

    profile_checklist = {
        "Profile Picture": "Clear, professional photo with good lighting and appropriate attire.",
        "Background Image": "Relevant, visually appealing banner image.",
        "Headline": "Describes current role or career aspirations with industry keywords.",
        "Summary/About": "Impactful summary with career highlights, values, and aspirations.",
        "Experience": "Detailed job descriptions with achievements, responsibilities, and quantifiable results.",
        "Skills": "Relevant skills endorsed by connections.",
        "Recommendations": "Genuine recommendations highlighting skills and work ethics.",
        "Education": "Degrees, certifications, and relevant coursework listed clearly.",
        "Certifications": "Professional certifications from recognized platforms or institutions.",
        "Projects": "Notable projects described with scope and impact.",
        "Achievements": "Awards, recognitions, milestones, and notable accomplishments.",
        "Activity": "Regular engagement: posts, comments, shares on relevant topics.",
        "Networking": "Professional network with 300+ connections.",
        "Contact Information": "Professional email and links to portfolio, website, or blog.",
        "Custom LinkedIn URL": "Personalized LinkedIn URL.",
        "SEO and Keywords": "Industry-relevant keywords throughout the profile for search visibility.",
        "Volunteering & Interests": "Volunteer work and personal interests showing personality and social responsibility.",
        "Languages": "Languages spoken with proficiency levels.",
        "Multimedia": "Portfolio, presentations, videos, or documents showcasing work.",
        "Profile Activity Stats": "Shows metrics like profile views, search appearances, and content engagement."
    }

    missing_items = []
    matched_items = 0
    total_items = len(profile_checklist)

    for item, description in profile_checklist.items():
        if item.lower() not in profile_text.lower():
            missing_items.append(f"❌ Missing: {item} → {description}")
        else:
            matched_items += 1

    if missing_items:
        st.subheader("⚠️ Profile Improvement Suggestions:")
        for suggestion in missing_items:
            st.warning(suggestion)
    else:
        st.success("✅ Your profile covers all major sections! Excellent job!")

    score = int((matched_items / total_items) * 100)

    st.subheader("📊 Profile Completeness Score")
    st.metric("⭐ Profile Score", f"{score} / 100")

    if score == 100:
        st.success("🎯 Excellent! Your LinkedIn profile is fully optimized!")
    elif score >= 80:
        st.info("👍 Great profile! Minor improvements possible.")
    elif score >= 60:
        st.warning("⚠️ Profile is decent but needs several improvements.")
    else:
        st.error("❌ Profile is incomplete. Major improvements needed.")

    # -------------------------------
    # 🔍 SUMMARY AND KEYWORDS
    # -------------------------------

    st.subheader("🔍 Profile Summary and Keywords")

    summary = profile_text[:300] + "..." if len(profile_text) > 300 else profile_text

    st.write("**Summary:**")
    st.success(summary)

    words = re.findall(r'\b\w+\b', profile_text.lower())
    common_words = ["the", "and", "with", "from", "about", "that", "this", "for", "have", "are"]
    keywords = [w for w in words if len(w) > 5 and w not in common_words]
    keywords = list(set(keywords))[:10]

    st.write("**Keywords:**")
    st.info(", ".join(keywords))


    # -------------------------------
    # 🔧 GRAMMAR CHECK (BASIC)
    # -------------------------------

    st.subheader("🔧 Grammar Check (Basic)")

    errors = []

    if "i am" in profile_text.lower():
        errors.append("🔧 Capitalize 'I' → should be 'I am'.")

    if "i have" in profile_text.lower():
        errors.append("🔧 Capitalize 'I' → should be 'I have'.")

    if profile_text.strip().endswith(".") == False:
        errors.append("🔧 End your summary with a period (.)")

    if len(errors) == 0:
        st.success("✅ No basic grammar issues found!")
    else:
        for error in errors:
            st.error(error)


    # -------------------------------
    # 📄 PDF RESUME GENERATOR
    # -------------------------------

    st.subheader("📄 Generate PDF Resume")

    if st.button("Download Resume as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Resume Generated by LinkedIn Profile Analyzer", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, profile_text)

        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, txt="Generated using Streamlit and Python", ln=True, align="C")

        pdf.output("Generated_Resume.pdf")
        st.success("✅ Resume saved as 'Generated_Resume.pdf' in your project folder.")


    # -------------------------------
    # ✍️ SIMPLE AI REWRITER
    # -------------------------------

    st.subheader("✍️ AI Rewriter (Simple Version)")

    if st.button("Rewrite My Profile"):
        if len(profile_text) < 50:
            st.warning("⚠️ Please enter more text to rewrite.")
        else:
            sentences = profile_text.split('.')
            rewritten = '. '.join([sentence.strip().capitalize() for sentence in sentences if sentence.strip()]) + '.'

            st.success("Here is your rewritten profile text:")
            st.write(rewritten)


    # -------------------------------
    # 🤖 ADVANCED AI REWRITER (HuggingFace)
    # -------------------------------

    st.subheader("🤖 Advanced AI Rewriter (Using HuggingFace)")

    @st.cache_resource
    def load_model():
        model_name = "ramsrigouthamg/t5_paraphraser"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        return tokenizer, model

    tokenizer, model = load_model()

    def paraphrase_text(input_text):
        text = "paraphrase: " + input_text + " </s>"
        encoding = tokenizer.encode_plus(text, padding='max_length', return_tensors="pt", max_length=256, truncation=True)
        input_ids, attention_masks = encoding["input_ids"], encoding["attention_mask"]

        outputs = model.generate(
            input_ids=input_ids, attention_mask=attention_masks,
            max_length=256,
            do_sample=True,
            top_k=120,
            top_p=0.95,
            early_stopping=True,
            num_return_sequences=1
        )

        paraphrased = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return paraphrased

    if st.button("Run Advanced AI Rewrite"):
        if len(profile_text) < 10:
            st.warning("⚠️ Please enter more text to rewrite.")
        else:
            with st.spinner("AI is rewriting..."):
                rewritten_output = paraphrase_text(profile_text)
                st.success("✅ Here is your rewritten profile text:")
                st.write(rewritten_output)


    # -------------------------------
    # 🎭 TONE CHANGER
    # -------------------------------

    st.subheader("🎭 Tone Changer")

    tone = st.selectbox("Choose tone", ["Formal", "Friendly", "Confident"])

    if st.button("Change Tone"):
        if len(profile_text) < 10:
            st.warning("⚠️ Please enter more text to change tone.")
        else:
            if tone == "Formal":
                changed_text = profile_text.replace("I'm", "I am").replace("I've", "I have").replace("don't", "do not")
            elif tone == "Friendly":
                changed_text = "Hey! 😊 " + profile_text.replace("I am", "I'm").replace("I have", "I've")
            elif tone == "Confident":
                changed_text = profile_text + " 💪 I am highly motivated and confident in my skills."

            st.success(f"✅ Tone changed to {tone}:")
            st.write(changed_text)
