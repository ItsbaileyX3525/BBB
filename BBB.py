from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.networking import *

app = Ursina(borderless=False)

#Stuff to do with the server, positions and hitpoints etc.

peer = RPCPeer()

class PlayerModel(Entity):
    def __init__(self):
        super().__init__()
        self.hp = 100
        self.model = 'cube'
        self.scale_y = 2
        self.color = color.blue
        self.face = Entity(parent=self, scale_y=.25, scale_x=.5, z=.05, y=.25, model='cube', color=color.green)

@rpc(peer)
def set_position(connection, time_received, player_id: str, username: str, position: Vec3, rotation: Vec3):
    if player_id not in players:
        players[player_id] = PlayerModel()
        usernames[player_id] = Text(parent=scene,text=username,billboard=True,scale=12)
    player = players[player_id]
    player.position = (position.x,position.y + 1,position.z)
    player.rotation = (rotation.x,rotation.y,rotation.z)

    username = usernames[player_id]
    username.x = position.x
    username.z = position.z
    username.y = position.y + 3


    # Forward the update to all other clients
    for other_connection in peer.get_connections():
        if other_connection != connection:
            peer.set_position(other_connection, player_id, position, rotation)

@rpc(peer)
def set_healthPoints(connection, time_received, player_id: str, health: int):
    print(health)
    if player_id in players:
        players[player_id].hp = health
        print(players[player_id].hp)
    # Forward the update to all other clients
    for other_connection in peer.get_connections():
        if other_connection != connection:
            peer.set_healthPoints(other_connection, player_id, health)

def update():
    global update_rate, update_timer
    peer.update(max_events=100)

    if not peer.is_running():
        status_text.text = start_text
        mainPlayer.x = 0.0
        mainPlayer.y = 0.0
        mainPlayer.z = -0.3
        for player in players.values():
            player.x = 0.0
            player.y = 0.0
            player.z = 0.3
        return

    if not peer.is_hosting():
        status_text.text = "Client"
        if mainPlayer.hp < 0:
            print("Dead lol")
            mouse.locked=True
            mainPlayer.rotation_y = 180
    elif peer.is_hosting():
        status_text.text = "Host"
    update_timer += time.dt
    if peer.is_running():
        for connection in peer.get_connections():
            player_id = str(id(connection))
            peer.set_position(connection, player_id, username_input_field.text, Vec3(mainPlayer.x, mainPlayer.y,mainPlayer.z), Vec3(mainPlayer.rotation_x, mainPlayer.rotation_y,mainPlayer.rotation_z))
    update_timer = 0.0

def input(key):
    global mainPlayer
    if key == 'e':
        for player in players.values():
            if player.hp <= 0:
                print("Player dead")
            elif player.hp >= 0:
                if peer.is_running():
                    mainPlayer.hp -= 10
                    for connection in peer.get_connections():
                        player_id = str(id(connection))
                        peer.set_healthPoints(connection, player_id, int(mainPlayer.hp))

ground = Entity(model='plane', scale_x=100, scale_z=100, texture='grass', collider='box')
mainPlayer = FirstPersonController(model='cube', color=color.red)
mouse.locked = False
mainPlayer.mouse_sensitivity = (0,0)
mainPlayer.speed = 0
mainPlayer.hp = 100
players = {}
usernames = {}
update_rate = 1.0 / 60.0
update_timer = 0.0

start_text = "Host or join a room."
status_text = Text(text=start_text, origin=(0, 0), z=1, y=0.1)
host_input_field = InputField(default_value="localhost", scale_x=0.6, scale_y=0.1)
host_button = Button(text="Host", scale_x=0.28, scale_y=0.1, x=-0.16, y=-0.11)
join_button = Button(text="Join", scale_x=0.28, scale_y=0.1, x=0.16, y=-0.11)

#Can only be set before you join for now I guess.
username_input_field = InputField(scale=0.6, scale_y=0.05, x=-0.48, y=-0.45, z=1)

#Maybe add this back later?
#chat_input_field = InputField(scale=0.6, scale_y=0.05, x=-0.48, y=-0.45, z=1)

def host():
    global mainPlayer
    h = host_input_field.text
    port = 8080
    
    mainPlayer.x = 0.0
    mainPlayer.y = 0.0
    mainPlayer.z = -0.3

    peer.start(h, port, is_host=True)
    mainPlayer.mouse_sensitivity = Vec2(40, 40)
    mainPlayer.speed = 5
    mouse.locked = True
    host_input_field.enabled = False
    host_button.enabled = False
    join_button.enabled = False

host_button.on_click = host

def join():
    global mainPlayer
    h = host_input_field.text
    port = 8080
    
    mainPlayer.x = 0.0
    mainPlayer.y = 0.0
    mainPlayer.z = 0.3


    peer.start(h, port, is_host=False)
    mainPlayer.color = color.blue
    mouse.locked = True
    mainPlayer.speed = 12
    mainPlayer.mouse_sensitivity = Vec2(40, 40)
    host_input_field.enabled = False
    host_button.disabled = True
    host_button.enabled = False
    join_button.disabled = True
    join_button.enabled = False

join_button.on_click = join

app.run()
