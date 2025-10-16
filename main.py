import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import gradio as gr
from typing import Optional




def main() -> None:
    load_dotenv()
    

    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env.")

    client = OpenAI()
    # Example: simple identity call to verify client is usable (no remote call here)
    print("OpenAI client initialized.")

    resources_dir = os.path.join(os.getcwd(), "myResource")
    pdf_path = os.path.join(resources_dir, "QuaziResumeAi.pdf")
    txt_path = os.path.join(resources_dir, "summary.txt")

    # Read PDF content
    resume_pdf_text = ""
    if os.path.isfile(pdf_path):
        reader = PdfReader(pdf_path)
        page_texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            page_texts.append(text)
        resume_pdf_text = "\n".join(page_texts).strip()
    else:
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    # Read TXT content
    if os.path.isfile(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            summary_text = f.read().strip()
    else:
        raise FileNotFoundError(f"Text file not found at {txt_path}")

    # Brief confirmation
    name='Quazi'
    
    system_prompt = (
        f"You are acting as {name}. You are answering questions on {name}'s website, "
        "particularly questions related to {name}'s career, background, skills and experience. "
        "Your responsibility is to represent {name} for interactions on the website as faithfully as possible. "
        "You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. "
        "Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
        "If you don't know the answer, say so."
    )
    
    system_prompt += (
        f"\n\n## Summary:\n{summary_text}\n\n## Resume:\n{resume_pdf_text}\n\n"
        f"With this context, please chat with the user, always staying in character as {name}."
    )
    #print(f"Loaded PDF text chars: {len(resume_pdf_text)}")
    #print(f"Loaded summary text chars: {len(summary_text)}")
    #print(f"name: {name}")
    #print(f"system_prompt chars: {len(system_prompt)}")

    # --- Gradio Chat Interface ---
    def chat(message, history):
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (history is list of [user_msg, assistant_msg] pairs)
        for user_msg, assistant_msg in history:
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response.choices[0].message.content


    # def chat1(message: str, history: list[tuple[str, str]]) -> str:
    #     # Build messages with system prompt, then alternating user/assistant history
    #     messages = [{"role": "system", "content": system_prompt}]
    #     for user_msg, assistant_msg in history:
    #         if user_msg:
    #             messages.append({"role": "user", "content": user_msg})
    #         if assistant_msg:
    #             messages.append({"role": "assistant", "content": assistant_msg})
    #     messages.append({"role": "user", "content": message})

    #     try:
    #         response = client.responses.create(
    #             model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    #             messages=messages,
    #         )
    #         # The SDK returns content in a list of content parts
    #         content_parts = response.output[0].content if hasattr(response, "output") else []
    #         if not content_parts and hasattr(response, "choices"):
    #             # Fallback for older structures
    #             text = response.choices[0].message.content
    #             return text
    #         text_chunks = []
    #         for part in content_parts:
    #             if part.get("type") == "output_text" and part.get("text"):
    #                 text_chunks.append(part["text"])
    #         return "".join(text_chunks) if text_chunks else "(No content returned)"
    #     except Exception as e:
     #         return f"Error: {e}"
    
    demo = gr.ChatInterface(
        fn=chat,
        title=f"Chat with {name}",
        description=f"You are chatting with {name}. The assistant will stay in character.",
    )

    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "8000"))
    demo.launch(server_name=server_name, server_port=server_port, share=False)

if __name__ == "__main__":
    main()


