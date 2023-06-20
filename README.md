# SimOpInt Laminar Airbus A330 EFIS
Sim Open Interface Configuration for Airbus A330 from Laminar

You have to declare the interface in the simopint.json

Add the following in the INTERFACES section :

"A3xxefis": {
      "configfile": "A3xxefis.json"
    }

Example if it's the first interface :

{
  "NETWORK": {
    "srvname": "SimOpIntSrv",
    "xpladdr": "<X-Plane PC Ip Addr>",
    "xplport": 49500
  },
  "INTERFACES": {
    "A3xxefis": {
      "configfile": "A3xxefis.json"
    }
  }
}
