# VIPR-MVP
### Concept:
This is an MVP of an interoperability harness. In this case it validates a piece of software called [**adsbcot**](https://github.com/ampledata/adsbcot) that can receive raw [ADS-B](https://mode-s.org/decode/content/ads-b/1-basics.html) messages across the network and translate them into CoT messages.

This version of the harness consists of a single *orchestrator* container that runs using the sysbox runtime. This allows this container to create nested containers inside of it without being privileged or needing access to the host's docker socket. 

System users only need to provide a repository URL for their project. This repository must contain a few properly-formatted files in the **/vipr** directory:
* config.yaml: Provides the configuration for the orchestrator to design and run the specified validation(s)
* /inputs directory: Provides the file(s) with the payloads necessary to stimulate the system under validation
* /outputs directory: Provides the file(s) that contain the expected outputs of the validation
* startup.sh: Describes the steps necessary to run the system under validation after the repository is cloned into the environment


In the case of **adsbcot**, the orchestrator:
* Parses the configuration file present in the repo in order to pull the necessary information into an accessible format. 
* Stands up the stimulus service in a container that will provide the ADS-B messages over port 30002 to **adsbcot**. Once this container receives a connection, it sends the payloads provided in the */inputs* folder of the repo.
* Stands up a TCP listener service in a container that will provide an output connection for **adsbcot**. Once this container recieves a connection, it records the payloads of the packets it receives.
* Stands up a **tshark** container to permit capturing network traffic arriving for and leaving the **adscbot** container.
* Stands up a container for **adsbcot** with the cloned project in a mounted volume. This container is created using the **tshark** container's network connection which allows **tshark** to capture the network traffic.
* Runs the *startup.sh* script provided in the repo. This should start the service and begin the validation steps.
* Kills the above containers once the wait time defined in the configuration has elapsed.
* Stands up an analysis service in a container for the files produced by the TCP listener and reports whether they are valid CoT messages.
* Stands up an analysis service in a container to identify and validate CoT messages in the network traffic capture.
* Copies all of the results of the validation to the host's VIPR directory.


### Dependencies:
* docker
* docker-compose
* sysbox runtime (https://github.com/nestybox/sysbox)

### Instructions:
* Launch using:
```{shell}
./VIPR-startup.sh
```

### Acknowledgments:
This repo contains a lot of code borrowed from:
* [adsbcot](https://github.com/ampledata/adsbcot)
* [taky](https://github.com/tkuester/taky)
* [pyModeS](https://github.com/junzis/pyModeS)
