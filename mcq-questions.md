# MCQ Questions - Local Load Balancer

## Instructions
Choose the best answer for each question. Each question has only one correct answer.

---

### Question 1: Load Balancing Purpose
What is the primary purpose of a load balancer?

A) To store data across multiple servers  
B) To distribute incoming traffic across multiple service instances for better performance and availability  
C) To encrypt network traffic  
D) To compile code faster  

**Answer: B**

---

### Question 2: Round-Robin Algorithm
How does the round-robin load balancing algorithm work?

A) Randomly selects an instance  
B) Always selects the fastest instance  
C) Distributes requests sequentially to each instance in rotation  
D) Sends all requests to one instance until it fails  

**Answer: C**

---

### Question 3: Circuit Breaker States
What are the three states of a circuit breaker?

A) ON, OFF, STANDBY  
B) CLOSED, OPEN, HALF_OPEN  
C) ACTIVE, INACTIVE, PENDING  
D) START, STOP, PAUSE  

**Answer: B**

---

### Question 4: Health Check Purpose
Why are health checks important in load balancing?

A) To make services run faster  
B) To detect and remove unhealthy instances from the pool to prevent routing traffic to failing services  
C) To reduce memory usage  
D) To encrypt data  

**Answer: B**

---

### Question 5: Weighted Round-Robin
In weighted round-robin, what does a higher weight value mean?

A) The instance is slower  
B) The instance receives proportionally more traffic  
C) The instance is less reliable  
D) The instance uses more memory  

**Answer: B**

---

### Question 6: Circuit Breaker OPEN State
What happens when a circuit breaker is in the OPEN state?

A) All requests are allowed through  
B) Requests are rejected immediately without calling the service  
C) Requests are queued for later  
D) Requests are sent to a backup service  

**Answer: B**

---

### Question 7: Least Connections Algorithm
How does the least connections algorithm select an instance?

A) Randomly  
B) In round-robin order  
C) Selects the instance with the fewest active connections  
D) Selects the newest instance  

**Answer: C**

---

### Question 8: Failover
What is failover in the context of load balancing?

A) Deleting failed instances  
B) Automatically switching traffic to a backup instance when the primary fails  
C) Restarting all services  
D) Logging errors  

**Answer: B**

---

### Question 9: Health Check Interval
What should you consider when setting the health check interval?

A) Shorter intervals detect failures faster but add more overhead  
B) The interval doesn't matter  
C) Longer intervals are always better  
D) Health checks should run only once  

**Answer: A**

---

### Question 10: Traffic Analytics
What metrics are typically tracked in traffic analytics for load balancing?

A) Only the total number of requests  
B) Request count, error rate, response time, and traffic distribution  
C) Only error messages  
D) Only server IP addresses  

**Answer: B**

---

### Question 11: Circuit Breaker Threshold
What does the failure threshold in a circuit breaker determine?

A) The maximum number of requests allowed  
B) How many consecutive failures occur before the circuit opens  
C) The timeout duration  
D) The number of instances  

**Answer: B**

---

### Question 12: Failback
What is failback in failover systems?

A) Deleting the backup instance  
B) Returning traffic to the primary instance after it recovers  
C) Permanently switching to backup  
D) Stopping all services  

**Answer: B**

---

### Question 13: Load Balancer Overhead
What is a potential drawback of using a load balancer?

A) Load balancers eliminate all failures  
B) Load balancers add latency and complexity to the system  
C) Load balancers make systems slower always  
D) Load balancers cannot handle HTTP requests  

**Answer: B**

---

### Question 14: Sticky Sessions
What are sticky sessions (session persistence) in load balancing?

A) Sessions that never expire  
B) Routing requests from the same client to the same backend instance  
C) Sessions stored in a database  
D) Encrypted sessions  

**Answer: B**

---

### Question 15: Health Check Endpoint
What should a health check endpoint typically return?

A) The entire database  
B) A simple status indicator (e.g., 200 OK) and optionally health metrics  
C) User passwords  
D) Source code  

**Answer: B**

---

## Answer Key Summary

1. B - Distribute traffic for performance and availability  
2. C - Sequential rotation through instances  
3. B - CLOSED, OPEN, HALF_OPEN states  
4. B - Detect and remove unhealthy instances  
5. B - Higher weight receives more traffic  
6. B - Requests rejected immediately  
7. C - Selects instance with fewest connections  
8. B - Switch to backup on primary failure  
9. A - Shorter intervals = faster detection + more overhead  
10. B - Request count, error rate, response time, distribution  
11. B - Consecutive failures before opening  
12. B - Return to primary after recovery  
13. B - Adds latency and complexity  
14. B - Route same client to same instance  
15. B - Status indicator and health metrics  

---

**Total Questions: 15**  
**Topics Covered:** Load balancing fundamentals, Algorithms (Round-robin, Weighted, Least connections), Circuit breaker pattern, Health monitoring, Failover mechanisms, Traffic analytics, Session persistence

**Difficulty Level:** Beginner to Intermediate  
**Passing Score:** 80% (12/15 correct answers)
