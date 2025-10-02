# 🇩🇪 Deutsch Learning Agent

An interactive **German learning agent**, built with **Streamlit** and **Ollama**.  
The agent corrects your German sentences, explains mistakes briefly, and continues the conversation in **German only**.

---

## 📦 Requirements

- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Getting Started

1. Clone this repository and start the application (this builds the images and runs the containers):

   ```bash
   git clone https://github.com/YOUR-USERNAME/deutsch-agent.git
   cd deutsch-agent
   docker compose up
   # Note: On the first run Ollama will automatically download the model "mistral:7b-instruct" (~4 GB).
   # This may take a few minutes the first time.
   # After the services are up, open http://localhost:8501 in your browser.
   ```
## 🛑 Stop the App
    docker compose down