# Java Full Stack — Interview Question Bank
> Questions only. Answers → WebJavaHelp/ day folders. Story hooks → ReadyChairs codebase.
> Format: Question | Material | ReadyChairs file to anchor the answer

---

## BLOCK 1 — Spring Boot Internals
> **Material:** Day 15 → `Spring Boot Internals.pdf` | Day 12 → `spring boot/`

1. How does Spring Boot auto-configuration work? What is `@SpringBootApplication` actually doing under the hood?
   - `ReadyChairsApplication.java`

2. What is the difference between `@SpringBootApplication`, `@EnableAutoConfiguration`, `@ComponentScan`, and `@Configuration`?

3. How does Spring Boot decide which beans to auto-configure? What is `spring.factories` / `AutoConfiguration.imports`?

4. What is the Spring Boot startup sequence — from `main()` to the first request being served?

5. What is `@Conditional`? Give a real example of when auto-configuration is conditionally applied.

6. How do you externalize configuration in Spring Boot? What is the property source priority order?
   - `application.properties` in `backend-readychairs/src/main/resources/`

---

## BLOCK 2 — Spring Core (IoC + DI + Bean Lifecycle)
> **Material:** Day 10 → `Spring/` | Day 11 → `readmes/`

7. What is Inversion of Control? How does the Spring IoC container implement it?

8. Constructor injection vs field injection vs setter injection — which do you prefer and why?
   - Any service class in ReadyChairs — all use constructor injection

9. What is the bean lifecycle? Walk through all stages from instantiation to destruction.
   - `AdminProvisioner.java` → `@PostConstruct` usage

10. What are bean scopes? When would you use `@Scope("prototype")` over singleton?

11. What is `@Primary` and `@Qualifier`? When do you need them?

12. What is `ApplicationContext` vs `BeanFactory`?

13. What is `@Lazy`? When should you use it?

---

## BLOCK 3 — Spring MVC + REST
> **Material:** Day 11 → `sequence.pdf` | Day 12 → `spring MVC flow.png` | Day 13 → `sequence.pdf` | Day 14 → `Advanced REST/`

14. Walk me through the full Spring MVC request lifecycle — from HTTP request to response.

15. What is `DispatcherServlet`? What role does it play?

16. What is the difference between `@Controller` and `@RestController`?

17. How do you handle global exceptions in Spring Boot? What is `@ControllerAdvice` and `@ExceptionHandler`?
    - `GlobalExceptionHandler.java` + every domain exception handler (`AuthExceptionHandler`, `BookingExceptionHandler`, etc.)

18. What is `ResponseEntity`? When do you use it vs just returning a POJO?
    - `ApiResponse.java`, `ApiResponseFactory.java`

19. What is the difference between `@RequestParam`, `@PathVariable`, `@RequestBody`?

20. How do you implement input validation in Spring Boot? What is `@Valid` and `@Validated`?

21. How do you handle API versioning in REST? Which strategy do you prefer?

22. What is idempotency? Which HTTP methods are idempotent and why does it matter?

23. What is `@CrossOrigin`? How do you handle CORS in a Spring Boot app?

---

## BLOCK 4 — Spring Security + JWT
> **Material:** Day 15 → `spring security/` | Day 15 → `filter-help/`

24. Explain the Spring Security filter chain. What is `SecurityFilterChain`?
    - `SecurityConfig.java`

25. How does JWT authentication work in Spring Boot? Walk through your implementation.
    - `JwtAuthenticationFilter.java` → `JwtUtil.java` → `JwtUserProvider.java` → `CurrentUserProvider.java`

26. What is `OncePerRequestFilter`? Why do we extend it for JWT validation?
    - `JwtAuthenticationFilter.java`

27. What is the difference between authentication and authorization in Spring Security?

28. How do you implement role-based access control (RBAC)?
    - `Role.java` (enum) → `SecurityConfig.java` → `@PreAuthorize` / `.hasRole()` in config

29. How do you store JWT — cookie vs localStorage? What are the security implications?
    - ReadyChairs uses HttpOnly cookies — explain why (XSS protection)

30. What is `UserDetails` and `UserDetailsService`? How does Spring Security use them?

31. What is password encoding in Spring Security? What is BCryptPasswordEncoder?

---

