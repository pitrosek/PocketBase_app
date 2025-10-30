# Dockerfile pro PocketBase
FROM alpine:3.18

# Nastavení pracovního adresáře
WORKDIR /app

# Stažení PocketBase (změňte verzi dle potřeby)
ENV PB_VERSION=0.22.11
RUN wget https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_$(uname -m).zip \
    && unzip pocketbase_$(uname -m).zip \
    && rm pocketbase_$(uname -m).zip \
    && chmod +x pocketbase

# Exponování portu
EXPOSE 8090

# Spuštění PocketBase
CMD ["./pocketbase", "serve", "--http=0.0.0.0:8090"]
