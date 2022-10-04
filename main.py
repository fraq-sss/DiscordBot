import discord
import bs_server

from discord.ext import commands
from discord.ext.commands import Context
from yaml import full_load
from googletrans import Translator, LANGUAGES


with open('config.yaml') as cfg_file:
    cfg = full_load(cfg_file)


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(cfg['discord_bot']['default_prefix']),
    intents=discord.Intents.all(),
    case_insensitive=True,
    owner_ids=cfg['discord_bot']['owner_ids']
)


@bot.event
async def on_command_error(ctx: Context, exc: Exception) -> None:
    if isinstance(exc, commands.NotOwner):
        await ctx.reply('You are not owner of the bot!')
    elif isinstance(exc, commands.CommandOnCooldown):
        await ctx.reply(f'Cooldown! Retry after {int(exc.retry_after)}s.')
    else:
        await ctx.reply(f'```Error: {exc}```')


@commands.is_owner()
@bot.command(name='prefix')
async def setup_prefix(ctx: Context, arg: str = cfg['discord_bot']['default_prefix']) -> None:
    bot.command_prefix = commands.when_mentioned_or(arg)
    await ctx.reply(f'Now the bot prefix is "{arg}"!')


@bot.command(name='trans')
async def translate(ctx: Context, *args: str) -> None:
    message = args
    language = 'en'
    if LANGUAGES.get(args[-1]):
        message = args[:-1]
        language = args[-1]
    await ctx.reply(Translator().translate(' '.join(message), dest=language).text)


@commands.cooldown(1, 20, commands.BucketType.user)
@bot.command(name='select')
async def select_server(ctx: Context, arg: int = -1) -> None:
    names = cfg['bs_servers']['folders']
    if -1 < arg < len(names):
        name = tuple(names)[arg]
        bs_server.update_data(name)
        await ctx.reply(f'Now the selected server is "{name}"!')
    else:
        description = '\n'.join([f'{i}) {n}' for i, n in enumerate(names)])
        await ctx.reply(embed=discord.Embed(
            title='Use a server index!',
            description=f'```{description}```',
            color=discord.Colour.dark_purple()
        ))


@commands.cooldown(1, 40, commands.BucketType.user)
@bot.command(name='top')
async def top_players(ctx: Context, arg: int = 10) -> None:
    top = bs_server.get_players_top()
    arg = arg if 1 <= arg <= len(top) else len(top)
    description = '\n'.join([f'{i + 1}) {top[i]["name"]}' for i in range(arg)])
    await ctx.reply(embed=discord.Embed(
        title=f'Top {arg} players of the {bs_server.Data.name}',
        description=f'```{description}```',
        color=discord.Colour.dark_purple()
    ))


@bot.command(name='info')
async def information(ctx: Context, arg: str) -> None:
    if arg.startswith('top-'):
        data = bs_server.get_players_top()[int(arg[4:]) - 1]
    elif bs_server.get_players_stats().get(arg):
        data = bs_server.get_players_stats().get(arg)
    else:
        await ctx.reply('Return data not-found!')
        return
    description = '\n'.join([f'{k}: {v}' for k, v in data.items()])
    await ctx.reply(embed=discord.Embed(
        title=f'Player information of the {bs_server.Data.name}',
        description=f'```{description}```',
        color=discord.Colour.dark_purple()
    ))


bot.run(cfg['discord_bot']['token'])
