import asyncio
import sys

async def tcp_netcat_client(ip, port):
    
    reader, writer = await asyncio.open_connection(
        ip, int(port))

    
    while True:
        data = await reader.read(256)
        # print(f'Received from server: {data.decode()!r}')
        print(data.decode())
        
        string = str(input())
        print(f'Send: {string!r}')
        writer.write(string.encode())
            
if __name__ == '__main__':
    ip = sys.argv[1]
    port = sys.argv[2]
    asyncio.run(tcp_netcat_client(ip, port))