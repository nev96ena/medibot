# medibot

## Getting Started: Setup Instructions

Follow these steps to set up the MediBot project environment on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python:** Version 3.9 or higher.
* **Git:** For cloning the repository.
* **Docker & Docker Compose:** (Recommended) For easily running the PostgreSQL database. Alternatively, you can use a local PostgreSQL installation (version 13+ recommended).
* **Ollama:** Installed and running. Download from [https://ollama.com/](https://ollama.com/).

### 1. Clone the Repository

Open your terminal or command prompt and clone the project repository:

```bash
git clone <your_repository_url>
cd medibot-project

### 2. Install dependencies
Install all required Python libraries listed in the requirements.txt file:

```bash

pip install -r requirements.txt
### 3. Database Setup 

### 4. Ollama Setup (LLM)
Make sure the Ollama application or service is running on your machine.
Pull the required language model using the terminal:

```bash
ollama pull mistral:7b

### 5. Running the Streamlit App

Navigate to the project's root directory in your terminal and run the following command:

```bash
streamlit run app/app_streamlit.py