import yaml
import sys
import argparse
import os
import validators
import docker

class System():
    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

class External_Service():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self._port = None
        self._hostname = None
        self._container = None

    def set_port(self, port):
        self._port = port
    
    def get_port(self):
        return self._port

    def del_port(self):
        self._port = None

    port = property(get_port, set_port, del_port)

    def set_hostname(self, hostname):
        self._hostname = hostname

    def get_hostname(self):
        return self._hostname
    
    def del_hostname(self, hostname):
        self._hostname = None

    hostname = property(get_hostname, set_hostname, del_hostname)

    def set_container(self, container):
        self._container = container
    
    def get_container(self):
        return self._container

    def del_container(self):
        self._container = None

    container = property(get_container, set_container, del_container)

class Output():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self._stimulus = []
        self._recipient = []

    def add_stimulus(self, Stimulus):
        self._stimulus.append(Stimulus)

    def rm_stimulus(self, Stimulus):
        self._stimulus.pop(Stimulus)

    def add_recipient(self, Recipient):
        self._recipient.append(Recipient)

    def rm_stimulus(self, Recipient):
        self._recipient.pop(Recipient)

class Stimulus():
    def __init__(self, external_service, type):
        self.service = external_service
        self.type = type
        self._file = None

    def set_file(self, file):
        self._file = file
    
    def get_file(self):
        return self._file

    def del_file(self):
        self._file = None

    file = property(get_file, set_file, del_file)

class Recipient():
    def __init__(self, external_service, type):
        self.service = external_service
        self.type = type
        self._file = None

    def set_file(self, file):
        self._file = file
    
    def get_file(self):
        return self._file

    def del_file(self):
        self._file = None

    file = property(get_file, set_file, del_file)
    

def parse_config(config_dict):
    #Build system class
    system = System(
        name = config_dict['system']['name'], 
        repo = config_dict['system']['repo']
        )


    #Build external-services class(es)
    ext_serv_list = []
    for k, v in config_dict['external-services'].items():
        assert (not ext_serv.name == k for ext_serv in ext_serv_list); "Multiple external services with the same name!"
        ext_serv = External_Service(
            name = k,
            type = v['type']
        )
        if not v['port'] == None:
            ext_serv.port = v['port']
        ext_serv_list.append(ext_serv)
    
    #Build output(s)
    outputs_list = []
    for k,v in config_dict['outputs'].items():
        output = Output(
            name = k,
            type = v['type']
        )
        for k_s, v_s in v['stimuli'].items():
            ext_srv_obj = None
            #Find ext_serv object for this stimulus
            for obj in ext_serv_list:
                if obj.name == k_s:
                    ext_srv_obj = obj
            assert ext_srv_obj != None; "Config contains undefined stimulus service."
            stimulus = Stimulus(
                external_service = ext_srv_obj,
                type = v_s['type']
            )
            if v_s['file'] != None:
                stimulus.file = v_s['file']
            output.add_stimulus(stimulus)
        
        for k_r, v_r in v['recipients'].items():
            ext_srv_obj = None
            #Find ext_serv object for this stimulus
            for obj in ext_serv_list:
                if obj.name == k_r:
                    ext_srv_obj = obj
            assert ext_srv_obj != None; "Config contains undefined recipient service."
            recipient = Recipient(
                external_service = ext_srv_obj,
                type = v_r['type']
            )
            if v_r['file'] != None:
                recipient.file = v_r['file']
            output.add_recipient(recipient)
        outputs_list.append(output)
    
    return system, ext_serv_list, outputs_list

def start_service(service, client, docker_network_name):
    script_dict = {'tcp':'tcp_listener'}
    #serv_command = 'python -u /vipr/scripts/' + script_dict[service.type] + '.py --port ' + str(service.port)
    serv_command = 'ls /vipr'
    serv_name = 'vipr-' + service.name
    print(os.getcwd())
    print(serv_name)
    container = client.containers.run(image = 'python:3.6-slim-buster',
                volumes = {'/vipr': {'bind': '/vipr', 'mode': 'ro'}},
                name = serv_name,
                command = serv_command,
                #detach = True,
                network = docker_network_name,
                #auto_remove = True
    )
    service.container = container


def main(args):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    project_name = args.repo.split('/')[-1]

    os.chdir("/")
    #This is going to eventually give me fits because of authentication
    os.system('git clone ' + args.repo)

    config_paths = [os.path.join('/', project_name,  'vipr/config.yaml'),
                    os.path.join('/',  project_name,  'vipr/config.yml')]
    if not os.path.exists(config_paths[0]):
        config_path = config_paths[1]
        if not os.path.exists(config_path):
            print('Configuration file not present in vipr/ folder in repository.')
            sys.exit()
    else:
        config_path = config_paths[0]


    with open(config_path) as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    
    system, services, outputs = parse_config(config_dict)

    docker_network_name = system.name + '-net'
    try:
        client.networks.create(docker_network_name, check_duplicate=True)
    except:
        pass

    for service in services:
        start_service(service, client, docker_network_name)

    #while True:
    #    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo", help="URL of repository of system under validation", required=True)
    args = parser.parse_args()

    assert validators.url(args.repo); "Malformed repo URL"

    main(args)