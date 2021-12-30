import yaml
import sys
import argparse
import os
import validators
import docker
import time
import shutil

class System():
    def __init__(self, name, repo, image, waittime):
        self.name = name
        self.repo = repo
        self.image = image
        self.waittime = waittime
        self.container = None

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
        self.stimuli = []
        self.recipients = []

    def add_stimulus(self, Stimulus):
        self.stimuli.append(Stimulus)

    def rm_stimulus(self, Stimulus):
        self.stimuli.pop(Stimulus)

    def add_recipient(self, Recipient):
        self.recipients.append(Recipient)

    def rm_stimulus(self, Recipient):
        self.recipients.pop(Recipient)

class Stimulus():
    def __init__(self, external_service, type):
        self.service = external_service
        self.type = type
        self._file = None
        self._container = None

    def set_file(self, file):
        self._file = file
    
    def get_file(self):
        return self._file

    def del_file(self):
        self._file = None

    file = property(get_file, set_file, del_file)

    def set_container(self, container):
        self._container = container
    
    def get_container(self):
        return self._container

    def del_container(self):
        self._container = None

    container = property(get_container, set_container, del_container)

class Recipient():
    def __init__(self, external_service, type):
        self.service = external_service
        self.type = type
        self._file = None
        self._container = None

    def set_file(self, file):
        self._file = file
    
    def get_file(self):
        return self._file

    def del_file(self):
        self._file = None

    file = property(get_file, set_file, del_file)

    def set_container(self, container):
        self._container = container
    
    def get_container(self):
        return self._container

    def del_container(self):
        self._container = None

    container = property(get_container, set_container, del_container)
    

