# trash-tracker
## Description
The app is a smart tool which helps trash company to find the most optimized path to collect trash from multiple points. The app is designed to be used by the trash company's drivers. The app will provide the driver with the most optimized path to collect trash from multiple points. The app will also provide the driver with the distance between each point and the total distance of the route.

## Infrastructure architecture
```mermaid
graph TB
    User["User Browser"]
    
    subgraph CF ["Cloudflare"]
        DNS["DNS Resolution<br/>*Global Anycast DNS*"]
        TLS["TLS Termination<br/>*Universal SSL Certificate*"]
        WAF["Web Application Firewall</br>*WAF*"]
        AntiDDoS["Anti-DDoS</br>*Unmetered DDoS Protection*"]
        Bot["Bot Protection</br>*Bot Fight Mode*"]
        
        TLS --> WAF --> AntiDDoS --> Bot
    end


    subgraph AWS ["AWS Cloud"]
        subgraph VPC ["Virtual Private Cloud"]
            subgraph Public ["Public Subnet"]
                TLS2["TLS Certificate<br/>AWS Certificate Manager"]
                
                subgraph PubAZ1["Availability Zone A"]
                    NATGW1["NAT Gateway"]
                    ALB1["Application Load Balancer<br/>• HTTPS 443<br/>• TLS Termination<br/>• Port Forwarding"]
                end
                subgraph PubAZ2["Availability Zone B"]
                    NATGW2["NAT Gateway"]
                    ALB2["Application Load Balancer<br/>• HTTPS 443<br/>• TLS Termination<br/>• Port Forwarding"]
                end
                TLS2 --> ALB1
                TLS2 --> ALB2
            end
            
            subgraph Private ["Private Subnet"]
                subgraph Fargate ["ECS Fargate"]
                    subgraph AZ1["AZ A"]
                        Task11["Django App"]
                        Task12["OSRM App"]
                        EC21["EC2 with IDS"]   
                    end
                    subgraph AZ2["AZ B"]
                        Task21["Django App"]
                        Task22["OSRM App"]
                        EC22["EC2 with IDS"]
                    end
                end
            end
            
            subgraph AuroraDB["Aurora DB Cluster - Multi-AZ"]
                DBW["Write Instance"]
                DBR1["Read Replica 1"]
                DBR2["Read Replica 2"]
            end
        end
    end

    %% Force layout order
    AZ1 ~~~ AZ2
    PubAZ1 ~~~ PubAZ2
    Public ~~~ Private
    Private ~~~ AuroraDB

    %% User to Cloudflare
    User -->|"1. DNS Query"| DNS
    DNS -->|"2. CloudFlare IP"| User
    User -->|"3. HTTPS Request"| TLS

    %% Cloudflare to AWS
    Bot -->|"Validated Traffic"| TLS2

    %% Load Balancing
    ALB1 -.->|"Load Balance"| Task11
    ALB2 -.->|"Load Balance"| Task21

    %% App Communication
    Task11 <-->|"2. Distance Request"| Task12
    Task21 <-->|"OSRM Routing"| Task22

    %% Database Access
    Task11 -->|"1. Read"| DBR1
    Task11 -->|"4. Write"| DBW
    Task21 -->|"Read"| DBR2
    Task21 -->|"Write"| DBW

    %% Response
    Task11 -->|"5. Response"| NATGW1 --> User
    Task21 --> NATGW2
```

## Workflow

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

## How to set up database
1. Install Docker
2. Install Docker Compose
3. Run ```docker-compose up -d``` in the persistence directory

## How to set up the OSRM
1. Install Docker
2. Install Docker Compose
2. Download the map data from [Geofabrik](https://download.geofabrik.de/europe/poland/dolnoslaskie.html)
3. Move it to the osrm directory
4. Run ```docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/dolnoslaskie-latest.osm.pbf```
5. Run ```docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/dolnoslaskie-latest.osrm```
6. Run ```docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/dolnoslaskie-latest.osrm```
7. Run ```docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/dolnoslaskie-latest.osrm```

## How to run the app
1. Clone the repository
2. Run ```pip install -r .\src\requirements\requirements.txt```
3. Navigate to the persistence directory: ```cd persistence``` and run ```docker-compose up -d```
4. Navigate to the src directory 
5. Run ```python manage.py makemigrations routes```
6. Run ```python manage.py migrate```
7. Run ```python manage.py runserver``` to start the server