# tradespark-challenge
Este repositorio contiene la solución al desafío técnico para la posición de **Desarrollador de Trading Algorítmico Trainee**.

El proyecto implementa un sistema de trading automatizado utilizando el framework `backtrader`, capaz de gestionar múltiples estrategias simultáneas sobre una cartera de activos (MSFT, GOOG, AAPL, TSLA) respetando la independencia de posiciones y capital asignado.

## Descripción del Desafío

El objetivo fue desarrollar una estrategia combinada que opere bajo las siguientes reglas:
1.  **Estrategia 1:** Cruce de precio sobre SMA 10.
2.  **Estrategia 2:** Cruce de precio sobre SMA 30.
3.  **Estrategia 3:** Golden Cross (SMA 10 cruza SMA 30).
4.  **Gestión de Capital:** 10% del valor del portfolio por operación, validando liquidez disponible.
5.  **Separación de Inventarios:** Las ventas solo afectan a las posiciones generadas por su propia estrategia.

## Decisiones Técnicas y Arquitectura

### 1. Gestión de Datos (Data Feeds)
* Los datasets históricos (Año 2021) son descargados mediante yfinance.download().
* El sistema carga estos archivos automáticamente mediante `bt.feeds.PandasData`.

### 2. Aislamiento de Estrategias
Para cumplir con el requisito de *"vender solo lo comprado por esa estrategia"*, se implementó un sistema de contabilidad interna dentro de la clase `MultiStrategy`:
* Uso de diccionarios para saber el tamaño de cada instrumento adquirido con cada estrategia.
* Lógica de `buy_condition` encapsulada para validar liquidez y tamaño de orden antes de emitir señales.

### 3. Clean Code & Reporting
* Se aplicaron principios de encapsulamiento con métodos auxiliares (`execute_buy`, `execute_sell`) para mantener el loop principal limpio y escalable.
* Se implementó un sistema de **Logging de Transacciones** y cálculo de **Variación del Portfolio** que se imprime al finalizar la ejecución.

## Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/IlariTomas/tradespark-challenge.git
   cd tradespark-challenge
   ```

3. **Crear y activar un ambiente**
    ```bash
    python -m venv <nombre_ambiente>
    <nombre_ambiente>\Scripts\activate
    ```

5. **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

7. **Ejecutar la estrategia**
    ```bash
    python main.py
    ```
