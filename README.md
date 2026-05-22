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

The **Student Mental Health Support Platform** is a digital peer-support system designed to address the growing mental health challenges faced by university students. The platform aims to reduce barriers to access by providing anonymous support, resource matching, appointment scheduling with professional counselors, and secure peer counselor connections.

The project is developed progressively through the Systems Analysis & Design course. Each workshop contributes to a different stage of the system engineering process: initial analysis, system design, and robust architecture validation.

The platform is based on three core principles:

- **Anonymity:** Students must be able to seek support without exposing their identity publicly.
- **Scalability:** The system must handle demand increases during academic peak periods such as midterms and finals.
- **Accessibility:** The platform must be easy to access through web and mobile environments.

---

## General System Scope

### In Scope

- Student registration and anonymous profile creation
- Peer counselor matching based on reported needs
- Anonymous communication between students and peer counselors
- Appointment scheduling with professional counselors
- Access to educational mental health resources
- Data privacy and consent management
- System monitoring and quality validation

### Out of Scope

- Clinical diagnosis
- Medical or psychiatric treatment
- Storage of clinical records
- Emergency psychiatric intervention
- Integration with hospital systems
- Academic performance tracking

---

## Workshop 1 — Systems Analysis

### Overview

Workshop 1 focused on understanding the problem context, identifying stakeholders, collecting primary data, and defining the system scope. The purpose was to determine whether a digital mental health support platform would respond to real student needs.

### Data Collection Methodology

Primary data was collected using three complementary methods:

**Structured Surveys:**  
An online survey with 10 multiple-choice questions was distributed to university students. The questions covered academic stress levels, access to mental health services, willingness to seek help, comfort with peer support, and interest in using a digital mental health platform.

**Usage Monitoring:**  
A conceptual monitoring approach was proposed to understand how users could interact with the platform in future stages. This included possible metrics such as access frequency, use of peer-support features, and interaction with mental health resources.

**Process Documentation:**  
The expected workflow of the system was documented, including student registration, browsing available resources, requesting support, connecting with peer counselors, and scheduling appointments.

### Key Findings

- 88% of surveyed students reported experiencing anxiety or emotional problems during university life.
- 68% of students had never sought professional help despite experiencing difficulties.
- No students rated existing university mental health services as easy or very easy to access.
- 64% of students preferred anonymous support.
- 76% of students expressed interest in using a digital mental health platform.
- 68% of students requested a comprehensive support model including peer support, professional counseling, and educational resources.
- Academic stress and service demand are expected to increase during midterm and final exam periods.

### Main Conclusions from Workshop 1

The results showed that students face significant barriers when trying to access mental health support. These barriers include lack of awareness, stigma, low trust, and difficulty accessing institutional services. The findings justified the development of a platform that prioritizes anonymity, accessibility, and multiple support pathways.

---

## Workshop 2 — Systems Design

### Overview

Workshop 2 translated the analysis from Workshop 1 into a structured system design. The objective was to define the system architecture, core modules, interfaces, functional requirements, non-functional requirements, and implementation strategy for the Student Mental Health Support Platform.

### Architecture

The proposed system follows a modular three-layer architecture:

### 1. Presentation Layer

This layer includes the user-facing interfaces of the platform.

Main components:

- Web application
- Mobile access
- User interface for students
- User interface for peer counselors
- User interface for professional counselors
- Administrative interface

The goal of this layer is to provide an intuitive, accessible, and privacy-conscious user experience.

### 2. Application Layer

This layer contains the core business logic of the system.

Main modules:

- User Registration Module
- Matching System
- Anonymous Communication Module
- Appointment Scheduling Module
- Resource Library Module
- Privacy & Consent Management Module

Each module is designed to operate independently while communicating with other modules through defined interfaces.

### 3. Infrastructure Layer

This layer provides the technical foundation required for system operation.

Main components:

- Cloud server infrastructure
- Encrypted database
- University authentication service
- Backup and recovery mechanisms
- Monitoring and logging tools

This layer supports availability, scalability, security, and data protection.

### Functional Requirements

| Category | Requirement |
|---|---|
| Authentication | Students must register and authenticate using university credentials while maintaining an anonymous public profile. |
| Matching | The system must match students with peer counselors based on reported needs and availability. |
| Communication | The system must provide secure and anonymous communication between students and peer counselors. |
| Scheduling | The system must allow appointment scheduling with professional counselors. |
| Resources | The system must provide access to a Resource Library with mental health materials. |
| Privacy | The system must protect user identity and avoid unnecessary storage of sensitive information. |
| Availability | The system must remain available during active academic periods. |

### Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | The platform should respond quickly under normal load conditions. |
| Usability | The platform should be easy to access through web and mobile devices. |
| Security | Communications and stored data must be protected using encryption and access control. |
| Maintainability | The system must follow modular design principles to support future updates. |
| Scalability | The platform must support demand increases during academic peak periods. |
| Reliability | The system should continue operating even if one module experiences failure. |

### Key Design Decisions

- Adoption of a three-layer modular architecture.
- Anonymity as a central design principle.
- Integration with institutional authentication through Single Sign-On.
- Separation between institutional identity and anonymous platform identity.
- Use of a Matching System to connect students with peer counselors.
- Inclusion of Appointment Scheduling for professional counselor support.
- Use of a Resource Library as a self-help and educational support mechanism.
- Cloud-based infrastructure to support scalability and availability.

### Main Conclusions from Workshop 2

Workshop 2 established a coherent technical design based on the needs identified in Workshop 1. The modular architecture allows the system to be scalable, maintainable, and privacy-focused. The design also confirms that the platform should not be treated as a clinical system, but as a support and connection platform that complements existing university services.

---

## Workshop 3 — Robust Architecture, Risk Management and Quality Validation

### Overview

Workshop 3 strengthened the system design by applying robust engineering principles, quality standards, and risk management strategies. The objective was to evaluate whether the proposed architecture could remain viable under technical, operational, security, and organizational constraints.

This workshop refined the system by focusing on:

- Robust architecture design
- Risk identification and mitigation
- Quality assurance
- Security and privacy controls
- Project management planning
- System reliability and maintainability

---

## Robust Architecture Design

The architecture was improved using principles of modularity, scalability, maintainability, security, privacy, and accessibility.

### Presentation Layer Improvements

The Presentation Layer was refined to support:

- Web and mobile access
- Accessibility criteria
- Simple and intuitive navigation
- Privacy and informed consent messages
- Cross-platform compatibility

This layer responds directly to the need for accessible and anonymous support identified in Workshop 1.

### Application Layer Improvements

The Application Layer was refined around independent modules:

- User Registration
- Matching System
- Anonymous Communication
- Appointment Scheduling
- Resource Library
- Privacy & Consent Management

The modular approach allows each component to be updated, tested, or improved without affecting the entire platform.

### Infrastructure Layer Improvements

The Infrastructure Layer was strengthened through:

- Cloud-based deployment planning
- Encrypted database design
- Institutional authentication services
- Backup and recovery strategies
- Monitoring and contingency planning

These decisions support availability, data protection, and operational continuity.

---

## Risk Management Plan

Workshop 3 included a risk management plan based on the identification, classification, mitigation, and monitoring of risks.

The risks were organized into the following categories:

- Technical risks
- Operational risks
- Security risks
- Human and social risks
- Project management risks

### Main Identified Risks

| Risk Category | Example Risks |
|---|---|
| Technical | Authentication service failure, database corruption, cloud infrastructure outage |
| Operational | Peer counselor shortage, peer counselor burnout, low student adoption |
| Security | User de-anonymization, account takeover, exploitation of anonymous communication |
| Human and Social | Loss of trust, harmful peer interaction, exploitation of vulnerable users |
| Project Management | Timeline overrun, stakeholder disengagement |

### Key Mitigation Strategies

- Use of encrypted communication and encrypted storage.
- Separation between authentication data and anonymous user profiles.
- Backup and recovery plans.
- Monitoring of counselor workload.
- Session limits to reduce peer counselor burnout.
- Clear privacy policies and informed consent.
- Incident response procedures.
- Peer counselor training and verification.
- Use of modular architecture to reduce the impact of component failures.

---

## Quality and Engineering Principles

Workshop 3 incorporated quality and engineering principles aligned with software engineering best practices.

### Quality Attributes Considered

| Quality Attribute | Application in the Project |
|---|---|
| Scalability | The platform is designed to handle increased demand during academic peak periods. |
| Maintainability | Modular components allow independent updates and easier maintenance. |
| Security | Encryption, authentication, and privacy controls protect users and system data. |
| Privacy | Anonymous profiles and data segregation reduce identity exposure risks. |
| Reliability | Backup, recovery, and monitoring strategies support continuous operation. |
| Accessibility | Web and mobile access reduce barriers for students. |
| Reproducibility | Documentation supports future implementation and validation. |

---

## Security and Privacy Considerations

Security and privacy are central to the platform because student trust is essential for adoption.

The system design includes:

- Institutional authentication through SSO
- Anonymous public profiles
- Separation between real identity and support interactions
- Encrypted communication channels
- Encrypted database storage
- Privacy and consent management
- Minimal storage of sensitive information
- Incident response procedures

These controls are intended to reduce the risk of identity exposure and increase student confidence in the platform.
