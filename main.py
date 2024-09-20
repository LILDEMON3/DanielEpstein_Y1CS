import tkinter as tk
from tkinter import scrolledtext
import threading
from huggingface_hub import InferenceClient

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = "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"


class ChatbotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Hugging Face Chatbot GUI")
        master.geometry("500x600")
        self.chat_history = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=25)
        self.chat_history.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.chat_history.config(state=tk.DISABLED)
        self.user_input = tk.Entry(master, width=60)
        self.user_input.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.user_input.bind("<Return>", self.send_message)
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(master, textvariable=self.status_var)
        self.status_label.pack(pady=(0, 10))
        self.client = InferenceClient(MODEL, token=HF_TOKEN)
        self.messages = []

    def send_message(self, event=None):
        user_message = self.user_input.get()
        if user_message.strip() == "":
            return

        self.user_input.delete(0, tk.END)
        self.append_message("You", user_message)
        self.status_var.set("Bot is thinking...")
        self.send_button.config(state=tk.DISABLED)
        self.messages.append({"role": "user", "content": user_message})
        threading.Thread(target=self.get_bot_response, daemon=True).start()

    def get_bot_response(self):
        try:
            bot_message = ""
            for message in self.client.chat_completion(
                    messages=self.messages,
                    max_tokens=500,
                    stream=True
            ):
                content = message.choices[0].delta.content
                if content:
                    bot_message += content
                    self.master.after(0, self.update_chat_stream, content)

            self.messages.append({"role": "assistant", "content": bot_message})
        except Exception as e:
            bot_message = f"Sorry, I couldn't process that request. Error: {str(e)}"
            self.master.after(0, self.update_chat, bot_message)

        self.master.after(0, self.finish_response)

    def update_chat_stream(self, content):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, content)
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def update_chat(self, message):
        self.append_message("Bot", message)

    def finish_response(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self.status_var.set("")
        self.send_button.config(state=tk.NORMAL)

    def append_message(self, sender, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatbotGUI(root)
    root.mainloop()