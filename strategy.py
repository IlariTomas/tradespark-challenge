import backtrader as bt
import pandas as pd


class MultiStrategy(bt.Strategy):
    params = (
        ('pfast', 10),
        ('pslow', 30),
        ('porc_inversion', 0.10),  # 10% del portafolio por estrategia
    )

    def __init__(self):
        # Diccionario de indicadores de cada instrumento
        self.inds = {}
        
        # Contador de posiciones por estrategia
        self.strat_positions = {}

        # Log para mostrar las variaciones del valor del portafolio
        self.portfolio_history = []

        # Log para escribir transacciones
        self.transactions = []

        for d in self.datas:
            smafast = bt.indicators.SMA(d.close, period=self.params.pfast)
            smaslow = bt.indicators.SMA(d.close, period=self.params.pslow)
            self.inds[d] = {
                'sma10': smafast,
                'sma30': smaslow,
                'crossover': bt.indicators.CrossOver(smafast, smaslow)
            }
            self.strat_positions[d._name] = {1: 0, 2: 0, 3: 0}

    def notify_order(self, order):
        # Metodo para notificar sobre el estado de las órdenes
        if order.status in [order.Completed]:
            # Recuperamos el ID de la estrategia
            strat_id = order.info.get('strategy_idx', 'N/A')

            if order.isbuy():
                # Guardo la transaccion para el output
                self.transactions.append({
                    'Fecha': self.datas[0].datetime.date(0),
                    'Instrumento': order.data._name,
                    'Estrategia': f"Estrategia {strat_id}",
                    'Operacion': 'COMPRA',
                    'Precio': order.executed.price,
                    'Cantidad': order.executed.size,
                    'Costo': order.executed.value,
                    'Comision': order.executed.comm
                })

                print(f'COMPRA EJECUTADA: {order.data._name} Precio: {order.executed.price:.2f} Costo: {order.executed.value:.2f}')
            elif order.issell():
                self.transactions.append({
                    'Fecha': self.datas[0].datetime.date(0),
                    'Instrumento': order.data._name,
                    'Estrategia': f"Estrategia {strat_id}",
                    'Operacion': 'VENTA',
                    'Precio': order.executed.price,
                    'Cantidad': order.executed.size,
                    'Resultado': order.executed.pnl,
                    'Comision': order.executed.comm
                })
                print(f'VENTA EJECUTADA: {order.data._name} Precio: {order.executed.price:.2f}')
            
    # Imprimo las transacciones al finalizar
    def stop(self):
        print("\n--- RESUMEN DE TRANSACCIONES ---")
        if self.transactions:
            df = pd.DataFrame(self.transactions)
            print(df.to_string())
        else:
            print("No se realizaron operaciones.")

        print("\n--- EVOLUCIÓN DEL PORTAFOLIO ---")
        if self.portfolio_history:
            df = pd.DataFrame(self.portfolio_history)
            print(df.to_string())
        else:
            print("No se realizaron operaciones.")

        

    # Verifica condiciones que haya liquidez y el tamaño suficiente para comprar
    def buy_condition(self, cash, target, size, name):
        if cash < target:
            print(f"NO HAY LIQUIDEZ: Quiero gastar {target:.2f} pero tengo {cash:.2f}")
            return False
        
        if size < 1:
            print(f"FONDOS INSUFICIENTES PARA 1 UNIDAD DEL INSTRUMENTO {name}")
            return False
        return True
    
    # Metodo que encapsula la lógica de compra y actualización de efectivo y posiciones
    def execute_buy(self, data, size, cash, strat_idx):
        self.strat_positions[data._name][strat_idx] += size

        # Obtengo la orden para agregarle con que estrategia fue realizada, para poder informarlo mas tarde en el log de transacciones
        order = self.buy(data=data, size=size)
        order.addinfo(strategy_idx=strat_idx)

        cash -= size * data.close[0]
        return cash
    
    def execute_sell(self, data, size, cash, strat_idx):
        order = self.sell(data=data, size=size)
        order.addinfo(strategy_idx=strat_idx)

        cash += size * data.close[0]
        self.strat_positions[data._name][strat_idx] = 0
        return cash

    def next(self):

        # Guardo datos del portafolio al principio del next para tener la foto del dia
        self.portfolio_history.append({
            'Fecha': self.datas[0].datetime.date(0),
            'Valor_Total': self.broker.getvalue(),
            'Efectivo': self.broker.get_cash()
        })

        # Itero sobre todos los instrumentos
        for d in self.datas:
            name = d._name
            cash = self.broker.get_cash()
            portfolio_value = self.broker.get_value()
            
            # Defino el tamaño de la inversión
            target_invest = portfolio_value * self.params.porc_inversion
            # Calculo cuántas acciones puedo comprar aproximadamente
            size_to_buy = int(target_invest / d.close[0])

            # ESTRATEGIA 1: Precio > SMA 10
            # Condición de COMPRA
            if d.close[0] > self.inds[d]['sma10'][0] and self.strat_positions[name][1] == 0:  # Verifico si la estrategia me eprmite comprar y si no compre antes con la misma estrategia
                if self.buy_condition(cash, target_invest, size_to_buy, name): # Si la estrategia permite comprar, verifico liquidez y tamaño
                # self.inds[instrumento][media_a_usar][tiempo (0 es el valor en este momento)]
                    cash = self.execute_buy(d, size_to_buy, cash, 1)
                

            # Condición de VENTA
            elif d.close[0] < self.inds[d]['sma10'][0]:
                qty_in_strat_1 = self.strat_positions[name][1] # Vendo solo lo comprado por esta estrategia
                if qty_in_strat_1 > 0:
                    cash = self.execute_sell(d, qty_in_strat_1, cash, 1)

            # ESTRATEGIA 2: Precio > SMA 30
            # Condición de COMPRA
            if d.close[0] > self.inds[d]['sma30'][0] and self.strat_positions[name][2] == 0:
                if self.buy_condition(cash, target_invest, size_to_buy, name):
                    cash = self.execute_buy(d, size_to_buy, cash, 2)

            # Condición de VENTA
            elif d.close[0] < self.inds[d]['sma30'][0]:
                qty_in_strat_2 = self.strat_positions[name][2]
                if qty_in_strat_2 > 0:
                    cash = self.execute_sell(d, qty_in_strat_2, cash, 2)
                

            # ESTRATEGIA 3: Cruce de 10 sobre 30
            if self.inds[d]['crossover'][0] > 0 and self.strat_positions[name][3] == 0: # Significa cruce hacia arriba (condicion de compra)
                if self.buy_condition(cash, target_invest, size_to_buy, name):
                    cash = self.execute_buy(d, size_to_buy, cash, 3)
            elif self.inds[d]['crossover'][0] < 0: # Significa cruce hacia abajo (condicion de venta)
                qty_in_strat_3 = self.strat_positions[name][3]
                if qty_in_strat_3 > 0:
                    cash = self.execute_sell(d, qty_in_strat_3, cash, 3)