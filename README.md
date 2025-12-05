# Simulación SIR — Secuencial y Paralela (Python)

**Proyecto**: simulación epidemiológica SIR en una grilla 2D (hasta **1000×1000 = 1,000,000** individuos) con versiones secuencial y paralela, comparaciones y visualizaciones.

---

## Descripción

Este repositorio contiene una implementación de un modelo SIR sobre una malla 2D con las siguientes capacidades:

* Implementación **secuencial**.
* Implementación **paralela** usando `multiprocessing` (varios workers).
* Comparación de *snapshots* entre ambas versiones para verificar equivalencia.
* Scripts para ejecutar experimentos de forma automática (pequeños y grandes).
* Scripts para generar animaciones (GIF / MP4) que comparan visualmente las ejecuciones.

El README explica cómo ejecutar todo desde cero en Windows o Linux.

---

## Requisitos

* Python 3.9+ (recomendado 3.10/3.11)
* `git`
* Memoria suficiente para simulaciones grandes (1000×1000 puede consumir varios GB de RAM)

Dependencias Python (instaladas desde `requirements.txt`):

```sh
pip install -r requirements.txt
```

Si quieres generar MP4 necesitarás `imageio[ffmpeg]` y/o `ffmpeg` instalado en el sistema:

```sh
pip install "imageio[ffmpeg]"
# en Linux (opcional, instalación del binario del sistema):
# Debian/Ubuntu: sudo apt install ffmpeg
# macOS (Homebrew): brew install ffmpeg
```

---

## Estructura del proyecto

```
mc_sir_project/
│── main.py
│── parallel.py
│── sequential.py
│── run_experiments.py
│── visualize_side_by_side.py
│── requirements.txt
│── snapshots_seq/          # generado automáticamente
│── snapshots_par_w4/      # generado automáticamente (ejemplo)
│── results/               # generado automáticamente
│── animations/            # generado automáticamente
```

---

## 1 — Crear un entorno virtual

### Windows (PowerShell / CMD)

```powershell
# Crear y activar virtualenv (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1    # PowerShell
# o en CMD:
# venv\Scripts\activate

pip install -r requirements.txt
```

### Linux / macOS

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 2 — Clonar el repositorio

```sh
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

Asegúrate de que los archivos principales estén en la raíz del proyecto:

* `main.py`
* `parallel.py`
* `sequential.py`
* `run_experiments.py`
* `visualize_side_by_side.py`

---

## 3 — Ejecutar `main.py` (demo y verificación rápida)

El script `main.py` ejecuta una demo pequeña de la versión paralela y la secuencial, guarda snapshots y realiza comparaciones básicas.

```sh
python main.py
```

Al finalizar, es normal encontrar carpetas como:

* `snapshots_seq/`
* `snapshots_par_w4/`
* `snapshots_seq_big/`
* `snapshots_par_w8/`

(si tu `main.py` está configurado para esas salidas).

---

## 4 — Ejecutar experimentos manualmente

Puedes abrir una terminal nueva para lanzar `run_experiments.py` con distintos tamaños y número de workers.

### Experimentos pequeños (ej. 200×200, modo rápido)

```sh
python run_experiments.py --H 200 --W 200 --days 60 --seed 42 --workers 1 2 4 8 --quick
```

### Experimentos grandes (ej. 1000×1000)

> **Advertencia**: 1000×1000 puede consumir mucha RAM y CPU. Asegúrate de tener suficiente memoria (~8–16 GB o más según configuración).

```sh
python run_experiments.py --H 1000 --W 1000 --days 365 --seed 42 --workers 1 2 4 8
```

Si deseas repetir los experimentos pequeños:

```sh
python run_experiments.py --H 200 --W 200 --days 60 --seed 42 --workers 1 2 4 8 --quick
```

Los resultados se guardarán en `results/` con subcarpetas típicas como:

```
results/Pequeno/
results/Grande/
```

(Ajusta los nombres según la implementación de `run_experiments.py` en tu repo.)

---

## 5 — Generar animaciones comparativas (GIF / MP4)

Para crear una animación lado a lado entre la versión secuencial y paralela:

```sh
python visualize_side_by_side.py --seq snapshots_seq --par snapshots_par_w4 --out animations/side_by_side_w4.gif
```

El script leerá los snapshots en las carpetas indicadas y generará `animations/side_by_side_w4.gif`.
Si `ffmpeg` está disponible, también podrá generar `animations/side_by_side_w4.mp4`.

---

## 6 — Notas prácticas y troubleshooting

* **Velocidad / paralelismo**: la mejora con `multiprocessing` depende del tamaño del problema y del coste de sincronización/IO. Para `1000×1000` suele notarse mejora con 4–8 workers en máquinas con varios núcleos.
* **Memoria**: una grilla 1000×1000 con varios arrays por celda puede usar decenas de MB o varios GB. Si ves `MemoryError`, reduce el tamaño H×W o usa menos workers.
* **Reproducibilidad**: usa `--seed` para fijar generadores aleatorios y comparar snapshots.
* **Comparación de snapshots**: si los snapshots no coinciden idénticamente, revisa si hay operaciones no deterministas (p. ej. orden en listas compartidas). La comparación debe tolerar pequeñas diferencias numéricas, o usar un *hash* determinista si el algoritmo lo permite.
* **FFmpeg**: si la conversión a MP4 falla, verifica que `ffmpeg` esté en el `PATH`.

---

## 7 — Ejemplo de comandos frecuentes (resumen rápido)

```sh
# Activar entorno (Linux/mac)
source venv/bin/activate

# Ejecutar demo completo
python main.py

# Experimentos pequeños (rápidos)
python run_experiments.py --H 200 --W 200 --days 60 --seed 42 --workers 1 2 4 8 --quick

# Experimentos grandes
python run_experiments.py --H 1000 --W 1000 --days 365 --seed 42 --workers 1 2 4 8

# Generar animación comparativa
python visualize_side_by_side.py --seq snapshots_seq --par snapshots_par_w4 --out animations/side_by_side_w4.gif
```
---

# Animación Final Generada Basado En Pruebas

VideoDelResultado/side_by_side_w4.gif
---


