# Design Patterns — Java / Spring Boot Interview Guide

> Interview-ready answers. Each pattern: Problem → Structure → Java Code → Where Spring uses it → Interview Q&A.
> Anchor every answer to ReadyChairs or your CDAC / enterprise Java knowledge.

---

## How To Speak About Patterns In An Interview

Never just define a pattern. The interviewer already knows the definition. The winning answer has three parts:

1. **Problem first** — "The problem this solves is..."
2. **Structure** — "The way it works is..."
3. **Real usage** — "In ReadyChairs / Spring, I've seen this in..."

If you can't say step 3, you don't own the pattern yet.

---

# PART 1 — CREATIONAL PATTERNS

> Creational patterns deal with **how objects are created**. The goal is to decouple the code that uses an object from the code that creates it.

---

## Pattern 1: Singleton

### Problem It Solves

You need exactly one instance of a class shared across the entire application — a database connection pool, a configuration object, a thread pool manager. If every class creates its own instance, you waste resources and get inconsistent state.

The naive approach is to use a static field. The danger is thread safety: if two threads call `getInstance()` simultaneously before the instance is created, they can both create a new object, breaking the "exactly one" guarantee.

### Structure

```java
public class DatabaseConnectionPool {
    
    // volatile ensures the write to instance is visible to all threads
    private static volatile DatabaseConnectionPool instance;
    
    private final List<Connection> pool = new ArrayList<>();
    
    // Private constructor — no one can call new DatabaseConnectionPool()
    private DatabaseConnectionPool() {
        initializePool();
    }
    
    // Double-checked locking — thread-safe and efficient after first creation
    public static DatabaseConnectionPool getInstance() {
        if (instance == null) {                      // First check (no lock)
            synchronized (DatabaseConnectionPool.class) {
                if (instance == null) {              // Second check (with lock)
                    instance = new DatabaseConnectionPool();
                }
            }
        }
        return instance;
    }
    
    private void initializePool() {
        // initialise connections
    }
}
```

**Why double-checked locking?**

Without it: `synchronized` on every `getInstance()` call is slow because 99.99% of calls happen after the instance already exists — you're locking unnecessarily.

With it: the first `if (instance == null)` without lock handles the common case (already created). Only the first few nanoseconds of startup ever hit the `synchronized` block.

**Why `volatile`?**

Without `volatile`, the CPU can reorder instructions. The JVM might write the reference to `instance` before the constructor has fully finished running. Another thread sees a non-null `instance` and uses a half-constructed object. `volatile` prevents this reordering.

### How Spring Implements Singleton

Spring beans are Singleton by default — the IoC container creates one instance per `ApplicationContext` and returns the same object every time `getBean()` or `@Autowired` is used. You never write the Singleton pattern yourself in Spring; the container does it.

```java
// Spring manages the singleton lifecycle
@Service  // scope = singleton by default
public class BookingService {
    // This exact instance is injected everywhere BookingService is needed
}

// When you need a new instance per request:
@Service
@Scope("prototype")  // new instance every time it's requested
public class ReportGenerator { }
```

**What happens under the hood:**

```
ApplicationContext startup
  → Scans @Component / @Service / @Repository / @Bean
  → For each singleton bean: calls constructor once
  → Stores in a ConcurrentHashMap<String, Object> (the bean registry)
  → On every @Autowired injection: returns the same object from the map
```

### ReadyChairs Connection

Every `@Service` in ReadyChairs is a Spring-managed singleton — `BookingServiceImpl`, `AuthServiceImpl`, `BillingServiceImpl`. You didn't write any Singleton boilerplate; Spring handled it.

`AdminProvisioner` uses `@PostConstruct` which runs once after the singleton bean is created — seeding the admin user exactly once at startup.

### Interview Questions

**Q: Is Spring's singleton the same as the GoF Singleton pattern?**

No. GoF Singleton is one instance per JVM (JVM-level). Spring Singleton is one instance per `ApplicationContext`. If you create two `ApplicationContext` instances (rare but possible in tests), you'd have two instances of the same bean. This distinction matters in large applications that create child contexts.

**Q: When would you NOT use singleton scope?**

When the bean holds state that changes per request — e.g., a `UserSession` object holding the current user's data. Making that singleton means user A's data leaks into user B's request. Use `@Scope("request")` for web-request-scoped beans.

**Q: What is the problem with Singleton + mutable state?**

```java
@Service  // singleton — one shared instance
public class CounterService {
    private int count = 0;  // DANGER: shared mutable state
    
    public void increment() { count++; }  // NOT thread-safe
    public int getCount() { return count; }
}
```

100 concurrent requests hit `increment()` simultaneously. `count++` is not atomic — it's read-compute-write. You lose increments. Fix: use `AtomicInteger`, `synchronized`, or avoid mutable state in singletons entirely.

---

## Pattern 2: Factory Method

### Problem It Solves

You want to create objects but don't want the calling code to know which concrete class to instantiate. The type of object needed might depend on runtime conditions — a config value, user role, or request parameter.

