from ursina import *
from networking import *
from FPC import *

app=Ursina(borderless=False)
start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0), z=1)

ground = Entity(model='plane',scale_x=100,scale_z=100,texture='grass',collider='box')
mainPlayer = FirstPersonController(model='cube',color=color.red)
otherPlayer = Entity(model='cube',color=color.blue)
peer = RPCPeer()
update_rate = 1.0 / 20.0
update_timer = 0.0


@rpc(peer)
def set_position(connection, time_received, position: Vec3):
    otherPlayer.x = position.x
    otherPlayer.y = position.y
    otherPlayer.z = position.z 

@rpc(peer)
def set_rotation(connection, time_received, rotation: Vec3):
    otherPlayer.rotation_x = rotation.x
    otherPlayer.rotation_y = rotation.y
    otherPlayer.rotation_z = rotation.z
    
def update():
    global update_rate,update_timer
    peer.update(max_events=100)

    if not peer.is_running():
        status_text.text = start_text
        mainPlayer.x = 0.0
        mainPlayer.y = 0.0
        mainPlayer.z = -0.3
        otherPlayer.x = 0.0
        otherPlayer.y = 0.0
        otherPlayer = 0.3
        return

    if not peer.is_hosting():
        status_text.text = "Client"
    elif peer.is_hosting():
        status_text.text = "Host"

    update_timer += time.dt
    if peer.is_running() and peer.connection_count() > 0:
        peer.set_position(peer.get_connections()[0], Vec3(mainPlayer.x, mainPlayer.y,mainPlayer.z))
        peer.set_rotation(peer.get_connections()[0], Vec3(mainPlayer.rotation_x, mainPlayer.rotation_y,mainPlayer.rotation_z))
    update_timer = 0.0
def input(key):
    global mainPlayer,otherPlayer
    if key == "h":
        mainPlayer.x = -0.3
        
        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        otherPlayer.x = -0.1
        peer.start("localhost", 8080, is_host=False)
        mainPlayer.color=color.blue
        otherPlayer.color=color.red

app.run()