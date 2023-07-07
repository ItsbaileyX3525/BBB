from ursina import *
from networking import *
from collections import deque
import requests
import os
from profanity import profanity


class InputState:
    def __init__(self, input_state=None):
        if input_state is not None:
            self.up = input_state.up
            self.down = input_state.down
            self.left = input_state.left
            self.right = input_state.right
            self.sequence_number = input_state.sequence_number
            return

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.sequence_number = 0

    def copy(self):
        return InputState(self)


def serialize_input_state(writer, input_state):
    writer.write(input_state.up)
    writer.write(input_state.down)
    writer.write(input_state.left)
    writer.write(input_state.right)
    writer.write(input_state.sequence_number)

def deserialize_input_state(reader):
    input_state = InputState()
    input_state.up = reader.read(bool)
    input_state.down = reader.read(bool)
    input_state.left = reader.read(bool)
    input_state.right = reader.read(bool)
    input_state.sequence_number = reader.read(int)
    return input_state


class BearState:
    def __init__(self, bear_state=None):
        if bear_state is not None:
            self.uuid = bear_state.uuid
            self.x = bear_state.x
            self.y = bear_state.y
            self.input_state = bear_state.input_state.copy()
            return

        self.uuid = 0
        self.x = 0.0
        self.y = 0.0
        self.input_state = InputState()

    def copy(self):
        return BearState(self)


def serialize_bear_state(writer, bear_state):
    writer.write(bear_state.uuid)
    writer.write(bear_state.x)
    writer.write(bear_state.y)
    serialize_input_state(writer, bear_state.input_state)

def deserialize_bear_state(reader):
    bear_state = BearState()
    bear_state.uuid = reader.read(int)
    bear_state.x = reader.read(float)
    bear_state.y = reader.read(float)
    bear_state.input_state = deserialize_input_state(reader)
    return bear_state

class Welcome():
    def __init__(self):
        super().__init__()
        self.parent=camera.ui
        self.model='quad'
        self.color=color.white
        self.version = "1.2.0"
        self.versionGet = requests.get("https://raw.githubusercontent.com/ItsbaileyX3525/BBB/main/version.txt")
        if self.versionGet.status_code != 200:
            print("Failed to retrieve file. Status code:", self.versionGet.status_code)
            print_on_screen("Unable to retrieve version info, auto-exiting",duration=6)
            Sequence(Wait(6),Func(application.quit)).start()
        self.actualVersion = self.versionGet.text
        if self.actualVersion != self.version:
            print_on_screen("Club_bear is outdated, do you want to auto-update?",duration=99,position=(-.1,.1))
            self.NoDontUpdate = Button(scale=.1,text='No',z=-1).on_click=application.quit
            self.YesUpdate = Button(scale=.1,x=.11,text='Yes',z=-1).on_click=self.AutoUpdate
        else:
            status_text.visible=True
            host_input_field.visible=True
            host_button.visible=True
            join_button.visible=True
            chat_input_field.visible=True
            ShowServerList.visible=True
            title.visible=True
            
    def AutoUpdate(self):
        self.response = requests.get("https://raw.githubusercontent.com/ItsbaileyX3525/BBB/main/club_bear.py")
        self.new_code = self.response.text
        with open(sys.argv[0], "w") as script_file:
            script_file.write(self.new_code)
            print("Script updated successfully!")
            
            file_path = "version.txt"

            if os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write(self.versionGet.text)
            else:
                pass
            
            python = sys.executable
            os.execl(python, python, *sys.argv)
          
