# filename: redis_lite_main.py
import sys
sys.path.append(".")
import asyncio
from memcached_lite import RedisLiteServer

if __name__ == '__main__':
    print("running RedisLiteServer")
    server = RedisLiteServer()

    async def main():
        """Gracefully handle shutdown signals and exceptions."""
        try:
            await server.start()
        except asyncio.CancelledError:
            pass  # Ignore cancellation errors
        finally:
            await server.shutdown()
            print("RedisLiteServer has been shut down gracefully.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def shutdown():
        """Stop the server and close the event loop."""
        print("\nReceived shutdown signal. Stopping RedisLiteServer...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting...")
        loop.run_until_complete(shutdown())
    finally:
        loop.close()
