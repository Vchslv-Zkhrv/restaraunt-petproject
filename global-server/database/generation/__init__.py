from . import reset as _reset


async def generate_default_data():
    await _reset.init_models()
