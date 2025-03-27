# trash-tracker
## Description
The app is a smart tool which helps trash company to find the most optimized path to collect trash from multiple points. The app is designed to be used by the trash company's drivers. The app will provide the driver with the most optimized path to collect trash from multiple points. The app will also provide the driver with the distance between each point and the total distance of the route.
## Workflows
```mermaid
flowchart TD
    user([User])
    backend[App server]
    db[(Database)]
    osrm[Open Source Routing Machine]
    user --> |1.Requests optimal route| backend
    backend <--> |Queries| db
    backend  --> |Multiple points requests| osrm
    osrm --> |Distane and path steps| backend
    backend --> |Response| user

```

```mermaid
flowchart TD
    user([User])
    backend[Backend Service]
    geocoder[Geocoding Service]
    
    user --> |Enters human address| backend
    backend --> |Sends address for lookup| geocoder
    geocoder --> |Returns coordinates| backend
    backend --> |Delivers coordinates| user
```

## How to run the app
1. Clone the repository
2. Run ```pip install -r .\src\requirements\requirements.txt```
3. Run ```python .\src\manage.py runserver``` to start the server