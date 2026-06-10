"""
Milestone 5 - Part 2: Gradio web interface.

A viewer enters a question; the app retrieves relevant chunks, generates a
grounded answer with Groq, and shows which source documents it drew from.

Run from the project root:
    source .venv-1/bin/activate
    python app.py
Then open http://localhost:7860
"""

import sys
from pathlib import Path

# generate.py lives in src/ and imports retrieve.py as a sibling.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import gradio as gr
from generate import ask


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sources)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide - Study Skills") as demo:
    gr.Markdown(
        "# The Unofficial Guide to Becoming a Straight-A Student\n"
        "Ask about study techniques, time management, active recall, spaced "
        "repetition, the Pomodoro and Feynman techniques, and more. "
        "**Answers come only from the source documents** - if the guide doesn't "
        "cover it, the assistant will say so."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. What is active recall?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