Without a factory, the caller has an `if-else` chain wherever objects are created. When you add a new type, you modify every caller. Factory centralises creation in one place.

### Structure

```java
// Abstract product
public interface NotificationSender {
    void send(String recipient, String message);
}

// Concrete products
@Component("EMAIL")
public class EmailSender implements NotificationSender {
    @Override
    public void send(String recipient, String message) {
        // AWS SES logic
        System.out.println("Sending email to " + recipient);
    }
}

@Component("SMS")
public class SmsSender implements NotificationSender {
    @Override
    public void send(String recipient, String message) {
        // Twilio logic
        System.out.println("Sending SMS to " + recipient);
    }
}

@Component("PUSH")
public class PushSender implements NotificationSender {
    @Override
    public void send(String recipient, String message) {
        // VAPID web push logic
    }
}

// Factory — knows which concrete type to return
@Service
public class NotificationSenderFactory {
    
    private final Map<String, NotificationSender> senders;
    
    // Spring injects all NotificationSender beans keyed by their bean name
    public NotificationSenderFactory(Map<String, NotificationSender> senders) {
        this.senders = senders;
    }
    
    public NotificationSender getSender(String type) {
        NotificationSender sender = senders.get(type.toUpperCase());
        if (sender == null) {
            throw new IllegalArgumentException("Unknown notification type: " + type);
        }
        return sender;
    }
}

// Caller — knows nothing about EmailSender, SmsSender, PushSender
@Service
public class NotificationService {
    
    private final NotificationSenderFactory factory;
    
    public NotificationService(NotificationSenderFactory factory) {
        this.factory = factory;
    }
    
    public void notify(String type, String recipient, String message) {
        factory.getSender(type).send(recipient, message);
        // Adding a new WhatsAppSender requires zero changes here
    }
}
```

**Why this is better than if-else:**

```java
// BAD — every time you add a new type, this method must change
public void notify(String type, String recipient, String message) {
    if ("EMAIL".equals(type)) {
        new EmailSender().send(recipient, message);
    } else if ("SMS".equals(type)) {
        new SmsSender().send(recipient, message);
    }
    // Adding WhatsApp? Must come here and modify this method.
}
```

Open/Closed Principle: the Factory is **open for extension** (add a new `@Component` implementation) but **closed for modification** (no existing code changes).

### How Spring Uses Factory Pattern

`BeanFactory` is Spring's core factory — it creates and manages beans. `ApplicationContext` extends `BeanFactory` and adds more features.

`FactoryBean<T>` is Spring's way of letting you plug in custom creation logic:

```java
@Component
public class DataSourceFactory implements FactoryBean<DataSource> {
    
    @Override
    public DataSource getObject() {
        // Custom creation: pick different DataSource based on environment
        if (isProduction()) {
            return createHikariPool();
        } else {
            return createH2InMemory();
        }
    }
    
    @Override
    public Class<?> getObjectType() { return DataSource.class; }
}
```

### ReadyChairs Connection

`NotificationService` in ReadyChairs sends email (SES), push (VAPID), and WhatsApp notifications. Rather than if-else chains, the factory pattern with Spring's `Map<String, NotificationSender>` injection cleanly routes to the right sender. `BookingNotificationService` acts as the orchestrator that calls the factory.

### Interview Questions

**Q: What is the difference between Factory Method and Abstract Factory?**

Factory Method: one factory, one product type. You have a `NotificationSenderFactory` that creates `NotificationSender` objects.

Abstract Factory: a factory of factories. You have a `UIComponentFactory` that creates families of related objects together — `WindowsButton` + `WindowsCheckbox` vs `MacButton` + `MacCheckbox`. The key is that the products are related and must be used together.

**Q: Why use `Map<String, NotificationSender>` injection in Spring instead of a switch statement?**

With a switch: you must modify `NotificationService` every time you add a new channel. With Map injection: you add a new `@Component("WHATSAPP")` class, Spring automatically includes it in the map, and the factory picks it up without any modification to the factory or the service. This is the Open/Closed Principle in action.

---

## Pattern 3: Builder

### Problem It Solves

A class has many optional fields. Using a constructor with all parameters is unreadable — which argument is which? Using multiple constructors (telescoping constructor anti-pattern) causes confusion. Builder separates the step-by-step construction of a complex object from its representation.

```java
// Telescoping constructor anti-pattern — which boolean is which?
Booking booking = new Booking(user, salon, staff, service, startTime, endTime, true, false, "NOTE");

// Builder — self-documenting
Booking booking = Booking.builder()
    .user(user)
    .salon(salon)
    .staff(staff)
    .service(service)
    .startTime(startTime)
    .endTime(endTime)
    .confirmed(true)
    .cancelled(false)
    .note("NOTE")
    .build();
```

### Structure (Manual Builder)

