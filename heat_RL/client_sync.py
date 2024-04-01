from app import forecast_hours, modeling_period, url_msk
from app.parsing import get_temperatures_forecast

import time
import numpy as np
from pymodbus.client import ModbusTcpClient as ModbusClient


def next_temp(tin, theat):
    temperature_current, temperature_next, wind, humidity, cloudiness = get_temperatures_forecast(url_msk)
    state = [tin, temperature_current, temperature_next, wind, humidity, cloudiness]
    betta = 1 + (state[4] + state[5] + state[3] / 5) / 3
    tout = (state[1] + state[2]) / 2
    tin = state[0]
    Q = (theat - 33) / 120
    tin_next = tout + Q / 0.007 + (tin - tout - Q / 0.007) / (np.exp(forecast_hours * betta / 70))
    return tin_next


def run_client(host: str,
               port: int,
               read_address: int,
               read_count: int,
               write_address: int,
               write_input: str) -> list:
    client = ModbusClient(host=host, port=port, timeout=30)
    assert client.connect()

    write_input_registers = client.convert_to_registers(write_input, client.DATATYPE.FLOAT32)
    client.write_registers(write_address, write_input_registers, slave=1)

    time.sleep(20)
    res = client.read_holding_registers(read_address, count=read_count, slave=1)
    assert not res.isError()
    result = [round(client.convert_from_registers(res.registers[i * 2:i * 2 + 2], client.DATATYPE.FLOAT32), 1) for i in
              range(2)]
    print(result)

    t_next = round(next_temp(result[1], result[0]) + np.random.uniform(-3, 0.5, 1)[0], 1)
    write_input_registers = client.convert_to_registers(t_next, client.DATATYPE.FLOAT32)
    client.write_registers(write_address, write_input_registers, slave=1)
    print('Записали в регистр температуру через 3 часа: {}'.format(t_next))

    client.close()
    return t_next


if __name__ == "__main__":
    Tin = 18.7
    while True:
        try:
            Tin_next = run_client(host='127.0.0.1',
                              port=5020,
                              read_address=0,
                              read_count=4,
                              write_address=2,
                              write_input=Tin)
            Tin = Tin_next
            time.sleep(modeling_period * 60 - 20)
        except:
            print('Client stopped...')
            break
