# filename: redis_notification_main.py
import asyncio
import sys
sys.path.append('.')
from memcached_lite import RedisNotificationServer

def main():
    print("Running RedisNotificationServer")
    server = RedisNotificationServer()

    async def run_server():
        try:
            await server.start()
        except asyncio.CancelledError:
            pass  # Ignore cancellation errors
        finally:
            # Call shutdown() if you have implemented any clean-up in your server class.
            try:
                await server.shutdown()
            except Exception as e:
                print("Error during shutdown:", e)
            print("RedisNotificationServer has been shut down gracefully.")

    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting gracefully...")
        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks(loop=loop) if not t.done()]
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    finally:
        loop.close()

if __name__ == '__main__':
    main()
