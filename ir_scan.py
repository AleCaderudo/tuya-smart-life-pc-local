import tkinter as tk
import webbrowser
from tkinter import messagebox
import json
from tinytuya import Contrib

# Configurações do IR Blaster Tuya
DEVICE_ID = '7478880498f4abfd1111'
DEVICE_IP = '192.168.0.114'
DEVICE_KEY = '40fec9919f6b5bbd'
ARQUIVO_BOTOES = "botoes_ir.json"

# Inicializa o dispositivo
ir = Contrib.IRRemoteControlDevice(DEVICE_ID, DEVICE_IP, DEVICE_KEY, persist=True)

def aprender_botao():
    try:
        resultado_text.set("📡 Aguardando sinal do controle remoto (15s)...")
        root.update()
        button_base64 = ir.receive_button(timeout=15)

        if button_base64 is None:
            resultado_text.set("⏰ Tempo esgotado. Nenhum botão recebido.")
            return

        nome = nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Dê um nome ao botão!")
            return

        pulses = ir.base64_to_pulses(button_base64)
        headkey = Contrib.IRRemoteControlDevice.pulses_to_head_key(pulses)

        if not headkey:
            resultado_text.set("❌ Erro ao converter para head/key.")
            return

        head, key = headkey

        # Salvar no arquivo
        try:
            with open(ARQUIVO_BOTOES, "r") as f:
                botoes = json.load(f)
        except FileNotFoundError:
            botoes = {}

        botoes[nome] = {"head": head, "key": key,"base64": button_base64}

        with open(ARQUIVO_BOTOES, "w") as f:
            json.dump(botoes, f, indent=2)

        resultado_final = f"✅ Botão '{nome}' salvo!\n\n📋  head:\n{head}\n\n🔶 key:\n{key} \n\n Não uso mas funciona - base64:\n{button_base64}\n\n🔷"
        resultado_text.set(resultado_final)
        copiar_btn.config(state=tk.NORMAL)

    except Exception as e:
        resultado_text.set(f"Erro: {e}")

def copiar_para_area_transferencia():
    root.clipboard_clear()
    root.clipboard_append(resultado_text.get())
    root.update()
    messagebox.showinfo("Copiado", "Texto copiado com sucesso!")

# Interface Tkinter
root = tk.Tk()
root.title("Aprender Botão IR - Head/Key Tuya")
root.geometry("700x450")

tk.Label(root, text="Preencha com um nome para o botão e clique em Aprender Botão", font=("Arial", 12, "bold")).pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="Nome do Botão:").grid(row=0, column=0, padx=5, pady=10)
nome_entry = tk.Entry(frame, width=30)
nome_entry.grid(row=0, column=1, padx=5)

aprender_btn = tk.Button(frame, text="📡 Aprender Botão", command=aprender_botao)
aprender_btn.grid(row=0, column=2, padx=10)

resultado_text = tk.StringVar()
resultado_label = tk.Label(root, textvariable=resultado_text, wraplength=650, justify="left", anchor="w")
resultado_label.pack(pady=20)

copiar_btn = tk.Button(root, text="📋 Copiar Resultado", command=copiar_para_area_transferencia, state=tk.DISABLED)
copiar_btn.pack()

#Link Pagina
def abrir_link(url):
    webbrowser.open_new_tab(url)

link = tk.Label(text="Desenvolvido por MHPS", fg="blue", cursor="hand2")
link.pack(side=tk.BOTTOM, pady=10)
link.bind("<Button-1>", lambda e: abrir_link("https://www.mhps.com.br"))

root.mainloop()