```java
public class BookingRequest {
    
    // Required
    private final Long userId;
    private final Long salonId;
    private final LocalDateTime startTime;
    
    // Optional
    private final Long staffId;
    private final String note;
    private final boolean sendReminder;
    
    private BookingRequest(Builder builder) {
        this.userId = builder.userId;
        this.salonId = builder.salonId;
        this.startTime = builder.startTime;
        this.staffId = builder.staffId;
        this.note = builder.note;
        this.sendReminder = builder.sendReminder;
    }
    
    public static class Builder {
        // Required — set via constructor
        private final Long userId;
        private final Long salonId;
        private final LocalDateTime startTime;
        
        // Optional — default values
        private Long staffId = null;
        private String note = "";
        private boolean sendReminder = true;
        
        public Builder(Long userId, Long salonId, LocalDateTime startTime) {
            this.userId = userId;
            this.salonId = salonId;
            this.startTime = startTime;
        }
        
        public Builder staffId(Long staffId) {
            this.staffId = staffId;
            return this;  // returns this for method chaining
        }
        
        public Builder note(String note) {
            this.note = note;
            return this;
        }
        
        public Builder sendReminder(boolean sendReminder) {
            this.sendReminder = sendReminder;
            return this;
        }
        
        public BookingRequest build() {
            // Validation before construction
            if (userId == null || salonId == null || startTime == null) {
                throw new IllegalStateException("userId, salonId, startTime are required");
            }
            return new BookingRequest(this);
        }
    }
}

// Usage
BookingRequest request = new BookingRequest.Builder(userId, salonId, startTime)
    .staffId(staffId)
    .note("Window seat preferred")
    .sendReminder(true)
    .build();
```

### Lombok @Builder (How You'd Actually Write It)

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BookingRequest {
    private Long userId;
    private Long salonId;
    private LocalDateTime startTime;
    
    @Builder.Default
    private boolean sendReminder = true;  // default value
    
    private Long staffId;
    private String note;
}

// Lombok generates the builder automatically
BookingRequest request = BookingRequest.builder()
    .userId(1L)
    .salonId(5L)
    .startTime(LocalDateTime.now().plusHours(2))
    .build();
```

### How Spring Uses Builder

`UriComponentsBuilder` for building URLs:
```java
URI uri = UriComponentsBuilder.newInstance()
    .scheme("https")
    .host("api.readychairs.com")
    .path("/v1/bookings/{id}")
    .queryParam("includeStaff", true)
    .buildAndExpand(bookingId)
    .toUri();
```

`MockMvcRequestBuilders` in tests, `ResponseEntity.ok().body(...)` — the fluent builder pattern throughout Spring.

### Interview Questions

**Q: Why make the object immutable in Builder (private final fields, no setters)?**

Once a `BookingRequest` is built, it should not change — the booking logic uses it to create a booking record. If it were mutable, a bug could modify the request mid-flow and create a booking with wrong data. Immutability makes the object safe to share across threads and easy to reason about.

**Q: What is the difference between Builder and Factory?**

Factory creates an object of a specific type based on runtime conditions — you ask for a `NotificationSender` and the factory decides whether you get `EmailSender` or `SmsSender`.

Builder constructs a single complex object step by step with many optional configurations — you know you want a `BookingRequest`, you just have many optional fields to set.

---

# PART 2 — STRUCTURAL PATTERNS

> Structural patterns deal with **how classes and objects are composed** to form larger structures.

---

## Pattern 4: Proxy

### Problem It Solves

You want to add behaviour (logging, access control, caching, transaction management) to an existing object without changing its code. The proxy wraps the original object and intercepts calls.

This is the most important pattern to know for Spring, because Spring AOP, `@Transactional`, Spring Security, and Spring Data JPA lazy loading all use proxies under the hood.

### Structure

```java
// Real object
public interface BookingService {
    Booking createBooking(CreateBookingDTO dto);
    Booking getBooking(Long id);
}

@Service
public class BookingServiceImpl implements BookingService {
    @Override
    public Booking createBooking(CreateBookingDTO dto) {
        // actual booking logic
        return bookingRepository.save(new Booking(dto));
    }
    
    @Override
    public Booking getBooking(Long id) {
        return bookingRepository.findById(id).orElseThrow();
    }
}

// Proxy — adds logging without touching BookingServiceImpl
public class BookingServiceLoggingProxy implements BookingService {
    
    private final BookingService real;  // wraps the real object
    
    public BookingServiceLoggingProxy(BookingService real) {
        this.real = real;
    }
    
    @Override
    public Booking createBooking(CreateBookingDTO dto) {
        long start = System.currentTimeMillis();
        try {
            Booking result = real.createBooking(dto);  // delegate to real object
            log.info("createBooking took {}ms", System.currentTimeMillis() - start);
            return result;
        } catch (Exception e) {
            log.error("createBooking failed: {}", e.getMessage());
            throw e;
        }
    }
    
    @Override
    public Booking getBooking(Long id) {
        return real.getBooking(id);
    }
}
```

### How Spring AOP Uses Proxy

When you add `@Transactional` to a method, Spring does NOT modify your class. At startup, Spring creates a **proxy object** that wraps your bean. The proxy intercepts method calls, starts a transaction, calls your actual method, then commits or rolls back.

```java
@Service
public class BookingServiceImpl implements BookingService {
    