## BLOCK 5 — Spring Data JPA + Hibernate
> **Material:** Day 6-7 → `hibernate help/` | Day 9 → `Hibernate Session get vs load` | Day 12 → `Spring Data JPA/`

32. What is the N+1 problem? How do you detect and fix it?
    - `BookingRepository.java` or `BusinessStaffRepository.java` — any `@OneToMany` relationship

33. What is the difference between lazy and eager loading? When does `LazyInitializationException` occur?

34. What is `@OneToMany`, `@ManyToOne`, `@ManyToMany`? Explain `mappedBy` and `CascadeType`.

35. What is Hibernate dirty checking? How does it work under the hood?
    - Day 7 → `Automatic dirty checking.pdf`

36. What is the difference between `get()` and `load()` in Hibernate?
    - Day 9 → `Hibernate Session get vs load`

37. What is `@Version`? How does optimistic locking prevent lost updates?

38. What is the difference between `JPQL`, `Criteria API`, and native queries?

39. How do you write custom queries in Spring Data JPA? (`@Query`, derived method names, `@NamedQuery`)

40. What is `@Transactional`? Explain propagation levels — especially `REQUIRED` vs `REQUIRES_NEW`.
    - `BillingServiceImpl.java` or `BookingServiceImpl.java`

41. What are isolation levels? What read phenomena do they prevent (dirty read, non-repeatable read, phantom read)?

---

## BLOCK 6 — AOP
> **Material:** Day 14 → `AOP/`

42. What is AOP? What problems does it solve?

43. What is a join point, pointcut, advice, aspect, and weaving?

44. What is the difference between `@Before`, `@After`, `@Around`, `@AfterReturning`, `@AfterThrowing`?

45. How does Spring AOP work — proxy-based or bytecode weaving? What is the limitation of proxy-based AOP?

---

## BLOCK 7 — Database + SQL
> **Material:** Day 6-7 Hibernate covers ORM layer; SQL knowledge comes from project experience

46. What is an index? How does a B-tree index work? When does an index NOT get used?

47. What is the difference between clustered and non-clustered index?

48. Explain `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN` with examples.

49. What is a transaction? Explain ACID properties.

50. How do you optimize a slow query? What does `EXPLAIN ANALYZE` tell you?

51. What is connection pooling? What is HikariCP and why does Spring Boot use it by default?

52. When would you choose MongoDB over PostgreSQL?

---

## BLOCK 8 — React / Frontend
> **Material:** Your own Next.js experience from ReadyChairs frontend-web/

53. Explain `useState`, `useEffect`, `useRef`, `useMemo`, `useCallback` — when to use each.

54. What is the React rendering cycle? What causes unnecessary re-renders?

55. What is the difference between `React.memo`, `useMemo`, and `useCallback`?

56. Redux vs Context API — when do you use which?
    - ReadyChairs uses Redux — why did you choose it over Context?

57. What is Next.js SSR vs SSG vs ISR vs CSR? When do you pick each?
    - ReadyChairs Next.js pages — which pages use SSR, which use CSR?

58. What are React keys and why do they matter in lists?

59. What is prop drilling? How do you solve it?

---

## BLOCK 9 — System Design (Practical, Mapped to ReadyChairs)
> **Material:** `system-design-theory/answers/` — Q1–Q8, Q14, Q15

60. Design a booking system (this IS ReadyChairs — know this cold)
    - FR: book appointment, view availability, manage staff
    - Key deep dive: how do you prevent double booking? → `BookingConflictException.java`

61. Design a notification system
    - ReadyChairs has this: `notification/` module — email (SES), push (VAPID), WhatsApp, appointment reminders via scheduler

62. Design a job scheduler
    - ReadyChairs: `WeeklyInvoiceScheduler.java`, `AppointmentReminderScheduler.java`, `InvoiceReminderScheduler.java` — `@Scheduled`

63. Design a multi-tenant SaaS
    - VidyaTrack — row-level isolation with `institute_id` from JWT

64. Design a file upload system
    - ReadyChairs: `S3FileUploadService.java`, `BusinessVerificationDocumentService.java`

---

## BLOCK 10 — Behavioral Stories
> **Material:** `interview/behavioral.md` — update these stories for this role

