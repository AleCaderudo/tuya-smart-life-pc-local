import tinytuya
import tkinter as tk
import webbrowser
from tkinter import messagebox
import sys
import subprocess
import json
import os
import time
from tinytuya import Contrib


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


def atualizar_ips():
    try:
        subprocess.run(["python", "-m", "tinytuya", "scan"], check=True)
        if not os.path.exists("snapshot.json"):
            messagebox.showerror("Erro", "snapshot.json não encontrado.")
            return

        with open("snapshot.json", "r") as file:
            data = json.load(file)

        for dev in devices:
            encontrado = False
            for item in data.get("devices", []):
                if dev["id"] == item.get("id"):
                    dev["ip"] = item.get("ip", "")
                    encontrado = True
                    break
            if not encontrado:
                dev["ip"] = ""

        salvar_dispositivos(devices)

        root.destroy()
        reiniciar_programa()

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar IPs: {e}")


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
        print(f"IP não encontrado para {dev['name']}.")
        return

    try:
        d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
        d.set_version(dev["version"])
        status = d.status()
        atual = status.get("dps", {}).get(str(dev["dps"]), False)

        novo_estado = not atual
        d.set_status(novo_estado, dev["dps"])

        atualizar_status()

    except Exception as e:
        print(f"Falha ao alternar {dev['name']}.\n{e}")


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
            temp = round(dps_data.get(dps_temp, 0) / 10, 1)

            if dps_umid and dps_umid in dps_data:
                hum = dps_data[dps_umid]
                if isinstance(hum, (int, float)):
                    if device_id == "eb4466351c3248941d7cg7":
                        hum = int(hum / 10)
                    else:
                        hum = round(hum)
            else:
                hum = ""

            return temp, hum

    except Exception as e:
        print(f"[ERRO] Sensor {device_id}: {e}")
        return "--", "--"

    return "--", "--"


def atualizar_temperaturas():
    tp, hp = obter_temp_e_umidade('eb4466351c3248941d7cg7')
    temp_piscina_label.config(text=f"  Piscina:     {tp}°C  -  {hp}%")

    tl, hl = obter_temp_e_umidade('eba0dc1d90fb34ec6dadlm')
    temp_loja_label.config(text=f"  Loja:          {tl}°C  -  {hl}%")

    root.after(40000, atualizar_temperaturas)

#ar condicionado
ar_device = next((d for d in devices if d.get("tipo") == "ar"), None)

if not ar_device:
    raise Exception("Dispositivo de ar-condicionado não encontrado em meus_dispositivos.json")

DEVICE_ID = ar_device["id"]
DEVICE_IP = ar_device.get("ip", "")
LOCAL_KEY = ar_device["key"]
HEAD_FIXO = ar_device.get("head", "")

ir = Contrib.IRRemoteControlDevice(DEVICE_ID, DEVICE_IP, LOCAL_KEY, persist=True)


# Dicionários de comandos do ar condicionado, usar o ir_scan.py ou buscar os dados no log do dispositivo na nuvem tuya
comandos_temp = {
    "esfriar": {
        16: "01&^00239800040A40@*002048040006@%",
        17: "01&^00239880040A40@*00204804000E@%",
        18: "01&^00239840040A40@*002048040001@%",
        19: "01&^002398C0040A40@*002048040009@%",
        20: "01&^00239820040A40@*002048040005@%",
        21: "01&^002398A0040A40@*00204804000D@%",
        22: "01&^00239860040A40@*002048040003@%",
        23: "01&^002398E0040A40@*00204804000B@%",
        24: "01&^00239810040A40@*002048040007@%",
        25: "01&^00239890040A40@*00204804000F@%",
        26: "01&^00239850040A40@*002048040000@%",
        27: "01&^002398D0040A40@*002048040008@%",
        28: "01&^00239830040A40@*002048040004@%",
        29: "01&^002398B0040A40@*00204804000C@%",
        30: "01&^00239870040A40@*002048040002@%"
    },
    "esquentar": {
        16: "01&^00233800040A40@*002048040009@%",
        17: "01&^00233880040A40@*002048040005@%",
        18: "01&^00233840040A40@*00204804000D@%",
        19: "01&^002338C0040A40@*002048040003@%",
        20: "01&^00233820040A40@*00204804000B@%",
        21: "01&^002338A0040A40@*002048040007@%",
        22: "01&^00233860040A40@*00204804000F@%",
        23: "01&^002338E0040A40@*002048040000@%",
        24: "01&^00233810040A40@*002048040008@%",
        25: "01&^00233890040A40@*002048040004@%",
        26: "01&^00233850040A40@*00204804000C@%",
        27: "01&^002338D0040A40@*002048040002@%",
        28: "01&^00233830040A40@*00204804000A@%",
        29: "01&^002338B0040A40@*002048040006@%",
        30: "01&^00233870040A40@*00204804000E@%"
            }
}

