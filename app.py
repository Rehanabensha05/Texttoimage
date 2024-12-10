import tkinter as tk
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from authtoken import auth_token
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from langdetect import detect
from googletrans import Translator


app = tk.Tk()
app.geometry("800x950")
app.title("Stable Diffusion Generator")
ctk.set_appearance_mode("dark")


background_image = Image.open("C:/Users/abi00/OneDrive/Desktop/WhatsApp Image 2024-11-28 at 19.50.28_ae5ad742.jpg") 
background_image = background_image.resize((800, 950))  
bg_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(app, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


header_label = tk.Label(
    app, 
    text="Text to Image Generation 🚀", 
    font=("TimesNewRoman", 24, "bold"), 
    fg="black"
)
header_label.place(x=20, y=20)


subheader_label = tk.Label(
    app,
    text="What you think, you become. What you feel, you attract. What you imagine, you create",
    font=("Arial", 12),
    fg="black",
    wraplength=760
)
subheader_label.place(x=20, y=60)


prompt = ctk.CTkEntry(
    app,
    height=40,
    width=750,
    font=("Arial", 18),
    text_color="black",
    fg_color="white"
)
prompt.place(x=20, y=110)


languages = ["English", "Hindi", "Tamil", "Spanish", "Chinese"]
selected_language = tk.StringVar()
selected_language.set("Select the Language")

language_menu = tk.OptionMenu(app, selected_language, *languages)
language_menu.place(x=20, y=160)


email_label = tk.Label(app, text="Recipient's Email:", font=("Arial", 12), bg="white")
email_label.place(x=320, y=160)

email_entry = ctk.CTkEntry(
    app,
    height=30,
    width=300,
    font=("Arial", 14),
    text_color="black",
    fg_color="white"
)
email_entry.place(x=450, y=160)


lmain = ctk.CTkLabel(
    app, 
    height=400, 
    width=512, 
    text="Generated image will appear here", 
    text_color="black"
)
lmain.place(x=144, y=220)  


generate_button = ctk.CTkButton(
    app, 
    height=40, 
    width=150, 
    font=("Arial", 20), 
    text_color="white", 
    fg_color="blue", 
    text="Generate", 
    command=lambda: generate()
)
generate_button.place(x=225, y=640)


email_button = ctk.CTkButton(
    app,
    height=40,
    width=150,
    font=("Arial", 20),
    text_color="white",
    fg_color="green",
    text="Sent Email ",
    command=lambda: email_image()
)
email_button.place(x=425, y=640)


original_label = tk.Label(app, text="Original Prompt:", font=("Arial", 12), bg="white")
original_label.place(x=20, y=720)

original_text = tk.Label(app, text="", font=("Arial", 10), bg="white", fg="black", wraplength=760)
original_text.place(x=140, y=720)

translated_label = tk.Label(app, text="Translated Prompt (English):", font=("Arial", 12), bg="white")
translated_label.place(x=20, y=760)

translated_text = tk.Label(app, text="", font=("Arial", 10), bg="white", fg="black", wraplength=760)
translated_text.place(x=220, y=760)


modelid = "CompVis/stable-diffusion-v1-4"
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(
    modelid,
    revision="fp16",
    torch_dtype=torch.float16,
    use_auth_token=auth_token
)
pipe.to(device)

translator = Translator()


def translate_prompt():
    input_text = prompt.get()
    selected_lang = selected_language.get()

    # Update original prompt display
    original_text.configure(text=input_text)

    if selected_lang != "English":
        lang_code = {
            "Hindi": "hi",
            "Tamil": "ta",
            "Spanish": "es",
            "Chinese": "zh-cn"
        }.get(selected_lang, "en")
        try:
            translated = translator.translate(input_text, src=lang_code, dest="en")
            translated_text.configure(text=translated.text)
            return translated.text
        except Exception as e:
            print(f"Translation error: {e}")
            return input_text
    translated_text.configure(text=input_text)
    return input_text


def generate():
    processed_prompt = translate_prompt()
    with autocast(device):
        output = pipe(processed_prompt, guidance_scale=8.5)
    image = output.images[0]
    image.save('generatedimage.png')
    img = Image.open('generatedimage.png')
    img = img.resize((400, 400))
    img_tk = ImageTk.PhotoImage(img)
    lmain.configure(image=img_tk)
    lmain.image = img_tk


def email_image():
    recipient = email_entry.get()
    if not recipient:
        messagebox.showerror("Error", "Please enter your friend's email address.")
        return

    try:
        
        sender_email = "rehanabensha2002@gmail.com"  
        sender_password = "ilij dipt teve icrrwsrni"  
        subject = "Your Generated Image!"
        body = "Here is the image generated using Stable Diffusion."

        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        
        with open("generatedimage.png", "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= generatedimage.png")
        msg.attach(part)

        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        messagebox.showinfo("Success", "Email sent successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")


app.mainloop()