    @Transactional  // Spring wraps this bean in a proxy
    public Booking createBooking(CreateBookingDTO dto) {
        // Your actual code — no transaction management here
        Booking booking = bookingRepository.save(...);
        notificationService.sendConfirmation(booking);  // if this throws, transaction rolls back
        return booking;
    }
}
```

**What Spring generates (conceptually):**

```java
// Spring creates this proxy at runtime — you never write this
public class BookingServiceProxy extends BookingServiceImpl {
    
    private final PlatformTransactionManager txManager;
    
    @Override
    public Booking createBooking(CreateBookingDTO dto) {
        TransactionStatus tx = txManager.getTransaction(new DefaultTransactionDefinition());
        try {
            Booking result = super.createBooking(dto);  // call actual method
            txManager.commit(tx);
            return result;
        } catch (RuntimeException e) {
            txManager.rollback(tx);
            throw e;
        }
    }
}
```

**Two proxy mechanisms Spring uses:**

```
JDK Dynamic Proxy:
  - Works when the bean implements an interface
  - Creates a proxy that implements the same interface
  - BookingService interface → BookingServiceImpl bean → Spring creates a JDK proxy
  - Reflection-based, slightly slower

CGLIB Proxy:
  - Works when the bean does NOT implement an interface (or for Spring Boot default)
  - Creates a subclass of your concrete class
  - Cannot proxy final classes or final methods (subclass cannot override final)
  - Spring Boot 2+ uses CGLIB by default
```

### The Self-Invocation Problem (Critical Interview Trap)

```java
@Service
public class BookingServiceImpl implements BookingService {
    
    @Transactional
    public void createBookingWithNotification(CreateBookingDTO dto) {
        createBooking(dto);  // calls THIS method directly, NOT through proxy
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public Booking createBooking(CreateBookingDTO dto) {
        // This @Transactional is IGNORED when called from createBookingWithNotification!
        return bookingRepository.save(...);
    }
}
```

When `createBookingWithNotification` calls `createBooking` directly, it bypasses the proxy. The proxy only intercepts calls from outside the bean. This is one of the most common `@Transactional` bugs.

**Fix:** Inject the bean into itself (Spring handles circular dependency) or extract to a separate service.

### ReadyChairs Connection

Every `@Transactional` method in ReadyChairs (`BillingServiceImpl`, `BookingServiceImpl`) is actually executed through a Spring CGLIB proxy. The proxy adds transaction management around your business logic. `JwtAuthenticationFilter` is a Proxy in the security chain — it intercepts every request and validates the JWT before passing control to the actual handler.

### Interview Questions

**Q: What is the difference between Proxy and Decorator pattern?**

Both wrap an object, but intent differs. Proxy controls access to the real object (security check, transaction, caching — the caller doesn't know they're not talking directly to the object). Decorator adds behaviour and the caller often creates the decorator chain explicitly (Java I/O: `new BufferedReader(new FileReader(file))` — you intentionally wrap for extra functionality).

**Q: Why can't Spring proxy a final class or final method?**

CGLIB creates a subclass to proxy. Final classes can't be subclassed, final methods can't be overridden. If you mark your `@Service` class as `final`, Spring will either throw an error or the proxy won't intercept the method. Practical rule: never mark Spring beans final.

**Q: What does `@Transactional` actually do step by step?**

1. Spring creates a CGLIB proxy of your service class at startup
2. When any code calls `createBooking()`, it hits the proxy, not your class
3. Proxy: calls `TransactionManager.getTransaction()` → opens a DB connection, begins transaction
4. Proxy: calls your actual `createBooking()` method
5. If no exception: proxy calls `transactionManager.commit()`
6. If `RuntimeException` or `Error` (by default): proxy calls `transactionManager.rollback()`
7. Proxy returns the result to the caller

---

## Pattern 5: Decorator

### Problem It Solves

You want to add responsibilities to an object dynamically at runtime, without changing the object's class. You can stack multiple decorators on top of each other, each adding a layer of behaviour.

The classic example is Java I/O — every reader/writer wraps another, adding buffering, charset conversion, compression, etc.

### Structure

```java
// Component interface
public interface TextProcessor {
    String process(String text);
}

// Concrete component
public class PlainTextProcessor implements TextProcessor {
    @Override
    public String process(String text) {
        return text;
    }
}

// Base Decorator
public abstract class TextProcessorDecorator implements TextProcessor {
    protected final TextProcessor wrapped;
    
    public TextProcessorDecorator(TextProcessor wrapped) {
        this.wrapped = wrapped;
    }
}

// Concrete Decorators
public class TrimDecorator extends TextProcessorDecorator {
    public TrimDecorator(TextProcessor wrapped) { super(wrapped); }
    
    @Override
    public String process(String text) {
        return wrapped.process(text).trim();  // add trim behaviour
    }
}

public class UpperCaseDecorator extends TextProcessorDecorator {
    public UpperCaseDecorator(TextProcessor wrapped) { super(wrapped); }
    
