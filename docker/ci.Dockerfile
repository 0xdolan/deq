# syntax=docker/dockerfile:1
# Clean, pinned toolchain image that runs `just ci` (PRD §13).
FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv

FROM node:24-bookworm-slim@sha256:01d566e8d94d8c619591d78652babfccd3c6992a3dffa9ed5ab39e11cf6c70e9

ARG JUST_VERSION=1.59.0
ARG JUST_SHA256=409044617b6f06517c1035e55ca38c8c856ff8b650e41bc2aa1ef82d5903a23e
ARG GITLEAKS_VERSION=8.30.1
ARG GITLEAKS_SHA256=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
ARG ACTIONLINT_VERSION=1.7.12
ARG ACTIONLINT_SHA256=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
ARG CARGO_DENY_VERSION=0.20.2
ARG CARGO_DENY_SHA256=9f12ed4c49936e09b48bf862b595cde2fe64fcbd9d74dfacac6131ca824c8d5f
ARG RUSTUP_VERSION=1.29.3
ARG RUSTUP_SHA256=b1c8cb14e30889e7e2999e6b69e62d9e9b9ffc0f4df8180564d306d9680e6c55

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /usr/local/bin/

# Download a release archive, verify its SHA-256, extract one binary into /usr/local/bin.
RUN fetch() { \
      local url=$1 sha=$2 bin=$3 tmp; tmp=$(mktemp -d); \
      curl --proto '=https' --tlsv1.2 -fsSL "$url" -o "$tmp/a.tgz"; \
      echo "$sha  $tmp/a.tgz" | sha256sum -c -; \
      tar -xzf "$tmp/a.tgz" -C "$tmp"; \
      install -m 0755 "$(find "$tmp" -type f -name "$bin" | head -1)" /usr/local/bin/; \
      rm -rf "$tmp"; }; \
    fetch "https://github.com/casey/just/releases/download/${JUST_VERSION}/just-${JUST_VERSION}-x86_64-unknown-linux-musl.tar.gz" "$JUST_SHA256" just; \
    fetch "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" "$GITLEAKS_SHA256" gitleaks; \
    fetch "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz" "$ACTIONLINT_SHA256" actionlint; \
    fetch "https://github.com/EmbarkStudios/cargo-deny/releases/download/${CARGO_DENY_VERSION}/cargo-deny-${CARGO_DENY_VERSION}-x86_64-unknown-linux-musl.tar.gz" "$CARGO_DENY_SHA256" cargo-deny

RUN corepack enable

# Everything below runs as the unprivileged `node` user (uid 1000).
USER node
ENV HOME=/home/node \
    PATH=/home/node/.cargo/bin:$PATH \
    LEFTHOOK=0 \
    UV_LINK_MODE=copy \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

RUN curl --proto '=https' --tlsv1.2 -fsSL \
      "https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/x86_64-unknown-linux-gnu/rustup-init" -o /tmp/rustup-init \
 && echo "${RUSTUP_SHA256}  /tmp/rustup-init" | sha256sum -c - \
 && chmod +x /tmp/rustup-init \
 && /tmp/rustup-init -y --profile minimal --default-toolchain none --no-modify-path \
 && rm /tmp/rustup-init

WORKDIR /workspace
COPY --chown=node:node . .

RUN rustup toolchain install \
 && pnpm install --frozen-lockfile \
 && uv sync --frozen

CMD ["just", "ci"]
