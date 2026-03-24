FROM node:20-bookworm-slim

# Pin this to a tag or commit for reproducible builds.
ARG PROOF_GIT_REF=main

WORKDIR /opt

RUN apt-get update \
  && apt-get install -y --no-install-recommends git ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/EveryInc/proof-sdk.git proof-sdk \
  && cd proof-sdk \
  && git checkout "${PROOF_GIT_REF}" \
  && npm install \
  && npm run build

WORKDIR /opt/proof-sdk

ENV PORT=4000
EXPOSE 4000

CMD ["npm", "run", "serve"]
