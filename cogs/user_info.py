import io

import discord
from discord.ext import commands

from cogs import utils


class UserInfo(utils.Cog):

    @commands.command(cls=utils.Command)
    async def avatar(self, ctx:utils.Context, user:discord.User=None):
        """Shows you the avatar of a given user"""

        if user is None:
            user = ctx.author
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.guild_only()
    async def createlog(self, ctx:utils.Context, amount:int=100):
        """Create a log of chat"""

        # Create the data we're gonna send
        data = {
            "channel_name": ctx.channel.name,
            "category_name": ctx.channel.category.name,
            "guild_name": ctx.guild.name,
            "guild_icon_url": str(ctx.guild.icon_url),
        }
        data_authors = {}
        data_messages = []

        # Get the data from the server
        async for message in ctx.channel.history(limit=min([max([1, amount]), 250])):
            for user in message.mentions + [message.author]:
                data_authors[user.id] = {
                    "username": user.name,
                    "discriminator": user.discriminator,
                    "avatar_url": str(user.avatar_url),
                    "bot": user.bot,
                    "display_name": user.display_name,
                    "color": user.colour.value,
                }
            message_data = {
                "id": message.id,
                "content": message.content,
                "author_id": message.author.id,
                "timestamp": int(message.created_at.timestamp()),
                "attachments": [str(i.url) for i in message.attachments],
                # "embeds": [i.to_dict() for i in message.embeds],
            }
            embeds = []
            for i in message.embeds:
                embed_data = i.to_dict()
                if i.timestamp:
                    embed_data.update({'timestamp': i.timestamp.timestamp()})
                embeds.append(embed_data)
            message_data.update({'embeds': embeds})
            data_messages.append(message_data)


        # Send data to the API
        data.update({"users": data_authors, "messages": data_messages[::-1]})
        async with self.bot.session.post("https://voxelfox.co.uk/discord/chatlog", json=data) as r:
            string = io.StringIO(await r.text())

        # Output it into the chat
        await ctx.send(file=discord.File(string, filename=f"Logs-{int(ctx.message.created_at.timestamp())}.html"))


def setup(bot:utils.Bot):
    x = UserInfo(bot)
    bot.add_cog(x)
