import openai
import streamlit as st
import PyPDF2
import docx
import re

# --- Load API key from secrets.toml ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Image path (consistently used) ---
image_path = "Logo.jpg"
st.sidebar.image(image_path)

# --- Header and Caption ---
st.header("Empower Your Ideas", divider="blue")
st.caption("Welcome to a platform designed to help students analyze real-world city and water challenges. Explore urban planning, environmental issues, or community well-being, and brainstorm impactful solutions!")

# --- Session Initialization ---
for key, default in [('conversation', []), ('current_problem', ""), ('analysis_completed', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- AI Call Function ---
def get_analysis(prompt, model="gpt-3.5-turbo"):
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert in analyzing real-world city and community challenges, particularly those relevant to the City of San Jose and Valley Water.  

                **Broader Context**  
                **Stakeholders and Their Challenges**  
                **Alternative Methods and Tools**  
                **Budget Considerations**  
                **Existing Efforts and Initiatives**  
                **Challenges in Implementation**  
                **Potential Impact if Unresolved**  
                **Overall Recommendation**  
                """
            },
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# --- File Parsing Function ---
def parse_files(files):
    insights = []
    for file in files:
        ext = file.name.split(".")[-1].lower()
        text = ""
        if ext == "txt":
            text = file.getvalue().decode("utf-8")
        elif ext == "pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif ext == "docx":
            doc = docx.Document(file)
            text = "\n".join(p.text for p in doc.paragraphs)
        snippet = text[:500].replace("\n", " ")
        insights.append(f"📄 **{file.name}** (excerpt): {snippet}...")
    return "\n".join(insights)

# --- Website Summary Function ---
def summarize_links(links):
    summaries = []
    for link in links:
        try:
            summary = get_analysis(f"Summarize concisely: {link}")
            summaries.append(f"🔗 **[{link}]({link})**: {summary}")
        except:
            summaries.append(f"🔗 **[{link}]({link})**: No summary available.")
    return "\n".join(summaries)

# --- Problem Input Handling ---
if not st.session_state['current_problem']:
    st.subheader("Let's Analyze a Real-World Problem!")
    
    # Ensure all input elements are correctly formatted
    problem = st.text_input("Describe the problem you are analyzing:", placeholder="e.g., How to increase foot traffic outside downtown San Jose")
    links = st.text_area("Add links or references (separate multiple links with commas):", placeholder="e.g., https://example1.com, https://example2.com")
    uploaded_files = st.file_uploader("Upload supporting documents:", type=["pdf", "txt", "docx"], accept_multiple_files=True)

    if st.button("Analyze the Problem") and problem:
        st.session_state['current_problem'] = problem
        summarized_links = summarize_links(links.split("\n")) if links else "No links provided."
        summarized_files = parse_files(uploaded_files) if uploaded_files else "No files uploaded."

        prompt = f"""
        **Problem Description:** {problem}

        **Relevant Website Links (if available):** {summarized_links}

        **Insights from Uploaded Files (if available):** {summarized_files}

        Use these insights to generate a **structured analysis** and actionable recommendations.
        """

        response = get_analysis(prompt)
        st.session_state['conversation'].append({'user': problem, 'ai': response})
        st.session_state['analysis_completed'] = True
        st.rerun()

# --- Display AI Response (Only if a problem is set) ---
if st.session_state['current_problem']:
    st.subheader("Analysis Results")

    # Display the AI response directly
    for entry in st.session_state['conversation']:
        st.markdown(entry['ai'])

    # --- Reset Problem ---
    if st.button("🔄 Start New Problem"):
        st.session_state['conversation'] = []
        st.session_state['current_problem'] = ""
        st.session_state['analysis_completed'] = False
        st.rerun()
