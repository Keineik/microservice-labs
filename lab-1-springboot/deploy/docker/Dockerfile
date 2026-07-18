# syntax=docker/dockerfile:1

# ============================ Build stage ============================
# One reactor build produces every module's jar. The runtime stage then
# copies just the one selected by the MODULE build-arg, so all five images
# share these (cached) build layers.
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /workspace

# --- Corporate TLS interception support ----------------------------------
# If a CA cert is placed under deploy/docker/certs/ (gitignored, machine-
# specific), import it into the JVM truststore so Maven can reach Maven Central
# through an SSL-inspecting proxy such as Cloudflare WARP or Zscaler.
# NOTE: Maven validates HTTPS against the *JVM* truststore (cacerts), not the
# system CA bundle, so this uses keytool -cacerts rather than
# update-ca-certificates. No-op when the directory holds no *.crt.
COPY deploy/docker/certs/ /tmp/certs/
RUN set -eu; \
    for c in /tmp/certs/*.crt; do \
      [ -e "$c" ] || continue; \
      echo "Importing CA $(basename "$c") into the JVM truststore"; \
      keytool -importcert -noprompt -trustcacerts \
        -alias "corp-$(basename "$c" .crt)" \
        -file "$c" -cacerts -storepass changeit; \
    done

# --- Dependency layer (cache-friendly) -----------------------------------
# Copy only the POMs first, then resolve dependencies. This layer is reused
# across code changes; it only rebuilds when a POM changes.
COPY pom.xml .
COPY discovery-server/pom.xml discovery-server/
COPY student-service/pom.xml student-service/
COPY course-service/pom.xml course-service/
COPY enrollment-service/pom.xml enrollment-service/
COPY web-client/pom.xml web-client/
RUN mvn -B -ntp dependency:go-offline || true

# --- Compile + package ----------------------------------------------------
COPY . .
RUN mvn -B -ntp -DskipTests clean package

# ============================ Runtime stage ==========================
FROM eclipse-temurin:17-jre AS runtime

# curl backs the docker-compose healthchecks (probing /actuator/health).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Which module's jar to run - overridden per service in docker-compose.yml.
ARG MODULE
COPY --from=build /workspace/${MODULE}/target/*.jar /app/app.jar

# Run as a non-root user. Do not pin the UID: the eclipse-temurin (Ubuntu) base
# already ships a default user at UID 1000, so let useradd pick a free one.
RUN useradd --create-home appuser
USER appuser

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
