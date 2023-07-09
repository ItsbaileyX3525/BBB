class ServerButton(Button):
    def __init__(self, ip="173.255.204.78", port=8080,Parent=None,ID=1,Slot=1, **kwargs):
        super().__init__(Parent=Parent,ip=ip,port=port,ID=ID,Slot=Slot,**kwargs)
        self.z = -2.05
        self.model = 'quad'
        self.scale_y = .1
        self.scale_x = 1
        self.x = -.2
        self.status = "unknown"
        self.running = threading.Event()
        
                
    def removeButton(self):
        global Slot1,Slot2,Slot3,Slot4,Slot5,Slot6,ServersInJson
        if self.Slot == 1:
            Slot1 = None
        elif self.Slot == 2:
            Slot2 = None
        elif self.Slot == 3:
            Slot3 = None
        elif self.Slot == 4:
            Slot4 = None
        elif self.Slot == 5:
            Slot5 = None
        elif self.Slot == 6:
            Slot6 = None
        with open("Settings.json", "r") as file:
            self.data = json.load(file)
        key_to_remove = f'Server{self.ID}IP'
        if key_to_remove in self.data:
            del self.data[key_to_remove]
        key_to_remove = f'Server{self.ID}Port'
        if key_to_remove in self.data:
            del self.data[key_to_remove]
        max_servers = 6
        num_servers = len(self.data) // 2
        for i in range(2, max_servers + 1):
            old_ip_key = f"Server{i}IP"
            new_ip_key = f"Server{i-1}IP"
            old_port_key = f"Server{i}Port"
            new_port_key = f"Server{i-1}Port"

            if old_ip_key in self.data:
                self.data[new_ip_key] = self.data[old_ip_key]
                del self.data[old_ip_key]

            if old_port_key in self.data:
                self.data[new_port_key] = self.data[old_port_key]
                del self.data[old_port_key]

        with open("Settings.json", 'w') as file:
            json.dump(self.data, file, indent=4)
        ServersInJson-=1
        destroy(self)


Slot1 = None
Slot2 = None
Slot3 = None
Slot4 = None
Slot5 = None
Slot6 = None
class ServerList(Entity):
    def __init__(self):
        super().__init__()
        global Slot1,Slot2,Slot3,Slot4,Slot5,Slot6
        
        self.Entities = [self,self.Exit,self.AddSever,self.ServerInput,self.confirmCustomServer]
        with open("Settings.json") as file:
            self.data = json.load(file)
        for i in range(ServersInJson+1):
            try:
                if not Slot1 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=.45,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=1)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot1 = "Occupied"
                elif not Slot2 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=.35,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=2)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot2 = "Occupied"
                elif not Slot3 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=.25,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=3)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot3 = "Occupied"
                elif not Slot4 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=.15,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=4)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot4 = "Occupied"
                elif not Slot5 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=.05,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=5)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot5 = "Occupied"
                elif not Slot6 == "Occupied":
                    exec(f"self.customButton{i} = ServerButton(y=-.05,ip=self.data[f'Server{i}IP'],port=self.data[f'Server{i}Port'],Parent=self, ID={i}, Slot=6)")
                    exec(f"self.Entities.append(self.customButton{i})")
                    Slot6 = "Occupied"
            except KeyError:
                pass
    
    def confirmSever(self,args):
        global ServersInJson,Slot1,Slot2,Slot3,Slot4,Slot5,Slot6
        if ServersInJson<6:
            try:
                args = args.split(":")
                port = args[1]
            except IndexError:
                port = 8080
            ip = args[0]
            if not str(ip).startswith(tuple(str(_) for _ in range(10))):
                print_on_screen("Domains not supported yet",position=(0,0,-2.4),duration=2)
                return
            else:
                pass
            with open("Settings.json") as file:
                data = json.load(file)
            ServersInJson += 1
            data[f"Server{ServersInJson}IP"] = ip
            data[f"Server{ServersInJson}Port"] = port
            with open("Settings.json", 'w') as file:
                json.dump(data, file, indent=4)
            if not Slot1 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=.45,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=1)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot1 = "Occupied"
            elif not Slot2 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=.35,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=2)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot2 = "Occupied"
            elif not Slot3 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=.25,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=3)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot3 = "Occupied"
            elif not Slot4 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=.15,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=4)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot4 = "Occupied"
            elif not Slot5 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=.05,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=5)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot5 = "Occupied"
            elif not Slot6 == "Occupied":
                exec(f"self.customButton{ServersInJson} = ServerButton(y=-.05,ip=ip,port=port,Parent=self, ID={ServersInJson}, Slot=6)")
                exec(f"self.Entities.append(self.customButton{ServersInJson})")
                Slot6 = "Occupied" 
        else:
            print_on_screen("Too many servers, remove one",position=(-.19,-0.2,-2.3),duration=2.4)