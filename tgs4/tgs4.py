#Standard Imports
import asyncio
import socket
import ipaddress
import re
import logging
from typing import Union
import json
import requests
import urllib.parse

#Discord Imports
import discord

#Redbot Imports
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify, box, humanize_list, warning
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

#Util Imports
from .util import key_to_ckey

# TODO: Cleanup imports

__version__ = "0.0.1"
__author__ = "ike709"

log = logging.getLogger("red.SS13TGS4")

BaseCog = getattr(commands, "Cog", object)

class Tgs4(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier, force_registration=True) # Wtf do I set identifier to?

        default_guild = {
            "tgs_host": "127.0.0.1",
            "tgs_port": 8080,
            "tgs_authenticated": False,
            "tgs_api": "Tgstation.Server.Api",
            "tgs_api_version": "8.2.0",
            "tgs_user_agent": "tgstation-server-redbot-cog"
        }

        self.config.register_guild(**default_guild)
        self.loop = asyncio.get_event_loop()
    

    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(administrator=True)
    async def tgs4(self,ctx): 
        """
        SS13 TGS4
        """
        pass

    @tgs4.command()
    @checks.is_owner()
    async def host(self, ctx, tgs_host: str):
        """
        Sets the TGS4 host, defaults to localhost (127.0.0.1)
        """
        try:
            await self.config.guild(ctx.guild).tgs_host.set(tgs_host)
            await ctx.send(f"TGS host set to: `{tgs_host}`")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the TGS4 ip/hostname. Please check your entry and try again!")
    

    @tgs4.command()
    @checks.is_owner()
    async def port(self, ctx, tgs_port: int):
        """
        Sets the TGS4 port, defaults to 8080.
        """
        try:
            if 1024 <= tgs_port <= 65535: # We don't want to allow reserved ports to be set
                await self.config.guild(ctx.guild).tgs_port.set(tgs_port)
                await ctx.send(f"Database port set to: `{db_port}`")
            else:
                await ctx.send(f"{tgs_port} is not a valid port! Please check to ensure you're attempting to use a port from 1024 to 65535.")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was a problem setting your port. Please check to ensure you're attempting to use a port from 1024 to 65535.") 
    
    @tgs4.command()
    @checks.is_owner()
    async def api(self, ctx, tgs_api: str):
        """
        Sets the TGS4 Api header (minus the version), defaults to Tgstation.Server.Api
        """
        try:
            await self.config.guild(ctx.guild).tgs_api.set(tgs_api)
            await ctx.send(f"TGS API set to: `{tgs_api}`")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the API. Please check your entry and try again!")
    
    @tgs4.command()
    @checks.is_owner()
    async def api_version(self, ctx, tgs_api_version: str):
        """
        Sets the TGS4 API version, defaults to 8.2.0
        """
        try:
            await self.config.guild(ctx.guild).tgs_api_version.set(tgs_api_version)
            await ctx.send(f"TGS API version set to: `{tgs_api_version}`")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the API version. Please check your entry and try again!")
    
    @tgs4.command()
    @checks.is_owner()
    async def user_agent(self, ctx, tgs_user_agent: str):
        """
        Sets the User-Agent header, defaults to tgstation-server-redbot-cog
        """
        try:
            await self.config.guild(ctx.guild).tgs_user_agent.set(tgs_user_agent)
            await ctx.send(f"User-Agent set to: `{tgs_user_agent}`")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the User-Agent header. Please check your entry and try again!")

    @tgs4.command()
    @checks.is_owner()
    async def user_agent(self, ctx, tgs_user_agent: str):
        """
        Sets the User-Agent header, defaults to tgstation-server-redbot-cog
        """
        try:
            await self.config.guild(ctx.guild).tgs_user_agent.set(tgs_user_agent)
            await ctx.send(f"User-Agent set to: `{tgs_user_agent}`")
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the User-Agent header. Please check your entry and try again!")
    
    async def get_url(self, ctx):
        try:
            url = self.config.guild(ctx.guild).tgs_host + ":" + str(self.config.guild(ctx.guild).tgs_port)
            return url
        except:
            await ctx.send("There was an error getting the URL.")

    async def get_headers(self, ctx):
        try:
            headers = {'User-Agent': self.config.guild(ctx.guild).tgs_user_agent, 'Api': self.config.guild(ctx.guild).tgs_api + '/' + self.config.guild(ctx.guild).tgs_api_version}
            return headers
        except:
            await ctx.send("There was an error getting the headers.")
    
    @tgs4.command()
    @checks.mod_or_permissions(administrator=True)
    async def info(self, ctx):
        """
        Retrieves basic TGS server info.
        """
        try:
            r = requests.get(get_url(), headers = get_headers())
            await ctx.send(r.text)
        except (ValueError, KeyError, AttributeError):
            await ctx.send("There was an error setting the User-Agent header. Please check your entry and try again!")