class ServerButton(Button):
    def __init__(self, ip="173.255.204.78", port=8080,Parent=None, **kwargs):
        super().__init__(Parent=Parent,ip=ip,port=port,**kwargs)
        self.z = -2
        self.model = 'quad'
        self.scale_y = .1
        self.scale_x = 1
        self.x = -.2
        self.on_click = self.Connect
        self.color = color.hex("#4f4c43")
        self.highlight_color = color.hex("#615e54")
        self.StatusCircle = Entity(parent=self, model='circle', z=-2.1, scale_y=.3, scale_x=.03, x=.45)
        self.serverText = Text(parent=self, z=-2.1, scale_x=.9, scale_y=9, text=f"{ip}:{port}", y=.1, x=-.45)
        if self.OnlineStatus(self.ip, self.port) == 'Online':
            self.StatusCircle.color=color.green
        elif self.OnlineStatus(self.ip, self.port) == 'Offline':
            self.StatusCircle.color=color.red
        else:
            self.StatusCircle.color=color.white

    def OnlineStatus(self, A, B):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(.2)
        self.A = A
        self.B = int(B)
        try:
            result = self.sock.connect_ex((self.A, self.B))
            if result == 0:
                return "Online"
            else:
                return "Offline"
        except socket.error:
            return "Unknown"
        finally:
            self.sock.close()
            
    def Connect(self):
        self.A = self.ip
        self.B = int(self.port)
        host_input_field.enabled = False
        host_button.disabled = True
        host_button.enabled = False
        join_button.disabled = True
        join_button.enabled = False
        status_text.visible=True
        chat_input_field.visible=True
        ShowServerList.visible=False
        title.visible=False
        for e in self.Parent.Entities:
            destroy(e)
        destroy(self)

        peer.start(host_name=self.A, port=self.B, is_host=False)

        
class ServerList(Entity):
    def __init__(self):
        super().__init__()
        status_text.visible=False
        host_input_field.visible=False
        host_button.visible=False
        join_button.visible=False
        chat_input_field.visible=False
        ShowServerList.visible=False
        title.visible=False
        self.parent=camera.ui
        self.model='quad'
        self.z=-1
        self.scale=2
        self.color=color.black
        self.ServerOneDisplay = ServerButton(y=.4,ip="173.255.204.78",port=8080,Parent=self)
        #self.ServerTwoDisplay = ServerButton(y=.25)
        
        self.Exit = Button(text="Exit",y=-.3,scale_x=.2,scale_y=.1,color=color.gray,z=-2.1,on_click=self.exit)
        
        self.Entities = [self,self.ServerOneDisplay,self.Exit]
        
    def exit(self):
        status_text.visible=True
        host_input_field.visible=True
        host_button.visible=True
        join_button.visible=True
        chat_input_field.visible=True
        ShowServerList.visible=True
        title.visible=True
        for e in self.Entities:
            destroy(e)
       
class Bear(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, model="quad", texture="unicode_bear", scale=0.1)

        self.state = BearState()
        self.state.y = 0.1

        self.new_state = BearState()
        self.prev_state = self.new_state.copy()

        self.speed = 0.4

        self.lerping = False
        self.lerp_time = 0.0
        self.lerp_timer = 0.0

        self.talking = True
        self.talk_time = 0.0
        self.talk_timer = 0.0
        self.speech_text = Text(visible=False, y=self.y+0.05, origin=(0, 0))
        self.speech_audio = Audio("sine", autoplay=False, loop=True, loops=20)

    def update(self):
        if self.lerping:
            self.lerp_timer += time.dt
            if self.lerp_timer >= self.lerp_time:
                self.state = self.new_state.copy()
                self.lerp_timer = self.lerp_time
                self.lerping = False
            self.state.x = lerp(self.prev_state.x, self.new_state.x, self.lerp_timer / self.lerp_time)
            self.state.y = lerp(self.prev_state.y, self.new_state.y, self.lerp_timer / self.lerp_time)

        if self.state.input_state.right:
            self.texture_scale = (1.0, 1.0)
        elif self.state.input_state.left:
            self.texture_scale = (-1.0, 1.0)

        self.x = self.state.x
        self.y = self.state.y

        self.speech_text.x = self.x
        self.speech_text.y = self.y + 0.05
        if self.talking:
            self.speech_text.visible = True
            self.talk_timer += time.dt
            if self.talk_timer >= self.talk_time:
                self.talk_timer = self.talk_time
                self.talking = False
        else:
            self.speech_text.visible = False

    def tick(self, dt):
        self.state.x += float(int(self.state.input_state.right) - int(self.state.input_state.left)) * self.speed * dt
        self.state.y += float(int(self.state.input_state.up) - int(self.state.input_state.down)) * self.speed * dt
        if self.state.x >= 0.45:
            self.state.x = 0.45
        elif self.state.x <= -0.45:
            self.state.x = -0.45
        if self.state.y >= 0.45:
            self.state.y = 0.45
        elif self.state.y <= -0.45:
            self.state.y = -0.45

    def interpolate(self, start_state, end_state, duration):
        if self.lerping:
            self.state = self.new_state.copy()
        self.lerping = True
        self.lerp_time = duration
        self.lerp_timer = 0.0
        self.prev_state = start_state.copy()
        self.new_state = end_state.copy()

    def set_speech(self, msg, duration):
        self.talking = True
        self.talk_time = duration
        self.talk_timer = 0.0
        self.speech_text.text = msg
        self.speech_audio.play()


