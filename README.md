# Python: DirecTV (SHEF) Client

Asynchronous Python client for DirectV receivers.

## Aboout

This package allows you to ....

## Installation

```bash
pip install directv
```

## Usage

```python
import asyncio

from directv import DIRECTV


async def main():
    """Show example of connecting to your DIRECTV receiver."""
    async with DIRECTV("192.168.1.100") as dtv:
        print(dtv)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
