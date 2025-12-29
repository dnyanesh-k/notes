- Initially, systems were designed to run on a single, high-priced computer. 
- The cost of such a computer was so high that only governments and big corporations could afford it. 
- Even so, as soon as we created computer networks, people started to connect multiple computer systems. 
- Their motivation was to overcome issues that still haunt us all: Faster results and better resilience.

- At a high level, a computer cluster is a group of two or more computers, or nodes, that run in parallel to achieve a common goal. 
- This allows workloads consisting of a high number of individual, parallelizable tasks to be distributed among the nodes in the cluster. 
- As a result, these tasks can leverage the combined memory and processing power of each computer to increase overall performance.
- To build a computer cluster, the individual nodes should be connected to a network to enable internode communication. 
- The software can then be used to join the nodes together and form a cluster. 
- It may have a shared storage device and/or local storage on each node.

[Cluster](../diagrams/cluster.png)

- Typically, at least one node is designated as the leader node and acts as the entry point to the cluster. 
- The leader node may be responsible for delegating incoming work to the other nodes and, if necessary, aggregating the results and returning a response to the user.
- Ideally, a cluster functions as if it were a single system. 
- A user accessing the cluster should not need to know whether the system is a cluster or an individual machine. 
- Furthermore, a cluster should be designed to minimize latency and prevent bottlenecks in node-to-node communication.

In order to work correctly, a cluster needs management nodes that will:
1. coordinate the load sharing
2. detect node failure and schedule its replacement

Usually, it implies the need for high compatibility between the nodes in the hardware and software aspects. 
The nodes keep pinging each other’s services to check if they are up — a technique called **heartbeat**. 
Besides that, they strongly rely on the data network connecting them. 
By the way, in most cases, we’ll use redundant network paths between the nodes. That way, the cluster can differ from a node failure to a network outage.


# Types of Clustering [ref](https://www.baeldung.com/cs/computer-clusters-types)
 In practice, the various kinds can coexist at the same time. For instance, a Load-balancing computing cluster can have a Fail-server configuration for its management cluster.

 ## 1. High Availability or Fail-over Cluster
 In the fail-over configuration, services run in one computing node while the other waits to take over during outages. It is mainly used to add failure resiliency

### Configurations
The two most commonly used high availability (HA) clustering configurations are active-active and active-passive.

1. Active-Active

![active-active](/diagrams/active-active.png)

An active-active cluster is typically made up of at least two nodes, both actively running the same kind of service simultaneously. The main purpose of an active-active cluster is to achieve load balancing. A load balancer distributes workloads across all nodes to prevent any single node from getting overloaded. Because there are more nodes available to serve, there will also be an improvement in throughput and response times.

2. Active-Passive

![active-passive](/diagrams/active-passive.png)

Like the active-active cluster configuration, an active-passive cluster also consists of at least two nodes. However, as the name active-passive implies, not all nodes are going to be active. For example, in the case of two nodes, if the first node is already active, then the second node must be passive or on standby.


 ## 2. Load Balancing
In the load balancing cluster, the load is distributed among the available computing nodes.
Independent Nodes from each other.

## 3. High-Performance Computing – HPC
In this cluster type, we will want all the available computing resources running.



# Load Balancing vs Clustering

| Aspect             | Load Balancing                                                                 | Clustering                                                                 |
|--------------------|---------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| **Definition**     | Distributes incoming traffic across multiple servers using a load balancer.    | A group of servers working together as a single system to provide redundancy and scalability. |
| **Server Awareness** | Servers are **not aware** of each other; they only respond to requests sent by the load balancer. | Servers are **aware** of each other and coordinate tasks collectively. |
| **Primary Purpose** | Optimizes performance and ensures efficient distribution of workload.          | Provides redundancy, fault tolerance, and high availability.               |
| **Failure Handling** | If a server fails, the load balancer redirects traffic to healthy servers.    | If a node fails, other nodes in the cluster take over its workload seamlessly. |
| **Scalability**    | Easy to scale horizontally by adding more servers behind the load balancer.    | Scaling requires careful synchronization and configuration among cluster nodes. |
| **Resource Sharing** | Servers operate independently; resources are not shared.                     | Servers share resources and state information to act as one logical unit.  |
| **Complexity**     | Simpler to set up; mainly requires a load balancer configuration.              | More complex; requires cluster management software and synchronization.    |
| **Use Cases**      | Websites, web services, applications needing performance optimization.         | Databases, mission-critical applications, systems needing high availability and fault tolerance. |
| **Example Tools**  | Nginx, HAProxy, AWS Elastic Load Balancer.                                     | Kubernetes clusters, Oracle RAC, Hadoop clusters.                          |
| **Session Management** | Often requires **sticky sessions** to maintain user state.                 | Supports session replication across nodes, reducing dependency on sticky sessions. |
| **Performance vs Reliability** | Focused on **performance optimization** and workload distribution. | Focused on **reliability, redundancy, and fault tolerance**.               |
| **Cost Consideration** | Generally cheaper to implement; less synchronization overhead.             | More expensive due to hardware, software, and management overhead.         |
| **Modern Cloud Integration** | Cloud providers use load balancers to distribute traffic across servers. | Cloud providers use clustering for database availability and mission-critical workloads. |



# Challenges
- increased complexity of installation and maintenance. An operating system, the application, and its dependencies must each be installed and updated on every node.
- This becomes even more complicated if the nodes in the cluster are not homogeneous. 
- Resource utilization for each node must also be closely monitored, and logs should be aggregated to ensure that the software is behaving correctly.
- storage becomes more difficult to manage, a shared storage device must prevent nodes from overwriting one another and distributed data stores have to be kept in sync.

# Examples
Clustering is commonly used in the industry, and often many technologies offer some sort of clustering mode. For example:

- Containers (e.g. Kubernetes, Amazon ECS)
- Databases (e.g. Cassandra, MongoDB)
- Cache (e.g. Redis)