65. Tell me about a complex feature you owned end to end.
    - **Story:** ReadyChairs booking engine — conflict detection, status state machine, notification on every transition

66. Tell me about a technical decision you made and defended.
    - **Story:** Chose Spring Boot over FastAPI for ReadyChairs because transactions + Spring Security handle booking integrity better than manual implementation

67. Tell me about a time you improved system reliability or performance.
    - **Story:** CitiusTech — automated Jira ticket creation, eliminated 48 hrs/day of manual effort, built eval framework to validate in production

68. Tell me about a challenge you faced in a project.
    - **Story:** Double-booking race condition in ReadyChairs — how you detected it and fixed it with conflict detection logic

---

## BLOCK 11 — Java Core Language
> **Material:** Java 8+ features — Streams, Optional, lambdas. Collections — HashMap internals. Concurrency — thread safety.
> These are asked in every Java interview regardless of role level.

69. How does `HashMap` work internally? What happens during `put()` — hash collision, load factor, rehashing?

70. What is the difference between `HashMap`, `LinkedHashMap`, `TreeMap`, and `ConcurrentHashMap`? When do you use each?

71. `ArrayList` vs `LinkedList` — time complexity of `add()`, `get()`, `remove()`. When does LinkedList actually win?

72. What is `HashSet` vs `TreeSet` vs `LinkedHashSet`? What contract must objects implement to work correctly in a `HashSet`?

73. Explain the `equals()` and `hashCode()` contract. What breaks if you override `equals()` but not `hashCode()`?

74. What are Java 8 Streams? Explain `map`, `filter`, `reduce`, `collect`, `flatMap` with examples.

75. What is the difference between `Stream.map()` and `Stream.flatMap()`?

76. What is `Optional`? Why was it introduced? How do you use `orElse` vs `orElseGet` vs `orElseThrow`?

77. What is a functional interface? Name four from `java.util.function` and what they do (`Function`, `Predicate`, `Consumer`, `Supplier`).

78. What is the difference between `Comparable` and `Comparator`? How do you sort a list of custom objects?

79. What is the difference between `==` and `.equals()` for Strings? What is the String pool?

80. What is `String`, `StringBuilder`, and `StringBuffer`? Why is `String` immutable and what are the performance implications?

81. What is autoboxing and unboxing? What is the performance risk of using `Integer` instead of `int` in a loop?

82. What are generics? What is type erasure? What is the difference between `List<?>`, `List<? extends T>`, and `List<? super T>`?

83. What is the difference between `synchronized`, `volatile`, and `AtomicInteger`?
    - When would you use each?

84. What is a `ThreadLocal`? When is it useful in a web application?
    - Spring uses `ThreadLocal` in `SecurityContextHolder` — each request thread has its own `SecurityContext`

85. What is the difference between `Callable` and `Runnable`? What does `Future` give you?

86. What is `ExecutorService`? What is the difference between `newFixedThreadPool`, `newCachedThreadPool`, and `newSingleThreadExecutor`?
    - Day 4 → `executor-framework/`

87. What is a `deadlock`? How do you detect and prevent it?

88. What is the difference between `final`, `finally`, and `finalize()`?

89. What is a `checked` vs `unchecked` exception? When should you use each?

90. What is Java reflection? What is one practical use case?

---

## BLOCK 12 — Design Patterns
> **Material:** `interview/design-patterns.md` — full answers with code are there
> This block is a checklist — know which category each pattern falls in and one Spring example

91. Explain Singleton. How does Spring implement it? What is the thread-safety issue in naive Singleton?
    - → `design-patterns.md` Pattern 1

92. Explain Factory Method. How do you use `Map<String, Bean>` injection in Spring to implement it cleanly?
    - → `design-patterns.md` Pattern 2

93. Explain Builder. When do you use it over a constructor? How does Lombok `@Builder` work?
    - → `design-patterns.md` Pattern 3

94. Explain Proxy. How does Spring AOP use proxies? What is the self-invocation problem with `@Transactional`?
    - → `design-patterns.md` Pattern 4

95. Explain Strategy. Give a Spring example (`PlatformTransactionManager`, `HttpMessageConverter`).
    - → `design-patterns.md` Pattern 7

96. Explain Observer. How does Spring `ApplicationEvent` implement it? Sync vs async listeners?
    - → `design-patterns.md` Pattern 8

