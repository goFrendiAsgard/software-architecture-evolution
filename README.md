# Contoh Evolusi Arsitektur Perangkat Lunak

Repository ini adalah pelengkap untuk artikel [Evolusi Perangkat Lunak](https://www.notion.so/gofrendi/Evolusi-Arsitektur-Perangkat-Lunak-1e80ad470b734ad4ab22d04e25ea372e)


# Ports

```yaml
dbExample:
    mySQL       : 3306
messageBusExample:
    rabbitmq    : 5672
    web         : 15672
frontendMonolith: 
    web         : 3000
backendMonolith:
    web         : 3010
frontendMicroservice:
    web         : 5000
backendGateway:
    web         : 5010
backendFetcher:
    web         : 5020 (tidak melayani API request)
backendFetcher2:
    web         : 5021 (tidak melayani API request)
backendFetcher3:
    web         : 5022 (tidak melayani API request)
backendVoter:
    web         : 5030 (tidak melayani API request)
dbWarehouseExample:
    mySQL       : 3307
dataStreamer:
    web         : 7010 (tidak melayani API request)
```
