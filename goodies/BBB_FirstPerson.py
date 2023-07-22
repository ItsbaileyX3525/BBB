from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from networking import *

app=Ursina(borderless=False)
start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0), z=1)

class otherPlayerModel(Entity):
    def __init__(self):
        super().__init__(self)
        self.hp=100
        self.model='cube'
        self.scale_y=2
        self.color=color.blue
        self.face=Entity(parent=self,scale_y=.25,scale_x=.5,z=.05,y=.25,model='cube',color=color.green)
        

ground = Entity(model='plane',scale_x=100,scale_z=100,texture='grass',collider='box')
mainPlayer = FirstPersonController(model='cube',color=color.red)
mainPlayer.hp=100
otherPlayer = otherPlayerModel()
peer = RPCPeer()
update_rate = 1.0 / 20.0
update_timer = 0.0

@rpc(peer)
def set_position(connection, time_received, position: Vec3, rotation: Vec3):
    otherPlayer.x = position.x
    otherPlayer.y = position.y
    otherPlayer.z = position.z 
    otherPlayer.rotation_x = rotation.x
    otherPlayer.rotation_y = rotation.y
    otherPlayer.rotation_z = rotation.z
    
@rpc(peer)
def set_healthPoints(connection, time_received, health: int):
    print(health)
    otherPlayer.hp = health
    print(otherPlayer.hp)
    
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
        otherPlayer.z = 0.3
        return

    if not peer.is_hosting():
        status_text.text = "Client"
    elif peer.is_hosting():
        status_text.text = "Host"
    update_timer += time.dt
    if peer.is_running() and peer.connection_count() > 0:
        peer.set_position(peer.get_connections()[0], Vec3(mainPlayer.x, mainPlayer.y,mainPlayer.z), Vec3(mainPlayer.rotation_x, mainPlayer.rotation_y,mainPlayer.rotation_z))
    update_timer = 0.0
def input(key):
    global mainPlayer,otherPlayer
    if key == "h":
        mainPlayer.x = 0.0
        mainPlayer.y = 0.0
        mainPlayer.z = -0.3
        
        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        otherPlayer.x = 0.0
        otherPlayer.y = 0.0
        otherPlayer.z = 0.3
        peer.start("localhost", 8080, is_host=False)
        mainPlayer.color=color.blue
        otherPlayer.color=color.red
        
    if key=='e' and otherPlayer.hp <=0:
        print("Other player dead")
    elif key=='e' and otherPlayer.hp >= 0:
        if peer.is_running() and peer.connection_count() > 0:
            #print(mainPlayer.hp - 10)
            mainPlayer.hp -= 10
            peer.set_healthPoints(peer.get_connections()[0], int(mainPlayer.hp))
            #print(otherPlayer.hp)

app.run()