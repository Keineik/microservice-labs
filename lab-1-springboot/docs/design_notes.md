# Design notes (for the report and the oral defense)

The learning goal of this lab is **service discovery + inter-service
communication**, so the design keeps the domain small and spends its complexity
budget on the microservice concerns: registration, name-based calls, contracts,
and failure handling.

## Service boundaries and data ownership

Four runtime services plus a Eureka registry:

- **discovery-server** - the Eureka registry. Nothing else registers with
  itself; it only holds the registry.
- **student-service** - owns the student catalog and its own database.
- **course-service** - owns the course catalog *and* its offerings (a course
  opened in a year / semester / section), in its own database.
- **enrollment-service** - owns enrollment records (each pointing at an offering)
  and *composes* the cross-service views (a student's transcript with GPA, and an
  offering's attendee list) by calling the other two.
- **web-client** - a server-rendered UI with no database of its own.

**No shared database.** Each service has its own in-memory H2. This is the rule
that makes them real services rather than modules of one app: there is no
cross-service table, no cross-service join, no shared schema.

**Reference by business key, hydrate over the API.** enrollment-service stores
only `studentCode` and `offeringCode` on each enrollment - not foreign keys into
other services' tables (which do not exist here) and not copies of names/titles.
The `offeringCode` (e.g. `CS101-2025-1-01`) encodes course + year + semester +
section. At read time it calls student-service and course-service
(`GET /api/offerings/{offeringCode}`) to resolve the human-readable details. This
is the canonical microservice pattern and it is the core thing the aggregation
endpoints demonstrate.

## Contracts: no shared DTO module

Each service defines its own DTOs, and each **consumer** declares its own view of
a producer's response (a "consumer-driven" view) that takes only the fields it
needs - see `enrollment-service`'s `client/StudentDto` and `client/OfferingDto`,
which are deliberate subsets of the producers' responses. There is intentionally
**no shared `common` jar**: a shared contract library would couple the services
at build time, which is exactly what we are trying to avoid. Unknown JSON fields
are ignored on deserialization, so a producer can add fields without breaking
consumers.

## Communication: Eureka + OpenFeign

Services never hold each other's host/port. A Feign client names the *logical
service* (`@FeignClient(name = "course-service")`); Spring Cloud LoadBalancer
resolves a live instance from the Eureka registry at call time. Benefits over a
hardcoded URL: instances can move, scale out, or restart on new ports without any
config change in callers; a caller can be load-balanced across instances; and
there is a single source of truth for "where is X".

## Derived academics (GPA / credits)

enrollment-service computes a student's totals and cumulative GPA during the
transcript aggregation (it already fetches each offering's credits from
course-service): credits earned (COMPLETED), credits in progress (REGISTERED),
and a credit-weighted GPA on a 0-10 scale over completed graded courses. Keeping
this in the service (not the web client) means it is computed once, close to the
data, and reusable - mirroring the "expose an academic-summary endpoint" note
from the FastAPI lab.

## Failure handling (not just the happy path)

The aggregation must not collapse because one downstream is momentarily down.

- **Timeouts.** Feign connect/read timeouts (2s/3s) so a slow downstream fails
  fast instead of hanging the request.
- **Circuit breaker + fallbacks (Resilience4j).** Each Feign call is wrapped in a
  circuit breaker (`spring.cloud.openfeign.circuitbreaker.enabled=true`) with a
  `FallbackFactory`. On failure:
  - course-service down -> the fallback returns a placeholder derived from the
    `offeringCode` itself (course code + term parsed from the key); the row still
    appears, flagged `detailsAvailable=false`.
  - student-service down -> the fallback returns null; the response omits student
    details but still lists the enrollments (which come from this service's own
    DB).
  - The response carries `partial=true` plus human-readable `warnings`, and the
    web client shows a banner. **Degrade, do not fail.**
- **404 vs outage.** A `FallbackFactory` receives the failure cause, so a genuine
  `404` from student-service (the student really does not exist) is rethrown as a
  404, while a real outage (timeout, connection refused, open circuit) degrades
  to partial. Conflating the two would be a lie to the caller.

## Deliberately out of scope (weighed, not skipped)

- **API Gateway (Spring Cloud Gateway):** not added. The rubric does not need a
  single entry point; the web client is the UI and enrollment-service is the
  composition point. A gateway would add a moving part without serving the
  learning goal. Easy to add later.
- **Config Server / externalized config:** not added. Per-service
  `application.yml` is enough; Eureka is the only Spring Cloud infrastructure the
  lab requires.
- **CourseOffering** (year / semester / section / instructor) is included so
  enrollments carry a term and courses show their sections + attendees. Still
  omitted on purpose: capacity, weekly schedule, and registration windows (the
  registration-rules richness from the earlier FastAPI lab), which would add
  domain depth without serving the discovery/Feign learning goal.
- **Writes kept minimal.** The only writes are `POST /api/students` (add student,
  the one create the rubric asks for) and `POST /api/enrollments`. Courses and
  offerings are seed-only; the web client exposes just the add-student form.

## Technology choices

- **Java 17** - the baseline for Spring Boot 4.x, and already the platform's LTS.
- **Spring Boot 4.1.0 + Spring Cloud 2025.1.2 (Oakwood)** - the current GA,
  matched release train. Both Eureka (netflix-eureka-server/-client) and
  OpenFeign ship on this train. Note: Spring Cloud OpenFeign is
  "feature-complete" - Spring steers *new* features toward declarative HTTP
  interface clients (`@HttpExchange` + `RestClient`) - but it is fully supported
  and is what this assignment asks for.
- **Maven, multi-module** - Spring's default and the idiom in every Spring Cloud
  tutorial; the parent POM centralizes versions via the Spring Cloud BOM. One
  reactor build, shared Docker cache. Runtime independence is preserved: each
  module is its own bootable jar / container / port / database.
- **H2 in-memory per service** - the lab is about discovery, not persistence.
  H2 starts instantly with no extra containers; swapping to Postgres later is a
  properties change.

## Build + run under Colima

- **One multi-stage Dockerfile**, module selected by a `MODULE` build-arg, so all
  five images share the (cached) Maven build layers.
- **Corporate TLS:** the build stage imports any CA under `deploy/docker/certs/`
  into the build image's JVM `cacerts` with `keytool`, because Maven validates
  HTTPS against the JVM truststore (not the system CA bundle, and not certifi as
  the earlier Python lab did). Certs are gitignored.
- **docker-compose** starts all five, gated on Eureka + upstreams being healthy
  (curl `/actuator/health`), so the first web request already has a populated
  registry. Eureka lease/fetch intervals are lowered to 10s so registration is
  visible quickly in a demo.

## Edge cases / things to mention when defending

- On a cold start there is still a short window before a just-registered instance
  is discoverable (Eureka is eventually consistent); the healthcheck gating and
  the 10s intervals shrink it.
- The `partial` flag intentionally does not distinguish "student has zero
  enrollments" from "student-service down" at the enrollment level - enrollments
  always come from the local DB; only the student block and per-offering (course)
  details can degrade.
- Tests run against mocked Feign clients (unit) and MockMvc web slices, so they
  need neither a running Eureka nor the other services.
