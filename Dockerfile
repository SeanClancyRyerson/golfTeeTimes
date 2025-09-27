FROM python:3.13-slim

#This is to get the print()s in the python show up immediately in the docker logs
ENV PYTHONUNBUFFERED=1

#Set the dir in the contianer
WORKDIR /app

# Copy requirements first so Docker can cache dependency installs
COPY requirements.txt ./

# Install build tools, install python deps, then purge build tools in the same layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

#Copy rest of the code
COPY . .

#Run the bot
CMD ["python", "discord_bot.py"]

#command to build and push multi-arch image
#docker buildx build --platform linux/amd64,linux/arm64 -t nickyparekh/golf-goon-finder:latest --push .