import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

dataset = pd.read_csv('datasetMbee.csv')
dataset['Data e hora'] = pd.to_datetime(dataset['Data e hora'])
dataset = dataset.sort_values('Data e hora')

subconjunto = 121
ordemPolinomial = 2
dataset['Massa_filtrada'] = savgol_filter(
    dataset['Massa'],
    subconjunto,
    ordemPolinomial
)

plt.style.use('dark_background')
plt.figure(figsize=(12, 6))

plt.plot(
    dataset['Data e hora'],
    dataset['Massa'],
    color='dimgray',
    linewidth=1,
    label='Massa (original)'
)

plt.plot(
    dataset['Data e hora'],
    dataset['Massa_filtrada'],
    color='cyan',
    linewidth=2,
    label='Massa (filtrada - Savitzky-Golay)'
)

plt.title('Massa da Colmeia - Suavização com Filtro Savitzky-Golay')
plt.xlabel('Data e Hora')
plt.ylabel('Massa (g)')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()