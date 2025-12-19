## Q. What is load balancing?
Load balancing is the process of distributing traffic among multiple servers to improve a service or application's performance and reliability.

Load balancing is the practice of distributing computational workloads between two or more computers.
On the Internet, load balancing is often employed to divide network traffic among several servers. 
This reduces the strain on each server and makes the servers more efficient, speeding up [performance](https://www.cloudflare.com/learning/performance/why-site-speed-matters/) and reducing [latency](https://www.cloudflare.com/learning/performance/glossary/what-is-latency/).

- By dividing user requests among multiple servers, user wait time is vastly cut down.

![LB](../diagrams/load-balancer.png)

For additional scalability and redundancy, we can try to load balance at each layer of our system:

![LB Layers](../diagrams/load-balancer-layers.png)

# Why Load Balancing?
Modern high-traffic websites must serve hundreds of thousands, if not millions, of concurrent requests from users or clients. To cost-effectively scale to meet these high volumes, modern computing best practice generally requires adding more servers.

A load balancer can sit in front of the servers and route client requests across all servers capable of fulfilling those requests in a manner that maximizes speed and capacity utilization. This ensures that no single server is overworked, which could degrade performance. If a single server goes down, the load balancer redirects traffic to the remaining online servers. When a new server is added to the server group, the load balancer automatically starts sending requests to it.

![without LB](../diagrams/without%20LB.png)

![with LB](../diagrams/with%20LB.png)


# Workload distribution
This is the core functionality provided by a load balancer and has several common variations:

**Host-based:** Distributes requests based on the requested hostname.

**Path-based:** Using the entire URL to distribute requests as opposed to just the hostname

**Content-based:** Inspects the message content of a request. This allows distribution based on content such as the value of a parameter.

# Layers
Generally speaking, load balancers operate at one of the two levels:

## Network layer
This is the load balancer that works at the network's transport layer, also known as layer 4. This performs routing based on networking information such as IP addresses and is not able to perform content-based routing. These are often dedicated hardware devices that can operate at high speed.

## Application layer
This is the load balancer that operates at the application layer, also known as layer 7. Load balancers can read requests in their entirety and perform content-based routing. This allows the management of load based on a full understanding of traffic.

# Types
Let's look at different types of load balancers:

## Software
Software load balancers usually are easier to deploy than hardware versions. They also tend to be more cost-effective and flexible, and they are used in conjunction with software development environments. The software approach gives us the flexibility of configuring the load balancer to our environment's specific needs. The boost in flexibility may come at the cost of having to do more work to set up the load balancer. Compared to hardware versions, which offer more of a closed-box approach, software balancers give us more freedom to make changes and upgrades.

Software load balancers are widely used and are available either as installable solutions that require configuration and management or as a managed cloud service.

## Hardware
As the name implies, a hardware load balancer relies on physical, on-premises hardware to distribute application and network traffic. These devices can handle a large volume of traffic but often carry a hefty price tag and are fairly limited in terms of flexibility.

Hardware load balancers include proprietary firmware that requires maintenance and updates as new versions, and security patches are released.

## DNS
DNS load balancing is the practice of configuring a domain in the Domain Name System (DNS) such that client requests to the domain are distributed across a group of server machines.

Unfortunately, DNS load balancing has inherent problems limiting its reliability and efficiency. Most significantly, DNS does not check for server and network outages, or errors. It always returns the same set of IP addresses for a domain even if servers are down or inaccessible.

# Routing Algorithms
Now, let's discuss commonly used routing algorithms:

**Round-robin:** Requests are distributed to application servers in rotation.
**Weighted Round-robin:** Builds on the simple Round-robin technique to account for differing server characteristics such as compute and traffic handling capacity using weights that can be assigned via DNS records by the administrator.
**Least Connections:** A new request is sent to the server with the fewest current connections to clients. The relative computing capacity of each server is factored into determining which one has the least connections.
**Least Response Time:** Sends requests to the server selected by a formula that combines the fastest response time and fewest active connections.
**Least Bandwidth:** This method measures traffic in megabits per second (Mbps), sending client requests to the server with the least Mbps of traffic.
**Hashing:** Distributes requests based on a key we define, such as the client IP address or the request URL.

# Benefits of load balancing
## 1. Availability 
- Load balancers perform health checks on servers before routing requests to them. If one server is about to fail, or is offline for maintenance or upgrades, load balancing automatically reroutes the workload to a working server to avoid service interruptions and maintain high availability.

## 2. Scalability
- Load balancing enables an on-demand, high-performance infrastructure that can handle the heaviest or lightest network traffic loads. Physical or virtual servers can be added or removed as needed, making scalability simple and automated.

## 3. Security
Load balancers can include security features such as SSL encryption, web application firewalls (WAF) and multi-factor authentication (MFA). They can also be incorporated into application delivery controllers (ADC) to improve application security. By safely routing or offloading network traffic, load balancing can help defend against security risks such as distributed denial-of-service (DDoS) attacks

## How does load balancing work?
Load balancing is handled by a tool or application called a load balancer. A load balancer can be either hardware-based or software-based.

When a request arrives from a user, the load balancer assigns the request to a given server, and this process repeats for each request. Load balancers determine which server should handle each request based on a number of different algorithms. These algorithms fall into two main categories: static and dynamic.

### 1. Static load balancing algorithms
Static load balancing algorithms distribute workloads without taking into account the current state of the system. 
A static load balancer will not be aware of which servers are performing slowly and which servers are not being used enough. 
Instead it assigns workloads based on a predetermined plan. Static load balancing is quick to set up, but can result in inefficiencies.

On a grocery store we are sending first customer to one cashier and then second to second but there is chance that first customer has long list of items, considering all cashiers has same efficiency, in that case that first row ma take more time comapred two row 2.

Static load balancing presents the risk: sometimes, individual servers can become overburdened.

### 2. Dynamic load balancing algorithms
Dynamic load balancing algorithms take the current availability, workload, and health of each server into account. They can shift traffic from overburdened or poorly performing servers to underutilized servers, keeping the distribution even and efficient. However, dynamic load balancing is more difficult to configure. A number of different factors play into server availability: the health and overall capacity of each server, the size of the tasks being distributed, and so on.

Suppose the grocery store employee who sorts the customers into checkout lines uses a more dynamic approach: the employee watches the lines carefully, sees which are moving the fastest, observes how many groceries each customer is purchasing, and assigns the customers accordingly. This may ensure a more efficient experience for all customers, but it also puts a greater strain on the line-sorting employee.

There are several types of dynamic load balancing algorithms, including least connection, weighted least connection, resource-based, and geolocation-based load balancing.


## Q. What is server monitoring?
- Dynamic load balancers must be aware of server health: their current status, how well they are performing, etc. 
- Dynamic load balancers monitor servers by performing regular server health checks. 
- If a server or group of servers is performing slowly, the load balancer distributes less traffic to it. 
- If a server or group of servers fails completely, the load balancer reroutes traffic to another group of servers, a process known as "failover."

## Q. What is failover?
- Failover occurs when a given server is not functioning and a load balancer distributes its normal processes to a secondary server or group of servers. 
- Server failover is crucial for reliability: if there is no backup in place, a server crash could bring down a website or application. 
- It is important that failover takes place quickly to avoid a gap in service.