    @Override
    public String process(String text) {
        return wrapped.process(text).toUpperCase();  // add uppercase behaviour
    }
}

public class ProfanityFilterDecorator extends TextProcessorDecorator {
    public ProfanityFilterDecorator(TextProcessor wrapped) { super(wrapped); }
    
    @Override
    public String process(String text) {
        return wrapped.process(text).replace("badword", "***");
    }
}

// Stack decorators at runtime
TextProcessor processor = new ProfanityFilterDecorator(
    new TrimDecorator(
        new UpperCaseDecorator(
            new PlainTextProcessor()
        )
    )
);

processor.process("  hello badword  "); // → "HELLO ***"
```

### Java I/O — The Classic Example

```java
// Reading a gzipped, UTF-8 encoded file with buffering
BufferedReader reader = new BufferedReader(          // adds buffering
    new InputStreamReader(                           // adds charset conversion
        new GZIPInputStream(                         // adds decompression
            new FileInputStream("data.gz")           // raw bytes from disk
        ),
        StandardCharsets.UTF_8
    )
);
```

Each class wraps the one inside, adding one responsibility. You compose the behaviour you need at the point of use.

### Interview Questions

**Q: Decorator vs Proxy — again, key distinction?**

In Proxy: the proxy controls access. The client doesn't choose the proxy — Spring creates it transparently. The proxy replaces the original object from the client's perspective.

In Decorator: the client deliberately assembles the chain. `new BufferedReader(new FileReader(...))` — you chose to add buffering. Decorator adds new behaviour; Proxy controls existing behaviour.

---

## Pattern 6: Facade

### Problem It Solves

A subsystem has many complex classes and the caller must coordinate multiple objects to accomplish a task. Facade provides a single simplified interface that hides the complexity.

The service layer in a Spring Boot application IS the Facade pattern.

### Structure

```java
// Complex subsystem classes
@Repository public class BookingRepository { /* complex JPA */ }
@Repository public class StaffRepository { /* availability queries */ }
@Service    public class NotificationService { /* email + push + WhatsApp */ }
@Service    public class BillingService { /* invoice generation */ }

// Facade — single interface hiding all coordination
@Service
public class BookingFacade {
    
    private final BookingRepository bookingRepo;
    private final StaffRepository staffRepo;
    private final NotificationService notifications;
    private final BillingService billing;
    
    public BookingConfirmation confirmBooking(CreateBookingDTO dto) {
        // Coordinate the subsystem — caller doesn't know about this complexity
        Staff staff = staffRepo.findAvailable(dto.getStaffId(), dto.getStartTime());
        Booking booking = bookingRepo.save(new Booking(dto, staff));
        notifications.sendConfirmation(booking);
        Invoice invoice = billing.generateDraft(booking);
        
        return new BookingConfirmation(booking, invoice);
    }
}

// Controller — only knows about the Facade
@RestController
public class BookingController {
    private final BookingFacade bookingFacade;
    
    @PostMapping("/bookings")
    public ResponseEntity<BookingConfirmation> create(@Valid @RequestBody CreateBookingDTO dto) {
        return ResponseEntity.ok(bookingFacade.confirmBooking(dto));
    }
}
```

### ReadyChairs Connection

`BookingController` calls `BookingServiceImpl` — the service IS the facade. It coordinates `BookingRepository`, `NotificationService`, staff availability checks, and status updates. The controller knows nothing about these details.

---

# PART 3 — BEHAVIORAL PATTERNS

> Behavioral patterns deal with **how objects communicate and distribute responsibilities**.

---

## Pattern 7: Strategy

### Problem It Solves

You have an algorithm that can vary — sorting, payment processing, discount calculation, notification delivery. Instead of if-else switching on type, you define a family of algorithms, encapsulate each as a class, and make them interchangeable.

### Structure

```java
// Strategy interface
public interface PaymentStrategy {
    PaymentResult process(PaymentRequest request);
    String getType();
}

// Concrete strategies
@Component
public class CreditCardStrategy implements PaymentStrategy {
    @Override
    public PaymentResult process(PaymentRequest request) {
        // Stripe integration
        return stripeClient.charge(request.getAmount(), request.getCardToken());
    }
    @Override public String getType() { return "CREDIT_CARD"; }
}

@Component
public class UpiStrategy implements PaymentStrategy {
    @Override
    public PaymentResult process(PaymentRequest request) {
        // Razorpay UPI integration
        return razorpay.createUpiPayment(request.getAmount(), request.getUpiId());
    }
    @Override public String getType() { return "UPI"; }
}

@Component
public class WalletStrategy implements PaymentStrategy {
    @Override
    public PaymentResult process(PaymentRequest request) {
        return walletService.deduct(request.getUserId(), request.getAmount());
    }
    @Override public String getType() { return "WALLET"; }
}

// Context — selects and uses strategy
@Service
public class PaymentService {
    
    private final Map<String, PaymentStrategy> strategies;
    
    public PaymentService(List<PaymentStrategy> strategyList) {
        // Build a map from getType() → strategy object
        this.strategies = strategyList.stream()
            .collect(Collectors.toMap(PaymentStrategy::getType, s -> s));
    }
    
