# ChatGPT Conversations to Obsidian Markdown Exporter

Easily convert your exported [ChatGPT](https://chat.openai.com/) conversations (from `conversations.json`) into clean, well-formatted Markdown notes.
---

## Features

- 📁 **One Markdown file per conversation**
- 🧑‍💻 **Supports code blocks, text, and multi-part messages**
- 🏷️ **Obsidian-friendly formatting and safe filenames**
- 🚫 **Skips empty/system messages**
- 📅 **Uses chat title and timestamp for file naming**
- 💥 **Fast and robust for thousands of chats**
- 📝 **Human-readable, easily customizable Python source**

---
## Installation

1. **Clone or Download** this repo:

    ```sh
    git clone https://github.com/csrobb/ChatGPTtoMD.git
    cd ChatGPTtoMD
    ```

2. **Place your ChatGPT `conversations.json` export** in the same directory.  
   - Get this file via ChatGPT: Settings → Data Controls → Export Data.

## Usage

```sh
python chatgpt_json_to_md.py
