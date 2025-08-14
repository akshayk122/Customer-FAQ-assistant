# 🧠 AI Voice FAQ Assistant

This project is an **AI-powered Voice FAQ Assistant** that automatically reads your organization's documents and answers questions about them through voice or text chat.

**What it does:**
- 📚 **Reads your documents** - Upload .docx, .pdf, .txt, .csv, or .json files
- 🎤 **Answers questions by voice** - Ask questions using your microphone
- 💬 **Answers questions by text** - Type questions and get instant responses
- 🧠 **Learns from your content** - Automatically understands your documents
- 🔄 **Stays updated** - Automatically refreshes when you add new files

**Perfect for:**
- **HR Teams** - Answer employee policy questions instantly
- **Customer Support** - Provide accurate product/service information
- **Training Departments** - Help new employees learn company procedures
- **Any Organization** - Make your documentation easily accessible

The system uses **Google's AI (Gemini)** and **open-source tools** like FastAPI, LlamaIndex, and HuggingFace embeddings to understand your content and provide intelligent responses.

Whether you're a **developer**, a **non-technical team member**, or a **project lead**, this assistant makes your organization's knowledge instantly accessible to everyone.


## ✅ What It Can Do

- 🎤 Understand your spoken questions (mic supported!)
- 💬 Let you type questions instead of speaking
- 📁 Automatically scan `.docx`, `.pdf`, `.txt`, `.csv`, and `.json` documents
- 🔍 Find the best answer using vector search (semantic similarity)
- 🗣 Speak the answer back using natural-sounding voice
- ✨ Make the response more human-like using Gemini AI (Google)
- 📊 File management dashboard for easy document uploads
- 🔄 Automatic knowledge base updates when files change
- 🧠 Smart content parsing for both Q&A and policy documents
- 📈 Real-time knowledge base status monitoring



## 🖼️ Web Interface Screenshots

### **Chat Interface**
<img width="1927" height="965" alt="image" src="https://github.com/user-attachments/assets/61e9dd49-f381-481f-be2e-bc6fd4458055" />


### **File Management Dashboard**
<img width="1919" height="962" alt="image" src="https://github.com/user-attachments/assets/67046485-8f5a-425e-ad01-8e81c2434d64" />



## 🧱 How It Works (Simple Explanation)

```text
Step 1: You ask a question using mic or by typing it
Step 2: The system finds the best-matching content from your documents
Step 3: Gemini AI rewrites that answer to sound natural and friendly
Step 4: You see the response and hear it read out loud if you want
```

This method is called **RAG** – Retrieval-Augmented Generation.

---

## 📁 Folder Structure (Explained for Everyone)

```bash
ai-voice-faq-assistant/
├── api/
│   └── main.py               # 🔥 The main FastAPI server – THIS is what runs the app
├── run.py                   # 🧪 Testing script (for devs only, not needed for regular use)
├── requirements.txt         # List of tools Python will install
├── .env.example             # Template for adding your private keys
├── .env                     # Your actual keys (will be hidden from Git)
├── core/                    # 💡 All the logic for reading files and understanding questions
│   ├── faq_loader.py       # 📚 Loads and processes all documents
│   ├── file_parser.py      # 🔍 Parses various file formats intelligently
│   ├── index_builder.py    # 🏗️ Builds searchable vector index
│   ├── rag.py              # 🔎 Handles question-answer retrieval
│   └── gemini_responder.py # ✨ Enhances responses with Gemini AI
├── utils/
│   └── faq-voice-keys.json  # 🔐 Google cloud credentials (you download this)
├── static/
│   ├── index.html           # 💬 Your chat interface
│   ├── dashboard.html       # 📊 NEW: File management dashboard
│   └── script.js            # 🎤 Makes the mic and chat box work
└── data/
    └── Your Documents/      # 📄 Your FAQ and policy files go here
```


## 🚀 Getting Started (For Everyone)

This section helps both **non-technical and technical** members get it running.

### 1. Install Python (Once)

Go to https://www.python.org/downloads/ and install **Python 3.10 or newer**.

### 2. Download This Project

Ask your team lead for the GitHub link or run this in your terminal:

```bash
git clone https://github.com/your-org/ai-voice-faq-assistant.git
cd ai-voice-faq-assistant
```

