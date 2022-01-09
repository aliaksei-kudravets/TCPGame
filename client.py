import asyncio
import sys



async def tcp_netcat_client(message=''):
    
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 4008)

    

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')
    
    print(f'Send: {message!r}')
    writer.write(message.encode())
    
    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

    
if __name__ == '__main__':
    ip = sys.argv[1]
    port = sys.argv[2]
    asyncio.run(tcp_netcat_client('start'))