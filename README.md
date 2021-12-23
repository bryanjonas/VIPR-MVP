# VIPR-MVP
### Concept:
This is an MVP of an interoperability harness. In this case it tests a piece of software called [**adsbcot**](https://github.com/ampledata/adsbcot) that can receive raw [ADS-B](https://mode-s.org/decode/content/ads-b/1-basics.html) messages across the network and translate them into CoT messages.

This harness consists of four containers that run together:
* A container that runs a mock TAK server gateway that recieves the CoT messages from **adsbcot**.
* A container that runs a mock ADS-B server that transmits ADS-B messages to **adsbcot**.
* A container that runs a CoT message validator that reports whether the CoT messages received pass basic CoT message format checks.
* A container that run the **adsbcot** software.

### Instructions:
* Launch using:
```{shell}
docker-compose up
```
* As we are testing **adbscot** as released by the developer, you'll have to exit all the containers using *CTRL-C* once you see two "CoT Validation" messages.

### Acknowledgments:
This repo contains a lot of code borrowed from:
* [adsbcot](https://github.com/ampledata/adsbcot)
* [taky](https://github.com/tkuester/taky)
* [pyModeS](https://github.com/junzis/pyModeS)