97. Explain Template Method. How does `JdbcTemplate` use it?
    - → `design-patterns.md` Pattern 9

98. Explain Chain of Responsibility. How is Spring Security's filter chain an example?
    - → `design-patterns.md` Pattern 10

---

## BLOCK 13 — Testing
> **Material:** Your own test files in ReadyChairs if any. General JUnit 5 + Mockito knowledge.

99. What is the difference between unit testing and integration testing in Spring Boot?

100. What is `@SpringBootTest`? What does it do? When is it too heavy and what do you use instead?

101. What is `@WebMvcTest`? How do you test a controller in isolation?
     - Tests only the web layer — no service, no repository; mock everything below

102. What is `@DataJpaTest`? What does it configure?
     - Tests only JPA layer with an in-memory H2 database; no full Spring context

103. What is Mockito? What is the difference between `@Mock`, `@Spy`, `@InjectMocks`, and `@MockBean`?

104. What is `when().thenReturn()` vs `doReturn().when()`? When do you need the second form?

105. How do you verify that a method was called with `Mockito.verify()`?

106. What is `ArgumentCaptor`? When do you use it?

107. How do you test `@Async` methods? (Hint: they run in a different thread — `CompletableFuture.get()`)

108. What is `@Transactional` on a test class? What does it do?
     - Rolls back the database after every test — no manual cleanup needed

109. How do you test Spring Security — authenticated requests in `@WebMvcTest`?
     - `@WithMockUser`, `SecurityMockMvcRequestPostProcessors.jwt()`

---

## BLOCK 14 — Microservices (Conceptual)
> **Material:** Day 12 → `spring boot/` for Spring Boot foundation. Conceptual only — you don't need to have built these.
> The JD mentions microservices — know when to use them and what problems they solve.

110. What is the difference between a monolith and microservices? When would you choose monolith?
     - ReadyChairs is a modular monolith — domain modules (auth, booking, billing) in one deployable. This is the right choice for a small team.

111. What is service discovery? What problem does Eureka solve?
     - Services register themselves; clients find each other by name, not hardcoded IP

112. What is an API Gateway? What does it handle centrally?
     - Single entry point: routing, rate limiting, auth, load balancing, SSL termination

113. What is a Config Server? What problem does centralised config solve?
     - One place to manage `application.properties` for all services; supports `@RefreshScope`

114. What is circuit breaker pattern? What is Resilience4j?
     - Stops cascading failures: after N failures, open circuit, return fallback, try again after timeout

115. How do microservices communicate? REST vs messaging (Kafka/RabbitMQ) — when do you choose each?
     - REST: synchronous, request-response, simple. Kafka: async, decoupled, high throughput, event-driven

116. What is eventual consistency? How is it different from strong consistency?

117. What is the saga pattern? When do you need it?
     - Distributed transactions across services — each service does its part, compensating transaction on failure

118. What is the difference between horizontal and vertical scaling?

119. What is a load balancer? What is the difference between L4 and L7 load balancing?

---

## BLOCK 15 — Docker + Deployment
> **Material:** Your ReadyChairs AWS EC2 deployment experience. CitiusTech Docker/K8s experience.

120. What is Docker? What is the difference between an image and a container?
     - ReadyChairs: Dockerfile in backend-readychairs — describe what it does

121. What is a `Dockerfile`? Explain `FROM`, `COPY`, `RUN`, `EXPOSE`, `CMD` / `ENTRYPOINT`.

122. What is Docker Compose? When do you use it vs Kubernetes?
     - Local dev: Docker Compose (simple multi-container). Production: Kubernetes (orchestration, scaling, self-healing)

123. What is Kubernetes? What is a pod, deployment, service, and ingress?
     - CitiusTech: you worked with EKS — connect it here

124. How did you deploy ReadyChairs to AWS EC2?
     - **Story:** EC2 instance → Nginx reverse proxy → Spring Boot on port 8080 → Cloudflare in front for SSL and CDN

125. What is Nginx? Why is it in front of the Spring Boot app?
     - SSL termination, static file serving, reverse proxy, rate limiting at network level, load balancing across multiple app instances

126. What is the difference between blue-green deployment and rolling deployment?

