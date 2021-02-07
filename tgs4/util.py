from swagger_client.rest import ApiException

async def parse_ex(ctx, error: ApiException):
    if error.status == 400:
        await ctx.send("ERROR 400 (Bad Request): {0}".format(error))
    elif error.status == 401:
        await ctx.send("ERROR 401 (Unauthorized): Invalid or expired credentials were provided. Try running `tgs4 authenticate`.") #This command does not exist yet
    elif error.status == 403:
        await ctx.send("ERROR 403 (Forbidden): You made a request that the authenticated user is not allowed to perform.")
    elif error.status == 404:
        await ctx.send("ERROR 404 (Not Found): A resource was requested that *never* existed.")
    elif error.status == 406:
        await ctx.send("ERROR 406 (Not Acceptable): No Accept header provided.")
    elif error.status == 408:
        await ctx.send("ERROR 408 (Request Timeout)")
    elif error.status == 409:
        await ctx.send("ERROR 409 (Conflict): Documented in the requests that use them.")
    elif error.status == 410:
        await ctx.send("ERROR 410 (Gone): Attempted to access/modify a resource that isn't ready or is no longer ready.")
    elif error.status == 422:
        await ctx.send("ERROR 422 (Unprocessable Entity): This should only be possible if your server configuration is incorrect. Specifically, the watchdog is not present in deployment.")
    elif error.status == 424:
        await ctx.send("ERROR 424 (Failed Dependency): When a request that depends on the GitHub API fails for a reason other than rate limiting. Check the server logs, usually this indicates a bad access token.")
    elif error.status == 426:
        await ctx.send("ERROR 426 (Upgrade Required): This cog's API version is not compatible with the server's API version.")
    elif error.status == 429:
        await ctx.send("ERROR 429 (Rate Limited): GitHub.com's rate limit has been reached.")
    elif error.status == 500:
        await ctx.send("ERROR 500 (Server Error): Please report the following error: {0}".format(error))
    elif error.status == 501:
        await ctx.send("ERROR 501 (Not Implemented): Functionality not available in the current server version.")
    elif error.status == 503:
        await ctx.send("ERROR 503 (Service Unavailable): The server is either starting up or shutting down and isn't ready to respond to requests. You can try again soon and a response/lack thereof will indicate which of the two events it was")
    else:
        await ctx.send("Unknown ApiException error {0}: {1}".format(error.status, error))
