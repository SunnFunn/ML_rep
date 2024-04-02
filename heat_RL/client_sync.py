#Данный клиент имитирует работу клиента SCADA исключительно для целей тестирования и корректировки работы сервера


from app import forecast_hours, modeling_period, url_msk
from app.parsing import get_temperatures_forecast

import time
import numpy as np
from tabulate import tabulate
from pymodbus.client import ModbusTcpClient as ModbusClient

#функция имитации остывания/нагревания объекта
#рассчитывает температуру внутри здания через заданный промежуток времени (3 часа) в зависимости от:
#температуры теплоносителя и погодных условий
def next_temp(tin, theat):
    temperature_current, temperature_next, wind, humidity, cloudiness = get_temperatures_forecast(url_msk)
    state = [tin, temperature_current, temperature_next, wind, humidity, cloudiness]
    betta = 1 + (state[4] + state[5] + state[3] / 5) / 3
    tout = (state[1] + state[2]) / 2
    tin = state[0]
    Q = (theat - 33) / 120
    tin_next = tout + Q / 0.007 + (tin - tout - Q / 0.007) / (np.exp(forecast_hours * betta / 70))
    return tin_next

#функция запуска клиента, передачи им серверу температуры внутри помещения и чтение температуры теплоносителя
#и других данных
def run_client(host: str,
               port: int,
               read_address: int,
               read_count: int,
               write_address: int,
               write_input: str) -> float:
    #создаем клиента и открываем соединение с сервером
    client = ModbusClient(host=host, port=port, timeout=30)
    assert client.connect()

    #пишем во второй регистр температуру
    write_input_registers = client.convert_to_registers(write_input, client.DATATYPE.FLOAT32)
    client.write_registers(write_address, write_input_registers, slave=1)

    #ждем работы модели сервера
    time.sleep(20)

    #читаем регистры
    res = client.read_holding_registers(read_address, count=read_count, slave=1)
    assert not res.isError()
    result = [round(client.convert_from_registers(res.registers[i * 2:i * 2 + 2], client.DATATYPE.FLOAT32), 1) for i in
              range(read_count//2)]

    #выводим на экран результат
    # для информации выводим в виде таблицы текущее состояние и предложенное моделью действие в этом состоянии
    data = [[result[-1]] + result[:-1]]
    headers = ['Tвн', 'Tнар', 'Тнар_сл', 'W', 'Hd', 'Cl', 'Tпод']
    print(tabulate(data, headers=headers))

    #делаем оценочный расчет температуры, которая установится через 3 часа при условии подачи теплоносителя по
    #полученной от модели температуре
    t_next = round(next_temp(result[-1], result[-2])# + np.random.uniform(-0.8, 0.2, 1)[0], 1)


    #пишем полученную через 3 часа температуру воздуха внутри помещения в регистры
    write_input_registers = client.convert_to_registers(t_next, client.DATATYPE.FLOAT32)
    client.write_registers(write_address, write_input_registers, slave=1)
    print('Записали в регистр температуру через 3 часа: {}'.format(t_next))

    client.close()
    return t_next


if __name__ == "__main__":
    Tin = 20.6
    while True:
        try:
            Tin_next = run_client(host='127.0.0.1',
                              port=5020,
                              read_address=0,
                              read_count=14,
                              write_address=12,
                              write_input=Tin)
            Tin = Tin_next
            time.sleep(modeling_period * 60 - 20)
        except:
            print('Client stopped...')
            break
