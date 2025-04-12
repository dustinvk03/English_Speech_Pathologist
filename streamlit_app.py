import streamlit as st
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import timedelta
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import tempfile
import base64
from matplotlib.path import Path
import matplotlib.patches as patches
import html
import streamlit.components.v1 as components
import re  # Add this for regex pattern matching


# Configure the page
st.set_page_config(
    page_title="English Speech Pathologist v1",
    page_icon="🎙️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        color: #2563EB;
        font-size: 2.5rem !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #2563EB;
        font-size: 1.8rem !important;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .recommendation {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #f0f9ff;
        border-left: 4px solid #2563EB;
        margin-bottom: 0.75rem;
    }
    .strengths {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        margin-bottom: 0.75rem;
    }
    .category-header {
        font-size: 1.2rem !important;
        font-weight: 600;
        color: #2563EB;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #f0f9ff;
        padding: 0.5rem;
        border-radius: 0.3rem;
    }
    .error-legend {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        padding: 0.5rem;
        background-color: #f8fafc;
        border-radius: 0.3rem;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .legend-color {
        width: 1rem;
        height: 1rem;
        border-radius: 0.2rem;
    }
    .api-input-container {
        padding: 1rem;
        background-color: #f8fafc;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .record-button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
    }
    .audio-player {
        width: 100%;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to parse the content into different sections
def parse_content_sections(content):
    sections = {
        "discussion_questions": "",
        "key_vocabulary": "",
        "useful_expressions": "",
        "grammar_focus": ""
    }
    
    # Define regex patterns to extract each section
    patterns = {
        "discussion_questions": r"##\s*Discussion Questions.*?(?=##\s*Key Vocabulary|$)",
        "key_vocabulary": r"##\s*Key Vocabulary.*?(?=##\s*Useful Expressions|$)",
        "useful_expressions": r"##\s*Useful Expressions.*?(?=##\s*Grammar Focus|$)",
        "grammar_focus": r"##\s*Grammar Focus.*?(?=$)"
    }
    
    # Extract each section using regex
    for section_key, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections[section_key] = match.group(0).strip()
    
    return sections


# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'evaluated' not in st.session_state:
    st.session_state.evaluated = False
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = None
if 'content' not in st.session_state:
    st.session_state.content = None
if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False

# Define the password
# CORRECT_PASSWORD1 = PASSWORD1
# CORRECT_PASSWORD2 = PASSWORD2
# DEFAULT_API_KEY = API_KEY  # Your API Key

# Gemini API Configuration
def setup_gemini(api_key):
    genai.configure(api_key=api_key)
    
    # Set up the model
    generation_config = {
        "temperature": 0.5,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 8192,
    }
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    return model

# Function to record audio directly in the browser
def record_audio():
    st.markdown("""
    <script>
    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];
        
        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            // Create a download link
            const a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            a.href = audioUrl;
            a.download = "recording.wav";
            a.click();
            
            // Send the audio data to Streamlit
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = () => {
                const base64data = reader.result;
                // Use Streamlit component to send data back
                if (window.Streamlit) {
                    window.Streamlit.setComponentValue({
                        type: "audio",
                        data: base64data
                    });
                }
            };
        });
        
        // Start recording
        mediaRecorder.start();
        document.getElementById("recordButton").innerText = "Stop Recording";
        document.getElementById("recordButton").onclick = () => {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
            document.getElementById("recordButton").innerText = "Start Recording";
            document.getElementById("recordButton").onclick = startRecording;
        };
    };
    
    // Add the button when the page loads
    window.addEventListener("load", () => {
        const button = document.getElementById("recordButton");
        if (button) {
            button.onclick = startRecording;
        }
    });
    </script>
    
    <button id="recordButton" class="record-button">Start Recording</button>
    """, unsafe_allow_html=True)

# Create radar chart function
def create_radar_chart(categories, scores):
    # Convert to numpy array
    scores = np.array(scores)
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each category
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    
    # Make the plot circular
    scores = np.concatenate((scores, [scores[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    categories = np.concatenate((categories, [categories[0]]))
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
    
    # Draw the outline of the data
    ax.plot(angles, scores, 'o-', linewidth=2, color='#2563EB')
    
    # Fill the area
    ax.fill(angles, scores, alpha=0.25, color='#2563EB')
    
    # Set the labels
    ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
    
    # Set y-axis limits
    ax.set_ylim(0, 10)
    
    # Set the tick labels
    ax.set_rlabel_position(0)
    ax.set_rticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='grey', fontsize=1.5)
    
    # Add a title
    ax.set_title('Speech Evaluation Scores', fontsize=5, pad=3)
    
    # Customize the grid
    ax.grid(True, color='grey', linestyle='--', linewidth=0.3, alpha=0.5)
    
    # Customize the plot
    plt.tight_layout()
    
    return fig

# Generate content function
def generate_content(model, topic, duration, content_type, difficulty):
    try:
        # Calculate content length based on duration
        words_per_minute = 90  # Average speaking rate
        words_for_passage = int(duration * words_per_minute)
        questions_per_minute = 1
        question_count = int(duration * questions_per_minute)
        
        # Adjust for difficulty
        difficulty_factors = {
            "Beginner": {
                "vocab_level": "simple everyday vocabulary",
                "grammar_complexity": "basic sentence structures",
                "passage_style": "concrete topics with simple language"
            },
            "Intermediate": {
                "vocab_level": "moderate vocabulary with some idiomatic expressions",
                "grammar_complexity": "varied sentence structures with some complex forms",
                "passage_style": "mix of concrete and abstract topics"
            },
            "Advanced": {
                "vocab_level": "advanced vocabulary with idiomatic expressions",
                "grammar_complexity": "complex sentence structures and varied tenses",
                "passage_style": "abstract concepts and nuanced arguments"
            }
        }
        
        difficulty_settings = difficulty_factors[difficulty]
        
          
        if content_type == "Reading Passage":
            prompt = f"""
        Generate an engaging, authentic reading passage about "{topic}" suitable for {duration} minutes of speaking practice 
        for an {difficulty.lower()} English learner.
        
        The passage should:
        - Be approximately {words_for_passage} words long
        - Use {difficulty_settings['vocab_level']}
        - Employ {difficulty_settings['grammar_complexity']}
        - Focus on {difficulty_settings['passage_style']}
        - Include natural dialogue if appropriate
        - Incorporate common collocations and expressions
        - Address real-world situations and contexts
        - Be culturally sensitive and globally relevant
        - Have a clear structure with introduction, body, and conclusion
        
        For beginners: Focus on present tense, simple vocabulary, short sentences.
        For intermediate: Mix tenses, include some idiomatic expressions, varied sentence structure.
        For advanced: Use complex grammar, sophisticated vocabulary, nuanced concepts.
        
        Return only the passage text without any additional instructions or notes.
        """
            
        else:  # Prompt Questions
            prompt = f"""
            Generate {question_count} prompt questions about "{topic}" suitable for {duration} minutes of speaking practice 
            for an {difficulty.lower()} English learner.
            
            The questions should:
            - Progress from simpler to more complex
            - Be open-ended to encourage detailed responses
            - Use {difficulty_settings['vocab_level']}
            - Employ {difficulty_settings['grammar_complexity']}
            - Include follow-up questions to extend the conversation
            - Cover different aspects of the topic (personal, societal, global, etc.)
            - Encourage the learner to use specific vocabulary and grammar structures
            - Be organized in a clear numbered list
            
            Also include:
            - 3-6 useful vocabulary words/phrases specifically relevant to this topic
            - 2-5 useful expressions or sentence frames to incorporate
            - 2-3 grammar patterns that would be natural to use when discussing this topic
            
            Format the output as:
            
            ## Discussion Questions (Read carefully and answer thoughtfully)
            1. [Main question] 
            - [Follow-up question]
            - [Follow-up question]
            2. [Main question]
            - [Follow-up question]
            - [Follow-up question]
            ...
            
            ## Key Vocabulary (Use these words to enhance your responses)
            - [Term]: [Brief definition/usage example]
            - [Term]: [Brief definition/usage example]
            ...
            
            ## Useful Expressions (Incorporate these phrases into your answers)
            - [Expression]: [When/how to use it]
            - [Expression]: [When/how to use it]
            ...
            
            ## Grammar Focus (Use these structures to improve your fluency)
            - [Grammar pattern]: [Example sentence related to the topic]
            - [Grammar pattern]: [Example sentence related to the topic]
            ...
            """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        content = response.text
        
        # Parse the content into sections if it's "Prompt Questions"
        if content_type == "Prompt Questions":
            sections = parse_content_sections(content)
            return sections
        else:
            return content
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None
        
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

# Function to transcribe audio
def transcribe_audio(model, audio_file):
    try:
        # Create a temporary file to process the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio_path = tmp.name
            # Write the uploaded file to the temporary file
            if isinstance(audio_file, str):  # Simulated audio for demo
                # Just a placeholder for demo purposes
                with open(audio_path, 'wb') as f:
                    f.write(b'dummy audio data')
            else:
                # Real uploaded file
                audio_file.seek(0)
                with open(audio_path, 'wb') as f:
                    f.write(audio_file.read())
        
        # Read the audio file as bytes
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Prepare transcription prompt
        transcription_prompt = """
        Please provide a verbatim transcription of the speech in this audio file.
        Transcribe exactly what you hear including any filler words, repetitions, 
        or grammatical errors. Do not correct mistakes. Only output the raw transcription.
        """
        
        # Call Gemini API with the audio file
        response = model.generate_content([
            transcription_prompt,
            {"mime_type": "audio/wav", "data": audio_data}
        ])
        
        transcription = response.text.strip()
        
        # Clean up the temporary file if needed
        if hasattr(audio_file, 'read'):
            os.unlink(audio_path)
            
        return transcription
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Evaluate speech function
def evaluate_speech(model, audio_file, topic, duration, difficulty):
    try:
        # Get transcription from the actual audio file using Gemini API
        with st.spinner("Transcribing your audio..."):
            transcription = transcribe_audio(model, audio_file)
        
        if not transcription:
            st.error("Failed to transcribe audio. Please try again.")
            return None
            
        st.success("Audio transcribed successfully!")
        
        # Prepare evaluation prompt with the actual transcription
        evaluation_prompt = f"""
        Act as an English speech pathologist and evaluate this transcribed speech. 
        The speaker is an {difficulty.lower()} level English learner who spoke about "{topic}" for approximately {duration} minutes.
        
        Transcription: "{transcription}"
        
        Evaluate the following criteria on a scale of 1-10:
        1. Pronunciation (10-point scale):
           - Accuracy of phonemes (individual sounds)
           - Word stress placement
           - Sentence intonation patterns
           - Specific sound challenges (th, r, l, etc.)
           - Rhythm and connected speech
        
        2. Vocabulary (10-point scale):
           - Range and variety of words used
           - Appropriateness for the topic
           - Use of advanced/precise vocabulary vs. basic terms
           - Collocations and idiomatic expressions
           - Word choice accuracy
        
        3. Grammar (10-point scale):
           - Verb tense consistency and accuracy
           - Subject-verb agreement
           - Article usage (a/an/the)
           - Preposition usage
           - Sentence structure complexity and correctness
        
        4. Fluency (10-point scale):
           - Speech rate (too slow/fast?)
           - Hesitations and fillers (um, uh, like)
           - Pausing patterns (natural vs. unnatural)
           - Flow between ideas
           - Self-corrections and repetitions
        
        5. Coherence & Cohesion (10-point scale):
           - Logical organization of ideas
           - Use of discourse markers and transitions
           - Topic development and relevance
           - Clear beginning, middle, and conclusion
           - Connective devices between sentences
        
        For each criterion:
        - Provide a numerical score (1-10)
        - Provide 2-3 specific examples from the transcription that justify your score
        - Identify patterns (not just isolated errors)
        - Give 1-2 specific, actionable improvement suggestions tailored to the speaker's level
        - For intermediate/advanced learners, suggest not just corrections but enhancements
        
        Mark errors in the transcription using simple HTML:
        - Grammar errors: "<span style='background-color: #ffdddd; border-bottom: 1px dotted red;' title='Grammar correction: [correct form]'>[incorrect text]</span>"
        - Vocabulary errors: "<span style='background-color: #ffe6cc; border-bottom: 1px dotted orange;' title='Better word choice: [better word]'>[original word]</span>"
        - Usage errors: "<span style='background-color: #e6f2ff; border-bottom: 1px dotted blue;' title='Natural expression: [natural expression]'>[unnatural expression]</span>"        
        
        Additionally, identify 0-3 strengths the speaker demonstrated, to provide balanced feedback.

        Format your response as JSON with these sections:
        1. scores (numerical values for each criterion)
        2. transcription_with_errors (original text with HTML markup for errors)
        3. detailed_feedback (detailed feedback by category)
        4. improvement_recommendations (3 friendly, encouraging suggestions)
        
        The JSON structure should look like:
        {{
            "scores": {{
                "pronunciation": 7,
                "vocabulary": 6,
                "grammar": 8,
                "fluency": 7,
                "coherence": 6
            }},
            "transcription_with_errors": "The marked up transcription with HTML spans",
            "detailed_feedback": {{
                "pronunciation": "Detailed analysis...",
                "vocabulary": "Detailed analysis...",
                "grammar": "Detailed analysis...",
                "fluency": "Detailed analysis...",
                "coherence": "Detailed analysis..."
            }},
            "strengths": [
                "Strength 1 with specific example",
                "Strength 2 with specific example",
                "Strength 3 with specific example"
            ],
            "improvement_recommendations": [
                "Specific recommendation 1",
                "Specific recommendation 2"
            ]
        }}
        Your response MUST be in valid JSON format with:
        1. All property names in double quotes (not single quotes)
        2. All string values in double quotes (not single quotes)
        3. No trailing commas
        4. No JavaScript-style comments
        Ensure your response is valid JSON and can be parsed with json.loads(). DO NOT include any text outside the JSON object.
        """
        
        # Call Gemini API for evaluation
        with st.spinner("Evaluating your speech..."):
            response = model.generate_content(evaluation_prompt)
            
            # Try to parse the JSON response
            try:
                # Clean the response text to ensure it's valid JSON
                clean_response = response.text.strip()
                # If the response is wrapped in backticks (code block), remove them
                if clean_response.startswith("```json") and clean_response.endswith("```"):
                    clean_response = clean_response[7:-3].strip()
                elif clean_response.startswith("```") and clean_response.endswith("```"):
                    clean_response = clean_response[3:-3].strip()
                
                evaluation_results = json.loads(clean_response)
                if 'transcription_with_errors' in evaluation_results:
                    evaluation_results['transcription_with_errors'] = html.unescape(evaluation_results['transcription_with_errors'])
                
                # Store the raw transcription too
                evaluation_results["raw_transcription"] = transcription
                
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse the AI response as JSON. Error: {e}")
                st.text("Raw response:")
                st.text(response.text)
                return None
            
        return evaluation_results
    except Exception as e:
        st.error(f"Error evaluating speech: {str(e)}")
        return None

# Main app
def main():
    # Header
    st.markdown("<h1 class='main-header'>🎙️ English Speech Pathologist</h1>", unsafe_allow_html=True)
    st.markdown("<p>Improve your English speaking skills with AI-powered feedback. Author: Dustin</p>", unsafe_allow_html=True)
    st.markdown("<p>You set up what you want to learn, get useful vocabs and hints, then get evaluation by AI</p>", unsafe_allow_html=True)
    st.markdown("<p>NOTE: To run this, you either need a **password** or a **Gemini API** which can be obtained easily with a gmail acount here: https://aistudio.google.com/app/apikey </p>", unsafe_allow_html=True)
    st.markdown('<p><a href="https://www.dropbox.com/scl/fi/ht3hk1nafgnh4mqoblh2q/AI_Speech_Evaluation_Tutorial.mkv?rlkey=bpvocqyol9y5rbxtfp0r9sbyr&e=1&st=fiic77m7&dl=0" target="_blank" style="text-decoration: none; font-size: 18px; font-weight: bold;">GO TO INSTRUCTION VIDEO</a></p>', unsafe_allow_html=True)

    # API Key or Password input
    if not st.session_state.api_key_entered:
        st.markdown("<div class='api-input-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Authentication Required</h3>", unsafe_allow_html=True)
        
        auth_option = st.radio("Choose authentication method:", ["Enter Google API Key", "Enter Password"])
        
        if auth_option == "Enter Google API Key":
            api_key = st.text_input("Enter your Google API Key:", type="password")
            if st.button("Submit API Key"):
                if api_key:
                    try:
                        # Test the API key
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.0-flash")
                        model.generate_content("Hello")
                        st.session_state.api_key = api_key
                        st.session_state.api_key_entered = True
                        st.success("API Key validated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Invalid API Key: {str(e)}")
                else:
                    st.warning("Please enter an API Key")
        else:
            password = st.text_input("Enter password:", type="password")
            if st.button("Submit Password"):
                if password == CORRECT_PASSWORD1 or password == CORRECT_PASSWORD2:
                    st.session_state.api_key = DEFAULT_API_KEY
                    st.session_state.api_key_entered = True
                    st.success("Password accepted!")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Setup Gemini model with the API key
    model = setup_gemini(st.session_state.api_key)
    
    # App container
    main_container = st.container()
    
    with main_container:
        # If we haven't evaluated yet, show the setup form
        if not st.session_state.evaluated:
            with st.form("setup_form"):
                st.markdown("<h2 class='sub-header'>Practice Setup</h2>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Duration selector
                    duration = st.slider("Speaking Duration (minutes)", 1, 10, 2)
                    
                    # Topic selector
                    topic_options = ["Daily Reflection", "A Recent Movie or TV Show", "My Typical Weekend",  "Grocery Shopping Habits", "A IELTS Part 2", "The Last Time I Traveled",
                                     "A Recent Conversation with a Friend", "Foods I Dislike and Why", "My Favorite Book or Movie", "A Memorable Vacation", "A Recent News Event",
                                     "My Hometown", "My Favorite Hobby", "A Memorable Birthday", "A Time I Overcame a Challenge",  "A Memorable Meal",
                                     "My Job or Studies", "A Skill That's Important in My Field"]                    
                    topic = st.selectbox("Select a Topic", topic_options)
                
                with col2:
                    # Content type selector
                    content_type = st.radio("Content Type", ["Prompt Questions"])
                    
                    # Difficulty level
                    difficulty = st.select_slider("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
                
                # Submit button
                submit_button = st.form_submit_button("Generate Content")
                
                if submit_button:
                    with st.spinner("Generating content..."):
                        content = generate_content(model, topic, duration, content_type, difficulty)
                        if content:
                            st.session_state.content = content
                            st.session_state.topic = topic
                            st.session_state.duration = duration
                            st.session_state.difficulty = difficulty
            
            # If content has been generated, display it and recording options
            if st.session_state.content:
                st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                st.markdown("<h2 class='sub-header'>Speaking Practice Content</h2>", unsafe_allow_html=True)
                # st.markdown(st.session_state.content, unsafe_allow_html=True)
                
                # If content has been generated, display it and recording options
            if st.session_state.content:
                st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                st.markdown("<h2 class='sub-header'>Speaking Practice Content</h2>", unsafe_allow_html=True)
                
                # Check if content is a dictionary (parsed sections) or raw string
                if isinstance(st.session_state.content, dict):
                    # Create tabs for each section
                    tabs = st.tabs(["Discussion Questions", "Key Vocabulary", "Useful Expressions", "Grammar Focus"])
                    
                    with tabs[0]:
                        st.markdown(st.session_state.content.get("discussion_questions", "No questions available."), unsafe_allow_html=True)
                    
                    with tabs[1]:
                        st.markdown(st.session_state.content.get("key_vocabulary", "No vocabulary available."), unsafe_allow_html=True)
                    
                    with tabs[2]:
                        st.markdown(st.session_state.content.get("useful_expressions", "No expressions available."), unsafe_allow_html=True)
                    
                    with tabs[3]:
                        st.markdown(st.session_state.content.get("grammar_focus", "No grammar focus available."), unsafe_allow_html=True)
                else:
                    # Display as before for Reading Passage
                    st.markdown(st.session_state.content, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)                            
               
                st.markdown("<h2 class='sub-header'>Record Your Speech</h2>", unsafe_allow_html=True)
                st.write(f"Please speak about the topic for approximately {st.session_state.duration} minutes.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Record directly--NOT WORKED YET, UPLOADING FILES INSTEAD:")
                    # Add microphone recording functionality 
                    record_audio()
                    # Display a placeholder for where the recording will appear
                    st.audio(None, format="audio/wav")
                
                with col2:
                    st.write("Or upload audio file:")
                    uploaded_file = st.file_uploader("Upload an MP3/WAV/M4A file", type=["mp3", "wav", "m4a"])
                    if uploaded_file is not None:
                        # Save the uploaded file temporarily
                        st.session_state.audio_file = uploaded_file
                        st.success("Audio file uploaded successfully!")
                        # Display the audio player
                        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
                
                # If we have an audio file, show the evaluate button
                if st.session_state.audio_file:
                    if st.button("Evaluate My Speech"):
                        # Evaluate the speech with the updated function
                        evaluation_results = evaluate_speech(
                            model, 
                            st.session_state.audio_file, 
                            st.session_state.topic, 
                            st.session_state.duration,
                            st.session_state.difficulty
                        )
                        
                        if evaluation_results:
                            st.session_state.evaluation_results = evaluation_results
                            st.session_state.evaluated = True
                            st.rerun()
                        
        # If we've evaluated, show the results
        else:
            # Show results
            st.markdown("<h2 class='sub-header'>Your Evaluation Results</h2>", unsafe_allow_html=True)
            
            # Extract scores for the radar chart
            categories = ["Pronunciation", "Vocabulary", "Grammar", "Fluency", "Coherence"]
            scores = [
                st.session_state.evaluation_results["scores"]["pronunciation"],
                st.session_state.evaluation_results["scores"]["vocabulary"],
                st.session_state.evaluation_results["scores"]["grammar"],
                st.session_state.evaluation_results["scores"]["fluency"],
                st.session_state.evaluation_results["scores"]["coherence"]
            ]
            
            # Calculate overall score
            overall_score = round(sum(scores) / len(scores), 1)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display radar chart
                fig = create_radar_chart(categories, scores)
                st.pyplot(fig)
            
            with col2:
                st.markdown(f"<div style='text-align: center; padding: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='font-size: 2rem; color: #2563EB;'>{overall_score}/10</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 1rem;'>Overall Score</p>", unsafe_allow_html=True)
                st.markdown(f"</div>", unsafe_allow_html=True)
                
                # Category scores
                for category, score in zip(categories, scores):
                    st.markdown(f"**{category}**: {score}/10")
            
            # Add error highlight legend
            st.markdown("<div class='error-legend'>", unsafe_allow_html=True)
            st.markdown("<div class='legend-item'><div class='legend-color' style='background-color: #ffdddd;'></div>Grammar Error</div>", unsafe_allow_html=True)
            st.markdown("<div class='legend-item'><div class='legend-color' style='background-color: #ffe6cc;'></div>Vocabulary Choice</div>", unsafe_allow_html=True)
            st.markdown("<div class='legend-item'><div class='legend-color' style='background-color: #e6f2ff;'></div>Natural Expression</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display transcription with highlighted errors
            st.markdown("<h3 class='sub-header'>Your Speech Transcription</h3>", unsafe_allow_html=True)
            # st.markdown(st.session_state.evaluation_results["transcription_with_errors"], unsafe_allow_html=True)
            
            # With this:
            html_content = f"""
            <div style="font-size: 1rem; line-height: 1.6;">
                {st.session_state.evaluation_results["transcription_with_errors"]}
            </div>
            """
            components.html(html_content, height=400, scrolling=True)            
            
            # Display detailed feedback with enhanced styling
            st.markdown("<h3 class='sub-header'>Detailed Feedback</h3>", unsafe_allow_html=True)
            
            for category in categories:
                category_key = category.lower()
                with st.expander(f"{category} - Score: {st.session_state.evaluation_results['scores'][category_key]}/10"):
                    # Add a category header with styling
                    st.markdown(f"<div class='category-header'>{category}</div>", unsafe_allow_html=True)
                    st.markdown(st.session_state.evaluation_results["detailed_feedback"][category_key])
            
            # Display strengths
            st.markdown("<h3 class='sub-header'>Strengths</h3>", unsafe_allow_html=True)
            
            # for strength in st.session_state.evaluation_results["strengths"]:
            #     st.markdown(f"<div class='strengths'>{strength}</div>", unsafe_allow_html=True)            
            
            # # Display improvement recommendations
            # st.markdown("<h3 class='sub-header'>Recommendations for Improvement</h3>", unsafe_allow_html=True)                          
            
            
            # for recommendation in st.session_state.evaluation_results["improvement_recommendations"]:
            #     st.markdown(f"<div class='recommendation'>{recommendation}</div>", unsafe_allow_html=True)
            
            # Display improvement recommendations
            # st.markdown("<h3 class='sub-header'>Strengths</h3>", unsafe_allow_html=True)
            
            for strengths in st.session_state.evaluation_results["strengths"]:
                st.markdown(f"<div class='strengths'>{strengths}</div>", unsafe_allow_html=True)            
            
            # Display improvement recommendations
            st.markdown("<h3 class='sub-header'>Recommendations for Improvement</h3>", unsafe_allow_html=True)       
            
            
            for recommendation in st.session_state.evaluation_results["improvement_recommendations"]:
                st.markdown(f"<div class='recommendation'>{recommendation}</div>", unsafe_allow_html=True)
                
            # Start over button
            if st.button("Start Over"):
                for key in ['recording', 'audio_file', 'evaluated', 'evaluation_results', 'content']:
                    if key in st.session_state:
                        st.session_state[key] = False if key == 'recording' or key == 'evaluated' else None
                st.rerun()

if __name__ == "__main__":
    main()
    
    
        # Mark errors in the transcription using HTML:
        # - Grammar errors: "<span class='error' title='Grammar correction: [correct form]'>[incorrect text]</span>"
        # - Vocabulary errors: "<span class='vocab-error' title='Better word choice: [better word]'>[original word]</span>"
        # - Usage errors: "<span class='usage-error' title='Natural expression: [natural expression]'>[unnatural expression]</span>"
        
