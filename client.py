import asyncio
import sys

async def tcp_netcat_client(message=''):
    
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 4008)

    
    while writer:
        data = await reader.read(256)
        # print(f'Received from server: {data.decode()!r}')
        print(data.decode())
        
        string = str(input())
        print(f'Send: {string!r}')
        writer.write(string.encode())
            
if __name__ == '__main__':
    ip = sys.argv[1]
    port = sys.argv[2]
    asyncio.run(tcp_netcat_client('start'))