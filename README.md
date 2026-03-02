# 🎥 Brand Compliance LLMOps with Azure

> 🚀 A Large-Language-Model-Driven Brand Compliance video validator built with Azure AI and Azure LLMOps architecture.

This project enables automated checking of **YouTube short ad videos** for brand compliance. It downloads an ad locally, extracts transcripts and OCR text using **Azure Video Indexer**, then uses **Azure Cognitive Search + Azure OpenAI (GPT-4)** to validate compliance against your knowledge base and rules.  
If the video violates compliance rules, `status == false`. This is built as a RAG (Retrieval Augmented Generation) pipeline with LangGraph orchestration.

---

## 🧠 Overview

### 📌 Purpose
This tool helps **brands, agencies, and compliance teams** to programmatically check whether YouTube short ads adhere to compliance guidelines before publish. It:

- Downloads YouTube videos
- Sends videos to Azure Video Indexer
- Extracts OCR and transcript text
- Checks content against company knowledge / compliance rules
- Generates compliant/non-compliant status via GPT-4

---

## 🧰 Architecture

```bash
flowchart TD
    A[YouTube Short Video] -->|Download| B(Local Storage)
    B --> C[Azure Video Indexer]
    C --> D[Text & OCR Transcripts]
    D --> E[Azure Cognitive Search]
    D --> F[Azure OpenAI GPT-4]
    E --> G[Knowledge Base Index]
    F --> H[Compliance Check Logic]
    H --> I[Compliant / Non-Compliant (status)]

```
## 📦 Features

✔️ Video download & local caching  
✔️ Azure Video Indexer integration  
✔️ OCR & transcript extraction  
✔️ LangGraph orchestration nodes  
✔️ Azure Cognitive Search integration  
✔️ GPT-4 powered compliance validation  
✔️ Binary compliance result (`true / false`)  

---

## ⚙️ Project Structure
```bash
/
├── backend/ # Python backend handlers
│ ├── main.py # Backend application entrypoint
│ └── ...
├── pyproject.toml # Python project config
├── README.md # This documentation
├── uv.lock # Dependencies lock
└── .gitignore
```

---

## 🚀 Getting Started

### 🧩 Prerequisites

Ensure the following:

- Python 3.10+
- Azure Subscription with:
  - Azure Video Indexer account
  - Azure Cognitive Search
  - Azure OpenAI (GPT-4 deployment)
- YouTube API key
- LangGraph configured

---

## 🛠️ Installation

### 1️⃣ Clone the repo

```bash
git clone https://github.com/aliahmad552/brand-compliacne-llmops-with-Azure.git
cd brand-compliacne-llmops-with-Azure
```
### 2️⃣ Install dependencies
```bash
python -m pip install -r requirements.txt
```
### 3️⃣ Set environment variables
```bash
export AZURE_VIDEO_INDEXER_KEY="..."
export AZURE_SEARCH_KEY="..."
export OPENAI_API_KEY="..."
export YOUTUBE_API_KEY="..."
```
### 4️⃣ Run the service\
```bash
python backend/main.py
```
## 📄 How It Works
### 1️⃣ Download Video

YouTube video is downloaded locally using a downloader utility.

### 2️⃣ Azure Video Indexer

Video is sent to Azure Video Indexer ➜ returns OCR & transcript text.

### 3️⃣ Text Extraction

Text is parsed and chunked.

### 4️⃣ Azure Search

Documents are indexed into Azure Cognitive Search.

### 5️⃣ GPT-4 Validation

Query GPT-4 with extracted text + KB rules for compliance verdict.

###  📈 Examples

📥 Request Example

POST /validate
```bash
{
  "youtube_url": "https://youtu.be/xyz123",
  "ruleset": "brand_policy_2026"
}
```
📤 Response Example
```bash
{
  "status": false,
  "score": 0.12,
  "violations": [
    "Improper text detected",
    "Trademark misuse"
  ],
  "raw_model_output": "..."
}
```
## 🧪 Testing

Run unit & integration tests:

pytest tests/
🤖 LangGraph Node Config (Example)

LangGraph nodes orchestrate the compliance workflow:
```bash
nodes:
  - name: download_video
    type: python

  - name: index_video
    type: azure_video_indexer

  - name: extract_text
    type: text_parser

  - name: search_index
    type: azure_search

  - name: compliance_check
    type: gpt4
```
### 💡 GitHub Workflows
🧹 Python Lint + Test Workflow
```bash
name: Lint & Test

on: [push, pull_request]

jobs:
  python-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - run: pip install flake8 pytest
      - run: flake8 .
      - run: pytest
```
### 🌐 Deploy to Azure Web App
```bash
name: Deploy Azure

on:
  push:
    branches: ["main"]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: azure/setup-python@v3
        with:
          python-version: "3.10"

      - run: pip install -r requirements.txt

      - uses: azure/webapps-deploy@v2
        with:
          app-name: "brand-compliance-app"
          slot-name: "production"
          publish-profile: ${{ secrets.AzureWebApp_PublishProfile }}
          package: .

```

### 📚 Related Links

- Azure Video Indexer Docs

- Azure Cognitive Search Docs

- Azure OpenAI Service

- YouTube Data API

### 🧑‍💻 Contributing

Feel free to contribute!
Please open issues or create pull requests for improvements.

### 📜 License

MIT © 2026