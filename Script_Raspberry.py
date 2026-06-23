import time
import smbus
import RPi.GPIO as GPIO
from hx711 import HX711
import board
import adafruit_ahtx0
import requests
import random as rd
import gc
import csv
from datetime import datetime
import os

url = "https://lse.cp.utfpr.edu.br/mbee/post-data.php"
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=6, pd_sck_pin=5)

def ler_sensor_interno():
    endereco = 0x38
    i2cbus = smbus.SMBus(1)
    time.sleep(1)
    data = i2cbus.read_i2c_block_data(endereco, 0x71, 1)
    
    if (data[0] | 0x08) == 0:
        t1 = 'ERRO'
        h1 = 'ERRO'
    else:
        i2cbus.write_i2c_block_data(endereco, 0xac, [0x33, 0x00])
        time.sleep(0.1)
        data = i2cbus.read_i2c_block_data(endereco, 0x71, 7)
        TempBruta = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
        temperatura = 200 * float(TempBruta) / 2**20 - 50
        UmidadeBruta = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
        umidade = 100 * float(UmidadeBruta) / 2**20
        t1 = temperatura
        h1 = umidade
    return t1, h1

def ler_sensor_externo():
    endereco = 0x39
    i2cbus = smbus.SMBus(1)
    time.sleep(1)
    data = i2cbus.read_i2c_block_data(endereco, 0x71, 1)
    
    if (data[0] | 0x08) == 0:
        t2 = 'ERRO'
        h2 = 'ERRO'
    else:
        i2cbus.write_i2c_block_data(endereco, 0xac, [0x33, 0x00])
        time.sleep(0.1)
        data = i2cbus.read_i2c_block_data(endereco, 0x71, 7)
        TempBruta = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
        temperatura = 200 * float(TempBruta) / 2**20 - 50
        UmidadeBruta = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
        umidade = 100 * float(UmidadeBruta) / 2**20
        t2 = temperatura
        h2 = umidade
    return t2, h2

def ler_sensor_carga():
    hx.reset()
    reading = hx.get_raw_data()
    media = 0
    for i in reading:
        media += i
    media /= 5
    offset = 556409
    tara_plataforma = 548
    massa = (((media + offset) / 1000) * 4.769921) - tara_plataforma
    
    if 2500 < massa < 4500:
        return massa
    else:
        return 'ERRO'

def salvar_localmente(t1, h1, t2, h2, massa):
    hive = 1
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = [
        data_hora,
        float("{:.1f}".format(t1)),
        float("{:.1f}".format(t2)),
        float("{:.1f}".format(h1)),
        float("{:.1f}".format(h2)),
        float("{:.0f}".format(massa)),
        hive
    ]
    arquivo_existe = os.path.exists("dados_locais.csv")
    try:
        with open("dados_locais.csv", "a", newline="") as arquivo:
            writer = csv.writer(arquivo)
            if not arquivo_existe:
                writer.writerow([
                    "Data e Hora",
                    "Temperatura Interna",
                    "Temperatura Externa",
                    "Umidade Interna",
                    "Umidade Externa",
                    "Hive"
                ])
            writer.writerow(payload)
    except:
        pass

while True:
    t1, h1 = ler_sensor_interno()
    time.sleep(3)
    t2, h2 = ler_sensor_externo()
    time.sleep(3)
    massa = ler_sensor_carga()
    time.sleep(3)
    
    if 'ERRO' not in [t1, h1, t2, h2, massa]:
        payload = {
            "api_key": "SEGREDO",
            "int_temp": float("{:.1f}".format(t1)),
            "ext_temp": float("{:.1f}".format(t2)),
            "int_humid": float("{:.1f}".format(h1)),
            "ext_humid": float("{:.1f}".format(h2)),
            "mass": float("{:.0f}".format(massa)),
            "hive": 1
        }
        time.sleep(3)
        try:
            response = requests.post(url, data=payload)
        except Exception as e:
            print(f"Erro na requisição HTTP: {e}")
            
        salvar_localmente(t1, h1, t2, h2, massa)
        del payload, t1, t2, h1, h2, massa
        gc.collect()
        
    time.sleep(20)