    public PaymentResult pay(String paymentType, PaymentRequest request) {
        PaymentStrategy strategy = strategies.get(paymentType);
        if (strategy == null) throw new IllegalArgumentException("Unknown payment type: " + paymentType);
        return strategy.process(request);
    }
}
```

### How Spring Uses Strategy

`PlatformTransactionManager` is a strategy — `JdbcTransactionManager`, `JpaTransactionManager`, `DataSourceTransactionManager` are all concrete strategies. Spring picks the right one based on what's on the classpath.

`HttpMessageConverter` is a strategy — Spring uses different converters depending on the `Accept` header: `MappingJackson2HttpMessageConverter` for JSON, `StringHttpMessageConverter` for plain text, etc.

### Interview Questions

**Q: Strategy vs Factory?**

Factory decides which object to create. Strategy decides which algorithm to run. You often use both together — a Factory selects the right Strategy, and the Strategy encapsulates the algorithm. In the payment example, you could argue `PaymentService` is both: it selects (Factory) and executes (Strategy).

**Q: When would you prefer Strategy over if-else?**

When the number of variations is likely to grow, or when different teams own different algorithms, or when you want to test each algorithm independently. For two or three simple conditions that won't change, if-else is fine and less complex.

---

## Pattern 8: Observer

### Problem It Solves

When one object (Subject) changes state, other objects (Observers) need to be notified automatically without the Subject knowing who the Observers are. This decouples the event producer from the event consumers.

### Structure

```java
// Event (the thing that happened)
public class BookingCreatedEvent {
    private final Booking booking;
    private final LocalDateTime createdAt;
    
    public BookingCreatedEvent(Booking booking) {
        this.booking = booking;
        this.createdAt = LocalDateTime.now();
    }
    
    public Booking getBooking() { return booking; }
}

// Subject — publishes events
@Service
public class BookingServiceImpl {
    
    private final ApplicationEventPublisher eventPublisher;
    private final BookingRepository bookingRepository;
    
    @Transactional
    public Booking createBooking(CreateBookingDTO dto) {
        Booking booking = bookingRepository.save(new Booking(dto));
        
        // Publish event — doesn't know who will handle it
        eventPublisher.publishEvent(new BookingCreatedEvent(booking));
        
        return booking;
    }
}

// Observer 1 — sends confirmation notification
@Component
public class BookingNotificationListener {
    
    private final NotificationService notificationService;
    
    @EventListener
    public void onBookingCreated(BookingCreatedEvent event) {
        notificationService.sendConfirmation(event.getBooking());
    }
}

// Observer 2 — updates analytics
@Component
public class BookingAnalyticsListener {
    
    private final AnalyticsService analyticsService;
    
    @EventListener
    @Async  // run in a separate thread — don't block the booking creation
    public void onBookingCreated(BookingCreatedEvent event) {
        analyticsService.recordBooking(event.getBooking());
    }
}

// Observer 3 — generates a draft invoice
@Component
public class InvoiceGenerationListener {
    
    private final BillingService billingService;
    
    @EventListener
    public void onBookingCreated(BookingCreatedEvent event) {
        billingService.generateDraftInvoice(event.getBooking());
    }
}
```

**Why this is better than calling notification + analytics + invoice directly in the service:**

```java
// BAD — BookingServiceImpl knows about too many things
public Booking createBooking(CreateBookingDTO dto) {
    Booking booking = bookingRepository.save(...);
    notificationService.sendConfirmation(booking);  // tight coupling
    analyticsService.recordBooking(booking);         // tight coupling
    billingService.generateDraftInvoice(booking);    // tight coupling
    return booking;
}
// Add a new step? Must modify BookingServiceImpl.
```

With events: `BookingServiceImpl` publishes one event and is done. Adding a new step means adding a new `@EventListener` class — zero changes to `BookingServiceImpl`.

### Interview Questions

**Q: What is the difference between synchronous and asynchronous event listeners?**

By default, `@EventListener` runs synchronously in the same thread as the publisher. The booking transaction is still open when the listener runs — the listener can participate in it.

`@Async` on a listener runs in a separate thread pool. The booking transaction has committed before the listener starts. Use `@Async` for operations that don't need to be in the booking transaction (analytics, slow third-party calls) and synchronous for operations that must succeed or fail together with the booking.

**Q: What happens if a synchronous listener throws an exception?**

Because it runs in the same thread and transaction, an exception rolls back the entire transaction — including the booking. This is sometimes exactly what you want (invoice generation failure should cancel the booking). Sometimes it's not — you don't want an analytics failure to cancel a real booking. Design your event listeners with this in mind.

---

## Pattern 9: Template Method

### Problem It Solves

You have an algorithm with a fixed skeleton but some steps vary. Define the skeleton in a base class (the "template method"), and let subclasses override only the steps that vary — without changing the overall algorithm structure.

### Structure

```java
// Abstract class defines the template method
public abstract class DataExportJob {
    
