
# Tuya Smart-life PC Local

Este projeto é uma solução local (offline) em Python com interface gráfica para controle de dispositivos inteligentes Tuya usando a biblioteca `tinytuya`. Ele permite o controle completo de dispositivos via rede LAN, sem depender da nuvem Tuya.

![Interface](offline.jpg)

## ⚙️ Funcionalidades

- Controle local (LAN) de dispositivos Tuya, sem uso da internet
- Suporte a dispositivos:
  - Comuns (ligar/desligar)
  - Cortinas (abrir/fechar)
  - Portões automáticos
  - Alarmes
  - Ar-condicionado IR com ajuste de temperatura, modo e intensidade
- Leitura de sensores de temperatura e umidade
- Detecção de IPs incorretos e opção de correção automática
- Armazenamento de status dos dispositivos
- Aprendizado de botões IR com extração de head/key (arquivo separado)

## 📦 Arquivos

- `tuya_lan.py`: Interface principal com controle dos dispositivos via LAN.
- `meus_dispositivos.json`: Lista com os dispositivos configurados (IDs, IPs, keys, tipo e versão).
- `ir_scan.py`: Ferramenta para aprender botões infravermelho, capturando `head` e `key` dos comandos.
- `offline.jpg`: Imagem ilustrativa da interface gráfica.

## 🛠️ Requisitos

- Python 3.9 ou superior
- Dispositivos compatíveis com controle via LAN (protocolo Tuya 3.3 ou 3.4)
- Biblioteca necessária:
  ```bash
  pip install tinytuya
  ```

## 🚀 Como usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/tuya-smartlife-pc-local.git
   cd tuya-smartlife-pc-local
   ```

2. Edite o arquivo `meus_dispositivos.json` com as configurações dos seus dispositivos:
   ```json
   {
     "name": "Luz Quarto",
     "id": "xxxxxxxxxxxxxxxx",
     "ip": "192.168.x.x",
     "key": "xxxxxxxxxxxxxxxx",
     "version": 3.3,
     "dps": 1
   }
   ```

3. Execute a interface gráfica:
   ```bash
   python tuya_lan.py
   ```

4. (Opcional) Para aprender comandos IR, execute:
   ```bash
   python ir_scan.py
   ```

## 🔄 Atualização de IPs

Se algum dispositivo mudar de IP, o programa detecta automaticamente e oferece uma opção para atualizar com um clique (requer `tinytuya scan`).

## 💡 Observações

- O controle de ar-condicionado funciona com IR Blaster Tuya. Os comandos devem ser previamente aprendidos e salvos como `head/key`.
- O sistema armazena o último status de uso localmente.
- O botão "Desligar TV + PC" pode ser personalizado para desligar qualquer dispositivo + o próprio computador.

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.

## 👨‍💻 Desenvolvido por

[MHPS](https://www.mhps.com.br) – Soluções em automação e sistemas inteligentes.
