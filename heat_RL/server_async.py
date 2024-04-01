import asyncio
from asyncio import CancelledError
import struct

from app import url_msk, modeling_period, server_time
from app.main import job

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


def setup_server():
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0x00, [0] * 10),
        zero_mode=True
    )
    context = ModbusServerContext(slaves=store, single=True)
    return context


async def start_server(context):
    await StartAsyncTcpServer(context, address=("localhost", 5020))


async def read_and_write_registers(context):
    while True:
        #читаем регистры с внутренней температурой
        await asyncio.sleep(20)
        registers = context[1].getValues(fc_as_hex=3, address=0x02, count=2)
        byte_list = bytearray()
        for reg in registers[::-1]:
            byte_list.extend(int.to_bytes(reg, 2, "little"))
        Tin = round(struct.unpack("f", byte_list)[0], 1)
        action = job(url_msk, Tin)

        #пишем в регистры температуру теплоносителя
        byte_list = struct.pack("f", action)
        regs = [int.from_bytes(byte_list[x: x + 2], "little") for x in range(0, len(byte_list), 2)]
        context[1].setValues(fc_as_hex=16, address=0x00, values=regs[::-1])
        await asyncio.sleep(modeling_period * 60 - 20)


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
    asyncio.run(main())