comandos_modo = {
    "automatico": "01&^00231800040A40@*00204804000A@%",
    "ventilar":   "01&^0023D8A0040A40@*00204804000B@%",
    "humidecer":  "01&^002358A0040A40@*002048040003@%",
    "esfriar":    "01&^002398A0040A40@*00204804000D@%",
    "esquentar":  "01&^002338A0040A40@*002048040007@%"
}

comandos_fan = {
    "baixo":      "01&^002338E0040A40@*002048040000@%",
    "medio":      "01&^002334E0040A40@*002048040000@%",
    "alto":       "01&^00233CE0040A40@*002048040000@%",
    "automatico": "01&^002330E0040A40@*002048040000@%"
}

comando_desligar = "01&^00238200040A40@*002088040007@%"

# Lista ordenada para alternar modo e fan
modos = list(comandos_modo.keys())
fans = list(comandos_fan.keys())

def carregar_status():
    global status
    for dev in devices:
        if dev.get("tipo") == "ar":
            return dev.get("status", {"temperatura": 23, "modo": "esfriar", "fan": "baixo", "ligado": False})
    return {"temperatura": 23, "modo": "esfriar", "fan": "baixo", "ligado": False}


status = carregar_status()


def salvar_status():
    global status
    for dev in devices:
        if dev.get("tipo") == "ar":
            dev["status"] = status
            break
    salvar_dispositivos(devices)

def enviar_comando(key):
    try:
        ir.send_key(HEAD_FIXO, key)
    except Exception as e:
        print("Erro ao enviar comando:", e)

def alternar_ar():
    global status
    if status.get("ligado"):
        enviar_comando(comando_desligar)
        status["ligado"] = False
    else:
        modo = status["modo"]
        temp = status["temperatura"]
        key = comandos_temp.get(modo, {}).get(temp)
        if key:
            enviar_comando(key)
            status["ligado"] = True
        else:
            print("[ERRO] Sem comando para ligar")
    salvar_status()
    atualizar_status_ar()

def aumentar_temp():
    global status
    modo = status["modo"]
    temp = status["temperatura"]
    temperaturas = sorted(comandos_temp.get(modo, {}).keys())
    if temp < temperaturas[-1]:
        nova = temperaturas[temperaturas.index(temp) + 1]
        status["temperatura"] = nova
        enviar_comando(comandos_temp[modo][nova])
        salvar_status()
        atualizar_status_ar()

def diminuir_temp():
    global status
    modo = status["modo"]
    temp = status["temperatura"]
    temperaturas = sorted(comandos_temp.get(modo, {}).keys())
    if temp > temperaturas[0]:
        nova = temperaturas[temperaturas.index(temp) - 1]
        status["temperatura"] = nova
        enviar_comando(comandos_temp[modo][nova])
        salvar_status()
        atualizar_status_ar()

def alternar_modo_ar(event=None):
    global status
    idx = modos.index(status["modo"])
    novo_modo = modos[(idx + 1) % len(modos)]
    status["modo"] = novo_modo
    enviar_comando(comandos_modo[novo_modo])
    salvar_status()
    atualizar_status_ar()

def alternar_wind_ar(event=None):
    global status
    idx = fans.index(status["fan"])
    novo_fan = fans[(idx + 1) % len(fans)]
    status["fan"] = novo_fan
    enviar_comando(comandos_fan[novo_fan])
    salvar_status()
    atualizar_status_ar()

def atualizar_status_ar():
    global status
    ligado = status.get("ligado")
    temp = status.get("temperatura")
    modo = status.get("modo", "esfriar")
    fan = status.get("fan", "baixo")

    btn_toggle_ar.config(text="Desligar" if ligado else "Ligar", bg="lightgreen" if ligado else "#aed6f1")
    status_temp_label.config(text=f"Temp: {temp}°C")

    cores = {"esfriar": "blue", "esquentar": "red", "automatico": "green", "ventilar": "orange", "humidecer": "purple"}
    status_modo_label.config(text=modo.capitalize(), fg=cores.get(modo, "black"))
    status_wind_label.config(text=f"Volume de ar: {fan.capitalize()}")


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
    d = tinytuya.Device('20087058f4cfa25fc71c', '192.168.0.140', '63dbc1c68a04c249', version=3.3)
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

