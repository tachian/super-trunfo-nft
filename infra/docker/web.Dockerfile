FROM node:22-alpine AS runtime

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /repo

RUN corepack enable

COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/api-contracts/package.json ./packages/api-contracts/package.json
COPY smart-contracts/package.json ./smart-contracts/package.json

RUN pnpm install --filter @super-trunfo/web --frozen-lockfile=false

COPY apps/web ./apps/web

RUN pnpm --filter @super-trunfo/web build

EXPOSE 3000

CMD ["pnpm", "--filter", "@super-trunfo/web", "start"]

