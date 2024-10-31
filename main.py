import os
import openai
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an OpenAI client instance
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Recommended: store API key in .env
)

# Base directory for all localization files
base_path = "C:/Users/BURAK/StudioProjects/Sociable-Android/Forplay/app/src/main/res/"

# Define language-specific paths
languages = {
    "EN": f"{base_path}values/strings.xml",
    "TR": f"{base_path}values-tr/strings.xml",
    "PT": f"{base_path}values-pt-rBR/strings.xml",
    "ES": f"{base_path}values-es/strings.xml",
    "DE": f"{base_path}values-de/strings.xml",
    "FR": f"{base_path}values-fr/strings.xml",
    "JA": f"{base_path}values-ja/strings.xml"
}

# Prompt template for OpenAI
prompt_template = """I need localizations for Sociable app ( https://apps.apple.com/tr/app/sociable-games-video-chat/id736275029?mt=8 ) with the following languages:

Notes:
1. Correct EN version using better English 
2. Use "sen" language when translating to TR. Ayrıca türkçe lokalizasyon yaparken 'e, 'a eki ekle.
3. Translate in a friendly tone by using "you" informally in all languages.
4. Do not provide pronunciations. 
5. Do not use quotes
6. Do not write pronunciation for any language
7. All translations should be based on the corrected EN version of the text
8. Use "sen" language in all languages
9. If I provide the text in all caps, you'll also use all caps

EN: {custom_input}


EN
TR
PT
ES
DE
FR
JA

dont give any other format except language_code: translation 
"""


def get_localized_text(custom_input):
    # Use the client instance to create a chat completion
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # Specify the model to use
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides localized translations."},
            {"role": "user", "content": prompt_template.format(custom_input=custom_input)}
        ]
    )

    # Parse response into dictionary form
    translation_text = response.choices[0].message.content.strip().split("\n")
    print(translation_text)
    # Display token usage information
    tokens_used = response.usage.total_tokens
    print(f"Total tokens used for this call: {tokens_used}")
    translations = {}
    for line in translation_text:
        if line:
            lang_code, text = line.split(": ", 1)
            translations[lang_code.strip()] = text.strip()
    return translations

def add_translation_to_xml(file_path, tag_name, translation):
    # Create file with basic structure if it doesn't exist
    if not os.path.isfile(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?><resources></resources>')

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find existing tag or create a new one
    existing_tag = root.find(f"./string[@name='{tag_name}']")
    if existing_tag is None:
        # Create and append new tag if it doesn't exist
        new_string = ET.SubElement(root, "string", name=tag_name)
        new_string.text = translation
    else:
        # Update existing tag's text
        existing_tag.text = translation

    # Write back the updated XML content to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    print(f"Updated {file_path} with tag '{tag_name}'.")



def save_to_xml(translations, tag_name):
    for lang, file_path in languages.items():
        # Determine the translation based on the language
        translation = translations.get(lang, translations["EN"])

        # Add or update translation in the existing XML file
        add_translation_to_xml(file_path, tag_name, translation)


# Main execution
if __name__ == "__main__":
    # Prompt the user for custom input and tag name
    custom_input = input("Enter the text to be localized: ").strip()
    tag_name = input("Enter the XML tag name (e.g., super_like_title): ").strip()
    translations = get_localized_text(custom_input)
    save_to_xml(translations, tag_name)
