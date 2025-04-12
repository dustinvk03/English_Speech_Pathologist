# English Speech Pathologist

[The app:](https://english-speech-pathologist.streamlit.app/): https://english-speech-pathologist.streamlit.app/

[Instruction video](https://www.dropbox.com/scl/fi/ht3hk1nafgnh4mqoblh2q/AI_Speech_Evaluation_Tutorial.mkv?rlkey=bpvocqyol9y5rbxtfp0r9sbyr&e=1&st=fiic77m7&dl=0)

**![gift](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/UI1.gif)

## Overview

English Speech Pathologist is an AI-powered web application that helps users improve their English speaking skills through automated speech evaluation and personalized feedback. This tool uses Google's Gemini AI to analyze speech recordings and provide detailed assessments on pronunciation, vocabulary, grammar, fluency, and coherence.

## Features

- **AI-Powered Speech Evaluation**: Get comprehensive feedback on your English speaking abilities
- **Customizable Practice Sessions**: Select topics, difficulty levels, and duration based on your needs
- **Real-time Audio Recording**: Record directly from your browser or upload audio files
- **Detailed Feedback**: Receive specific scores and recommendations across 5 key areas
- **Visual Analytics**: View your performance through an intuitive radar chart
- **Error Highlighting**: See grammar, vocabulary, and expression suggestions directly in your transcription

## Tech Stack

- **Frontend & Backend**: Streamlit
- **AI Model**: Google Gemini 2.0 Flash
- **Data Visualization**: Matplotlib
- **Audio Processing**: Browser-based audio recording

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dustinvk03/English_Speech_Pathologist
   cd english-speech-pathologist
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Requirements

```
streamlit
numpy
matplotlib
google-generativeai
```

## Usage

1. **Authentication**: Enter your Google API key or use the provided password
2. **Set up your practice session**:
   - Choose a speaking topic
   - Set the duration (1-10 minutes)
   - Select your difficulty level (Beginner, Intermediate, Advanced)
3. **Practice speaking**:
   - Record directly using your microphone
   - Or upload an audio file (WAV, MP3, M4A)
4. **Review your results**:
   - Overall score and detailed breakdown
   - Transcription with highlighted improvement areas
   - Strengths and recommendations for improvement

## Speech Evaluation Criteria

The application evaluates your speech based on five critical areas:

- **Pronunciation**: Accuracy of sounds, stress, and intonation
- **Vocabulary**: Word choice, variety, and appropriateness
- **Grammar**: Correctness of sentence structure and grammar rules
- **Fluency**: Smoothness, pace, and natural flow of speech
- **Coherence**: Organization, logical flow, and clarity of ideas

## API Key Setup

To use this application, you need a Google API key with access to the Gemini model:

1. Get your API key from the [Google AI Studio](https://aistudio.google.com/prompts/new_chat)
2. Enter it in the application when prompted

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- This application uses Google's Gemini AI technology
- UI components powered by Streamlit
- Visualization created with Matplotlib

**![screenshot1](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p1.png)

**![screenshot2](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p2.png)

**![screenshot3](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p3.png)

**![screenshot4](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p4.png)

**![screenshot5](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p5.png)

**![screenshot6](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p6.png)

**![screenshot7](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p7.png)

**![screenshot8](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p8.png)

**![screenshot9](https://github.com/dustinvk03/English_Speech_Pathologist/blob/master/screenshot/p9.png)