app = Ursina(borderless=False)

uuid_counter = 0

start_text = "Host or join a room."
status_text = Text(text=start_text, origin=(0, 0), z=1, y=0.1,visible=False)
host_input_field = InputField(default_value="localhost", scale_x=0.6, scale_y=0.1,visible=False)
host_button = Button(text="Host", scale_x=0.28, scale_y=0.1, x=-0.16, y=-0.11,visible=False)
join_button = Button(text="Join", scale_x=0.28, scale_y=0.1, x=0.16, y=-0.11,visible=False)

chat_input_field = InputField(scale=0.6, scale_y=0.05, x=-0.48, y=-0.45, z=1,visible=False,character_limit=30)

ShowServerList = Button(text='Server List',y=-.3,on_click=ServerList,visible=False,scale_x=.2,scale_y=.1)

bears = []

title=Animation('BBB_client.gif',y=2)

my_bear_uuid = None
uuid_to_bear = dict()

connection_to_bear = dict()

input_state = InputState()

inputs_received = dict()
input_buffer = []
send_input_buffer = []

tick_rate = 1.0 / 60.0
tick_timer = 0.0
time_factor = 1.0

update_rate = 1.0 / 20.0
update_timer = 0.0

speech_duration = 3.0

peer = RPCPeer()

peer.register_type(InputState, serialize_input_state, deserialize_input_state)
peer.register_type(BearState, serialize_bear_state, deserialize_bear_state)

welcomeMenu=Welcome()


@rpc(peer)
def on_connect(connection, time_connected):
    global uuid_counter

    if peer.is_hosting():
        b = Bear()
        b.state.uuid = uuid_counter
        uuid_counter += 1
        bears.append(b)
        uuid_to_bear[b.state.uuid] = b
        connection_to_bear[connection] = b
        inputs_received[b.state.uuid] = deque()
        connection.rpc_peer.set_bear_uuid(connection, b.state.uuid)
        s = [b.state for b in bears]
        for conn in connection.peer.get_connections():
            connection.rpc_peer.spawn_bears(conn, s)
        print("Bear count:", len(bears))

@rpc(peer)
def on_disconnect(connection, time_disconnected):
    if peer.is_hosting():
        b = connection_to_bear.get(connection)
        if b is not None:
            destroy(b)
            bears.remove(b)
            del uuid_to_bear[b.state.uuid]
            del connection_to_bear[connection]
            del inputs_received[b.state.uuid]
            for conn in connection.rpc_peer.get_connections():
                connection.rpc_peer.remove_bears(conn, [b.state.uuid])
        print("Bear count:", len(bears))
    else:
        for bear in bears:
            destroy(bear)
            del uuid_to_bear[bear.state.uuid]
        bears.clear()
        my_bear_uuid = None


@rpc(peer)
def set_bear_uuid(connection, time_received, uuid: int):
    global my_bear_uuid

    if connection.peer.is_hosting():
        return

    my_bear_uuid = uuid

