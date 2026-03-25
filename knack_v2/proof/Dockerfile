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
  && node -e "const fs=require('fs'); const file='server/index.ts'; const needle=\"app.use(express.static(path.join(__dirname, '..', 'public')));\"; const replacement=\"app.use(express.static(path.join(__dirname, '..', 'public'))); app.use('/assets', express.static(path.join(__dirname, '..', 'dist', 'assets'))); app.use(express.static(path.join(__dirname, '..', 'dist')));\"; const source=fs.readFileSync(file,'utf8'); if(!source.includes(needle)) throw new Error('Could not find static mount in server/index.ts'); fs.writeFileSync(file, source.replace(needle, replacement));" \
  && npm install \
  && npm run build

WORKDIR /opt/proof-sdk

ENV PORT=4000
EXPOSE 4000

CMD ["npm", "run", "serve"]
