# trash-tracker

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