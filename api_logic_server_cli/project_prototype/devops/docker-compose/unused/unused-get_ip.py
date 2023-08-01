import socket, os

def get_internal_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def get_external_ip():
    return socket.gethostbyname(socket.gethostname())

hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)   
print("Your Computer Name is:"+hostname)   
print("Your Computer IP Address is:"+IPAddr)
print("")

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
 
print("\nYour Computer Name is:" + hostname)
print("Your Computer IP Address is:" + IPAddr + ",  ha! mine is 10.0.0.77\n")

print('\nInternal (this is the one to use):', get_internal_ip())
print('External:', get_external_ip())


