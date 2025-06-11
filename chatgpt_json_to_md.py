import json
import os
import re
from datetime import datetime

# --- CONFIGURATION ---
INPUT_FILE = 'conversations.json'
OUTPUT_DIR = 'chatgpt_exports'
# -------------------

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    - Removes illegal characters.
    - Replaces spaces with underscores.
    - Truncates to a reasonable length.
    """
    # Remove illegal characters for filenames
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Truncate to avoid overly long filenames
    return sanitized[:100]

def format_message_part(part):
    """Formats a single part of a message content, handling text and code."""
    if isinstance(part, str):
        return part
    elif isinstance(part, dict):
        # This handles more complex structures, like code blocks
        if part.get('content_type') == 'code':
            language = part.get('language', '')
            code = part.get('text', '')
            return f"\n```python\n{code}\n```\n"
        elif part.get('content_type') == 'text':
            return part.get('text', '')
    return ''


def get_conversation_messages(convo_data):
    """
    Extracts and orders messages from the conversation's mapping dictionary.
    Returns a list of formatted strings.
    """
    if not convo_data or 'mapping' not in convo_data:
        return []

    mapping = convo_data['mapping']
    messages = []
    
    # Find the root node (the one with no parent)
    root_node_id = None
    for node_id, node in mapping.items():
        if node.get('parent') is None:
            root_node_id = node_id
            break
            
    # If no root node found, try to find the one with the earliest message
    if root_node_id is None:
        # Fallback for slightly different structures: find the first chronological node
        sorted_nodes = sorted(
            (node for node in mapping.values() if node.get('message')),
            key=lambda x: x['message']['create_time']
        )
        if sorted_nodes:
            root_node_id = sorted_nodes[0]['id']
        else:
            return [] # No messages in this conversation

    # Traverse the conversation from the root node
    current_node_id = root_node_id
    while current_node_id in mapping:
        node = mapping[current_node_id]
        message_data = node.get('message')

        if (message_data and 
            message_data.get('content') and 
            message_data['author']['role'] != 'system'):
            
            author_role = message_data['author']['role'].title()
            content_parts = message_data['content'].get('parts', [])
            
            # Combine all parts of the message into a single text block
            full_text = "".join(format_message_part(part) for part in content_parts)

            if full_text.strip():
                messages.append(f"## {author_role}\n\n{full_text}\n\n---\n\n")

        # Move to the next message in the main conversational thread
        children = node.get('children', [])
        if children:
            current_node_id = children[0]
        else:
            break
            
    return messages

def main():
    """
    Main function to parse the JSON file and create markdown files.
    """
    print("Starting ChatGPT conversation parser...")

    # 1. Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        print("Please make sure your ChatGPT export's 'conversations.json' is in the same directory.")
        return

    # 2. Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: '{OUTPUT_DIR}'")

    # 3. Load the conversations JSON file
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{INPUT_FILE}'. The file might be corrupted.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    # 4. Process each conversation
    count = 0
    for convo in conversations:
        title = convo.get('title')
        create_time = convo.get('create_time')
        
        # Generate a filename
        if title and title.lower() not in ["new chat", ""]:
            filename = sanitize_filename(title) + '.md'
        else:
            # Fallback to using the creation date
            date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"conversation_{date_str}.md"
            
        # Extract and format messages
        messages = get_conversation_messages(convo)
        if not messages:
            print(f"Skipping conversation (no messages found): {title or 'Untitled'}")
            continue

        # Write the markdown file
        output_path = os.path.join(OUTPUT_DIR, filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title or 'Conversation'}\n\n")
                f.write("".join(messages))
            print(f"Successfully saved: {output_path}")
            count += 1
        except Exception as e:
            print(f"Error writing file {output_path}: {e}")

    print(f"\nProcessing complete. Successfully exported {count} conversations.")

if __name__ == '__main__':
    main()