def tem_erro_de_comunicacao(devices):
    global name_erro
    for dev in devices:
        if dev.get("tipo") == "ar":
            continue

        if not dev.get("ip"):
            continue

        try:
            d = tinytuya.OutletDevice(dev["id"], dev["ip"], dev["key"])
            d.set_version(dev["version"])
            resp = d.status()

            if isinstance(resp, dict):
                if resp.get("Err") in ['901', '904', '905', '914']:
                    print(f"[ERRO {resp.get('Err')}] {dev['name']} - {resp.get('Error')}")
                    name_erro = dev['name']
                    return True

        except Exception as e:
            print(f"[EXCEÇÃO] ao testar {dev['name']}: {e}")
            name_erro = dev['name']
            return True

    return False


devices = carregar_dispositivos()

if tem_erro_de_comunicacao(devices):
    root = tk.Tk()
    root.title("Erro de IP/Configuração")
    root.geometry("550x200")
    root.configure(bg="#B0E0E6")

    aviso = tk.Label(root, text=f"O dispositivo {name_erro} está com IP, key ou configuração incorreta.\nClique abaixo para atualizar.", bg="#B0E0E6", font=("Arial", 12))
    aviso.pack(pady=20)

    atualizar_ip_btn = tk.Button(root, text="Atualizar IPs", command=atualizar_ips, bg="blue", fg="white", width=20)
    atualizar_ip_btn.pack(pady=10)

    root.mainloop()
    exit()


# Interface Tkinter
root = tk.Tk()
root.title("Controle de Dispositivos Tuya Offline by MHPS.com.br")
root.geometry("500x800")
root.resizable(True, True)
root.configure(bg="#B0E0E6")

tk.Label(root, text="Controle de Dispositivos Offline", bg="#B0E0E6", font=("Arial", 16)).pack(pady=15)

#Dados dos Sensores
sensor_frame = tk.Frame(root)
sensor_frame.pack(pady=15)


temp_piscina_label = tk.Label(sensor_frame, text="Piscina: --", bg="#B0E0E6", font=("Arial", 13), width=23, anchor="w")
temp_piscina_label.grid(row=1, column=0, padx=2, pady=2)

temp_loja_label = tk.Label(sensor_frame, text="Loja: --", bg="#B0E0E6", font=("Arial", 13), width=23, anchor="w")
temp_loja_label.grid(row=1, column=1, padx=2, pady=2)

#Botoes Ar-condicionado
frame_ar = tk.Frame(root,  bg="#B0E0E6")
frame_ar.pack(pady=5)

linha_botoes_ar = tk.Frame(frame_ar,  bg="#B0E0E6")
linha_botoes_ar.pack()

btn_toggle_ar = tk.Button(linha_botoes_ar, text="Ligar/Desligar", width=15, bg="#aed6f1", command=alternar_ar)
btn_toggle_ar.pack(side="left", padx=20)

btn_temp_mais = tk.Button(linha_botoes_ar, text="+", width=5, bg="#FF4500", command=aumentar_temp)
btn_temp_mais.pack(side="left", padx=10)

btn_temp_menos = tk.Button(linha_botoes_ar, text="−", width=5, bg="#00BFFF", command=diminuir_temp)
btn_temp_menos.pack(side="left", padx=10)

status_ar_labels_frame = tk.Frame(frame_ar, bg="#B0E0E6")
status_ar_labels_frame.pack(pady=5)

status_power_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_power_label.pack(side="left", padx=2)

status_temp_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_temp_label.pack(side="left", padx=2)

status_modo_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_modo_label.pack(side="left", padx=2)
status_modo_label.bind("<Button-1>", alternar_modo_ar)

status_wind_label = tk.Label(status_ar_labels_frame, bg="#B0E0E6", text="", font=("Arial", 11))
status_wind_label.pack(side="left", padx=2)
status_wind_label.bind("<Button-1>", alternar_wind_ar)

atualizar_status_ar()

status_labels = {}
toggle_buttons = {}

device_frame = tk.Frame(root)
device_frame.pack(pady=1)

colunas = 2
linha = 0
coluna = 0

dispositivos_visiveis = [dev for dev in devices if dev.get("tipo") != "temp" and dev.get("tipo") != "ar"]

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

#Botão Atualizar IP
frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=5)
atualizar_ip_btn = tk.Button(frame_bottom, text="Atualizar IPs", command=atualizar_ips, bg="blue", fg="white", width=15)
atualizar_ip_btn.pack()

#Link Pagina
def abrir_link(url):
    webbrowser.open_new_tab(url)

link = tk.Label(text="Desenvolvido por MHPS", bg="#B0E0E6", fg="blue", cursor="hand2")
link.pack(pady=20)
link.bind("<Button-1>", lambda e: abrir_link("https://www.mhps.com.br"))

# Inicializar atualizações
status = carregar_status()
atualizar_status_ar()
atualizar_status()
atualizar_temperaturas()

root.mainloop()