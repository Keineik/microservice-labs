# Course Registration Microservices (Lab 1 - Spring Boot + Spring Cloud)

A small microservice system for course registration, built to demonstrate
**service discovery (Eureka)** and **inter-service communication (OpenFeign)**.
Each service is independent, registers with Eureka, and calls the others **by
service name** (never a hardcoded URL).

## Architecture

```
                        +-------------------+
        browser ------> |    web-client     |  (Thymeleaf UI, :8080)
                        +---------+---------+
                                  | Feign (by name, via Eureka)
             +--------------------+--------------------+
             v                                         v
     +---------------+                        +----------------------+
     | student-svc   | <----- Feign --------- |  enrollment-service  |
     | (:8081, H2)   |                        |  (:8083, H2)         |
     +---------------+                        +----------+-----------+
                                                         | Feign
     +---------------+                                   v
     | course-svc    | <---------------------------------+
     | (:8082, H2)   |
     +---------------+

           all services register with / are discovered through
                    +-------------------------------+
                    | discovery-server (Eureka :8761)|
                    +-------------------------------+
```

| Service | Port | Owns | Key endpoints |
|---|---|---|---|
| discovery-server | 8761 | the Eureka registry | dashboard at `/` |
| student-service | 8081 | students (H2) | `GET /api/students`, `GET /api/students/{code}`, `POST /api/students` |
| course-service | 8082 | courses (H2) | `GET /api/courses`, `GET /api/courses/{code}` |
| enrollment-service | 8083 | enrollments (H2) | `GET /api/enrollments/student/{code}` (aggregation), `POST /api/enrollments` |
| web-client | 8080 | nothing (UI only) | `/`, `/students/{code}` |

- **No shared database.** Each service has its own in-memory H2, seeded on
  startup. enrollment-service stores only the business keys (`studentCode`,
  `courseCode`) and resolves details from the other services at read time.
- **Stack:** Java 17, Spring Boot 4.1.0, Spring Cloud 2025.1.2 (Oakwood),
  Maven (multi-module). See [`docs/design_notes.md`](docs/design_notes.md) for
  the rationale.

## Prerequisites

- Docker (Colima or Docker Desktop). No host Java/Maven install is required -
  everything builds inside containers.
- For the report only: `pandoc` and `typst` (`brew install pandoc typst`).

## Quick start

```bash
make up      # build all images and start the whole stack
make ps      # watch containers become healthy
```

Then open:

- **Eureka dashboard:** http://localhost:8761 (all four services listed under
  "Instances currently registered with Eureka")
- **Web client:** http://localhost:8080 (student list -> click "Xem đăng ký"
  to see a student's enrolled courses)

The first `make up` downloads Maven dependencies inside the build image, so it
takes a few minutes. Subsequent builds are cached.

```bash
make logs s=enrollment-service   # tail one service
make down                        # stop everything
```

### Try the graceful degradation

The aggregation in enrollment-service uses **Resilience4j** fallbacks. To see a
partial (not failed) response when a downstream is down:

```bash
docker compose -f deploy/compose/docker-compose.yml stop course-service
```

Reload a student page: the enrolled courses still list (with codes and status
from enrollment-service's own DB), the missing course titles are marked
unavailable, and a warning banner appears. Restart with:

```bash
docker compose -f deploy/compose/docker-compose.yml start course-service
```

## Tests

```bash
make test    # runs all unit tests inside the Docker build image
```

## Corporate TLS interception (Cloudflare WARP / Zscaler)

Maven resolves dependencies over HTTPS against the **JVM truststore**, so behind
an SSL-inspecting proxy the build can fail cert validation. If that happens, drop
the corporate CA (PEM, `.crt`) into `deploy/docker/certs/` and rebuild - the
Dockerfile imports every `*.crt` there into the build image's `cacerts` via
`keytool`. That directory is gitignored (certs are machine-specific and must
never be committed).

## Report

```bash
make report  # builds report/report.pdf from report/*.md (Pandoc + Typst)
```

Diagrams are Mermaid code blocks; install `mermaid-filter` (`npm i -g
mermaid-filter`) to render them as images, otherwise they appear as code.

## Project layout

```
lab-1-springboot/
  pom.xml                      parent POM (Boot parent + Spring Cloud BOM, Java 17)
  discovery-server/            Eureka server
  student-service/             students  (web + JPA + H2 + Eureka)
  course-service/              courses   (web + JPA + H2 + Eureka)
  enrollment-service/          enrollments + Feign + Resilience4j aggregation
  web-client/                  Thymeleaf UI (Feign, no DB)
  deploy/docker/Dockerfile     multi-stage build (CA -> JVM truststore)
  deploy/compose/              docker-compose.yml (5 services, Eureka-gated)
  docs/design_notes.md         engineering rationale + trade-offs
  report/                      Vietnamese report (Pandoc + Typst)
  Makefile
```
