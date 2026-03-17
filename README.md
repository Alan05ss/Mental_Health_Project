# Mental Health Project
## Student Mental Health Support Platform
**Systems Analysis & Design — 2026-I**
Universidad Distrital Francisco José de Caldas

---

## Team Members
| Name | Student ID |
|------|------------|
| Alan Santiago Agudelo Sarmiento | 20222020170 |
| Julian Ernesto Romero Gutierrez | 20231020164 |
| Juan David Cardozo Trujillo | 20231020155 |
| Nicolas Alexander Sierra Contreras | 20222020197 |

**Professor:** Eng. Carlos Andrés Sierra, M.Sc.

---

## Project Description
Digital peer support platform addressing rising mental health issues among university students. Includes resource matching, appointment scheduling with counseling services, and anonymous peer counselor connections. The platform is built around three core principles: anonymity, scalability, and accessibility.

---

## Repository Structure
| Folder | Contents |
|--------|----------|
| /data | Raw data files, survey responses, measurements |
| /diagrams | System architecture diagrams, process flow maps |
| /docs | Final PDF reports and academic documents |
| /analysis | Analysis scripts and methodology documentation |

---

## Workshop 1 — Systems Analysis

### Data Collection Methodology
Primary data was collected using three methods: Structured Surveys, Usage Monitoring, and Process Documentation.

**Structured Surveys:** An online survey of 10 multiple-choice questions was distributed to university students covering academic stress levels, access to mental health services, willingness to seek help, and interest in a digital support platform.

**Usage Monitoring:** Conceptual monitoring of potential interaction patterns including frequency of platform access, usage of peer-support features, and interaction with mental health resources.

**Process Documentation:** Documentation of the proposed system workflow including user registration, resource access, peer counselor connections, and appointment scheduling.

### Key Findings
- 88% of students reported experiencing anxiety or emotional problems during university life
- 68% of students have never sought professional help despite experiencing difficulties
- Zero students found existing university mental health services easy or very easy to access
- 64% of students require anonymity as a precondition for seeking support
- 76% of students expressed interest in using a digital mental health platform
- Peak demand is predictable during midterm and final exam periods

---

## Workshop 2 — Systems Design

### Overview
Building upon the Workshop 1 findings, Workshop 2 translates the analytical insights into a comprehensive System Design Document. The design defines the architecture, components, interfaces, and implementation strategy for the Student Mental Health Support Platform.

### Key Design Decisions
- Three-layer modular architecture: User, Application, and Infrastructure
- Anonymity as the foundational design principle
- Tiered support model: self-help resources → peer counseling → professional appointments
- Predictive peer recruitment strategy aligned with the academic calendar
- Cloud-hosted, platform-independent infrastructure with auto-scaling

