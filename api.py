import aiohttp

BASE_URL = "https://www.gazbalon.retraining.uz/api/v1"
GAZBALON_DETAIL_URL = "https://www.gazbalon.retraining.uz/api/v1/gazbalon/"
ORDER_DETAIL_URL = "https://www.gazbalon.retraining.uz/api/v1/orders/"
SITE_URL = "https://www.gazbalon.retraining.uz/admin/"

async def get_gazbalon_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GAZBALON_DETAIL_URL}{url}/") as response:
            return {
                "status_code": response.status,
                "data": await response.json(),

            }

async def gazbalon_add_new_last_data(gazbalon_id, new_status):
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{GAZBALON_DETAIL_URL}{gazbalon_id}/", data={"last_status": new_status}) as response:
            return {
                "status_code": response.status,
                "data": await response.json(),

            }

async def order_create(gazbalon, user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(ORDER_DETAIL_URL, data={"gazbalon": gazbalon, "user_id": user_id}) as response:
            return {
                "status_code": response.status,
                "data": await response.json(),

            }

async def get_last_order(gazbalon_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/last-order/{gazbalon_id}/") as response:
            return {
                "status_code": response.status,
                "data": await response.json(),

            }

async def get_gazbalon_id(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/gazbalon-id/{id}/") as response:
            return {
                "status_code": response.status,
                "data": await response.json(),

            }