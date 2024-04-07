import asyncio
from asyncio import CancelledError
import struct
import pandas as pd

from app import url_msk, modeling_period, server_time, batch_size
from app.main_jobs import job, renew_model_job

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

import logging

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(level=logging.INFO,
                    filename='server.log',
                    format=FORMAT,
                    filemode='a')
log = logging.getLogger()
log.setLevel(logging.INFO)


#конфигурируем сервер (используем holding-registers 16 bytes)
#нам необходимо передавать 7 переменных (температура теплоносителя и состояние: t внутри помещения, t наружная,
# t наружная через 3 часа, ветер, влажность, облачность)
# итого 14 регистров по два на каждую переменную типа float
def setup_server():
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0x00, [0] * 14),
        zero_mode=True
    )
    context = ModbusServerContext(slaves=store, single=True)
    return context


#запуск сервера в асинхронном режиме
async def start_server(context):
    await StartAsyncTcpServer(context, address=("localhost", 5020))


#функция чтения и обновления регистров сервера
async def read_and_write_registers(context):
    while True:
        #делаем небольшую задержку по времени, чтобы SCADA успела положить в ргистры сервера внутреннюю температуру
        await asyncio.sleep(20)

        #читаме регистры (температуру от SCADA) и передаем прочитанное в функцию job
        registers = context[1].getValues(fc_as_hex=3, address=12, count=2)
        byte_list = bytearray()
        for reg in registers[::-1]:
            byte_list.extend(int.to_bytes(reg, 2, "little"))
        Tin = round(struct.unpack("f", byte_list)[0], 1)
        state_current_and_action = job(url_msk, Tin)

        #обновляем модель, если опыта достаточно (больше размера батча, по дефолту 64 эпизодов опыта)
        experience_dataframe = pd.read_csv('./data/experience_RL.csv')
        if len(experience_dataframe[1:-1]) > batch_size:
            renew_model_job(experience_dataframe[1:-1])

        #пишем в регистры температуру теплоносителя, предложенную моделью
        start_address = 0
        for idx, val in enumerate(state_current_and_action):
            byte_list = struct.pack("f", val)
            regs = [int.from_bytes(byte_list[x: x + 2], "little") for x in range(0, len(byte_list), 2)]
            context[1].setValues(fc_as_hex=16, address=start_address + idx*2, values=regs[::-1])

        #ждем окончания цикла
        await asyncio.sleep(modeling_period * 60 - 20)


#основная функция запуска сервера в асинхронном режиме, модели и периодического чтения и обновления регистров
async def main():
    context = setup_server()
    task1 = asyncio.create_task(start_server(context))
    task2 = asyncio.create_task(read_and_write_registers(context))

    await asyncio.sleep(server_time*60)
    task1.cancel()
    task2.cancel()
    print('Server stopped...')
    print('Registers reading and updating process stopped...')

    try:
        await task1
        await task2
    except CancelledError:
        print('All tasks have been cancelled...')


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
