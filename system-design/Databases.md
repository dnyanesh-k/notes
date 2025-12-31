# What is a Database?
A database is an **organized collection of structured information, or data**, typically stored electronically in a computer system. 
A database is usually controlled by a Database Management System (DBMS). 
Together, the data and the DBMS, along with the applications that are associated with them, are referred to as a database system, often shortened to just database.

# What is DBMS?
A database typically requires a comprehensive database software program known as a Database Management System (DBMS). 
A DBMS serves as an interface between the database and its end-users or programs, allowing users to retrieve, update, and manage how the information is organized and optimized. 
A DBMS also facilitates oversight and control of databases, enabling a variety of administrative operations such as performance monitoring, tuning, and backup and recovery.

# Components
Here are some common components found across different databases:

## Schema
The role of a schema is to define the shape of a data structure, and specify what kinds of data can go where. 
Schemas can be strictly enforced across the entire database, loosely enforced on part of the database, or they might not exist at all.

## Table
Each table contains various columns just like in a spreadsheet. 
A table can have as meager as two columns and upwards of a hundred or more columns, depending upon the kind of information being put in the table.

## Column
A column contains a set of data values of a particular type, one value for each row of the database. A column may contain text values, numbers, enums, timestamps, etc.

## Row
Data in a table is recorded in rows. 
There can be thousands or millions of rows in a table having any particular information.

Below are different types of databases:

- SQL
- NoSQL
   - Document
   - Key-value
   - Graph
   - Timeseries
   - Wide column
   - Multi-model

# Challenges
Some common challenges faced while running databases at scale:

- **Absorbing significant increases in data volume:** The explosion of data coming in from sensors, connected machines, and dozens of other sources.

- **Ensuring data security:** Data breaches are happening everywhere these days, it's more important than ever to ensure that data is secure but also easily accessible to users.

- **Keeping up with demand:** Companies need real-time access to their data to support timely decision-making and to take advantage of new opportunities.

- **Managing and maintaining the database and infrastructure:** As databases become more complex and data volumes grow, companies are faced with the expense of hiring additional talent to manage their databases.

- **Removing limits on scalability:** A business needs to grow if it's going to survive, and its data management must grow along with it. But it's very difficult to predict how much capacity the company will need, particularly with on-premises databases.

- **Ensuring data residency, data sovereignty, or latency requirements:** Some organizations have use cases that are better suited to run on-premises. 
In those cases, engineered systems that are pre-configured and pre-optimized for running the database are ideal.

# SQL databases
A SQL (or relational) database is a collection of data items with pre-defined relationships between them.
These items are organized as a set of tables with columns and rows. 
Tables are used to hold information about the objects to be represented in the database. 
Each column in a table holds a certain kind of data and a field stores the actual value of an attribute. The rows in the table represent a collection of related values of one object or entity.

