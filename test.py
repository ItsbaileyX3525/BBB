

var = "192.168.2.151:25565"

try:
    var = var.split(":")
    port = var[1]
except IndexError:
    port = 8080
ip = var[0]
print(f'Ip: {ip} \nPort: {port}')