    // Template method — defines the algorithm skeleton
    // final: subclasses cannot override the skeleton, only the steps
    public final void execute() {
        List<Object> data = fetchData();       // step 1 — varies
        List<Object> processed = transform(data); // step 2 — varies
        validate(processed);                   // step 3 — fixed
        export(processed);                     // step 4 — varies
        notifyComplete();                      // step 5 — fixed (hook)
    }
    
    // Abstract — subclasses MUST implement these
    protected abstract List<Object> fetchData();
    protected abstract List<Object> transform(List<Object> data);
    protected abstract void export(List<Object> data);
    
    // Hook — subclasses MAY override (optional step)
    protected void validate(List<Object> data) {
        if (data.isEmpty()) throw new IllegalStateException("No data to export");
    }
    
    // Concrete — same for all subclasses
    private void notifyComplete() {
        log.info("Export completed at {}", LocalDateTime.now());
    }
}

// Concrete implementation 1
public class CsvExportJob extends DataExportJob {
    
    @Override
    protected List<Object> fetchData() {
        return bookingRepository.findAllForMonth(YearMonth.now());
    }
    
    @Override
    protected List<Object> transform(List<Object> data) {
        return data.stream().map(this::toCsvRow).collect(Collectors.toList());
    }
    
    @Override
    protected void export(List<Object> data) {
        csvWriter.write("bookings.csv", data);
    }
}

// Concrete implementation 2
public class PdfExportJob extends DataExportJob {
    
    @Override
    protected List<Object> fetchData() {
        return invoiceRepository.findUnpaid();
    }
    
    @Override
    protected List<Object> transform(List<Object> data) {
        return data.stream().map(this::toInvoicePdf).collect(Collectors.toList());
    }
    
    @Override
    protected void export(List<Object> data) {
        s3Service.uploadPdfs(data);
    }
}
```

### How Spring Uses Template Method

`JdbcTemplate` is the classic example. The template method handles connection acquisition, statement preparation, exception translation, and connection release. You provide only the SQL and how to map the result row:

```java
// You provide step 3 (mapRow) — JdbcTemplate handles everything else
List<Booking> bookings = jdbcTemplate.query(
    "SELECT * FROM bookings WHERE user_id = ?",
    (rs, rowNum) -> new Booking(rs.getLong("id"), rs.getString("status")),
    userId
);
```

`AbstractController`, `AbstractTransactionalJUnit4SpringContextTests`, `RestTemplate` — all use Template Method. The framework defines the skeleton; you fill in the steps.

### ReadyChairs Connection

`InvoicePDFService` and `PdfGenerationService` in ReadyChairs are natural Template Method candidates — the PDF generation process (fetch data → build template → render → upload to S3) is always the same skeleton; only the data and template vary per document type.

---

## Pattern 10: Chain of Responsibility

### Problem It Solves

A request needs to pass through a series of handlers. Each handler decides to either process the request, pass it to the next handler, or stop the chain. The sender doesn't know which handler will handle it, and handlers can be added or removed without changing the sender.

### Structure

```java
// Handler interface
public abstract class RequestHandler {
    
    protected RequestHandler next;
    
    public RequestHandler setNext(RequestHandler next) {
        this.next = next;
        return next;  // return next for fluent chaining
    }
    
    public abstract void handle(HttpRequest request);
    
