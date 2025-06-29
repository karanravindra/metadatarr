# main.py
import os
import sys
import logging
import time
import qbittorrentapi
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger("metadatarr")

# silence third-party DEBUG/INFO chatter
for noisy in ("urllib3", "requests", "qbittorrentapi"):
    logging.getLogger(noisy).setLevel(logging.CRITICAL)


def get_client() -> qbittorrentapi.Client | None:
    client = qbittorrentapi.Client(
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 8080)),
        username=os.getenv("USERNAME", "admin"),
        password=os.getenv("PASSWORD", "adminadmin"),
    )
    try:
        client.auth_log_in()
        logger.info("Connected to qBittorrent.")
        return client
    except qbittorrentapi.LoginFailed:
        logger.error("Bad qBittorrent credentials.")
    except qbittorrentapi.APIConnectionError as e:
        logger.error(
            "Cannot reach qBittorrent at %s:%s - %s", client.host, client.port, e
        )
    except Exception as e:
        logger.error("Unexpected error talking to qBittorrent: %s", e)
    return None  # caller can decide what to do next


def main() -> None:
    logger.info("Starting metadatarr…")
    client = get_client()
    if client is None:
        sys.exit(1)  # no stack-trace, clean exit
    while True:
        try:
            logger.info("Fetching torrents…")

            for t in client.torrents_info():
                if (
                    t.has_metadata
                    and t.state == qbittorrentapi.TorrentState.DOWNLOADING
                ):
                    logger.debug("Torrent %s already has metadata.", t.name)
                    continue

                elif (
                    not t.has_metadata
                    and t.state == qbittorrentapi.TorrentState.QUEUED_DOWNLOAD
                ):
                    logger.info("Torrent %s is missing metadata. Downloading…", t.name)
                    client.torrents.set_force_start(torrent_hashes=t.hash)

                    # Wait for metadata to be downloaded
                    logger.info("Waiting for torrent %s to download metadata…", t.name)
                    while True:
                        time.sleep(5)  # Check every 5 seconds
                        updated_torrent = client.torrents_info(torrent_hashes=t.hash)[0]
                        if updated_torrent.has_metadata:
                            logger.info(
                                "Torrent %s has metadata. Stopping download…", t.name
                            )
                            client.torrents.set_force_start(
                                torrent_hashes=t.hash, enable=False
                            )
                            break
                        logger.debug(
                            "Still waiting for metadata for torrent %s…", t.name
                        )

        except qbittorrentapi.APIConnectionError as exc:
            logger.error("Lost connection: %s", exc)
        except Exception as exc:
            logger.error("Runtime error: %s", exc)
        finally:
            logger.info("Sleeping for %s seconds…", os.getenv("INTERVAL", 60))
            time.sleep(int(os.getenv("INTERVAL", 60)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting gracefully…")