### 3. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate          # On Windows use: venv\Scripts\activate
```

### 4. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 5. Add Your API Keys

1. Copy the template:

```bash
cp .env.example .env
```

2. Edit the `.env` file and add your **Google Gemini API key**:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. Also download your **Google service account key (JSON)** and place it in:

```
utils/faq-voice-keys.json
```

This is needed for voice-to-text and text-to-voice features.

---

## 🗃️ Managing Your Documents

### **Easy File Upload**
1. **Go to Dashboard:** Visit `/dashboard` in your browser
2. **Drag & Drop:** Simply drag files into the upload area
3. **Automatic Processing:** Files are automatically processed and indexed
4. **Real-time Updates:** Knowledge base updates immediately

### **Supported File Types**
- **`.docx`** - Microsoft Word documents
- **`.pdf`** - PDF files
- **`.txt`** - Plain text files
- **`.csv`** - Spreadsheet data (with question/answer columns)
- **`.json`** - Structured data files

### **Smart Content Processing**
- **Q&A Format:** Automatically detects question-answer pairs
- **Policy Documents:** Intelligently chunks policy content for search
- **General Content:** Processes any document type into searchable chunks
- **Automatic Indexing:** No manual configuration needed

---

## ▶️ Run the Assistant (Production)

```bash
uvicorn api.main:app --reload
```

Now open your browser and go to:

```
http://localhost:8000          # 💬 Chat Interface
http://localhost:8000/dashboard # 📊 File Management Dashboard
```

### **Chat Interface Features:**
- Click the  mic to ask your question
- Type in the input box for text questions
- See and hear the assistant's response
- Modern blue-themed interface

### **Dashboard Features:**
- 📤 Upload new documents easily
- 📋 View all uploaded files
- 🗑️ Delete files when needed
- 🔄 Refresh knowledge base manually
- 📊 Monitor FAQ entry count

---

## 🧪 Run for Testing (Developers Only)

For CLI-based testing (no frontend), run:

```bash
python run.py
```

---

## 🧠 API Endpoints (For Developers)

| Method | Endpoint                | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | `/api/ask-text`         | Ask a question via text              |
| POST   | `/api/ask-audio`        | Ask a question via audio             |
| POST   | `/api/ask-tts`          | Convert text to speech               |
| POST   | `/api/ask-text-transcribe` | Just get a transcript from audio |
| GET    | `/health`               | Check if backend is running          |
| **NEW** | `/dashboard`            | File management dashboard            |
| **NEW** | `/api/upload-file`      | Upload new documents                 |
| **NEW** | `/api/files`            | List all uploaded files              |
| **NEW** | `/api/files/{filename}` | Delete specific files                |
| **NEW** | `/api/refresh`          | Manually refresh knowledge base      |

---

## 🔄 Knowledge Base Management

### **Automatic Updates**
- **Upload:** Knowledge base refreshes automatically after file upload
- **Delete:** Knowledge base refreshes automatically after file deletion
- **Real-time:** No server restart needed

### **Manual Refresh**
- **Dashboard Button:** Click "Refresh Knowledge Base" in dashboard
- **API Endpoint:** Use `/api/refresh` for programmatic refresh
- **Status Monitoring:** See current FAQ entry count in real-time

### **Smart Content Processing**
- **Intelligent Parsing:** Handles both Q&A and policy documents
- **Content Chunking:** Splits long documents into searchable pieces
- **Metadata Tracking:** Tracks source files and document IDs
- **Error Handling:** Graceful fallbacks for parsing issues

---

## 👩‍💻 Team Workflow (For Developers)

```bash
# Create a new feature branch
git checkout -b feature/my-task-name

# Make changes and commit
git add .
git commit -m "Add feature: improve response formatting"

# Push and open pull request
git push origin feature/my-task-name
```

---

## 🛠️ Requirements

- Python 3.10+
- Google API Key (for Gemini)
- Google Cloud Service Account (for TTS/STT)
- Web browser with microphone access
- **NEW:** Modern web browser for dashboard features

---

## 🔐 Security & Best Practices

- `.env` and key files are ignored in Git and must be set up manually
- Voice input is rate-limited to prevent abuse
- No user data is stored or shared
- **NEW:** File upload validation and type checking
- **NEW:** Secure file handling with proper error handling

---

## 🚀 Recent Updates

### **v2.0.0 - Enhanced File Management**
- ✨ **New Dashboard:** Complete file management interface
- 🔄 **Auto-refresh:** Knowledge base updates automatically
- 🧠 **Smart Parsing:** Handles all document types intelligently
- 📊 **Real-time Status:** Monitor knowledge base health
- 🎨 **Modern UI:** Blue-themed, responsive design

### **v1.0.0 - Core Features**
- 🎤 Voice input and output
- 💬 Text-based chat interface
- 🔍 RAG-powered question answering
- ✨ Gemini AI enhancement

---

## Troubleshooting

### **New Files Not Loading?**
1. **Check Dashboard:** Go to `/dashboard` and verify file is listed
2. **Refresh Knowledge Base:** Click the refresh button
3. **Check Logs:** Look for processing errors in console
4. **File Format:** Ensure file is in supported format

### **Knowledge Base Issues?**
1. **Manual Refresh:** Use `/api/refresh` endpoint
2. **Check File Count:** Verify expected number of FAQ entries
3. **Restart Server:** If all else fails, restart the application

### **Upload Problems?**
1. **File Size:** Check if file is too large
2. **File Type:** Verify file extension is supported
3. **Permissions:** Ensure write access to data folder

---
