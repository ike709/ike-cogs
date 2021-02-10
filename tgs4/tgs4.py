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
from .util import acknowledge
from .util import Api

# TODO: Cleanup imports

__version__ = "0.0.1"
__author__ = "ike709"

log = logging.getLogger("red.SS13TGS4")

BaseCog = getattr(commands, "Cog", object)

class Tgs4(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 709709709, force_registration=True)

        default_global = {
            "guild_id": None,
            "tgs_host": "http://127.0.0.1",
            "tgs_port": 8080,
            "tgs_api": "Tgstation.Server.Api",
            "tgs_api_version": "8.3.0",
            "tgs_user_agent": "tgstation-server-redbot-cog",
            "tgs_auth_token": None,
            "tgs_username": None,
            "tgs_password": None
        }

        self.config.register_global(**default_global)
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
                port = await self.config.tgs_port()
                host_split.append(str(port))
            elif int(host_split[2]) not in range(1024, 65536): # We don't want to allow reserved ports to be set             
                await ctx.send(f"Error: {host_split[2]} is not a valid port! Please check to ensure you're attempting to use a port from 1024 to 65535.")
                return
            else: # Set the new, valid port
                await self.config.tgs_port.set(host_split[2])
            tgs_host = f"{host_split[0]}:{host_split[1]}"
            await self.config.tgs_host.set(tgs_host)
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
            await self.config.tgs_api.set(tgs_api)
            tgs_api = tgs_api.rstrip("/")
            if tgs_api[-1].isdigit():
                await ctx.send("Error: Do not include the version in the API.")
                return
            await ctx.send(f"TGS API set to: `{tgs_api}`. Please be absolutely sure that you actually needed to change this from the default `Tgstation.Server.Api`.")
            await ctx.send(f"TGS API header: `{await self.get_api_header(ctx)}`.")
        except Exception as err:
            await ctx.send(f"There was an error setting the API: {err}")
    
    @tgs4.command()
    @checks.is_owner()
    async def agent(self, ctx, tgs_user_agent: str):
        """
        Sets the User-Agent header, defaults to tgstation-server-redbot-cog
        """
        try:
            await self.config.tgs_user_agent.set(tgs_user_agent)
            await ctx.send(f"User-Agent set to: `{tgs_user_agent}`")
        except (ValueError, KeyError, AttributeError) as err:
            await ctx.send(f"There was an error setting the User-Agent header: {err}")
    
    async def get_url(self, ctx):
        try:
            url = f"{await self.config.tgs_host()}:{await self.config.tgs_port()}"
            return url
        except Exception as err:
            await ctx.send(f"There was an error getting the URL: {err}")

    async def get_api_header(self, ctx):
        try:
            header = str(await self.config.tgs_api()) + "/" + str(await self.config.tgs_api_version()),
            header = "".join(header) # For some reason header is a fucking tuple
            return str(header)
        except Exception as err:
            await ctx.send(f"There was an error getting the API header: {err}")
    
    async def get_tgs_config(self, ctx):
        try:
            if self.tgs_config is None:
                self.tgs_config = Configuration()
                self.tgs_config.host = await self.get_url(ctx)
                self.tgs_config.username = await self.config.tgs_username()
                self.tgs_config.password = await self.config.tgs_password()
            return self.tgs_config
        except Exception as err:
            await ctx.send(f"There was an error getting the TGS config: {err}")
    
    async def get_api_client(self, ctx):
        try:
            if self.api_client is None:
                self.api_client = swagger_client.ApiClient(await self.get_tgs_config(ctx), header_name = "Authorization:Bearer", header_value = await self.tgs_auth_token())
            return self.api_client
        except ApiException as err:
            parse_ex(ctx, err)
        except Exception as err:
            await ctx.send(f"There was an error getting the API client: {err}")
    
    async def reload_tgs_config(self, ctx):
        try:
            self.tgs_config = None
            self.api_client = None
            self.api_client = await self.get_api_client(ctx) # ALso sets tgs_config
        except Exception as err:
            await ctx.send(f"There was an error reloading the TGS config: {err}")
    
    @tgs4.command()
    @checks.mod_or_permissions(administrator=True)
    async def config(self, ctx):
        """
        Displays basic config info.
        """
        try:
            url = await self.get_url(ctx)
            api = await self.get_api_header(ctx)
            agent = await self.config.tgs_user_agent()
            await ctx.send(f"Server URL: `{url}`\nCog API: `{api}`\nUser-Agent: `{agent}`")
        except Exception as err:
            await ctx.send(f"There was an error retrieving config info: {err}")

    @tgs4.command()
    @checks.mod_or_permissions(administrator=True)
    async def info(self, ctx):
        """
        Retrieves basic TGS server info.
        """
        try:
            #await acknowledge(ctx)
            #api_instance = swagger_client.HomeApi(await self.get_api_client(ctx))
            #api_response = api_instance.home_controller_home(await self.get_api_header(ctx), await self.config.tgs_user_agent())
            #await ctx.send(api_response)
            await ctx.send(await self.call_api(ctx, Api.HOME, home_controller_home))
        except ApiException as err:
            await parse_ex(ctx, err)
        except Exception as err:
            await ctx.send(f"There was an error retrieving the TGS info: {err}")
            #await ctx.send(traceback.print_exc())
    
    @tgs4.command()
    @checks.is_owner()
    async def account(self, ctx):
        """
        Begins the account configuration process. You do actually need to run this before setting the account info.
        """
        try:
            await self.config.guild_id.set(ctx.guild.id)
            await ctx.author.send("TGS4 account setup is a three-step process.")
            await acknowledge(ctx)
            await ctx.send("Check your direct messages for account configuration instructions.")
            await ctx.author.send("Step 1: In TGS4, create a user account for the bot. Give it permissions for whatever relevant things you want it to be able to do.")
            await ctx.author.send("Step 2: Run the `tgs_user <username>` command to set the username. For security purposes, this must be done in a direct message.") 
            await ctx.author.send("Step 3: Run the `tgs_pass <password>` command to set the password. For security purposes, this must be done in a direct message.") 
            await ctx.author.send("You should now be able to run `tgs4 authenticate` to log in and retrieve an authentication token. This is *not* a direct message command.")
        except discord.Forbidden:
            await ctx.send("I can't send direct messages to you. Please change your DM settings and try again.")
    
    @checks.is_owner()
    @commands.command()
    @commands.dm_only()
    async def tgs_user(self, ctx, username: str):
        """
        This command only works in DMs! Sets the username for the bot's TGS4 account.
        """
        try:
            guild = self.bot.get_guild(await self.config.guild_id())
            if guild is None:
                return await ctx.send("Error: You need to run `tgs4 account` in the discord server first!")
            await self.config.tgs_username.set(username)
            await self.reload_tgs_config(ctx)
            await ctx.send(f"TGS username set to: `{username}`.")
        except Exception as err:
            await ctx.send(f"There was an error setting the username: {err}")
    
    @checks.is_owner()
    @commands.command()
    @commands.dm_only()
    async def tgs_pass(self, ctx, password: str):
        """
        This command only works in DMs! Sets the password for the bot's TGS4 account.
        """
        try:
            guild = self.bot.get_guild(await self.config.guild_id())
            if guild is None:
                return await ctx.send("Error: You need to run `tgs4 account` in the discord server first!")
            await self.config.tgs_password.set(password)
            await self.reload_tgs_config(ctx)
            await ctx.send(f"TGS password set to: `{password}`.")
        except Exception as err:
            await ctx.send(f"There was an error setting the password: {err}")
    
    async def authenticate(self, ctx):
        try:
            api_instance = swagger_client.HomeApi(await self.get_api_client(ctx))
            token = api_instance.home_controller_create_token(await self.get_api_header(ctx), await self.config.tgs_user_agent())
            await self.config.tgs_auth_token.set(token)
            await self.reload_tgs_config(ctx)
            await ctx.send("Successfully authenticated") # TODO: Remove this
        except ApiException as err:
            await parse_ex(ctx, err)
        except Exception as err:
            await ctx.send(f"There was an error during authentication: {err}")

    async def call_api(self, ctx, api, method):
        # Make sure we have authenticated before.
        try:
            token = await self.config.tgs_auth_token()
            if token is None: # We've never authenticated
                await self.authenticate(ctx)
        except Exception as err:
            await ctx.send(f"Error: First-time authentication failed: {err}")
        tries = 0
        
        while tries < 3: # Why three you ask? Excellent question. /shrug
            try:
                await acknowledge(ctx)
                api_instance = api(await self.get_api_client(ctx))
                response = api_instance.method(await self.get_api_header(ctx), await self.config.tgs_user_agent())
                return response
            except ApiException as err:
                if err.status == 401:
                    await self.authenticate(ctx)
                    tries += 1
                    continue
                await parse_ex(ctx, err)
            except Exception as err:
                await ctx.send(f"Error: Unable to complete the API call: {err}")
            break