# Disaster Recovery

A comprehensive guide to disaster recovery strategies, backup procedures, and business continuity planning for ensuring system resilience and data protection.

---

## Table of Contents

1. [What is Disaster Recovery?](#what-is-disaster-recovery)
2. [Why Disaster Recovery?](#why-disaster-recovery)
3. [Disaster Types](#disaster-types)
4. [Recovery Objectives](#recovery-objectives)
5. [Backup Strategies](#backup-strategies)
6. [Disaster Recovery Strategies](#disaster-recovery-strategies)
7. [Recovery Procedures](#recovery-procedures)
8. [Testing and Validation](#testing-and-validation)
9. [Real-World Examples](#real-world-examples)
10. [Interview Tips](#interview-tips)

---

# What is Disaster Recovery?

## What is Disaster Recovery?

**Disaster Recovery (DR)** is a set of policies, procedures, and technologies designed to enable the recovery or continuation of technology infrastructure and systems following a natural or human-induced disaster.

**Simple definition:** A plan and process to get your systems back up and running after a major failure, like having a backup plan when your primary plan fails completely.

Disaster recovery focuses on restoring IT infrastructure and systems after a disaster, ensuring business continuity and minimizing downtime and data loss.

## Key Concepts

### Disaster vs. Incident

**Disaster:** A major event that causes complete or near-complete failure of a system or data center, requiring recovery from backups or failover to alternate sites.

**Incident:** A smaller event that may cause partial failure but can be handled with normal operational procedures.

**Example:**
- **Disaster:** Entire data center destroyed by fire
- **Incident:** Single server failure (handled by redundancy)

### Business Continuity vs. Disaster Recovery

**Business Continuity:** Broader concept covering all aspects of keeping business running during and after a disaster, including people, processes, and technology.

**Disaster Recovery:** Focused specifically on IT systems and data recovery, a subset of business continuity.

**Relationship:**
- Business Continuity (broader) → Disaster Recovery (IT-focused)

---

# Why Disaster Recovery?

## Consequences of No Disaster Recovery

**Data Loss:**
- Permanent loss of customer data
- Loss of business records
- Loss of intellectual property
- Regulatory compliance violations

**Business Impact:**
- Extended downtime (hours to days)
- Lost revenue during downtime
- Customer trust and reputation damage
- Competitive disadvantage

**Costs:**
- Recovery costs (often much higher than prevention)
- Lost business revenue
- Legal and regulatory penalties
- Customer compensation

## Benefits of Disaster Recovery

**Data Protection:**
- Prevents permanent data loss
- Enables data recovery
- Maintains data integrity
- Compliance with regulations

**Business Continuity:**
- Minimizes downtime
- Faster recovery
- Maintains customer service
- Protects reputation

**Risk Mitigation:**
- Reduces business risk
- Meets compliance requirements
- Insurance benefits
- Stakeholder confidence

---

# Disaster Types

## Natural Disasters

### 1. Natural Events

**Examples:**
- Earthquakes
- Floods
- Hurricanes/Typhoons
- Fires
- Tornadoes
- Power outages

**Impact:**
- Physical damage to data centers
- Extended power outages
- Network connectivity loss
- May affect entire region

**Mitigation:**
- Geographic distribution
- Multiple data centers
- Backup power (generators)
- Redundant network paths

## Human-Induced Disasters

### 1. Cyber Attacks

**Examples:**
- Ransomware attacks
- DDoS attacks
- Data breaches
- Malware infections

**Impact:**
- System unavailability
- Data corruption or theft
- Service disruption
- Reputation damage

**Mitigation:**
- Security measures
- Regular backups
- Incident response plans
- Network segmentation

### 2. Human Error

**Examples:**
- Accidental data deletion
- Configuration mistakes
- Code deployment errors
- Database corruption

**Impact:**
- Data loss
- Service disruption
- Configuration issues
- May cascade to other systems

**Mitigation:**
- Access controls
- Change management
- Regular backups
- Testing procedures

### 3. Equipment Failure

**Examples:**
- Hardware failures
- Storage system failures
- Network equipment failures
- Power system failures

**Impact:**
- Service unavailability
- Data inaccessibility
- May affect multiple systems
- Recovery time varies

**Mitigation:**
- Redundant hardware
- Regular maintenance
- Monitoring and alerts
- Spare equipment

---

# Recovery Objectives

## RTO (Recovery Time Objective)

### What is RTO?

**Recovery Time Objective (RTO)** is the maximum acceptable time to restore a system or service after a disaster. It defines how quickly you need to recover.

**Simple definition:** How long you can afford to be down - if RTO is 4 hours, you must be back up within 4 hours of the disaster.

RTO answers the question: "How quickly do we need to recover?"

### RTO Examples

**Mission-Critical System:**
- RTO: 1 hour
- Meaning: Must recover within 1 hour
- Example: Payment processing system

**Critical Business System:**
- RTO: 4 hours
- Meaning: Must recover within 4 hours
- Example: E-commerce website

**Standard System:**
- RTO: 24 hours
- Meaning: Must recover within 24 hours
- Example: Internal reporting system

**Non-Critical System:**
- RTO: 72 hours
- Meaning: Must recover within 72 hours
- Example: Development environments

### Factors Affecting RTO

**Business Impact:**
- Revenue loss per hour
- Customer impact
- Regulatory requirements
- Competitive pressure

**Technical Complexity:**
- System complexity
- Dependencies
- Recovery procedures
- Available resources

## RPO (Recovery Point Objective)

### What is RPO?

**Recovery Point Objective (RPO)** is the maximum acceptable amount of data loss measured in time. It defines how much data you can afford to lose.

**Simple definition:** How much data you can afford to lose - if RPO is 1 hour, you can lose up to 1 hour of data.

RPO answers the question: "How much data can we afford to lose?"

### RPO Examples

**Zero Data Loss:**
- RPO: 0 (real-time replication)
- Meaning: No data loss acceptable
- Example: Financial transactions

**Minimal Data Loss:**
- RPO: 15 minutes
- Meaning: Can lose up to 15 minutes of data
- Example: Customer orders

**Acceptable Data Loss:**
- RPO: 1 hour
- Meaning: Can lose up to 1 hour of data
- Example: User activity logs

**Tolerable Data Loss:**
- RPO: 24 hours
- Meaning: Can lose up to 24 hours of data
- Example: Analytics data

### Factors Affecting RPO

**Data Criticality:**
- Business value of data
- Regulatory requirements
- Customer impact
- Irreversibility of operations

**Technical Feasibility:**
- Replication technology
- Network bandwidth
- Storage costs
- System performance impact

## RTO vs RPO Relationship

### Independent but Related

**RTO and RPO are independent:**
- RTO: How quickly to recover (time to restore)
- RPO: How much data to lose (point in time to recover to)

**Example Scenarios:**

**Scenario 1: High RTO, Low RPO**
- RTO: 24 hours (can take time to recover)
- RPO: 15 minutes (minimal data loss)
- Strategy: Frequent backups, manual recovery

**Scenario 2: Low RTO, High RPO**
- RTO: 1 hour (must recover quickly)
- RPO: 4 hours (can lose more data)
- Strategy: Fast failover, less frequent backups

**Scenario 3: Low RTO, Low RPO**
- RTO: 1 hour (must recover quickly)
- RPO: 15 minutes (minimal data loss)
- Strategy: Real-time replication, automated failover

---

# Backup Strategies

## Backup Types

### 1. Full Backup

**What is Full Backup?**

Full backup is a complete copy of all data at a point in time. It includes all files, databases, and system state.

**Characteristics:**
- Complete data copy
- Slow to create (all data)
- Fast to restore (single backup)
- Requires most storage
- Baseline for other backup types

**Use When:**
- Initial backup
- Periodic complete backup
- Long-term archival
- Disaster recovery baseline

**Example:**
- Full backup every Sunday
- Contains all data as of Sunday
- Restore from single backup

### 2. Incremental Backup

**What is Incremental Backup?**

Incremental backup only backs up data that has changed since the last backup (full or incremental).

**Characteristics:**
- Only changed data
- Fast to create (small amount)
- Slower to restore (need full + all incrementals)
- Requires less storage
- Depends on previous backups

**Use When:**
- Frequent backups needed
- Limited storage available
- Most data unchanged
- Between full backups

**Example:**
- Full backup Sunday
- Incremental Monday (only Monday changes)
- Incremental Tuesday (only Tuesday changes)
- Restore: Full + Monday + Tuesday

### 3. Differential Backup

**What is Differential Backup?**

Differential backup backs up all data that has changed since the last full backup.

**Characteristics:**
- All changes since full backup
- Moderate speed to create
- Moderate speed to restore (full + latest differential)
- Moderate storage requirement
- Only depends on full backup

**Use When:**
- Balance between speed and restore time
- Moderate change rate
- Simpler restore than incremental

**Example:**
- Full backup Sunday
- Differential Monday (all changes since Sunday)
- Differential Tuesday (all changes since Sunday)
- Restore: Full + Latest differential

## Backup Comparison

| Type | Backup Speed | Restore Speed | Storage | Dependencies |
|------|-------------|---------------|---------|--------------|
| **Full** | Slow | Fast | High | None |
| **Incremental** | Fast | Slow | Low | All previous |
| **Differential** | Moderate | Moderate | Moderate | Full backup only |

## Backup Strategies

### 1. 3-2-1 Backup Rule

**What is 3-2-1 Rule?**

A best practice backup strategy: 3 copies of data, 2 different media types, 1 offsite copy.

**Breakdown:**
- **3 Copies:** Original + 2 backups
- **2 Media Types:** Different storage types (disk, tape, cloud)
- **1 Offsite:** At least one backup in different location

**Example:**
- Original: Production server
- Backup 1: Local disk backup
- Backup 2: Cloud backup (offsite)
- Media: Disk + Cloud (2 types)

### 2. Grandfather-Father-Son (GFS)

**What is GFS Strategy?**

A backup rotation scheme with daily (son), weekly (father), and monthly (grandfather) backups.

**Structure:**
- **Daily (Son):** Incremental backups, kept for 1 week
- **Weekly (Father):** Full backups, kept for 1 month
- **Monthly (Grandfather):** Full backups, kept for 1 year

**Example:**
- Daily: Monday-Friday incremental
- Weekly: Sunday full backup
- Monthly: First Sunday of month full backup

### 3. Continuous Data Protection (CDP)

**What is CDP?**

Continuous data protection continuously backs up data as changes occur, providing near-zero RPO.

**Characteristics:**
- Real-time or near-real-time backup
- Very low RPO (minutes or seconds)
- Higher storage and network requirements
- More complex implementation

**Use When:**
- Very low RPO required
- Critical data
- Can afford CDP infrastructure

---

# Disaster Recovery Strategies

## Recovery Strategy Types

### 1. Backup and Restore

**What is Backup and Restore?**

Traditional strategy: regularly backup data, restore from backups after disaster.

**How it works:**
1. Regular backups to storage
2. Store backups offsite
3. After disaster, restore from backups
4. Rebuild systems from backups

**Characteristics:**
- Simple to implement
- Lower cost
- Longer RTO (hours to days)
- Higher RPO (depends on backup frequency)

**Use When:**
- Non-critical systems
- Longer RTO acceptable
- Budget constraints
- Simple systems

**RTO/RPO:**
- RTO: Hours to days
- RPO: Hours to days (backup frequency)

### 2. Pilot Light

**What is Pilot Light?**

Minimal infrastructure running in DR site, ready to scale up quickly when needed.

**How it works:**
1. Minimal infrastructure in DR site
2. Data replicated to DR site
3. On disaster, scale up infrastructure
4. Switch traffic to DR site

**Characteristics:**
- Lower ongoing cost
- Faster than backup/restore
- Requires scaling infrastructure
- Moderate RTO

**Use When:**
- Moderate RTO acceptable
- Cost-conscious
- Can scale infrastructure quickly

**RTO/RPO:**
- RTO: Hours
- RPO: Minutes to hours (replication lag)

### 3. Warm Standby

**What is Warm Standby?**

DR site with infrastructure running but not processing production traffic, ready to take over.

**How it works:**
1. Infrastructure running in DR site
2. Data replicated to DR site
3. Systems configured but idle
4. On disaster, activate and switch traffic

**Characteristics:**
- Infrastructure always running
- Faster recovery than pilot light
- Higher ongoing cost
- Moderate RTO

**Use When:**
- Moderate RTO required
- Can afford running infrastructure
- Need faster recovery than pilot light

**RTO/RPO:**
- RTO: Minutes to hours
- RPO: Minutes (replication lag)

### 4. Hot Standby (Active-Passive)

**What is Hot Standby?**

DR site with fully running infrastructure, synchronized with primary, ready to take over immediately.

**How it works:**
1. Full infrastructure running in DR site
2. Real-time data replication
3. Systems synchronized and ready
4. On disaster, immediate failover

**Characteristics:**
- Fastest recovery
- Lowest RTO
- Highest ongoing cost
- Real-time replication

**Use When:**
- Low RTO required
- Critical systems
- Can afford duplicate infrastructure

**RTO/RPO:**
- RTO: Minutes
- RPO: Minutes or zero (real-time replication)

### 5. Multi-Site Active-Active

**What is Multi-Site Active-Active?**

Multiple sites actively processing traffic, load balanced across sites.

**How it works:**
1. Multiple sites running
2. Traffic distributed across sites
3. Data replicated between sites
4. On disaster, remaining sites handle traffic

**Characteristics:**
- Zero downtime (if site fails)
- Highest availability
- Highest cost
- Most complex

**Use When:**
- Zero downtime required
- Global distribution needed
- Highest availability critical

**RTO/RPO:**
- RTO: Zero (no failover needed)
- RPO: Zero (real-time replication)

## Strategy Comparison

| Strategy | RTO | RPO | Cost | Complexity |
|----------|-----|-----|------|------------|
| **Backup/Restore** | Hours-Days | Hours-Days | Low | Low |
| **Pilot Light** | Hours | Minutes-Hours | Low-Medium | Medium |
| **Warm Standby** | Minutes-Hours | Minutes | Medium | Medium |
| **Hot Standby** | Minutes | Minutes-Zero | High | High |
| **Active-Active** | Zero | Zero | Very High | Very High |

---

# Recovery Procedures

## Recovery Process Steps

### 1. Disaster Declaration

**What to do:**
- Assess the situation
- Determine if disaster recovery needed
- Declare disaster officially
- Notify stakeholders

**Checklist:**
- [ ] Assess impact and scope
- [ ] Verify primary site status
- [ ] Determine if DR needed
- [ ] Notify DR team
- [ ] Notify management
- [ ] Document disaster declaration

### 2. Assessment

**What to do:**
- Evaluate damage extent
- Identify affected systems
- Determine recovery approach
- Estimate recovery time

**Checklist:**
- [ ] Assess primary site damage
- [ ] Identify affected systems
- [ ] Check backup availability
- [ ] Verify DR site status
- [ ] Estimate RTO/RPO impact

### 3. Recovery Execution

**What to do:**
- Execute recovery procedures
- Restore systems from backups
- Or failover to DR site
- Verify system functionality

**Checklist:**
- [ ] Activate DR site (if needed)
- [ ] Restore data from backups
- [ ] Restore applications
- [ ] Configure systems
- [ ] Verify connectivity
- [ ] Test critical functions

### 4. Validation

**What to do:**
- Test recovered systems
- Verify data integrity
- Validate functionality
- Confirm business operations

**Checklist:**
- [ ] Test system functionality
- [ ] Verify data integrity
- [ ] Test critical business processes
- [ ] Validate user access
- [ ] Confirm monitoring working

### 5. Cutover

**What to do:**
- Switch traffic to recovered systems
- Update DNS/routing
- Notify users
- Monitor closely

**Checklist:**
- [ ] Update DNS records
- [ ] Update load balancer config
- [ ] Switch traffic
- [ ] Notify users
- [ ] Monitor systems
- [ ] Document cutover

### 6. Post-Recovery

**What to do:**
- Monitor systems
- Document lessons learned
- Plan primary site recovery
- Update DR procedures

**Checklist:**
- [ ] Monitor recovered systems
- [ ] Document issues
- [ ] Conduct post-mortem
- [ ] Update procedures
- [ ] Plan primary recovery

---

# Testing and Validation

## Why Test Disaster Recovery?

**Benefits:**
- Verify procedures work
- Identify gaps and issues
- Train team members
- Validate RTO/RPO
- Build confidence

**Risks of Not Testing:**
- Procedures may not work
- Team may not know what to do
- RTO/RPO may not be met
- Data may not be recoverable

## Testing Types

### 1. Tabletop Exercise

**What is Tabletop Exercise?**

Walkthrough of DR procedures without actually executing them, discussing scenarios and responses.

**Purpose:**
- Review procedures
- Identify gaps
- Train team
- Low risk

**Frequency:**
- Quarterly or semi-annually

### 2. Simulation Test

**What is Simulation Test?**

Simulate disaster scenario and execute recovery procedures in controlled environment.

**Purpose:**
- Test procedures
- Train team
- Identify issues
- Moderate risk

**Frequency:**
- Semi-annually or annually

### 3. Full DR Test

**What is Full DR Test?**

Complete disaster recovery test, including failover to DR site and full recovery.

**Purpose:**
- Validate complete recovery
- Test all systems
- Verify RTO/RPO
- High risk (may impact production)

**Frequency:**
- Annually or bi-annually

## Testing Checklist

**Pre-Test:**
- [ ] Schedule test date
- [ ] Notify stakeholders
- [ ] Prepare test environment
- [ ] Review procedures
- [ ] Assign roles

**During Test:**
- [ ] Execute procedures
- [ ] Document issues
- [ ] Measure RTO/RPO
- [ ] Test all systems
- [ ] Verify data integrity

**Post-Test:**
- [ ] Document results
- [ ] Identify issues
- [ ] Update procedures
- [ ] Conduct review
- [ ] Plan improvements

---

# Real-World Examples

## Cloud Provider DR

### AWS Multi-Region

**Strategy:** Active-Active across regions
**RTO:** Zero (automatic failover)
**RPO:** Zero (real-time replication)
**Implementation:** Route 53, Multi-AZ, Cross-region replication

### Azure Site Recovery

**Strategy:** Hot standby
**RTO:** Minutes
**RPO:** Minutes
**Implementation:** Azure Site Recovery service

## Enterprise DR

### Financial Institution

**Strategy:** Hot standby
**RTO:** 15 minutes
**RPO:** 5 minutes
**Requirements:** Regulatory compliance, zero data loss tolerance

### E-commerce Platform

**Strategy:** Multi-region active-active
**RTO:** Zero
**RPO:** Zero
**Implementation:** Global load balancing, real-time replication

---

# Interview Tips

## Common Questions

**Q: What is disaster recovery?**
- Set of policies and procedures to recover systems after disaster
- Focuses on IT systems and data recovery
- Part of business continuity planning
- Ensures systems can be restored after major failure

**Q: What is the difference between RTO and RPO?**
- **RTO (Recovery Time Objective):** Maximum time to restore system (how quickly)
- **RPO (Recovery Point Objective):** Maximum data loss acceptable (how much data)
- RTO = Time to recover, RPO = Data loss tolerance
- Independent but related metrics

**Q: What are different disaster recovery strategies?**
- **Backup/Restore:** Traditional, longer RTO/RPO, lower cost
- **Pilot Light:** Minimal DR infrastructure, moderate RTO
- **Warm Standby:** Infrastructure running, ready to activate
- **Hot Standby:** Fully running, immediate failover
- **Active-Active:** Multiple sites, zero downtime

**Q: What is the 3-2-1 backup rule?**
- **3 Copies:** Original + 2 backups
- **2 Media Types:** Different storage types
- **1 Offsite:** At least one backup offsite
- Best practice for data protection

**Q: What is the difference between full, incremental, and differential backup?**
- **Full:** Complete copy, slow backup, fast restore
- **Incremental:** Only changes since last backup, fast backup, slow restore
- **Differential:** All changes since full backup, moderate both
- Choose based on backup/restore speed needs

**Q: How do you test disaster recovery?**
- **Tabletop:** Walkthrough without execution
- **Simulation:** Controlled test environment
- **Full DR Test:** Complete failover test
- Regular testing essential to verify procedures work

**Q: What factors affect RTO and RPO?**
- **RTO Factors:** System complexity, recovery procedures, available resources
- **RPO Factors:** Data criticality, replication technology, business requirements
- Trade-offs between cost, complexity, and recovery objectives

## Key Points to Remember

- **Disaster Recovery** = Plan to recover systems after major failure
- **RTO** = Maximum time to recover (how quickly)
- **RPO** = Maximum data loss (how much data)
- **Backup Types** = Full, incremental, differential
- **DR Strategies** = Backup/restore, pilot light, warm/hot standby, active-active
- **3-2-1 Rule** = 3 copies, 2 media types, 1 offsite
- **Testing** = Essential to verify procedures work
- **Use DR** for business continuity, data protection, risk mitigation

---

## Related Topics

- [Availability](./Availability.md) - High availability concepts
- [Backup & Storage](./Storage.md) - Storage and backup systems
- [Databases](./Databases.md) - Database backup and replication
- [Architecture Patterns](./Architecture-Patterns.md) - Building resilient systems