@rpc(peer)
def spawn_bears(connection, time_received, new_bears: list[BearState]):
    if connection.peer.is_hosting():
        return

    for state in new_bears:
        if state.uuid not in uuid_to_bear:
            b = Bear()
            b.state = state.copy()
            bears.append(b)
            uuid_to_bear[state.uuid] = b

@rpc(peer)
def remove_bears(connection, time_received, to_be_removed: list[int]):
    global my_bear_uuid

    if connection.peer.is_hosting():
        return

    for uuid in to_be_removed:
        bear = uuid_to_bear.get(uuid)
        if bear is not None:
            destroy(bear)
            bears.remove(bear)
            del uuid_to_bear[uuid]
            if uuid == my_bear_uuid:
                my_bear_uuid = None

@rpc(peer)
def set_states(connection, time_received, bear_states: list[BearState]):
    global time_factor

    if connection.peer.is_hosting():
        return

    for new_bear_state in bear_states:
        bear = uuid_to_bear.get(new_bear_state.uuid)
        if bear is None:
            continue

        if my_bear_uuid is None or my_bear_uuid != new_bear_state.uuid:
            bear.interpolate(bear.state, new_bear_state, update_rate * 2.0)
        else:
            # Compute processed input difference between client and host.
            sequence_delta = input_state.sequence_number - new_bear_state.input_state.sequence_number
            # Maybe slow down if ahead of host.
            max_delta = ((update_rate / tick_rate) + 1) * 2.5
            if sequence_delta > max_delta:
                time_factor = 0.95
            elif sequence_delta < max_delta * 0.75:
                time_factor = 1.0
            my_bear = uuid_to_bear.get(my_bear_uuid)
            if my_bear is None:
                continue
            # Reconcile with host.
            my_bear.state = new_bear_state.copy()
            if sequence_delta > 0 and sequence_delta < len(input_buffer):
                # Re-apply all inputs after the last processed input.
                for state in input_buffer[len(input_buffer) - sequence_delta:]:
                    bear.state.input_state = state.copy()
                    bear.tick(tick_rate)

@rpc(peer)
def set_inputs(connection, time_received, input_states: list[InputState]):
    if not connection.peer.is_hosting():
        return

    for state in input_states:
        b = connection_to_bear.get(connection)
        if b is None:
            return
        input_queue = inputs_received.get(b.state.uuid)
        if input_queue is None:
            return
        if len(input_queue) > 100:
            # Host is being spammed, disconnect.
            print("Peer is spamming inputs, disconnecting...")
            connection.disconnect()
            return
        input_queue.append(state)

@rpc(peer)
def chat(connection, time_received, uuid: int, msg: str):
    if connection.rpc_peer.is_hosting():
        bear = connection_to_bear.get(connection)
        if bear is None:
            return
        if bear.state.uuid == uuid:
            for conn in connection.rpc_peer.get_connections():
                connection.rpc_peer.chat(conn, uuid, msg)
            bear.set_speech(msg, speech_duration)
    else:
        bear = uuid_to_bear.get(uuid)
        if bear is None:
            return
        bear.set_speech(msg, speech_duration)

def host():
    global uuid_counter, my_bear_uuid

    b = Bear()
    b.state.uuid = uuid_counter
    uuid_counter += 1
    bears.append(b)
    uuid_to_bear[b.state.uuid] = b
    my_bear_uuid = b.state.uuid

    h = host_input_field.text
    try:
        h = h.split(":")
        port = int(h[1])
    except IndexError:
        port = 8080
    h = h[0]
    
    if h == "":
        h = "localhost"

    peer.start(h, port, is_host=True)
    host_input_field.enabled = False
    host_button.enabled = False
    join_button.enabled = False
    ShowServerList.enabled = False
    title.enabled=True

host_button.on_click = host

