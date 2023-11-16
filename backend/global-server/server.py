from fastapi import FastAPI


api = FastAPI()


@api.head("/", status_code=204)
async def handshake():
    pass

