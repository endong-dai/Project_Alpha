import asyncio
import os
import sys
import traceback

IS_WEB = sys.platform == "emscripten"


def startup_log(message):
    if not IS_WEB:
        return

    print(message)
    try:
        import platform

        platform.window.console.log(message)
    except Exception:
        pass


if IS_WEB:
    startup_log("START main.py")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

startup_log("BEFORE importing pygame runtime")
import pygame  # Ensure pygbag resolves the pygame runtime package during startup.
startup_log("AFTER importing pygame runtime")

startup_log("BEFORE importing gui_main")
import gui_main
startup_log("AFTER importing gui_main")


async def main():
    try:
        try:
            gui_main.init_game()
            startup_log("BEFORE entering loop")
            running = True
            while running:
                running = gui_main.run_frame()
                await asyncio.sleep(0)
        except Exception as exc:
            formatted = traceback.format_exc()
            print(formatted)

            if IS_WEB:
                try:
                    import platform

                    platform.window.console.error(formatted)
                except Exception:
                    pass

                gui_main.show_startup_error(type(exc).__name__, str(exc))
                for _ in range(300):
                    await asyncio.sleep(0)
            else:
                raise
    finally:
        gui_main.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