127. What is GitHub Actions? How have you used CI/CD?
     - ReadyChairs `.github/` folder — describe the workflows if any

128. What is AWS S3? How do you upload and retrieve files from S3 in Spring Boot?
     - `S3FileUploadService.java`, `S3Config.java`, `S3Properties.java` in ReadyChairs

129. What is AWS SES? How did you integrate it?
     - `AwsSesService.java` in ReadyChairs auth module — email OTP sending

130. What is the difference between `RDS` and `EC2`-hosted database? Why did you choose one over the other for ReadyChairs?

---

## BLOCK 16 — Spring Advanced Features
> **Material:** Day 15 → `Spring Boot Internals.pdf` | Spring docs knowledge

131. What is Spring Boot Actuator? What endpoints does it expose?
     - `/actuator/health`, `/actuator/metrics`, `/actuator/info`, `/actuator/beans` — useful for K8s health checks

132. What is `@Async`? How do you enable it? What thread pool does it use by default?
     - ReadyChairs: `AppointmentReminderService.java` — async notification sending

133. What is `@Scheduled`? What are `fixedRate`, `fixedDelay`, and `cron`?
     - ReadyChairs: `WeeklyInvoiceScheduler.java` (`@Scheduled(cron = "0 0 0 * * MON")`), `InvoiceReminderScheduler.java`

134. What is Spring Cache? What is `@Cacheable`, `@CacheEvict`, `@CachePut`?
     - Cache method results; evict on data change; update cache on write

135. What is `@Profile`? How do you have different config for dev vs prod?
     - `application-dev.properties` vs `application-prod.properties`; `@Profile("prod")`

136. What is `@EventListener` vs `@TransactionalEventListener`? When does the event fire in each?
     - `@TransactionalEventListener` fires after transaction commits — useful for sending email only if the booking transaction succeeded

137. What is Flyway? How does it work? What happens if a migration fails?
     - ReadyChairs: `resources/db/migration/V1__...sql` files — Flyway runs pending migrations on startup; failed migration halts startup

138. What is Spring's `@Value` annotation? How does it differ from `@ConfigurationProperties`?
     - `@Value("${jwt.secret}")` for single values; `@ConfigurationProperties(prefix = "aws.s3")` for grouped config → `S3Properties.java`

---

## BLOCK 17 — SOLID Principles
> **Material:** No specific day folder — pure OOP knowledge. Anchor every principle to ReadyChairs code.
> Lead-level interviews always ask this — it signals whether you can mentor others on code quality.

139. What does SOLID stand for? Give one-line definition of each principle.

140. **S — Single Responsibility Principle.** What is it? How do you know when a class violates it?
     - ReadyChairs: `BookingServiceImpl` handles booking logic only — notification is in `NotificationService`, billing in `BillingService`. Each class has one reason to change.
     - Violation example: a `UserService` that handles registration + email sending + PDF generation + audit logging — too many reasons to change.

141. **O — Open/Closed Principle.** What is it? Give a Spring example.
     - Open for extension, closed for modification.
     - ReadyChairs: `NotificationSender` interface with `EmailSender`, `PushSender`, `WhatsAppSender`. Adding a new channel = new class, zero changes to existing code.
     - Violation: adding a new notification type requires modifying an if-else chain in `NotificationService`.

142. **L — Liskov Substitution Principle.** What is it? What breaks when it's violated?
     - Any subclass must be substitutable for its parent without changing program correctness.
     - Classic violation: `Square extends Rectangle` — setting width on a Square changes both width and height (to maintain square constraint), breaking `Rectangle` behavior. Code expecting a `Rectangle` breaks when handed a `Square`.

143. **I — Interface Segregation Principle.** What is it? When is an interface "fat"?
     - Clients should not be forced to depend on methods they don't use.
     - Fat interface violation: `UserRepository extends JpaRepository` forced to implement 20 methods, but your class only needs `findByEmail()`. Fix: define a narrow custom interface.
     - ReadyChairs: `BillingService` interface exposes only billing methods — not mixed with booking or notification methods.

144. **D — Dependency Inversion Principle.** What is it? How does Spring enforce it?
     - High-level modules should not depend on low-level modules. Both should depend on abstractions.
     - `BookingServiceImpl` depends on `BookingRepository` interface, not on `BookingRepositoryImpl`. Spring injects the implementation — the service never knows the concrete class.
     - This is the entire premise of Spring DI — coding to interfaces.

