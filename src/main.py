import asyncio
import configparser
from docker_side import DockerMonitor
from discord_side import DiscordLogBot
import os

CHECK_INTERVAL = 10  # seconds

if __name__ == "__main__":

    # ----- Read environment variables -----
    discord_token = os.getenv("DISCORD_TOKEN")
    guild_id = int(os.getenv("GUILD_ID", "0"))
    docker_socket = os.getenv("DOCKER_SOCKET", "unix:///var/run/docker.sock").strip('"')
    category_name = os.getenv("CATEGORY_NAME", "containers-logs")

    if not discord_token or not guild_id:
        print("[ERROR] Missing environment variables DISCORD_TOKEN or DISCORD_GUILD_ID")
        exit(1)


    # ----- Start Discord bot -----
    bot = DiscordLogBot(
        token=discord_token,
        guild_id=guild_id,
        category_name="containers-logs",
        container_names=[] 
    )

    monitor = DockerMonitor(base_url=docker_socket)
    monitored_containers = set()

    async def monitor_loop():
            """Continuously check for new or stopped containers."""
            await bot.bot.wait_until_ready()  
            guild = await bot.bot.fetch_guild(bot.guild_id)
            if guild is None:
                print("[ERROR] Guild not found — cannot manage channels.")
                return
            while True:
                try:
                    current_containers = {
                        c.name for c in monitor.client.containers.list(filters={"status": "running"})
                    }

                    # Detect new containers
                    new_containers = current_containers - monitored_containers
                    stopped_containers = monitored_containers - current_containers
                    if new_containers:
                        print(f"[NEW] Containers started: {', '.join(sorted(new_containers))}")
                        for name in new_containers:
                            # Create Discord channel on the fly
                            await bot.ensure_channels([name], bot.bot.get_guild(bot.guild_id))

                            # Start log streaming
                            monitor.add_container(
                                name,
                                callback=lambda log_entry, cname=name: asyncio.run_coroutine_threadsafe(
                                    bot.send_log(cname, log_entry),
                                    bot.loop
                                )
                            )

                    # Detect stopped containers
                    if stopped_containers:
                        print(f"[STOPPED] Containers stopped: {', '.join(sorted(stopped_containers))}")
                        for stopped_name in stopped_containers:
                            log_obj = monitor.containers.pop(stopped_name, None)
                            if log_obj:
                                log_obj.stop_stream()


                    # Update the tracked set
                    monitored_containers.clear()
                    monitored_containers.update(current_containers)
                except Exception as e:
                    print(f"[ERROR] In monitor loop: {e}")

                await asyncio.sleep(CHECK_INTERVAL)

    # ----- Run monitor loop -----
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_loop())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping monitor and bot...")