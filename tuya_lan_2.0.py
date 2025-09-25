import tinytuya
import threading
import controle_ar
import tkinter as tk
import webbrowser
import sys
import subprocess
import json
import os
import time
from datetime import datetime


ARQUIVO_DISPOSITIVOS = "meus_dispositivos.json"


# Funções locais dos dispositivos
def carregar_dispositivos():
    if os.path.exists(ARQUIVO_DISPOSITIVOS):
        with open(ARQUIVO_DISPOSITIVOS, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        tk.messagebox.showerror("Erro", f"Arquivo {ARQUIVO_DISPOSITIVOS} não encontrado.")
        return []

def salvar_dispositivos(dispositivos):
    with open(ARQUIVO_DISPOSITIVOS, "w", encoding="utf-8") as file:
        json.dump(dispositivos, file, indent=4, ensure_ascii=False)


devices = carregar_dispositivos()

def atualizar_relogio():
    agora = datetime.now()
    hora_formatada = agora.strftime("%H:%M")
    horario.config(text=hora_formatada)
    root.after(5000, atualizar_relogio)


def reiniciar_programa():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            subprocess.Popen([exe_path])
        else:
            subprocess.Popen([sys.executable, __file__])
    except Exception as e:
        print(f"Erro ao reiniciar o programa: {e}")
    finally:
        sys.exit()


def alternar_dispositivo(dev):
    if not dev.get("ip"):
        return

    d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
    d.set_version(dev["version"])
    status = d.status()
    atual = status.get("dps", {}).get(str(dev["dps"]), False)
    novo_estado = not atual
    d.set_status(novo_estado, dev["dps"])
    atualizar_status()


ultima_temp_quarto = None
ultima_hum_quarto = None
ultima_temp_banheiro = None
ultima_hum_banheiro = None

def temp_hum_off(device_id):
    """Lê diretamente temperatura (dps1) e umidade (dps2) via LAN"""
    try:
        dev = next((d for d in devices if d["id"] == device_id), None)

        if dev and dev.get("tipo") == "temp_lan" and dev.get("ip"):
            d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
            d.set_version(dev["version"])
            status = d.status()
            dps_data = status.get("dps", {})

            temp = None
            hum = None

            # DPS fixos: 1 = temperatura (x10), 2 = umidade (%)
            if "1" in dps_data:
                temp = round(dps_data["1"] / 10, 1)
            if "2" in dps_data:
                hum = round(dps_data["2"] / 10, 1)

            return temp, hum

    except Exception as e:
        print(f"[ERRO] LAN {device_id}: {e}")

    return None, None         

# Obter Temperaturas dos sensores
def obter_temp_e_umidade(device_id):
    try:
        dev = next((d for d in devices if d["id"] == device_id), None)

        if dev and dev.get("tipo") == "temp" and dev.get("ip"):
            d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
            d.set_version(dev["version"])
            status = d.status()
            dps_data = status.get("dps", {})

            dps_temp = str(dev.get("dps_temp"))
            dps_umid = str(dev.get("dps_umid"))
            # Verifica se o DPS existe e tem valor válido
            if dps_temp in dps_data and isinstance(dps_data[dps_temp], (int, float)):
                temp = round(dps_data[dps_temp] / 10, 1)

                if dps_umid and dps_umid in dps_data:
                    hum = dps_data[dps_umid]
                    if isinstance(hum, (int, float)):
                        if device_id == "ebce725b1b52faacan1gk":  # piscina
                            hum = int(hum / 10)
                        else:
                            hum = int(hum)
                    else:
                        hum = ""
                return temp, hum

    except Exception as e:
        print(f"[ERRO] Sensor {device_id}: {e}")
        return "--", "--"

    return "--", "--"
    

def atualizar_temperaturas():
    def worker():
        # Piscina
        tp, hp = obter_temp_e_umidade('ebce725b1b52fdacan1gk')
        root.after(0, lambda: temp_piscina_label.config(text=f"  Piscina:   {tp}°C  -  {hp}%"))

        # Loja
        tl, hl = obter_temp_e_umidade('eba0dc1d90fb34e6dadln')
        root.after(0, lambda: temp_loja_label.config(text=f"  Loja:         {tl}°C  -  {hl}%"))

    threading.Thread(target=worker, daemon=True).start()
    root.after(10000, atualizar_temperaturas)


def atualizar_temperaturas_off():
    def worker():
        global ultima_temp_quarto, ultima_hum_quarto
        global ultima_temp_banheiro, ultima_hum_banheiro

        # Quarto
        tq, hq = temp_hum_off('eb0e1ad772be7841dkef4')
        if tq is not None:
            ultima_temp_quarto = tq
        if hq is not None:
            ultima_hum_quarto = hq
        root.after(0, lambda: temp_quarto_label.config(
            text=f"  Quarto:   {ultima_temp_quarto if ultima_temp_quarto is not None else '--'}°C"
                 f" - {ultima_hum_quarto if ultima_hum_quarto is not None else '--'}%"
        ))

        # Banheiro
        tb, hb = temp_hum_off('eb6366ce881bb12eb5hpj')
        if tb is not None:
            ultima_temp_banheiro = tb
        if hb is not None:
            ultima_hum_banheiro = hb
        root.after(0, lambda: temp_banheiro_label.config(
            text=f"  Banheiro: {ultima_temp_banheiro if ultima_temp_banheiro is not None else '--'}°C"
                 f" - {ultima_hum_banheiro if ultima_hum_banheiro is not None else '--'}%"
        ))

    # roda em background para não travar GUI
    threading.Thread(target=worker, daemon=True).start()
    root.after(10000, atualizar_temperaturas_off)
    

#Ar Condicionado
controle_ar.inicializar_ar(devices)


def alternar_alarme(dev):
        d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
        d.set_version(dev["version"])
        status = d.status()
        current_alarm_state = status.get("dps", {}).get('104', False)

        new_alarm_state = not current_alarm_state
        d.set_status(new_alarm_state, 104)

        atualizar_status()

estado_cortina = {}

def alternar_cortina(dev):
        global estado_cortina

        d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
        d.set_version(dev["version"])

        current_dps_state = d.status().get("dps", {}).get("1", "close")
        estado_atual = estado_cortina.get(dev["id"], current_dps_state)

        if estado_atual == "open":
            d.set_status("close", 1)
            estado_cortina[dev["id"]] = "close"
        else:
            d.set_status("open", 1)
            estado_cortina[dev["id"]] = "open"

        atualizar_status()


def alternar_portao(dev):
    d = tinytuya.Device(dev["id"], dev["ip"], dev["key"], version=dev["version"])
    status = d.status()
    dps_status = status.get("dps", {})
    atual = dps_status.get("1", False)
    d.set_status(not atual, 1)
    atualizar_status()


def desligar_tv_e_pc():
    d = tinytuya.Device('20087058f4fa25fc71b', '192.168.0.140', '63dbc1c68a04248', version=3.3)
    d.set_status(False, 1)
    time.sleep(1)
    os.system("shutdown /s /t 1")


def atualizar_status():
    root.after(30000, atualizar_status)
    for dev in devices:
        dps_key = str(dev.get("dps", "104" if dev.get("tipo") == "alarme" else "1" if dev.get("tipo") == "cortina" else "0"))
        chave = f"{dev['id']}_{dps_key}"

        label = status_labels.get(chave)
        btn = toggle_buttons.get(chave)

        if not label:
            continue

        if not dev.get("ip"):
            label.config(text="Sem IP", fg="gray")
            btn.config(relief="raised", bg="gray")
            continue

        try:
            d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
            d.set_version(dev["version"])
            data = d.status()

            if dev.get("tipo") == "alarme":
                valor = data["dps"].get('104', False)

                if valor:
                    label.config(text="Alarme Ativo", fg="green")
                    btn.config(relief="sunken", bg="lightgreen")
                else:
                    label.config(text="Desligado", fg="red")
                    btn.config(relief="raised", bg="lightcoral")

            elif dev.get("tipo") == "portao":
                valor = data["dps"].get("101", False)
                if valor:
                    label.config(text="Aberto", fg="green")
                    btn.config(relief="sunken", bg="lightgreen")
                else:
                    label.config(text="Fechado", fg="red")
                    btn.config(relief="raised", bg="lightcoral")

            elif dev.get("tipo") == "cortina":
                valor = data["dps"].get("3", 100)
                if valor:
                    label.config(text="Aberto", fg="green")
                    btn.config(relief="sunken", bg="lightgreen")
                else:
                    label.config(text="Fechado", fg="red")
                    btn.config(relief="raised", bg="lightcoral")

            #Dispositivo comum
            elif "dps" in dev and str(dev["dps"]) in data.get("dps", {}):
                valor = data["dps"][str(dev["dps"])]

                if valor in [True, "open", "on"]:
                    label.config(text="Ligado", fg="green")
                    btn.config(relief="sunken", bg="lightgreen")
                elif valor in [False, "close", "off"]:
                    label.config(text="Desligado", fg="red")
                    btn.config(relief="raised", bg="lightcoral")
                else:
                    label.config(text=str(valor), fg="black")
                    btn.config(relief="raised")
            else:
                label.config(text="DPS não encontrado", fg="gray")
                btn.config(relief="raised")

        except Exception:
            label.config(text="Offline", fg="gray")
            btn.config(relief="raised")


# Interface Tkinter
root = tk.Tk()
root.title("Controle de Dispositivos Tuya Offline 2.0 MHPS.com.br")
root.geometry("500x800")
root.resizable(True, True)
root.configure(bg="#B0E0E6")

horario = tk.Label(root, bg="#B0E0E6", font=("Arial", 14, "bold"))
horario.pack(pady=2)

#Dados dos Sensores
sensor_frame = tk.Frame(root)
sensor_frame.pack(pady=15)

temp_quarto_label = tk.Label(sensor_frame, text="  Quarto: --", bg="#B0E0E6", font=("Arial", 13, "bold"), width=23, anchor="w")
temp_quarto_label.grid(row=0, column=0, padx=2, pady=2)

temp_banheiro_label = tk.Label(sensor_frame, text="  Banheiro: --", bg="#B0E0E6", font=("Arial", 13, "bold"), width=23, anchor="w")
temp_banheiro_label.grid(row=0, column=1, padx=2, pady=2)

temp_piscina_label = tk.Label(sensor_frame, text="  Piscina: --", bg="#B0E0E6", font=("Arial", 13, "bold"), width=23, anchor="w")
temp_piscina_label.grid(row=1, column=0, padx=2, pady=2)

temp_loja_label = tk.Label(sensor_frame, text="  Loja: --", bg="#B0E0E6", font=("Arial", 13, "bold"), width=23, anchor="w")
temp_loja_label.grid(row=1, column=1, padx=2, pady=2)
atualizar_temperaturas()
atualizar_temperaturas_off()

#Botoes Ar-condicionado
frame_ar = tk.Frame(root,  bg="#B0E0E6")
frame_ar.pack(pady=5)

linha_botoes_ar = tk.Frame(frame_ar,  bg="#B0E0E6")
linha_botoes_ar.pack()

btn_toggle_ar = tk.Button(linha_botoes_ar, text="Ligar/Desligar", width=15, bg="#aed6f1", command=lambda: controle_ar.alternar_ar(devices, btn_toggle_ar, status_temp_label, status_modo_label, status_wind_label))
btn_toggle_ar.pack(side="left", padx=20)

btn_temp_mais = tk.Button(linha_botoes_ar, text="+", width=5, bg="#FF4500", command=lambda: controle_ar.aumentar_temp(devices, btn_toggle_ar, status_temp_label, status_modo_label, status_wind_label))
btn_temp_mais.pack(side="left", padx=10)

btn_temp_menos = tk.Button(linha_botoes_ar, text="−", width=5, bg="#00BFFF", command=lambda: controle_ar.diminuir_temp(devices, btn_toggle_ar, status_temp_label, status_modo_label, status_wind_label))
btn_temp_menos.pack(side="left", padx=10)

status_ar_labels_frame = tk.Frame(frame_ar, bg="#B0E0E6")
status_ar_labels_frame.pack(pady=5)

status_power_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_power_label.pack(side="left", padx=2)

status_temp_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_temp_label.pack(side="left", padx=2)

status_modo_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_modo_label.pack(side="left", padx=2)
status_modo_label.bind("<Button-1>", lambda e: controle_ar.alternar_modo_ar(e, devices, status_temp_label, status_modo_label, status_wind_label))

status_wind_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_wind_label.pack(side="left", padx=2)
status_wind_label.bind("<Button-1>", lambda e: controle_ar.alternar_wind_ar(e, devices, status_temp_label, status_modo_label, status_wind_label))

controle_ar.atualizar_status_ar(btn_toggle_ar, status_temp_label, status_modo_label, status_wind_label)

status_labels = {}
toggle_buttons = {}

device_frame = tk.Frame(root)
device_frame.pack(pady=1)

colunas = 2
linha = 0
coluna = 0

dispositivos_visiveis = [dev for dev in devices if dev.get("tipo") != "temp" and dev.get("tipo") != "ar" and dev.get("tipo") != "temp_lan"]

for dev in dispositivos_visiveis:
    frame = tk.Frame(device_frame, bg="#B0E0E6", padx=5, pady=5, bd=1, relief="ridge")
    frame.grid(row=linha, column=coluna, padx=1, pady=1, sticky="n")

    label_nome = tk.Label(frame, text=dev["name"], bg="#B0E0E6", font=("Arial", 10), width=12, anchor="e")
    label_nome.grid(row=0, column=0, padx=5, pady=2, sticky="e")

    if dev.get("tipo") == "alarme":
        btn = tk.Button(frame, text="Alarme", width=10, height=1, bg="gray", command=lambda d=dev: alternar_alarme(d))
    elif dev.get("tipo") == "cortina":
        btn = tk.Button(frame, text="Abre/Fecha", width=10, height=1, bg="lightgray", command=lambda d=dev: alternar_cortina(d))
    elif dev.get("tipo") == "portao":
        btn = tk.Button(frame, text="Abre/Fecha", width=10, height=1, bg="lightgray", command=lambda d=dev: alternar_portao(d))
    else:
        btn = tk.Button(frame, text="Liga/Desliga", width=10, height=1, bg="lightgray", command=lambda d=dev: alternar_dispositivo(d))

    btn.grid(row=0, column=1, padx=5, pady=2, sticky="w")

    status = tk.Label(frame, text="Status", bg="#B0E0E6", font=("Arial", 9))
    status.grid(row=1, column=0, columnspan=2, pady=3)

    dps_key = str(dev.get("dps", "104" if dev.get("tipo") == "alarme" else "1" if dev.get("tipo") == "cortina" else "0"))
    chave = f"{dev['id']}_{dps_key}"

    status_labels[chave] = status
    toggle_buttons[chave] = btn

    coluna += 1
    if coluna >= colunas:
        coluna = 0
        linha += 1

# Preencher com frame vazio se número de dispositivos for ímpar
if len(dispositivos_visiveis) % colunas != 0:
    frame_vazio = tk.Frame(device_frame, bg="#B0E0E6", width=213, height=67)
    frame_vazio.grid(row=linha, column=coluna, padx=1, pady=1)

#Botão Desligar TV + PC
btn_desligar_tv_pc = tk.Button(root, text="Desligar TV + PC", bg="red", fg="white", font=("Arial", 12), width=20, command=desligar_tv_e_pc)
btn_desligar_tv_pc.pack(pady=5)


#Link Pagina
def abrir_link(url):
    webbrowser.open_new_tab(url)

link = tk.Label(text="Desenvolvido por MHPS", bg="#B0E0E6", fg="blue", cursor="hand2")
link.pack(pady=20)
link.bind("<Button-1>", lambda e: abrir_link("https://www.mhps.com.br"))

# Inicializar atualizações
atualizar_relogio()
atualizar_status()
atualizar_temperaturas()
atualizar_temperaturas_off()

root.mainloop()