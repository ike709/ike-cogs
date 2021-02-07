#Standard Imports
import asyncio
import logging
import traceback

#Discord Imports
import discord

#Redbot Imports
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify, box, humanize_list, warning
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

#API Client
import swagger_client
from swagger_client.rest import ApiException
from swagger_client.configuration import Configuration

#Util imports
from .util import parse_ex

# TODO: Cleanup imports

__version__ = "0.0.1"
__author__ = "ike709"

log = logging.getLogger("red.SS13TGS4")

BaseCog = getattr(commands, "Cog", object)

class Tgs4(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 709709709, force_registration=True)

        default_guild = {
            "tgs_host": "http://127.0.0.1",
            "tgs_port": 8080,
            "tgs_authenticated": False,
            "tgs_api": "Tgstation.Server.Api",
            "tgs_api_version": "8.3.0",
            "tgs_user_agent": "tgstation-server-redbot-cog"
        }

        self.config.register_guild(**default_guild)
        self.loop = asyncio.get_event_loop()

        self.tgs_config = None
        self.api_client = None

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
        Sets the TGS4 host, defaults to localhost (http://127.0.0.1:8080)
        """
        try:
            if tgs_host.startswith("https"):
                await ctx.send("Error: The host must be HTTP, not HTTPS.")
                return
            tgs_host = tgs_host.rstrip("/") # No trailing /
            if tgs_host[1].isdigit(): # They forgot the http:// prefix
                tgs_host = f"http://{tgs_host}"
            host_split = tgs_host.split(":")
            if len(host_split) == 2: # They didn't include a port so just use the existing one
                port = await self.config.guild(ctx.guild).tgs_port()
                host_split.append(str(port))
            elif int(host_split[2]) not in range(1024, 65536): # We don't want to allow reserved ports to be set             
                await ctx.send(f"Error: {host_split[2]} is not a valid port! Please check to ensure you're attempting to use a port from 1024 to 65535.")
                return
            else: # Set the new, valid port
                await self.config.guild(ctx.guild).tgs_port.set(host_split[2])
            tgs_host = f"{host_split[0]}:{host_split[1]}"
            await self.config.guild(ctx.guild).tgs_host.set(tgs_host)
            await self.reload_tgs_config(ctx)
            await ctx.send(f"TGS host set to: `{await self.get_url(ctx)}`") # Use get_url() so the user sees exactly how the cog interprets the data
        except:
            await ctx.send("There was an error setting the TGS4 host URL. Please check your entry and try again!")
    
    @tgs4.command()
    @checks.is_owner()
    async def api(self, ctx, tgs_api: str):
        """
        Sets the TGS4 API header (minus the version), defaults to Tgstation.Server.Api. You typically shouldn't ever need to use this command.
        """
        try:
            await self.config.guild(ctx.guild).tgs_api.set(tgs_api)
            tgs_api = tgs_api.rstrip("/")
            if tgs_api[-1].isdigit():
                await ctx.send("Error: Do not include the version in the API.")
                return
            await ctx.send(f"TGS API set to: `{tgs_api}`")
            await ctx.send(f"TGS API header: `{await self.get_api_header(ctx)}`")
        except Exception as err:
            await ctx.send("There was an error setting the API: {0}".format(err))
    
    @tgs4.command()
    @checks.is_owner()
    async def agent(self, ctx, tgs_user_agent: str):
        """
        Sets the User-Agent header, defaults to tgstation-server-redbot-cog
        """
        try:
            await self.config.guild(ctx.guild).tgs_user_agent.set(tgs_user_agent)
            await ctx.send(f"User-Agent set to: `{tgs_user_agent}`")
        except (ValueError, KeyError, AttributeError) as err:
            await ctx.send("There was an error setting the User-Agent header: {0}".format(err))
    
    async def get_url(self, ctx):
        try:
            url = await self.config.guild(ctx.guild).tgs_host() + ":{0}".format(await self.config.guild(ctx.guild).tgs_port())
            return url
        except Exception as err:
            await ctx.send("There was an error getting the URL: {0}".format(err))

    async def get_api_header(self, ctx):
        try:
            header = str(await self.config.guild(ctx.guild).tgs_api()) + "/" + str(await self.config.guild(ctx.guild).tgs_api_version()),
            header = "".join(header) # For some reason header is a fucking tuple
            return str(header)
        except Exception as err:
            await ctx.send("There was an error getting the API header: {0}".format(err))
    
    async def get_tgs_config(self, ctx):
        try:
            if self.tgs_config is None:
                self.tgs_config = Configuration()
                self.tgs_config.host = await self.get_url(ctx)
            return self.tgs_config
        except Exception as err:
            await ctx.send("There was an error getting the TGS config: {0}".format(err))
    
    async def get_api_client(self, ctx):
        try:
            if self.api_client is None:
                self.api_client = swagger_client.ApiClient(await self.get_tgs_config(ctx))
            return self.api_client
        except ApiException as err:
            parse_ex(ctx, err)
        except Exception as err:
            await ctx.send("There was an error getting the API client: {0}".format(err))
    
    async def reload_tgs_config(self, ctx):
        try:
            self.tgs_config = None
            self.api_client = None
            self.api_client = await self.get_api_client(ctx) # ALso sets tgs_config
        except Exception as err:
            await ctx.send("There was an error reloading the TGS config: {0}".format(err))
    
    @tgs4.command()
    @checks.mod_or_permissions(administrator=True)
    async def config(self, ctx):
        """
        Displays basic config info.
        """
        try:
            url = await self.get_url(ctx)
            api = await self.get_api_header(ctx)
            agent = await self.config.guild(ctx.guild).tgs_user_agent()
            await ctx.send("Server URL: `{0}`\nCog API: `{1}`\nUser-Agent: `{2}`".format(url, api, agent))
        except Exception as err:
            await ctx.send("There was an error retrieving config info: {0}".format(err))

    @tgs4.command()
    @checks.mod_or_permissions(administrator=True)
    async def info(self, ctx):
        """
        Retrieves basic TGS server info.
        """
        try:
            #await ctx.send(await self.get_url(ctx))
            api_instance = swagger_client.HomeApi(await self.get_api_client(ctx))
            api_response = api_instance.home_controller_home(await self.get_api_header(ctx), await self.config.guild(ctx.guild).tgs_user_agent())
            await ctx.send(api_response)
        except ApiException as err:
            parse_ex(ctx, err)
        except Exception as err:
            await ctx.send("There was an error retrieving the TGS info: {0}".format(err))
            #await ctx.send(traceback.print_exc())