Each row in a table could be marked with a unique identifier called a primary key, and rows among multiple tables can be made related using foreign keys. 
This data can be accessed in many different ways without re-organizing the database tables themselves. 
SQL databases usually follow the [ACID consistency model](https://www.karanpratapsingh.com/courses/system-design/acid-and-base-consistency-models).

## Materialized views
A materialized view is a pre-computed data set derived from a query specification and stored for later use. Because the data is pre-computed, querying a materialized view is faster than executing a query against the base table of the view. 
This performance difference can be significant when a query is run frequently or is sufficiently complex.

It also enables data subsetting and improves the performance of complex queries that run on large data sets which reduces network loads. 
There are other uses of materialized views, but they are mostly used for performance and replication.

## N+1 query problem
The N+1 query problem happens when the data access layer(DAL) executes N additional SQL statements to fetch the same data that could have been retrieved when executing the primary SQL query. 
The larger the value of N, the more queries will be executed, the larger the performance impact.

1. **The "1" Query:** The application executes one SQL statement to retrieve a collection of \(N\) parent objects (e.g., SELECT * FROM Orders).
2. **The "N" Queries:** For each parent record returned, the application triggers an additional SQL statement to fetch related data (e.g., SELECT * FROM Items WHERE OrderID = ?) [2, 5]. 

This is commonly seen in GraphQL and ORM (Object-Relational Mapping) tools and can be addressed by optimizing the SQL query or using a dataloader that batches consecutive requests and makes a single data request under the hood.

## Advantages
Let's look at some advantages of using relational databases:

- Simple and accurate
- Accessibility
- Data consistency
- Flexibility

## Disadvantages
Below are the disadvantages of relational databases:

- Expensive to maintain
- Difficult schema evolution
- Performance hits (join, denormalization, etc.)
- Difficult to scale due to poor horizontal scalability

## Examples
Here are some commonly used relational databases:

- PostgreSQL(https://www.postgresql.org/)
- MySQL(https://www.mysql.com/)
- MariaDB(https://mariadb.org/)
- Amazon Aurora(https://aws.amazon.com/rds/aurora)

# NoSQL databases
NoSQL is a broad category that includes any database that doesn't use SQL as its primary data access language. 
These types of databases are also sometimes referred to as non-relational databases. 
Unlike in relational databases, data in a NoSQL database doesn't have to conform to a pre-defined schema. NoSQL databases follow BASE consistency model.

Below are different types of NoSQL databases:
## Document
A document database (also known as a document-oriented database or a document store) is a database that stores information in documents. They are general-purpose databases that serve a variety of use cases for both transactional and analytical applications.

### Advantages

- Intuitive and flexible
- Easy horizontal scaling
- Schemaless

### Disadvantages

- Schemaless
- Non-relational

### Examples
- MongoDB
- Amazon DocumentDB
- CouchDB

## Key-value
One of the simplest types of NoSQL databases, key-value databases save data as a group of key-value pairs made up of two data items each. 
They're also sometimes referred to as a key-value store.

### Advantages

- Simple and performant
- Highly scalable for high volumes of traffic
- Session management
- Optimized lookups

### Disadvantages

- Basic CRUD
- Values can't be filtered
- Lacks indexing and scanning capabilities
- Not optimized for complex queries

### Examples
- Redis
- Memcached
- Amazon DynamoDB
- Aerospike

## Graph
A graph database is a NoSQL database that uses graph structures for semantic queries with nodes, edges, and properties to represent and store data instead of tables or documents.

The graph relates the data items in the store to a collection of nodes and edges, the edges representing the relationships between the nodes. The relationships allow data in the store to be linked together directly and, in many cases, retrieved with one operation.

### Advantages

- Query speed
- Agile and flexible
- Explicit data representation

### Disadvantages

- Complex
- No standardized query language

### Use cases

- Fraud detection
- Recommendation engines
- Social networks
- Network mapping

### Examples

- Neo4j
- ArangoDB
- Amazon Neptune
- JanusGraph

## Time series
A time-series database is a database optimized for time-stamped, or time series, data.

### Advantages

- Fast insertion and retrieval
- Efficient data storage

### Use cases

- IoT data
- Metrics analysis
- Application monitoring
- Understand financial trends

### Examples

- InfluxDB
- Apache Druid

## Wide column
Wide column databases, also known as wide column stores, are schema-agnostic. Data is stored in column families, rather than in rows and columns.

### Advantages

- Highly scalable, can handle petabytes of data
- Ideal for real-time big data applications

### Disadvantages

- Expensive
- Increased write time

### Use cases

- Business analytics
- Attribute-based data storage

### Examples

- BigTable
- Apache Cassandra
- ScyllaDB

## Multi-model
Multi-model databases combine different database models (i.e. relational, graph, key-value, document, etc.) into a single, integrated backend. 
This means they can accommodate various data types, indexes, queries, and store data in more than one model.

### Advantages

- Flexibility
- Suitable for complex projects
- Data consistent

### Disadvantages

- Complex
- Less mature
### Examples

- ArangoDB
- Azure Cosmos DB
- Couchbase

# SQL vs NoSQL databases
In the world of databases, there are two main types of solutions, SQL (relational) and NoSQL (non-relational) databases. 
Both of them differ in the way they were built, the kind of information they store, and how they store it. 
Relational databases are structured and have predefined schemas while non-relational databases are unstructured, distributed, and have a dynamic schema.

## High-level differences
Here are some high-level differences between SQL and NoSQL:

### Storage
- SQL stores data in tables, where each row represents an entity and each column represents a data point about that entity.

- NoSQL databases have different data storage models such as key-value, graph, document, etc.

### Schema
- In SQL, each record conforms to a fixed schema, meaning the columns must be decided and chosen before data entry and each row must have data for each column. The schema can be altered later, but it involves modifying the database using migrations.

- Whereas in NoSQL, schemas are dynamic. Fields can be added on the fly, and each record (or equivalent) doesn't have to contain data for each field.

### Querying
- SQL databases use SQL (structured query language) for defining and manipulating the data, which is very powerful.

- In a NoSQL database, queries are focused on a collection of documents. Different databases have different syntax for querying.

### Scalability
- In most common situations, SQL databases are vertically scalable, which can get very expensive. It is possible to scale a relational database across multiple servers, but this is a challenging and time-consuming process.

- On the other hand, NoSQL databases are horizontally scalable, meaning we can add more servers easily to our NoSQL database infrastructure to handle large traffic. Any cheap commodity hardware or cloud instances can host NoSQL databases, thus making it a lot more cost-effective than vertical scaling. A lot of NoSQL technologies also distribute data across servers automatically.

### Reliability
The vast majority of relational databases are ACID compliant. So, when it comes to data reliability and a safe guarantee of performing transactions, SQL databases are still the better bet.

Most of the NoSQL solutions sacrifice ACID compliance for performance and scalability.

## Reasons
As always we should always pick the technology that fits the requirements better. So, let's look at some reasons for picking SQL or NoSQL based database:

### For SQL

- Structured data with strict schema
- Relational data
- Need for complex joins
- Transactions
- Lookups by index are very fast

### For NoSQL

- Dynamic or flexible schema
- Non-relational data
- No need for complex joins
- Very data-intensive workload
- Very high throughput for IOPS

# Database Replication
Database replication is the process of creating and maintaining identical copies (replicas) of a database across multiple servers or locations to ensure high availability, fault tolerance, performance, and scalability, allowing users to access consistent, up-to-date data from different points while distributing workload and protecting against data loss. 
It typically involves a primary database receiving writes and propagating changes to secondary replicas, ensuring redundancy and faster access for users globally. 

## Why? 
- **Reducing Latency:** By geographically distributing replicas, systems can serve data from the closest node to the user, significantly reducing response times for read operations.

- **Increasing Throughput:** Replication allows systems to handle more read operations by distributing the load across multiple nodes. For certain replication strategies, write throughput can also be enhanced by parallelizing write operations.

- **Improving Availability:** Replication ensures that even in the event of a node failure, the system can continue to operate by failing over to replicas, thereby minimizing downtime and maintaining continuous access to data.

- **Enhancing Durability:** In scenarios of hardware failure or data center outages, having replicated data across multiple locations ensures that data is not lost and can be recovered, supporting robust disaster recovery strategies.

Replication strategies are critical in defining how data is copied and maintained across systems, each with its unique benefits and challenges.

## Leader-Follower Replication
Also known as Master/Backup or Master/Standby replication, this model employs a single Leader/Master node for write and data definition operations, such as database alterations, while follower/backup/standby nodes replicate and synchronize data from the master. 
This structure simplifies implementation by avoiding write conflicts, as only the master node handles write transactions.
If the master goes offline, the system can continue to operate in read-only mode until a follower is promoted to a master or a new master is provisioned.

![leader-follower](../diagrams/leader-follower.png)

### Failures in Leader-Follower Replication

#### Follower Failures:
Regular health checks identify any follower node failures, prompting an immediate reroute of its traffic to operational replicas while efforts are made to recover or replace the compromised node. 
It’s critical to manage the distribution of traffic to avoid overburdening other nodes, which could risk the stability of the entire system.

#### Leader Failures:
Leader node failures present a more challenging scenario due to the exclusive write capabilities of the leader. 
Through heartbeat monitoring, a failed leader is quickly identified, necessitating a manual promotion of a follower to leader status or initiating an automatic leader election process, such as employing the Raft protocol. 
Transition periods may temporarily disrupt write capabilities, posing potential issues for systems requiring continuous write access.

## Multi-Leader Replication
Expanding on the leader-follower model, multi-leader replication allows multiple nodes to accept writes, enhancing write availability and system resilience. 
This strategy excels in distributed environments but requires sophisticated conflict resolution to manage concurrent data modifications.

![multi-leader](../diagrams/multi-leader.png)

In this architecture, redundancy ensures system reliability; if a leader fails, another takes over, utilizing consensus algorithms like Paxos for seamless leadership transition. 
Despite potential delays due to data needing replication across leaders and the complexities in aligning data among them, the system’s enhanced fault tolerance generally compensates for these drawbacks.

### Managing Conflict in Multi-Leader Replication
In multi-leader replication, managing conflicts is critical due to simultaneous write operations by multiple leaders. A primary strategy, **Last Write Wins (LWW)**, prioritizes the most recent update, though it may overlook significant changes.

Other approaches include Conflict-free Replicated Data Types (CRDTs), which merge conflicting updates seamlessly; Operational Transformation (OT), offering detailed control for collaborative applications; and application-specific solutions, where conflicts are resolved based on the domain’s unique requirements. These methods collectively aim to maintain data consistency and integrity within distributed systems.

### Some Use Cases for Multi-Leader Replication

- **E-commerce Platforms:** Multi-leader replication is beneficial for large e-commerce sites that operate across different regions, enabling localized transaction processing and inventory management to enhance user experience and operational efficiency.

- **Internet of Things (IoT) Systems:** In IoT applications where devices are distributed globally and need to operate reliably even in disconnected modes, multi-leader replication allows for decentralized decision-making and data aggregation, improving responsiveness and system resilience.

## Leaderless Replication
Leaderless replication models represent a paradigm shift towards distributed authority in data management. By eliminating the traditional leader-follower hierarchy, these systems distribute write operations across nodes, leveraging consensus mechanisms to ensure data integrity and consistency.

![leader-less](../diagrams/leaderless.png)

### Challenges and Considerations

While leaderless replication enhances system availability and fault tolerance, it introduces complexities in managing data consistency, especially under high write loads and across geographically distributed nodes. Systems must be designed to handle replication lag and transient inconsistencies, ensuring that applications can tolerate or rectify state discrepancies.

### Leveraging Leaderless Replication

Ideal for scenarios demanding high availability and distributed data access, leaderless replication suits applications with global user bases and those requiring robust fault tolerance. Implementing this model demands a nuanced understanding of its trade-offs, particularly in conflict resolution and system design to balance consistency with availability.


## Synchronous Replication
This method ensures strict data consistency by waiting for acknowledgment from all follower nodes before completing write operations. 
While it guarantees that followers always have the latest data, it introduces write latency, particularly in geographically dispersed setups.

![sync-replication](../diagrams/sync-replication.png)

## Asynchronous Replication
Enhancing performance, asynchronous replication allows the leader to proceed with operations without immediate acknowledgment from followers. 
This approach reduces write latency but risks data loss if the leader fails before followers are updated, leading to eventual consistency challenges.

![async-replication](../diagrams/async-replication.png)


## Pros and Cons of Database Replication

### Advantages 
- **Scalability and Performance:** Replication enables systems to handle increased load by distributing reads and, in some models, writes across multiple nodes.

- **Data Locality:** By positioning data closer to users, replication can significantly reduce latency, enhancing the user experience.

- **Enhanced Durability and Availability:** Replication ensures data persistence across system failures, maintaining service continuity.

### Challenges:
- **Data Consistency:** Achieving strict consistency can be challenging, especially in asynchronous and leaderless models where eventual consistency prevails.

- **System Complexity:** Implementing and managing replication, particularly in multi-leader and leaderless setups, adds complexity to system design and operation.

- **Write Latency:** In synchronous replication, the integrity comes at the cost of increased latency due to the need for cross-node communication.


# Indexes
- a specialized data structure that speeds up data retrieval operations (queries) by providing quick lookup access to data

- Indexes are well known when it comes to databases, they are used to improve the speed of data retrieval operations on the data store. 

- A database index is a super-efficient lookup table that allows a database to find data much faster.

- It holds the indexed column values along with pointers to the corresponding rows in the table.

- Without an index, the database might have to scan every single row in a massive table to find what you want – a painfully slow process.

- But, with an index, the database can zero in on the exact location of the desired data using the index’s pointers.

**Trade-off**
- An index makes the trade-offs of increased storage overhead, and slower writes (since we not only have to write the data but also have to update the index) for the benefit of faster reads. 
- Indexes can be created using one or more columns of a database table, providing the basis for both rapid random lookups and efficient access to ordered records.

- Indexes are also used to create different views of the same data. 
- For large data sets, this is an excellent way to specify different filters or sorting schemes without resorting to creating multiple additional copies of the data.
- One quality that database indexes can have is that they can be dense or sparse. Each of these index qualities comes with its own trade-offs. 
- Let's look at how each index type would work:

## Dense Index
In a dense index, an index record is created for every row of the table. Records can be located directly as each record of the index holds the search key value and the pointer to the actual record.

![dense-index](../diagrams/dense-index.png)

Dense indexes require more maintenance than sparse indexes at write-time. 
Since every row must have an entry, the database must maintain the index on inserts, updates, and deletes. 
Having an entry for every row also means that dense indexes will require more memory. 
The benefit of a dense index is that values can be quickly found with just a binary search. 
Dense indexes also do not impose any ordering requirements on the data.

## Sparse Index
In a sparse index, index records are created only for some of the records.

![sparse-index](../diagrams/sparse-index.png)

Sparse indexes require less maintenance than dense indexes at write-time since they only contain a subset of the values. This lighter maintenance burden means that inserts, updates, and deletes will be faster. Having fewer entries also means that the index will use less memory. Finding data is slower since a scan across the page typically follows the binary search. Sparse indexes are also optional when working with ordered data.

## How to create index:
`CREATE INDEX idx_last_name ON employees(last_name);`

`SELECT * FROM employees WHERE last_name = 'Smith'`

## Here's a step-by-step explanation of how database indexes work:

1. **Index Creation:** The database administrator creates an index on a specific column or set of columns.

2. **Index Building:** The database management system builds the index by scanning the table and storing the values of the indexed column(s) along with a pointer to the corresponding data.

3. **Query Execution:** When a query is executed, the database engine checks if an index exists for the requested column(s).

4. **Index Search:** If an index exists, the database searches the index for the requested data, using the pointers to quickly locate the data.

5. **Data Retrieval:** The database retrieves the requested data, using the pointers from the index.

![db-indexes-basic](../diagrams/db-indexes-basic.png)

## Benefits of DB Idexes
- **Faster Query Performance:** Indexes can significantly improve query performance especially for large datasets by reducing the amount of data that needs to be scanned.

- **Reduced CPU Usage:** By reducing the number of rows that need to be scanned, indexes can decrease CPU usage and optimize resource utilization.

- **Rapid Data Retrieval:** Indexes enable quick data retrieval for queries that involve equality or range conditions on the indexed columns.

- **Efficient Sorting:** Indexes can also be used to efficiently sort data based on the indexed columns, eliminating the need for expensive sorting operations.

- **Better Data Organization:** Indexes can help maintain data organization and structure, making it easier to manage and maintain the database.

## Types of Database Indexes

### Indexes based on Structure and Key Attributes:
- **Primary Index:** Automatically created when a primary key constraint is defined on a table. Ensures uniqueness and helps with super-fast lookups using the primary key.

- **Clustered Index:** Determines the order in which data is physically stored in the table. A clustered index is most useful when we’re searching in a range. Only one clustered index can exist per table.

- **Non-clustered or Secondary Index:** This index does not store data in the order of the index. Instead, it provides a list of virtual pointers or references to the location where the data is actually stored.

### Indexes based on Data Coverage:
- **Dense index:** Has an entry for every search key value in the table. Suitable for situations where the data has a small number of distinct search key values or when fast access to individual records is required.
- **Sparse index:** Has entries only for some of the search key values. Suitable for situations where the data has a large number of distinct search key values.

### Specialized Index Types:
- **Bitmap Index:** Excellent for columns with low cardinality (few distinct values). Common in data warehousing.

*Cardinality -{A, B, C} has cardinality 3. How many unique values a column has?. High cardinality (like unique user IDs) can increase memory usage and slow down queries, while low cardinality is more efficient.*

- **Hash Index:** A index that uses a hash function to map values to specific locations. Great for exact match queries.

- **Filtered Index:** Indexes a subset of rows based on a specific filter condition. Useful to improve query speed on commonly filtered columns.

- **Covering Index:** Includes all the columns required by a query in the index itself, eliminating the need to access the underlying table data.

- **Function-based index:** Indexes that are created based on the result of a function or expression applied to one or more columns of a table.

- **Full-Text Index:** A index designed for full-text search, allowing for efficient searching of text data.

- **Spatial Index:** Used for indexing geographical data types.

## Data Structures used in indexes:
Most commonly used data structures that power indexes are B-Trees, Hash Tables and Bitmaps.

### B-Tree(Balanced Tree)

![B-tree](../diagrams/b-tree.png)

Most database engines use either a B-Tree or a variation of B-Trees like B+ Trees.

B-Trees have a hierarchical structure with a root node, internal nodes (index nodes), and leaf nodes.

Each node in a B-Tree contains a sorted array of keys and pointers to child nodes.

Here's why they are so well-suited:

- **Self-Balancing:** B-trees ensure that the 'height' of the tree stays balanced even when inserting or deleting data. This ensures logarithmic time complexity for insertion, deletion, and searching.

- **Ordered:** B-trees keep the data sorted, making range queries ("find all orders between date X and Y") and inequality comparisons very fast.

- **Disk-Friendly:** B-trees are designed to work well with disk-based storage. A single node of a B-tree often corresponds to a disk block, minimizing disk access operations.

Many databases use a slightly modified B-tree variant called the B+ tree.

In a B+ tree, all data values are stored only in the leaf nodes, which can further improve performance for certain use cases like range queries.

### Hash Table

![hash-table](../diagrams/hash-table.png)

Hash tables are used for hash indexes, which are based on a hash function.

A hash table consists of an array of buckets, with each bucket containing the addresses for rows in the data.

Hash indexes employ a hash function to map keys to their corresponding bucket in the hash table, enabling constant-time lookup operations.

Hash indexes provide fast equality lookups, as the hash function determines the exact location of the data based on the key.

However, hash indexes do not support range queries or sorting efficiently.

### BitMap

![BitMap](../diagrams/bitmap.png)

Each bit in the bitmap corresponds to a row, and the value of the bit indicates whether the key value exists in that row.

Bitmap indexes use a bitmap (a binary array) to represent the presence or absence of a specific key value in each row of a table.

Bitmap indexes are well-suited for columns with low cardinality (a small number of distinct values) and for performing complex queries involving multiple conditions.

Bitmap operations like AND, OR, and NOT are performed efficiently using bitwise operations, making bitmap indexes suitable for analytical queries involving multiple columns.

## How to use Database Indexes Smartly?

- **Identify Query Patterns:** Analyze the most frequent and critical queries executed against your database to determine which columns to index and which type of index to use.

- **Index Frequently Used Columns:** Consider indexing columns that are frequently used in WHERE, JOIN, and ORDER BY clauses.

- **Index Selective Columns:** Indexes are most effective on columns with a good spread of data values (high cardinality). Indexing a gender column might be less beneficial than one with a unique customer_id.

- **Use Appropriate Index Types:** Choose the right index type for your data and queries.

- **Consider Composite Indexes:** For queries involving multiple columns, consider creating composite indexes that encompass all relevant columns. This reduces the need for multiple single-column indexes and improves query performance.

- **Monitor Index Performance:** Regularly monitor index performance, remove unused indexes and adjust your indexing strategy as the database workload evolves.

- **Avoid Over-Indexing:** Avoid creating too many indexes, as this can lead to increased storage requirements and slower write performance.

   - Indexes take up extra disk space since they're additional data structures that need to be stored alongside your tables.

   - Every time you insert, update, or delete data in a table with an index, the index needs to update too. This can slightly slow down write operations.
