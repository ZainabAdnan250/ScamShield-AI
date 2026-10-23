
import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

try:
    API_KEY = st.secrets.get(
        "GEMINI_API_KEY",
        os.getenv("GEMINI_API_KEY")
    )
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemma-4-26b-a4b-it"

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# DARK CYBERSECURITY UI
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: #0B1120;
        color: #E2E8F0;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.95);
    }

    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
    }

    p, label, .stCaption {
        color: #CBD5E1;
    }

    .hero {
        background: linear-gradient(135deg, #111827, #172554);
        border: 1px solid #1D4ED8;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;
    }

    .eyebrow {
        color: #38BDF8;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin: 12px 0;
        color: #F8FAFC;
    }

    .hero-description {
        color: #CBD5E1;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-card {
        background: #111827;
        border: 1px solid #293548;
        border-radius: 14px;
        padding: 20px;
        margin: 12px 0;
    }

    div[data-testid="stTextArea"] textarea {
        background: #111827;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #38BDF8;
        box-shadow: 0 0 0 1px #38BDF8;
    }

    div.stButton > button {
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.2rem;
        font-weight: 700;
        min-height: 46px;
    }

    div.stButton > button:hover {
        background: #1D4ED8;
        color: white;
        border: 1px solid #38BDF8;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: #293548;
    }

    .footer {
        text-align: center;
        color: #64748B;
        font-size: 12px;
        margin-top: 35px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD AGENT SKILL
# --------------------------------------------------

SKILL_PATH = (
    BASE_DIR / "skills" / "scam-analysis" / "SKILL.md"
)

if SKILL_PATH.exists():
    SKILL_INSTRUCTIONS = SKILL_PATH.read_text(
        encoding="utf-8"
    )
else:
    SKILL_INSTRUCTIONS = """
Identify scam indicators using evidence.
Explain risk and suggest safe actions.
Do not invent facts or claim certainty without evidence.
"""

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="eyebrow">AI-POWERED SECURITY</div>
    <div class="hero-title">🛡️ ScamShield AI</div>
    <p class="hero-description">
        Detect suspicious messages. Understand the risks.
        Make safer decisions.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# MESSAGE INPUT
# --------------------------------------------------

st.markdown("## 🔍 Scan a Suspicious Message")

st.markdown(
    "Analyze suspicious SMS messages, emails, job offers, "
    "and prize notifications using Gemma AI."
)

message = st.text_area(
    "Message to analyze",
    placeholder=(
        "Paste a suspicious message here...\n\n"
        "Example: You won a prize! Pay a fee immediately "
        "to claim your reward."
    ),
    height=190,
)

st.caption(
    "🔒 Do not enter passwords, verification codes, "
    "or other private information."
)

analyze = st.button(
    "🔍  Analyze Message",
    type="primary",
    use_container_width=True,
)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if analyze:

    if not message.strip():
        st.warning("Please enter a message first.")

    elif not API_KEY:
        st.error(
            "Gemini API key not found. Check GEMINI_API_KEY "
            "in your local .env file."
        )

    else:
        prompt = f"""
You are ScamShield AI, a careful scam-analysis assistant.

Follow these agent skill instructions:
{SKILL_INSTRUCTIONS}

Analyze the message below using evidence only.

MESSAGE:
--- START ---
{message}
--- END ---

Write a complete, useful report using EXACTLY these four
headings, in this order:

## Risk Level
Choose High, Medium, or Low. Explain the rating briefly.

## Red Flags
List warning signs actually present in the message.
If evidence is limited, say so.

## Why It May Be Suspicious
Explain the evidence and why it may indicate a scam.
Separate facts from uncertainty.

## Recommended Safety Steps
Give practical steps the user can take to stay safe.

IMPORTANT:
- Complete all four sections.
- Do not stop after the risk rating.
- Keep each section concise but informative.
- Do not invent links, facts, or sender details.
- Do not claim a message is definitely safe.
- If evidence is insufficient, explain that clearly.
"""

        try:
            client = genai.Client(api_key=API_KEY)

            with st.spinner(
                "🛡️ Gemma is analyzing your message..."
            ):
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config={
                        "max_output_tokens": 800,
                    },
                )

            result = (response.text or "").strip()

            st.markdown("---")
            st.markdown("## 🛡️ Security Analysis")
            st.caption(
                f"Model: {MODEL_NAME} · ScamShield AI"
            )

            if not result:
                st.warning(
                    "The model returned an empty response. "
                    "Please try again."
                )

            else:
                # Split the report into its named sections.
                parts = re.split(
                    r"(?m)^##\s+",
                    result
                )

                sections = {}

                for part in parts:
                    part = part.strip()

                    if not part:
                        continue

                    lines = part.splitlines()
                    heading = lines[0].strip().rstrip("#")
                    body = "\n".join(lines[1:]).strip()

                    if body:
                        sections[heading.lower()] = (
                            heading,
                            body
                        )

                expected = [
                    "risk level",
                    "red flags",
                    "why it may be suspicious",
                    "recommended safety steps",
                ]

                # Display a section card for each heading found.
                found_sections = 0

                for expected_heading in expected:
                    matched = next(
                        (
                            value
                            for key, value in sections.items()
                            if expected_heading in key
                        ),
                        None,
                    )

                    if matched:
                        heading, body = matched
                        with st.container(border=True):
                            st.markdown(f"### {heading}")
                            st.markdown(body)

                        found_sections += 1

                # Preserve the model's response if its formatting
                # does not match the expected headings.
                if found_sections == 0:
                    with st.container(border=True):
                        st.markdown(result)

                elif found_sections < len(expected):
                    st.warning(
                        "The AI returned an incomplete report. "
                        "Review the sections shown above and "
                        "try again if necessary."
                    )

            st.caption(
                "⚠️ AI can make mistakes. Verify suspicious "
                "messages independently before taking action."
            )

        except Exception as error:
            st.error(
                "Gemma API request failed. Check your internet "
                "connection, API key, model access, and quota."
            )
            with st.expander("Technical details"):
                st.code(str(error))

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    SCAMSHIELD AI · AI-POWERED SCAM AWARENESS
</div>
""", unsafe_allow_html=True)
