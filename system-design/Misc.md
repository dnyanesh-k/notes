# What is DDoS(Distributed Denial of Service)?
- A DDoS attack uses multiple servers and Internet connections to flood the targeted resource. 
- DDoS attack where an attacker sends a large number of User Datagram Protocol (UDP) packets to a target port exploiting UDP’s connectionless nature.

## Attack Process
1. The attacker sends massive UDP packets with spoofed IP addresses to random ports on the target.
2. The target checks for active applications at those ports (usually none).
3. It responds with ICMP "Destination Unreachable" messages, overloading its own resources.


# Idempotency
In HTTP, a method is considered idempotent if the intended effect on the server is the same whether the request is made once or multiple times. 
The key to understanding why PUT is idempotent despite changing state lies in the difference between a state change and a cumulative effect.

1. ## State Change vs. Cumulative Effect
State Change (PUT): When you send a PUT request, you provide a complete replacement for a resource. If you send PUT /user/1 with {"status": "active"}, the server sets the status to "active." If you send that exact same request 10 more times, the status remains "active." The state changed from its original value once, but it does not change again with subsequent identical requests.
Cumulative Effect (Non-Idempotent): A non-idempotent operation like "increment counter by 1" (often implemented via POST or some PATCH instructions) changes the state every single time it is called. 
2. ## PUT vs. POST Analogy
- **PUT (Idempotent):** Like an "Elevator Call" button. Pressing it once requests the elevator. Pressing it five more times doesn't call five elevators; it just reinforces the same single request.
- **POST (Non-Idempotent):** Like a "Submit Order" button. If you press it five times without protections, the server might create five separate orders, each with a different ID. 
3. ## Comparison of Definitions

Term 	     Meaning	                                                        Is PUT...?
Safe	    Does not change the resource state at all (read-only).	    No (It modifies data)
Idempotent	Multiple identical requests have the same final effect as one.	Yes (Final state is consistent)

### HTTP Methods: Safety and Idempotency

| Method | Safe? | Idempotent? | Effect on Server State |
|--------|-------|-------------|----------------------|
| GET | Yes | Yes | Retrieves data without modification. |
| POST | No | No | Creates new resources or triggers cumulative actions (e.g., adding to a list). |
| PUT | No | Yes | Completely replaces a resource with the provided representation. |
| PATCH | No | No* | Applies partial modifications; idempotency depends on implementation logic. |
| DELETE | No | Yes | Ensures the specified resource no longer exists on the server. |
| HEAD | Yes | Yes | Identical to GET but only returns headers, no response body. |

**Note:** PATCH idempotency depends on implementation. If the patch operation is designed to be idempotent (e.g., "set field X to value Y"), it can be idempotent. If it performs cumulative operations (e.g., "increment counter"), it is not idempotent.

4. ## Implementation Requirement
According to RFC 9110 (the current HTTP standard), servers are required to implement PUT so that it is idempotent. This allows clients to safely retry a PUT request if a network error occurs, knowing that the retry won't accidentally create duplicate data or cause unintended side effects. 