    protected void passToNext(HttpRequest request) {
        if (next != null) {
            next.handle(request);
        }
    }
}

// Concrete handlers
public class AuthenticationHandler extends RequestHandler {
    @Override
    public void handle(HttpRequest request) {
        String token = request.getHeader("Authorization");
        if (token == null || !jwtUtil.isValid(token)) {
            throw new UnauthorizedException("Invalid token");
        }
        // Token valid — pass to next handler
        passToNext(request);
    }
}

public class RateLimitHandler extends RequestHandler {
    @Override
    public void handle(HttpRequest request) {
        String userId = request.getAttribute("userId");
        if (rateLimiter.isExceeded(userId)) {
            throw new RateLimitException("Too many requests");
        }
        passToNext(request);
    }
}

public class LoggingHandler extends RequestHandler {
    @Override
    public void handle(HttpRequest request) {
        log.info("Request: {} {}", request.getMethod(), request.getPath());
        passToNext(request);
        log.info("Response time: {}ms", elapsed);
    }
}

// Build the chain
RequestHandler chain = new AuthenticationHandler();
chain.setNext(new RateLimitHandler())
     .setNext(new LoggingHandler());

chain.handle(incomingRequest);
```

### Spring Security Filter Chain — The Real Example

Spring Security IS the Chain of Responsibility pattern. Every HTTP request passes through a chain of `Filter` objects. Each filter decides to proceed (call `chain.doFilter()`) or stop (write a 401/403 response directly).

```java
// Your custom filter — adds to the chain
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws IOException, ServletException {
        
        String token = extractToken(request);
        
        if (token != null && jwtUtil.isValid(token)) {
            // Set authentication in SecurityContext
            UsernamePasswordAuthenticationToken auth = createAuthentication(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        
        // Pass to next filter in chain — regardless of auth result
        // The next filter (or AuthorizationFilter) will check if the endpoint requires auth
        filterChain.doFilter(request, response);
    }
}
```

The Spring Security filter chain (in order):
```
DisableEncodeUrlFilter
    → WebAsyncManagerIntegrationFilter
    → SecurityContextHolderFilter
    → HeaderWriterFilter
    → CorsFilter
    → CsrfFilter
    → LogoutFilter
    → JwtAuthenticationFilter  ← your custom filter
    → ExceptionTranslationFilter
    → AuthorizationFilter      ← checks @PreAuthorize / role requirements
    → DispatcherServlet        ← Spring MVC takes over
```

### ReadyChairs Connection

`JwtAuthenticationFilter` in ReadyChairs is a link in Spring Security's filter chain. It validates the JWT and sets the `SecurityContext`. Downstream filters and the `AuthorizationFilter` then use that context to enforce role-based access.

### Interview Questions

**Q: How do you add a custom filter to the Spring Security chain?**

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http,
                                               JwtAuthenticationFilter jwtFilter) throws Exception {
    http
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/v1/auth/**").permitAll()
            .anyRequest().authenticated()
        );
    return http.build();
}
```

`addFilterBefore` places your filter before `UsernamePasswordAuthenticationFilter` in the chain, ensuring JWT validation runs before Spring tries form-based auth.

**Q: What happens if a filter does not call `chain.doFilter()`?**

The chain stops. No further filters run, and the request never reaches `DispatcherServlet`. The filter must write the response directly. This is exactly how authentication rejection works — `ExceptionTranslationFilter` catches the `AuthenticationException` and writes a 401 response without forwarding.

---

## Pattern 11: Command

### Problem It Solves

Encapsulate a request as an object. This lets you parameterise methods with actions, queue operations, log requests, and support undo/redo.

### Structure

```java
// Command interface
public interface Command {
    void execute();
    void undo();
}

// Concrete commands
public class CreateBookingCommand implements Command {
    
    private final BookingRepository repository;
    private final CreateBookingDTO dto;
    private Booking createdBooking;
    
    public CreateBookingCommand(BookingRepository repository, CreateBookingDTO dto) {
        this.repository = repository;
        this.dto = dto;
    }
    
    @Override
    public void execute() {
        createdBooking = repository.save(new Booking(dto));
    }
    
    @Override
    public void undo() {
        if (createdBooking != null) {
            repository.delete(createdBooking);
        }
    }
}

// Invoker — executes commands and maintains history
public class BookingCommandInvoker {
    
    private final Deque<Command> history = new ArrayDeque<>();
    
    public void execute(Command command) {
        command.execute();
        history.push(command);
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}
```

### How Spring Uses Command

Spring's `@Scheduled` tasks, Spring Batch `Step` and `Job` configuration, Spring Integration `MessageHandler` — all follow the Command pattern. The command is an action encapsulated as an object, scheduled or queued for execution.

Spring's `@Transactional` rollback is conceptually an undo command — if the transaction fails, the database reverts the executed commands.

---

## Quick Pattern Reference Card

| Pattern | Category | One-line purpose | Spring example |
|---|---|---|---|
| Singleton | Creational | One instance per context | Every `@Service` bean |
| Factory Method | Creational | Create objects without specifying concrete class | `BeanFactory`, Spring bean creation |
| Builder | Creational | Construct complex objects step by step | `UriComponentsBuilder`, Lombok `@Builder` |
| Proxy | Structural | Control access to an object | `@Transactional`, Spring AOP, JPA lazy loading |
| Decorator | Structural | Add behaviour dynamically | Java I/O streams, `HttpServletRequestWrapper` |
| Facade | Structural | Simplified interface to a subsystem | Service layer hiding Repository complexity |
| Strategy | Behavioral | Interchangeable family of algorithms | `PlatformTransactionManager`, `HttpMessageConverter` |
| Observer | Behavioral | Notify dependents of state change | `ApplicationEvent` / `@EventListener` |
| Template Method | Behavioral | Algorithm skeleton, subclass fills steps | `JdbcTemplate`, `RestTemplate` |
| Chain of Responsibility | Behavioral | Pass request through handler chain | Spring Security filter chain |
| Command | Behavioral | Encapsulate request as object | Spring Batch `Step`, `@Scheduled` |

---

## Interview Cheat Sheet — How To Answer "Explain [Pattern]"

```
1. State the problem in one sentence
   "The problem is... [coupling / too many constructors / scattered creation logic]"

2. Name the pattern and its structure in one sentence
   "The [Pattern] solves this by... [encapsulating / delegating / wrapping]"

3. Give a Spring or ReadyChairs example
   "In Spring, this is exactly how @Transactional works — Spring creates a CGLIB proxy..."
   "In ReadyChairs, I have a NotificationSenderFactory that..."

4. State the trade-off
   "The cost of this pattern is [added classes / indirection / startup time]
    but the benefit is [testability / extensibility / separation of concerns]"
```
