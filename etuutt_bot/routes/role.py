from os import getenv

import aiohttp_jinja2
from aiohttp import web


async def handler(req: web.Request) -> web.Response:
    if req.method != "POST":
        return web.HTTPMethodNotAllowed(req.method, ["POST"])  # HTTP 405
    post = await req.post()
    if "etu-token" and "discord-username" in post:
        if post.get("check-GDPR") != "on":
            return await aiohttp_jinja2.render_template_async(
                "error.html.jinja",
                req,
                {
                    "error": "Vous n'avez pas coché la case de consentement RGPD. "
                    "Vos données n'ont pas été traitées."
                },
            )
        params = {"access_token": post.get("etu-token")}
        async with req.app["bot"].session.get(
            f"{getenv('API_URL')}/public/user/account", params=params
        ) as response:
            if response.status != 200:
                return web.Response(status=response.status)
            resp: dict = (await response.json()).get("data")
            if all(  # Check if the fields we need are present
                field in resp
                for field in [
                    "isStudent",
                    "firstName",
                    "lastName",
                    "formation",
                    "branch_list",
                    "branch_level_list",
                    "uvs",
                ]
            ):
                return web.Response(
                    text=f"{post.get('discord-username')}\n{resp.get('firstName')}"
                )
                # TODO: process information in another file
    return web.HTTPBadRequest()