145. How do SOLID principles relate to testability?
     - SRP → small classes are easy to test in isolation.
     - DIP → you can mock the interface and inject the mock, so tests don't need a real database.
     - OCP → new behaviour added via new class = you test the new class, existing tests unchanged.

146. Give an example of a SOLID violation in real code and how you refactored it.
     - **Story:** A service class doing too many things — split into focused services. Or a God Object that was hard to test — extracted interfaces and injected dependencies.

---

## BLOCK 18 — Git Workflow
> **Material:** Your own ReadyChairs git history (161 commits, 15 PRs). Practical experience.

147. What is the difference between `git merge` and `git rebase`? When do you use each?
     - Merge: preserves history, creates a merge commit — good for integrating feature branches into main.
     - Rebase: rewrites history, replays your commits on top of another branch — good for cleaning up feature branch before merging, keeping linear history. Never rebase shared/public branches.

148. What is `git cherry-pick`? When would you use it?
     - Apply a specific commit from another branch without merging the whole branch. Useful for hotfixes — cherry-pick the fix from main into a release branch.

149. What is `git stash`? When is it useful?
     - Temporarily saves uncommitted changes without committing. Useful when you need to switch branches mid-work without losing your changes.

150. What is the difference between `git reset`, `git revert`, and `git restore`?
     - `reset`: moves HEAD backward, can discard commits (use with caution on shared branches).
     - `revert`: creates a new commit that undoes a previous commit — safe for shared branches, history is preserved.
     - `restore`: discards uncommitted changes in working directory.

