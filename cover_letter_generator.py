import gradio as gr
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# === Gemini API Key Setup ===
genai.configure(api_key="AIzaSyABjjtDkWlJTGYgy5mkagHlDAEhpPTm1JI")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

cover_history = []

# === PDF Export ===
def export_pdf(text):
    filename = f"Cover_Letter_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename

# === Cover Letter Generator ===
def generate_cover_letter(name, title, company, experience, skills, achievements, tone):
    prompt = f"""
    Write a professional cover letter in a {tone.lower()} tone using the following details:
    - Name: {name}
    - Job Title: {title}
    - Company: {company}
    - Experience: {experience}
    - Skills: {skills}
    - Achievements: {achievements}
    Format it as a formal job application cover letter.
    """
    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        cover_history.append(f"[{timestamp}] {title} at {company}")
        return output, "\n".join(cover_history[-5:])
    except Exception as e:
        return f"Error: {str(e)}", ""

# === Gradio App ===
with gr.Blocks(css="""
    .gr-box {
        max-width: 900px;
        margin: auto;
        padding: 30px 40px;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 0 12px rgba(0,0,0,0.05);
    }
    .gr-button {
        font-weight: bold;
        padding: 12px 18px;
        border-radius: 8px;
    }
    .main-title {
        font-size: 2.6rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #cbd5e1;
        font-size: 1.1rem;
        max-width: 750px;
        margin: auto;
    }
    footer {
        text-align: center;
        margin-top: 40px;
        font-size: 0.85rem;
        color: #aaa;
    }
""") as app:
    
    # === Header Section ===
    gr.HTML("""
    <div style='text-align:center; padding: 32px; background-color:#1e293b; border-radius:12px;'>
        <h1 class='main-title'>AI Cover Letter Generator</h1>
        <p class='subtitle'>Generate tailored, professional cover letters based on your skills and experience. Download as PDF or copy instantly.</p>
    </div>
    """)

    # === Input Section Title ===
    gr.Markdown("### 🧾 Enter Your Details")

    # === Layout ===
    with gr.Row():
        with gr.Column():
            name = gr.Textbox(label="Your Name")
            title = gr.Textbox(label="Target Job Title")
            company = gr.Textbox(label="Company Name")
            experience = gr.Textbox(label="Relevant Experience", lines=3, placeholder="Mention years and industries")
            skills = gr.Textbox(label="Key Skills", lines=2, placeholder="E.g. Python, Project Management, Leadership")
            achievements = gr.Textbox(label="Notable Achievements", lines=3, placeholder="E.g. Led a team of 10, published 2 research papers")
            tone = gr.Radio(["Formal", "Confident", "Friendly"], label="Tone", value="Formal")
            generate_btn = gr.Button("✨ Generate Cover Letter")

        with gr.Column():
            output = gr.Textbox(label="Generated Cover Letter", lines=20, interactive=False)
            history_box = gr.Textbox(label="Session History", lines=4, interactive=False)
            with gr.Row():
                pdf_btn = gr.Button("⬇️ Download as PDF")
                copy_btn = gr.Button("📋 Copy to Clipboard")
            download_file = gr.File(label="Download File")

    # === Button Events ===
    generate_btn.click(fn=generate_cover_letter, 
                       inputs=[name, title, company, experience, skills, achievements, tone],
                       outputs=[output, history_box])
    
    pdf_btn.click(fn=export_pdf, inputs=output, outputs=download_file)
    copy_btn.click(None, inputs=output, outputs=None, js="navigator.clipboard.writeText(arguments[0]);")

    # === Footer ===
    gr.HTML("<footer>© 2024 Cover Letter Generator · Built with Gradio & Gemini API</footer>")

app.launch()