def join():
    h = host_input_field.text
    try:
        h = h.split(":")
        port = int(h[1])
    except IndexError:
        port = 8080
    h = h[0]
    
    if h == "":
        h = "localhost"

    peer.start(h, port, is_host=False)
    host_input_field.enabled = False
    host_button.disabled = True
    host_button.enabled = False
    join_button.disabled = True
    join_button.enabled = False
    ShowServerList.enabled = False
    title.enabled=False

join_button.on_click = join

def on_chat_submit():
    if len(chat_input_field.text) == 0:
        return

    if profanity.contains_profanity(chat_input_field.text):
        chat_input_field.text = random.choice(['I swore', 'Look ma, I swore', 'I feel like a big boy', 'sus amogus', 'I am a big boy now!'])

    if not peer.is_running():
        return

    if my_bear_uuid is not None:
        for conn in peer.get_connections():
            peer.chat(conn, my_bear_uuid, chat_input_field.text)

    if peer.is_hosting():
        if my_bear_uuid is not None:
            bear = uuid_to_bear.get(my_bear_uuid)
            if bear is not None:
                bear.set_speech(chat_input_field.text, speech_duration)

    chat_input_field.text = ""
    chat_input_field.active = False

def tick(dt):
    global last_input_sequence_number_processed

    if time_factor < 1.0:
        pass

    if not chat_input_field.active:
        input_state.up = bool(held_keys["w"])
        input_state.down = bool(held_keys["s"])
        input_state.right = bool(held_keys["d"])
        input_state.left = bool(held_keys["a"])
    if my_bear_uuid is not None:
        my_bear = uuid_to_bear.get(my_bear_uuid)
        if my_bear is not None:
            my_bear.state.input_state = input_state
            my_bear.tick(dt)

    if not peer.is_hosting():
        if my_bear_uuid is not None:
            input_state.sequence_number += 1
            input_buffer.append(input_state.copy())
            if len(input_buffer) >= 100:
                input_buffer.pop(0)
            send_input_buffer.append(input_buffer[-1])
            if len(send_input_buffer) > 10:
                send_input_buffer.pop(0)
    else:
        for bear in bears:
            if my_bear_uuid is None or my_bear_uuid != bear.state.uuid:
                input_queue = inputs_received.get(bear.state.uuid)
                if input_queue is None:
                    continue
                if len(input_queue) > 0:
                    bear.state.input_state = input_queue.popleft()
                else:
                    bear.state.input_state.up = False
                    bear.state.input_state.down = False
                    bear.state.input_state.left = False
                    bear.state.input_state.right = False
                bear.tick(dt)

def update():
    global update_timer, tick_timer

    peer.update()
    if not peer.is_running():
        status_text.text = start_text
        status_text.y = 0.1
        host_input_field.enabled = True
        host_button.disabled = False
        host_button.enabled = True
        join_button.disabled = False
        join_button.enabled = True
        chat_input_field.enabled = False
        return

    host_input_field.enabled = False
    host_button.disabled = True
    host_button.enabled = False
    join_button.disabled = True
    join_button.enabled = False
    chat_input_field.enabled = True
    if peer.is_hosting():
        status_text.text = "Hosting.\nWASD to move."
        status_text.y = -0.45
    else:
        status_text.text = "Connected to host.\nWASD to move."
        status_text.y = -0.45

    tick_timer += time.dt * time_factor
    while tick_timer >= tick_rate:
        tick(tick_rate)
        tick_timer -= tick_rate

    update_timer += time.dt
    if update_timer >= update_rate:
        if peer.is_running() and peer.connection_count() > 0:
            if peer.is_hosting():
                s = [b.state for b in bears]
                for connection in peer.get_connections():
                    peer.set_states(connection, s)
            else:
                peer.set_inputs(peer.get_connections()[0], send_input_buffer)
                send_input_buffer.clear()
        update_timer = 0.0

def input(key):
    if not peer.is_running():
        return
    if key == "enter up":
        if not chat_input_field.active:
            chat_input_field.active = True
        else:
            on_chat_submit()
    elif key == "escape up" and chat_input_field.active:
        chat_input_field.text = ""
        chat_input_field.active = False

app.run()