151. What is a branching strategy? Explain Git Flow vs trunk-based development.
     - Git Flow: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` branches — structured, good for release-cycle products.
     - Trunk-based: all developers commit to `main` frequently (with feature flags for incomplete features) — faster, requires strong CI/CD. ReadyChairs likely used a simpler feature-branch model.

152. How do you resolve a merge conflict? Walk through it step by step.
     - `git pull origin main` → conflict markers appear in file → open file, decide which version to keep → `git add <file>` → `git commit`. In IDE: use the 3-way merge editor.

153. What is `.gitignore`? What should always be in it for a Spring Boot + Next.js project?
     - ReadyChairs `.gitignore` — `.env`, `target/`, `node_modules/`, `*.class`, `application-prod.properties`

154. What is a Pull Request? What do you look for in a code review?
     - **As reviewer:** correctness, edge cases, tests, naming, SOLID violations, security (SQL injection, hardcoded secrets), performance (N+1 queries, missing indexes), readability.
     - ReadyChairs has 15 open PRs — you've been doing this.

155. What is `git bisect`? When is it useful?
     - Binary search through git history to find which commit introduced a bug. Run `git bisect start`, mark good/bad commits, git checks out midpoints until it finds the culprit.

156. What is the difference between `git fetch` and `git pull`?
     - `fetch`: downloads changes from remote but does NOT merge. Safe — lets you inspect before merging.
     - `pull`: fetch + merge in one step. Convenient but merges immediately.

157. How do you squash commits before merging a PR?
     - `git rebase -i HEAD~N` → change `pick` to `squash` for commits to combine → edit the combined commit message. Keeps the main branch history clean.

---

## BLOCK 19 — TypeScript
> **Material:** ReadyChairs `frontend-web/` — 73.4% TypeScript. Your own codebase is the material.

158. What is TypeScript? Why use it over plain JavaScript?
     - TypeScript is a statically typed superset of JavaScript. Catches type errors at compile time, not at runtime. Enables better IDE support (autocomplete, refactoring). Scales better in large codebases.

159. What is the difference between `interface` and `type` in TypeScript?
     - `interface`: can be extended with `extends`, can be merged (declaration merging — two `interface User` declarations merge into one). Best for object shapes.
     - `type`: more flexible — can represent unions, intersections, primitives, tuples. Cannot be merged.
     - In practice: use `interface` for object shapes (React props, API responses), `type` for unions and utility types.

160. What are union types and intersection types?
     ```typescript
     // Union — one OR the other
     type Status = "pending" | "confirmed" | "cancelled";
     type StringOrNumber = string | number;

     // Intersection — both at once
     type AdminUser = User & { adminRole: string };
     ```

161. What is `any` vs `unknown` vs `never` in TypeScript?
     - `any`: opt-out of type checking — dangerous, avoid in production code.
     - `unknown`: type-safe alternative to `any` — must narrow (check) the type before using it.
     - `never`: a value that never occurs — a function that always throws, or an exhaustive switch default case.

162. What are generics in TypeScript? Give an example.
     ```typescript
     // Without generics — loses type info
     function getFirst(arr: any[]): any { return arr[0]; }

     // With generics — preserves type
     function getFirst<T>(arr: T[]): T { return arr[0]; }

     const first = getFirst([1, 2, 3]);   // TypeScript knows: first is number
     const name  = getFirst(["a", "b"]);  // TypeScript knows: name is string
     ```

163. What are utility types? Explain `Partial`, `Required`, `Pick`, `Omit`, `Record`, `Readonly`.
     ```typescript
     interface User { id: number; name: string; email: string; }

     Partial<User>          // all fields optional
     Required<User>         // all fields required (removes ?)
     Pick<User, "id"|"name"> // only id and name
     Omit<User, "email">    // everything except email
     Record<string, number>  // { [key: string]: number }
     Readonly<User>          // cannot modify any field after creation
     ```

164. What is `keyof` and `typeof` in TypeScript?
     ```typescript
     type UserKeys = keyof User;  // "id" | "name" | "email"

     const config = { apiUrl: "https://api.example.com", timeout: 5000 };
     type Config = typeof config;  // { apiUrl: string; timeout: number }
     ```

165. What are React prop types in TypeScript? How do you type a component?
     ```typescript
     interface BookingCardProps {
       booking: Booking;
       onCancel: (id: number) => void;
       isLoading?: boolean;  // optional
     }

     const BookingCard: React.FC<BookingCardProps> = ({ booking, onCancel, isLoading = false }) => {
       return <div>{booking.id}</div>;
     };
     ```

166. How do you type `useState` and `useRef` in TypeScript?
     ```typescript
     const [booking, setBooking] = useState<Booking | null>(null);
     const [count, setCount] = useState(0);  // inferred as number

     const inputRef = useRef<HTMLInputElement>(null);
     ```

167. What is `as` (type assertion) in TypeScript? When should you use it and when should you avoid it?
     - Use: when you know more than TypeScript — `document.getElementById("form") as HTMLFormElement`.
     - Avoid: using `as` to silence type errors you haven't actually resolved — this is the same as `any`, it just hides the problem.

168. What is the difference between `null` and `undefined` in TypeScript? What is strict null checking?
     - With `strictNullChecks: true` (default in strict mode): `null` and `undefined` are not assignable to other types unless explicitly declared. Forces you to handle the null case. Without it, `null` can be assigned to anything — JavaScript's biggest footgun.

169. What is an `enum` in TypeScript? How is it different from a string union type?
     ```typescript
     // Enum
     enum BookingStatus { PENDING = "PENDING", CONFIRMED = "CONFIRMED" }

     // String union (preferred in most cases)
     type BookingStatus = "PENDING" | "CONFIRMED" | "CANCELLED";
     ```
     - String unions are preferred: simpler, tree-shakeable, no runtime overhead. Enums generate extra JavaScript.

---

## QUICK REVISION ORDER (Days Before Interview)

```
Day -5:  Block 11 (Java Core) + Block 17 (SOLID)                 → Pure recall — no material needed
Day -4:  Block 18 (Git) + Block 19 (TypeScript)                  → ReadyChairs repo + frontend-web/
Day -3:  Block 1 (Spring Boot Internals) + Block 2 (IoC/DI)      → Day 15 PDF + Day 10 material
Day -2:  Block 3 (MVC/REST) + Block 4 (Security/JWT)             → Day 13, 14, 15 material
Day -1:  Block 5 (JPA/Hibernate) + Block 12 (Design Patterns)    → Day 6, 7, 12 + design-patterns.md
Day 0:   Block 7 (SQL) + Block 9 (System Design) + Block 10      → ReadyChairs cold walk-through + stories
Buffer:  Block 6 (AOP) + Block 13 (Testing) + Block 14–16        → If time permits
```
