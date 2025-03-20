import openai
import streamlit as st
import PyPDF2
import docx
import re

# --- Load API key from secrets.toml ---
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

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
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"""
                You are an expert in analyzing real-world city and community challenges, particularly those relevant to the City of San Jose and Valley Water.  
                
                **Instructions for Formatting:**  
                - Use clear section headers (e.g., "Broader Context", "Stakeholders and Challenges").  
                - Organize information into **concise paragraphs** for readability.  
                - Use **bullet points only where necessary** (avoid overusing lists).  
                - Avoid unnecessary formatting symbols (e.g., "**", "##", "--").  
                - Reference provided sources (website links/files) when relevant.  
                
                **Analysis Outline:**  
                1. **Broader Context** – Explain how this problem fits into larger economic, social, or environmental issues.  
                2. **Stakeholders and Their Challenges** – Discuss the key groups affected and their specific difficulties.  
                3. **Alternative Methods and Tools** – Suggest possible strategies, technologies, or policies.  
                4. **Budget Considerations** – Identify financial challenges and funding opportunities.  
                5. **Existing Efforts and Initiatives** Highlight ongoing city programs or policies.  
                6. **Challenges in Implementation** – Discuss barriers (political, technical, financial).  
                7. **Potential Impact if Unresolved**  Explain the risks of inaction.  
                8. **Overall Recommendation** – Summarize the best approach and provide a call to action.  
                
                **Keep responses well-structured, concise, and easy to read.**  
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

# --- Display AI Response (Only if a problem is set) ---
if st.session_state['current_problem']:
    st.subheader("Analysis Results")

    # Display the AI response directly (No user messages, No text bubbles)
    for entry in st.session_state['conversation']:
        st.markdown(entry['ai'])  # Just show AI output as Markdown

    # --- Move "Start New Problem" Button Here ---
    if st.button("🔄 Start New Problem"):
        st.session_state['conversation'] = []
        st.session_state['current_problem'] = ""
        st.session_state['analysis_completed'] = False
        st.rerun()

# --- Problem Input Handling ---
if not st.session_state['current_problem']:
    st.subheader("Let's Analyze a Real-World Problem!")
    
    problem = st.text_input("Describe the problem you are analyzing:", placeholder="e.g., How to increase foot traffic outside downtown San Jose")
    links = st.text_area(
    "Add links or references (separate multiple links with commas):",
    placeholder="e.g., https://example1.com, https://example2.com"
)
    uploaded_files = st.file_uploader("Upload supporting documents:", type=["pdf", "txt", "docx"], accept_multiple_files=True)

    if st.button("Analyze the Problem") and problem:
        st.session_state['current_problem'] = problem
        summarized_links = summarize_links(links.split("\n"))
        summarized_files = parse_files(uploaded_files)

        prompt = f"""
        **Problem Description:** {problem}

        **Relevant Website Links (if available):** {summarized_links if summarized_links else "No links provided."}

        **Insights from Uploaded Files (if available):** {summarized_files if summarized_files else "No files uploaded."}

        Use these insights to generate a **structured analysis** and actionable recommendations.
        """

        response = get_analysis(prompt)
        st.session_state['conversation'].append({'user': problem, 'ai': response})
        st.session_state['analysis_completed'] = True

# 1. If there is no current problem, show the input form
if not st.session_state['current_problem']:
    st.subheader("Let's Analyze a Real-World Problem!")
    problem = st.text_input(...)
    links = st.text_area(...)
    uploaded_files = st.file_uploader(...)
    
    if st.button("Analyze the Problem") and problem:
        # Summaries, parsing, call the model, etc.
        st.session_state['current_problem'] = problem
        response = get_analysis(...)
        st.session_state['conversation'].append({'user': problem, 'ai': response})
        st.session_state['analysis_completed'] = True

# 2. Else, if a problem is set, display results and let the user reset
else:
    st.subheader("Analysis Results")
    for entry in st.session_state['conversation']:
        st.markdown(entry['ai'])
    
    if st.button("🔄 Start New Problem"):
        st.session_state['conversation'] = []
        st.session_state['current_problem'] = ""
        st.session_state['analysis_completed'] = False
        st.rerun()

