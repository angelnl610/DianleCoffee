import asyncio

from apify import Actor

from src.operations import execute


async def main():
    async with Actor:
        try:
            records = execute(await Actor.get_input())
            for key, value in records.items():
                if key in ("CAFE_RAW", "CAFE_CLEAN"):
                    await Actor.set_value(key, value, content_type="text/csv; charset=utf-8")
                else:
                    await Actor.set_value(key, value)
        except ValueError as error:
            await Actor.set_value("OUTPUT", {"status": "error", "error": str(error)})
            raise
        except Exception:
            await Actor.set_value("OUTPUT", {"status": "error", "error": "Error interno. Revisá el log del Actor."})
            raise


if __name__ == "__main__":
    asyncio.run(main())
