# Docker Containers Logs to Discord Channels

A Python-based application that monitors Docker containers and streams their logs to dedicated Discord channels in real-time. This tool automatically creates Discord text channels for each running container and forwards log entries as messages.

## Features

- **Automatic Channel Creation**: Dynamically creates Discord channels for newly started containers.
- **Real-time Log Streaming**: Continuously monitors and forwards container logs to corresponding Discord channels.
- **Container Lifecycle Management**: Handles container start/stop events, creating/removing channels as needed.
- **Docker Integration**: Uses Docker Python SDK to interact with the Docker daemon.
- **Discord Bot Integration**: Leverages Discord.py for seamless bot functionality.
- **Configurable**: Environment variable-based configuration for easy deployment.

## Prerequisites

- Docker installed and running on the host system
- A Discord bot token (create one at [Discord Developer Portal](https://discord.com/developers/applications))
- Python 3.13+ (for local development)
- Access to a Discord server (guild) where the bot has permissions to create channels

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/dibaltzis/Container-Log-Aggregation-and-Monitoring-to-Discord-channels.git
   cd Container-Log-Aggregation-and-Monitoring-to-Discord-channels
   ```

2. Build the Docker image:
   ```bash
   docker build -t discord-logger .
   ```

3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/dibaltzis/Container-Log-Aggregation-and-Monitoring-to-Discord-channels.git
   cd Container-Log-Aggregation-and-Monitoring-to-Discord-channels
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (see Configuration section).

4. Run the application:
   ```bash
   python src/main.py
   ```

## Configuration

The application is configured via environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_TOKEN` | Discord bot token | Yes | - |
| `GUILD_ID` | Discord server (guild) ID | Yes | - |
| `DOCKER_SOCKET` | Docker socket path | No | `unix:///var/run/docker.sock` |
| `CATEGORY_NAME` | Discord category name for channels | No | `containers-logs` |

### Setting Environment Variables

For Docker Compose, create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_guild_id_here
```

For local development, export them in your shell:

```bash
export DISCORD_TOKEN="your_discord_bot_token_here"
export GUILD_ID="123456789012345678"
```

## Usage

1. Ensure your Discord bot has the following permissions in your server:
   - Manage Channels
   - Send Messages
   - Read Message History

2. Start the application using Docker Compose or locally.

3. The bot will:
   - Connect to your Discord server
   - Create a category named "containers-logs" (or your configured name)
   - Monitor running Docker containers
   - Create a text channel for each container
   - Stream logs from each container to its respective channel

4. View logs in real-time by checking the Discord channels.

## Docker Compose Configuration

The included `docker-compose.yml` mounts the Docker socket to allow the container to monitor other containers. Ensure your user has permissions to access `/var/run/docker.sock`.

## Architecture

- `main.py`: Entry point, orchestrates monitoring and Discord bot
- `docker_side.py`: Handles Docker container monitoring and log streaming
- `discord_side.py`: Manages Discord bot, channel creation, and message sending

## Troubleshooting

### Common Issues

1. **Permission Denied on Docker Socket**:
   - Ensure the user running the container has access to `/var/run/docker.sock`
   - On Linux, you might need to add the user to the `docker` group

2. **Discord Bot Permissions**:
   - Verify the bot has "Manage Channels" permission in the server
   - Check that the `GUILD_ID` is correct

3. **No Logs Appearing**:
   - Confirm containers are running: `docker ps`
   - Check application logs for errors
   - Ensure Discord bot is online in your server

### Logs

Application logs are printed to stdout. When running in Docker, view them with:

```bash
docker-compose logs -f discord-logger
```
