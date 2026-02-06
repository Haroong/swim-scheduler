# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm ci

# 소스 코드 복사 및 빌드
COPY . .
ENV VITE_API_BASE_URL=""
ENV VITE_GA_MEASUREMENT_ID="G-HMQHJEH62Q"
RUN npm run build

# Production stage
FROM nginx:alpine

# Nginx 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