def parse_config(config_dict):
    #Build system class
    system = System(
        name = config_dict['system']['name'], 
        repo = config_dict['system']['repo'],
        image = config_dict['system']['image'],
        waittime = config_dict['system']['waittime']
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

def start_system(system, client, project_path, docker_network_name):
    ###CHANGE TO PROJECT_PATH'S startup.sh###
    sys_command = '/vipr/test/startup.sh'
    container = client.containers.run(image = system.image,
                name = system.name,
                detach = True,
                #auto_remove = True,
                #network = docker_network_name,
                network = 'container:tshark',
                volumes = {project_path: {'bind': '/system', 'mode': 'rw'},
                           '/vipr': {'bind': '/vipr', 'mode': 'ro'}},###REMOVE THIS###
                command = sys_command
                )
    i=0
    while container.status != 'running':
        container.reload()
        time.sleep(1)
        i+=1
        if i >= 30:
            print('Error starting system service.')
            exit()
    print('Started system: ', system.name)
    system.container = container

def start_tcp_server(stimulus, client, project_path, docker_network_name):
    #Load all stimulus files into single file
    payload_list = []
    for file in stimulus.file:
        file_path = os.path.join(project_path, 'vipr/', file)
        with open(file_path, 'rb') as f:
            for line in f.readlines():
                payload_list.append(line)

    new_file_path = os.path.join(project_path, 'vipr/', 'inputs/payloads.txt')
    with open(new_file_path, 'wb') as f:
        for payload in payload_list:
            f.write(payload)

    serv_command = 'python -u /vipr/scripts/tcp_server.py -p ' + str(stimulus.service.port) + ' -f ' + new_file_path
    port_map_dict = {stimulus.service.port: stimulus.service.port}
    container = client.containers.run(image = 'python:3.6-slim-buster',
                volumes = {'/vipr': {'bind': '/vipr', 'mode': 'ro'},
                            project_path: {'bind': project_path, 'mode': 'rw'}},
                name = stimulus.service.name,
                command = serv_command,
                ports = port_map_dict,
                detach = True,
                network = docker_network_name,
                #auto_remove = True
    )
    i=0
    while container.status != 'running':
        container.reload()
        time.sleep(1)
        i+=1
        if i >= 30:
            print('Error starting: ', stimulus.service.name)
            exit()
    print('Stimulus service started: ', stimulus.service.name)
    stimulus.container = container
    stimulus.service.container = container

def start_output_server(recipient, client, project_path, docker_network_name):
    serv_command = 'python -u /vipr/scripts/tcp_listener.py -p '+ str(recipient.service.port) + ' -f ' + str(project_path)
    port_map_dict = {recipient.service.port: recipient.service.port}
    container = client.containers.run(image = 'python:3.6-slim-buster',
                volumes = {'/vipr': {'bind': '/vipr', 'mode': 'ro'},
                            project_path: {'bind': project_path, 'mode': 'rw'}},
                name = recipient.service.name,
                command = serv_command,
                ports = port_map_dict,
                detach = True,
                network = docker_network_name,
                #auto_remove = True
    )
    i=0
    while container.status != 'running':
        container.reload()
        time.sleep(1)
        i+=1
        if i >= 30:
            print('Error starting: ', recipient.service.name)
            exit()
    print('Recipient service started: ', recipient.service.name)
    recipient.container = container
    recipient.service.container = container

def start_tshark(client, project_path, docker_network_name):
    client.images.pull('cincan/tshark:latest')
    output_path = os.path.join(project_path + '/vipr/outputs/output.pcap')
    serv_command = '-w ' + output_path
    container = client.containers.run(image = 'cincan/tshark',
                volumes = {'/vipr': {'bind': '/vipr', 'mode': 'ro'},
                            project_path: {'bind': project_path, 'mode': 'rw'}},
                user = 'root',
                name = 'tshark',
                cap_add = ['NET_ADMIN', 'NET_RAW'],
                command = serv_command,
                detach = True,
                network = docker_network_name,
                #auto_remove = True
    )
    i=0
    while container.status != 'running':
        container.reload()
        time.sleep(1)
        i+=1
        if i >= 30:
            print('Error starting tshark service.')
            exit()
    print('Started tshark service.')
    return container

def start_analysis_service(type, client, project_path):
    cmd_dict = {'cot-file': 'sh -c "pip3 install -r /vipr/requirements/cot_file.txt && python -u /vipr/scripts/cot_file.py -p' + project_path + '"',
                'cot-pcap': 'sh -c "pip3 install -r /vipr/requirements/cot_pcap.txt && python -u /vipr/scripts/cot_pcap.py -p' + project_path + '"'}
    container = client.containers.run(image = 'python:3.6-slim-buster',
                volumes = {'/vipr': {'bind': '/vipr', 'mode': 'ro'},
                            project_path: {'bind': project_path, 'mode': 'rw'}},
                name = type,
                command = cmd_dict[type],
                #auto_remove = True,
                detach = True
    )
    i=0
    while container.status != 'running':
        container.reload()
        time.sleep(1)
        i+=1
        if i >= 30:
            print('Error starting analysis service: ', type)
            exit()
    print('Started analysis service: ', type)
    return container




def main(args):
    #client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    client = docker.from_env()

    project_name = args.repo.split('/')[-1]
    project_path = os.path.join('/', project_name)
    os.chdir("/")
    #This is going to eventually give me fits because of authentication
    os.system('git clone ' + args.repo + ' ' + project_path)
 
    ### Uncomment for primetime
    #config_paths = [os.path.join(project_path,  'vipr/config.yaml'),
    #                os.path.join(project_path,  'vipr/config.yml')]
    
    #if not os.path.exists(config_paths[0]):
    #    config_path = config_paths[1]
    #    if not os.path.exists(config_path):
    #        print('Configuration file not present in vipr/ folder in repository.')
    #        sys.exit()
    #else:
    #    config_path = config_paths[0]
    config_path = '/vipr/test/config.yaml'

    with open(config_path) as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    print('Loaded repo config file.')

    system, services, outputs = parse_config(config_dict)
    print('Parsed repo config file.')

    docker_network_name = system.name + '-net'
    try:
        client.networks.create(docker_network_name, check_duplicate=True)
    except:
        pass
    print('Created container network.')

    print('Starting stimulus/recipient services.')
    for output in outputs:
        #parse stimuli
        for stimulus in output.stimuli:
            if stimulus.type == 'tcp':
                start_tcp_server(stimulus, client, project_path, docker_network_name)
        for recipient in output.recipients:
            if recipient.type == 'tcp': ### Add more flexibility in this ###
                start_output_server(recipient, client, project_path, docker_network_name)

    ###Remove output PCAP file for testing re-runs
    try:
        os.remove(os.path.join(project_path, 'vipr/outputs/output.pcap'))
    except:
        pass
    ###

    print('Starting network capture service.')
    tshark_cont = start_tshark(client, project_path, docker_network_name)
    
    print('Starting system container.')
    start_system(system, client, project_path, docker_network_name)

    print('Waiting for validation task completion.')
    time.sleep(system.waittime)

    #Starting killing services
    for output in outputs:
        for stimulus in output.stimuli:
            stimulus.container.kill()
            print('Killed service: ', stimulus.service.name)
        for recipient in output.recipients:
            recipient.container.kill()
            print('Killed service: ', recipient.service.name)
    
    system.container.kill()
    print('Killed system service.')

    tshark_cont.kill()
    print('Killed tshark container.')

    print('Starting analysis service.')
    #Start analysis
    for output in outputs:
        if output.type == 'cot':
            #File analysis
            start_analysis_service('cot-file', client, project_path)
            #PCAP analysis
            #start_analysis_service('cot-pcap', client, project_path)

    ### Subsitute for a file exists check for the validation results
    time.sleep(30)

    #while True:
    #    pass
    #Copy test files from orchestrator container to VIPR directory on host
    from_path = os.path.join(project_path + '/vipr')
    to_path = os.path.join('/vipr', project_name)
    shutil.copytree(from_path, to_path)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo", help="URL of repository of system under validation", required=True)
    args = parser.parse_args()

    assert validators.url(args.repo); "Malformed repo URL"

    main(args)