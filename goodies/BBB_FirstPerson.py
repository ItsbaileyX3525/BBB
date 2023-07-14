from ursina import *
from networking import *
from FPC import *

app=Ursina(borderless=False)
start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0), z=1)


ground = Entity(model='plane',scale_x=100,scale_z=100,texture='grass',collider='box')
hostPlayer = FirstPersonController(model='cube')
clientPlayer = FirstPersonController(model='cube')
hostPlayer.new_x = hostPlayer.x
hostPlayer.new_y = hostPlayer.y
hostPlayer.new_z = hostPlayer.z
hostPlayer.new_rx = hostPlayer.rotation_x
hostPlayer.new_ry = hostPlayer.rotation_y
hostPlayer.new_rz = hostPlayer.rotation_z
hostPlayer.prev_x = hostPlayer.x
hostPlayer.prev_y = hostPlayer.y
hostPlayer.prev_z = hostPlayer.z
hostPlayer.prev_rx = hostPlayer.x
hostPlayer.prev_ry = hostPlayer.y
hostPlayer.prev_rz = hostPlayer.z
update_rate = 1.0 / 20.0
update_timer = 0.0

lerp_time = update_rate * 1.25
lerp_timer = 0.0
peer = RPCPeer()
@rpc(peer)
def set_position(connection, time_received, position: Vec3):
    global lerp_timer

    hostPlayer.x = hostPlayer.new_x
    hostPlayer.y = hostPlayer.new_y
    hostPlayer.z = hostPlayer.new_z
    hostPlayer.prev_x = hostPlayer.x
    hostPlayer.prev_y = hostPlayer.y
    hostPlayer.prev_z = hostPlayer.z
    hostPlayer.new_x = position.x
    hostPlayer.new_y = position.y
    hostPlayer.new_z = position.z 

    lerp_timer = 0.0

@rpc(peer)
def set_rotation(connection, time_received, rotation: Vec3):
    global lerp_timer
    hostPlayer.rotation_x = hostPlayer.new_rx
    hostPlayer.rotation_y = hostPlayer.new_ry
    hostPlayer.rotation_z = hostPlayer.new_rz
    hostPlayer.prev_rx = hostPlayer.rotation_x
    hostPlayer.prev_ry = hostPlayer.rotation_y
    hostPlayer.prev_rz = hostPlayer.rotation_z
    hostPlayer.new_rx = rotation.x
    hostPlayer.new_ry = rotation.y
    hostPlayer.new_rz = rotation.z
    
    lerp_timer = 0.0
def update():
    global update_timer, lerp_timer 

    peer.update()
    if not peer.is_running():
        status_text.text = start_text
        clientPlayer.x = 0.3
        clientPlayer.y = 0.0
        clientPlayer.z = 0.0
        hostPlayer.x = -0.3
        hostPlayer.y = 0.0
        hostPlayer.z = 0.0
        return

    if peer.is_hosting():
        status_text.text = "Hosting on localhost, port 8080.\nWASD to move."
    else:
        status_text.text = "Connected to host with address localhost, port 8080.\nWASD to move."

    lerp_timer += time.dt
    hostPlayer.x = lerp(hostPlayer.prev_x, hostPlayer.new_x, lerp_timer / lerp_time)
    hostPlayer.y = lerp(hostPlayer.prev_y, hostPlayer.new_y, lerp_timer / lerp_time)
    hostPlayer.z = lerp(hostPlayer.prev_z, hostPlayer.new_z, lerp_timer / lerp_time)
    hostPlayer.rotation_x = lerp(hostPlayer.prev_rx, hostPlayer.new_rx, lerp_timer / lerp_time)
    hostPlayer.rotation_y = lerp(hostPlayer.prev_ry, hostPlayer.new_ry, lerp_timer / lerp_time)
    hostPlayer.rotation_z = lerp(hostPlayer.prev_rz, hostPlayer.new_rz, lerp_timer / lerp_time)
    if lerp_timer >= lerp_time:
        hostPlayer.x = hostPlayer.new_x
        hostPlayer.y = hostPlayer.new_y
        hostPlayer.z = hostPlayer.new_z
        hostPlayer.rotation_x = hostPlayer.new_rx
        hostPlayer.rotation_y = hostPlayer.new_ry
        hostPlayer.rotation_z = hostPlayer.new_rz
        hostPlayer.prev_x = hostPlayer.x
        hostPlayer.prev_y = hostPlayer.y
        hostPlayer.prev_z = hostPlayer.z
        hostPlayer.prev_rx = hostPlayer.rotation_x
        hostPlayer.prev_ry = hostPlayer.rotation_y
        hostPlayer.prev_rz = hostPlayer.rotation_z
        hostPlayer.new_x = hostPlayer.x
        hostPlayer.new_y = hostPlayer.y
        hostPlayer.new_z = hostPlayer.z
        hostPlayer.new_rx = hostPlayer.rotation_x
        hostPlayer.new_ry = hostPlayer.rotation_y
        hostPlayer.new_rz = hostPlayer.rotation_z
        lerp_timer = 0.0

    update_timer += time.dt
    if update_timer >= update_rate:
        if peer.is_running() and peer.connection_count() > 0:
            peer.set_position(peer.get_connections()[0], Vec3(clientPlayer.x, clientPlayer.y,clientPlayer.z))
            peer.set_rotation(peer.get_connections()[0], Vec3(clientPlayer.rotation_x, clientPlayer.rotation_y,clientPlayer.rotation_z))
        update_timer = 0.0

def input(key):
    if key == "h":
        clientPlayer.x = 0.3
        hostPlayer.x = -0.3
        hostPlayer.new_x = hostPlayer.x
        hostPlayer.new_y = hostPlayer.y
        hostPlayer.new_z = hostPlayer.z
        hostPlayer.new_rx = hostPlayer.rotation_x
        hostPlayer.new_ry = hostPlayer.rotation_y
        hostPlayer.new_rz = hostPlayer.rotation_z
        hostPlayer.prev_x = hostPlayer.x
        hostPlayer.prev_y = hostPlayer.y
        hostPlayer.prev_z = hostPlayer.z
        hostPlayer.prev_rx = hostPlayer.rotation_x
        hostPlayer.prev_ry = hostPlayer.rotation_y
        hostPlayer.prev_rz = hostPlayer.rotation_z

        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        clientPlayer.x = -0.1
        hostPlayer.x = 0.1
        hostPlayer.new_x = hostPlayer.x
        hostPlayer.new_y = hostPlayer.y
        hostPlayer.new_z = hostPlayer.z
        hostPlayer.new_rx = hostPlayer.rotation_x
        hostPlayer.new_ry = hostPlayer.rotation_y
        hostPlayer.new_rz = hostPlayer.rotation_z
        hostPlayer.prev_x = hostPlayer.x
        hostPlayer.prev_y = hostPlayer.y
        hostPlayer.prev_z = hostPlayer.z
        hostPlayer.prev_rx = hostPlayer.rotation_x
        hostPlayer.prev_ry = hostPlayer.rotation_y
        hostPlayer.prev_rz = hostPlayer.rotation_z

        peer.start("localhost", 8080, is_host=False)

app.run()