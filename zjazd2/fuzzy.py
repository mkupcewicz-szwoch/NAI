"""
Projekt: Rozmyty regulator prędkości wentylatora procesora.

Opis problemu:
Celem projektu jest stworzenie regulatora rozmytego,
który na podstawie temperatury procesora, jego obciążenia
oraz temperatury otoczenia wyznacza odpowiednią prędkość
wentylatora chłodzącego procesor.

Autorzy:
- Szymon Witowski s29099
- Maciej Kupcewicz-Szwoch s29467


Środowisko:
- Python 3
- NumPy
- scikit-fuzzy
- Matplotlib
- NetworkX
- SciPy


Instalacja bibliotek:
pip install numpy scikit-fuzzy matplotlib

Uruchomienie:
python fuzzy_generator.py
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


# =====================================================
# 1. DEFINICJA WEJŚĆ I WYJŚCIA
# =====================================================

cpu_temperature = ctrl.Antecedent(np.arange(20, 101, 1), 'cpu_temperature')
cpu_usage = ctrl.Antecedent(np.arange(0, 101, 1), 'cpu_usage')
ambient_temp = ctrl.Antecedent(np.arange(10, 41, 1), 'ambient_temp')

fan_speed = ctrl.Consequent(np.arange(0, 101, 1), 'fan_speed')


# =====================================================
# 2. FUNKCJE PRZYNALEŻNOŚCI
# =====================================================

cpu_temperature['low'] = fuzz.trimf(cpu_temperature.universe, [20, 20, 50])
cpu_temperature['medium'] = fuzz.trimf(cpu_temperature.universe, [40, 60, 80])
cpu_temperature['high'] = fuzz.trimf(cpu_temperature.universe, [70, 100, 100])

cpu_usage['low'] = fuzz.trimf(cpu_usage.universe, [0, 0, 40])
cpu_usage['medium'] = fuzz.trimf(cpu_usage.universe, [20, 50, 80])
cpu_usage['high'] = fuzz.trimf(cpu_usage.universe, [60, 100, 100])

ambient_temp['low'] = fuzz.trimf(ambient_temp.universe, [10, 10, 22])
ambient_temp['medium'] = fuzz.trimf(ambient_temp.universe, [18, 25, 32])
ambient_temp['high'] = fuzz.trimf(ambient_temp.universe, [28, 40, 40])

fan_speed['low'] = fuzz.trimf(fan_speed.universe, [0, 0, 40])
fan_speed['medium'] = fuzz.trimf(fan_speed.universe, [25, 50, 75])
fan_speed['high'] = fuzz.trimf(fan_speed.universe, [60, 100, 100])


# =====================================================
# 3. REGUŁY ROZMYTE
# =====================================================

# Wysoka temperatura CPU powoduje ustawienie wysokiej prędkości wentylatora.
rule1 = ctrl.Rule(
    cpu_temperature['high'],
    fan_speed['high']
)

rule2 = ctrl.Rule(
    cpu_temperature['medium'] & cpu_usage['high'],
    fan_speed['high']
)

rule3 = ctrl.Rule(
    cpu_temperature['medium'] & ambient_temp['high'],
    fan_speed['high']
)

rule4 = ctrl.Rule(
    cpu_temperature['medium'] & cpu_usage['medium'] & ambient_temp['low'],
    fan_speed['medium']
)

rule5 = ctrl.Rule(
    cpu_temperature['medium'] & cpu_usage['medium'] & ambient_temp['medium'],
    fan_speed['medium']
)

rule6 = ctrl.Rule(
    cpu_temperature['medium'] & cpu_usage['low'] & ambient_temp['medium'],
    fan_speed['medium']
)

rule7 = ctrl.Rule(
    cpu_temperature['medium'] & cpu_usage['low'] & ambient_temp['low'],
    fan_speed['low']
)

rule8 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['high'] & ambient_temp['high'],
    fan_speed['high']
)

rule9 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['high'] &
    (ambient_temp['low'] | ambient_temp['medium']),
    fan_speed['medium']
)

rule10 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['medium'] & ambient_temp['high'],
    fan_speed['medium']
)

rule11 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['medium'] & ambient_temp['medium'],
    fan_speed['medium']
)

rule12 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['medium'] & ambient_temp['low'],
    fan_speed['low']
)

rule13 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['low'] & ambient_temp['high'],
    fan_speed['medium']
)

rule14 = ctrl.Rule(
    cpu_temperature['low'] & cpu_usage['low'] &
    (ambient_temp['low'] | ambient_temp['medium']),
    fan_speed['low']
)


# =====================================================
# 4. SYSTEM WNIOSKOWANIA
# =====================================================

fan_ctrl = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, rule6, rule7,
    rule8, rule9, rule10, rule11, rule12, rule13, rule14
])

fan_sim = ctrl.ControlSystemSimulation(fan_ctrl)


# =====================================================
# 5. WARTOŚCI POCZĄTKOWE
# =====================================================

val_cpu_temperature = 35.0
val_cpu_usage = 20.0
val_ambient_temp = 22.0
val_fan_speed = 0.0


# =====================================================
# 6. HISTORIA DANYCH DO WYKRESU
# =====================================================

history_temp = []
history_usage = []
history_ambient = []
history_fan = []
iterations = []


# =====================================================
# 7. WYKRESY FUNKCJI PRZYNALEŻNOŚCI
# =====================================================

plt.ion()
fig_membership, axes = plt.subplots(2, 2, figsize=(11, 7))

variables = [
    (cpu_temperature, axes[0, 0], 'Temperatura CPU (°C)'),
    (cpu_usage, axes[0, 1], 'Obciążenie CPU (%)'),
    (ambient_temp, axes[1, 0], 'Temperatura otoczenia (°C)'),
    (fan_speed, axes[1, 1], 'Prędkość wentylatora (%)')
]

for variable, ax, title in variables:
    for label in variable.terms:
        ax.plot(
            variable.universe,
            variable[label].mf,
            label=label
        )

    ax.set_title(title)
    ax.set_xlabel('Wartość')
    ax.set_ylabel('Stopień przynależności')
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True)

fig_membership.tight_layout()


# =====================================================
# 8. WYKRES SYMULACJI
# =====================================================

fig, (ax_temp, ax_percent) = plt.subplots(
    2, 1, figsize=(10, 7), sharex=True
)

# Wykres temperatur
line_temp, = ax_temp.plot(
    [], [], color='red', label='Temperatura CPU (°C)'
)

line_ambient, = ax_temp.plot(
    [], [], color='green', label='Temperatura otoczenia (°C)'
)

ax_temp.set_title('Symulacja pracy regulatora wentylatora')
ax_temp.set_ylabel('Temperatura (°C)')
ax_temp.set_ylim(10, 100)
ax_temp.legend()
ax_temp.grid(True)

# Wykres wartości procentowych
line_usage, = ax_percent.plot(
    [], [], color='orange', label='Obciążenie CPU (%)'
)

line_fan, = ax_percent.plot(
    [], [], color='blue', label='Prędkość wentylatora (%)'
)

ax_percent.set_xlabel('Krok symulacji')
ax_percent.set_ylabel('Wartość (%)')
ax_percent.set_ylim(0, 100)
ax_percent.legend()
ax_percent.grid(True)

fig.tight_layout()

fig_membership.canvas.draw()
fig.canvas.draw()
plt.pause(0.1)


# =====================================================
# 9. FUNKCJA AKTUALIZUJĄCA WYKRES
# =====================================================

def update_plot():
    """Aktualizuje wykres na podstawie zapisanej historii danych."""

    line_temp.set_data(iterations, history_temp)
    line_ambient.set_data(iterations, history_ambient)

    line_usage.set_data(iterations, history_usage)
    line_fan.set_data(iterations, history_fan)

    ax_temp.relim()
    ax_temp.autoscale_view(scalex=True, scaley=False)

    ax_percent.relim()
    ax_percent.autoscale_view(scalex=True, scaley=False)

    plt.pause(0.1)

# =====================================================
# 10. FUNKCJA SYMULUJĄCA PRACĘ KOMPUTERA
# =====================================================

def operate_computer(step):
    """
    Oblicza prędkość wentylatora i symuluje zmianę temperatury CPU.

    Argument:
        step - numer aktualnego kroku symulacji.
    """

    global val_cpu_temperature, val_fan_speed

    # Przekazanie aktualnych danych do systemu rozmytego
    fan_sim.input['cpu_temperature'] = val_cpu_temperature
    fan_sim.input['cpu_usage'] = val_cpu_usage
    fan_sim.input['ambient_temp'] = val_ambient_temp

    fan_sim.compute()

    # Odczyt obliczonej prędkości wentylatora
    val_fan_speed = fan_sim.output['fan_speed']

    # Generowanie ciepła zależne od obciążenia procesora
    heat_gain = val_cpu_usage * 0.10

    # Chłodzenie zależne od prędkości wentylatora i temperatury otoczenia
    cooling = (val_cpu_temperature - val_ambient_temp) * (val_fan_speed / 100) * 0.4

    # Aktualizacja temperatury procesora
    val_cpu_temperature += heat_gain - cooling

    # Ograniczenie temperatury do zakresu 20-100°C
    val_cpu_temperature = max(20, min(100, val_cpu_temperature))

    # Wyświetlenie aktualnych wartości
    print("\nKrok Symulacji:", step)
    print(f"Temperatura CPU: {val_cpu_temperature:.2f} °C")
    print(f"Obciążenie CPU: {val_cpu_usage:.2f}%")
    print(f"Temperatura otoczenia: {val_ambient_temp:.2f} °C")
    print(f"Prędkość wentylatora: {val_fan_speed:.2f}%")

    # Zapis aktualnych danych do historii
    iterations.append(step)
    history_temp.append(val_cpu_temperature)
    history_usage.append(val_cpu_usage)
    history_ambient.append(val_ambient_temp)
    history_fan.append(val_fan_speed)

    # Aktualizacja wykresu
    update_plot()


# =====================================================
# 11. PĘTLA SYMULACJI
# =====================================================

step = 0

print("SYMULACJA REGULATORA WENTYLATORA CPU")
print("------------------------------------")
print("Enter - kontynuuj z aktualnymi wartościami")
print("70 - ustaw obciążenie CPU na 70%")
print("70,30 - ustaw obciążenie CPU na 70% i otoczenie na 30°C")
print("exit - zakończ symulację")

while True:

    value = input(
        "\nNowe obciążenie CPU, opcjonalnie temperatura otoczenia: "
    ).strip()

    if value.lower() == "exit":
        break

    if value != "":
        values = value.split(",")

        if len(values) > 2:
            print("Podaj obciążenie,temperaturę otoczenia.")
            continue

        try:
            new_usage = float(values[0])
            new_ambient = val_ambient_temp

            if len(values) == 2:
                new_ambient = float(values[1])

        except ValueError:
            print("Nieprawidłowe dane. Przykład: 70 lub 70,30")
            continue

        if not 0 <= new_usage <= 100:
            print("Obciążenie musi być w zakresie 0-100%.")
            continue

        if not 10 <= new_ambient <= 40:
            print("Temperatura otoczenia musi być w zakresie 10-40°C.")
            continue

        val_cpu_usage = new_usage
        val_ambient_temp = new_ambient

    step += 1

    operate_computer(step)



print("\nSymulacja została zakończona.")