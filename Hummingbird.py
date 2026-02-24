import asyncio
import discord
from discord.ext import commands, tasks

PREFIX = "!"
TOKEN = "TOKEN"
BANS_FILE = "ids.txt"
CHECK_INTERVAL_SECONDS = 120 # The interval the bot checks in. dont put it too low or it will be flagged and rate limited by discord. i found out 2 min working the best

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"Logging in as {bot.user} ({bot.user.id})")
    print(f"I am on {len(bot.guilds)} Servers")
    ban_loop.start()


@tasks.loop(seconds=CHECK_INTERVAL_SECONDS)
async def ban_loop():
    if not bot.is_ready():
        return

    try:
        with open(BANS_FILE, encoding="utf-8") as f:
            raw = f.read().strip()
        user_ids = set()
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            try:
                uid = int(line)
                user_ids.add(uid)
            except ValueError:
                print(f"Invalid id skipped: {line}")
    except FileNotFoundError:
        print(f"File {BANS_FILE} not found → Stopping process")
        return
    except Exception as e:
        print(f"Failed to read {BANS_FILE}: {e}")
        return

    if not user_ids:
        print("found no valid ids in ids.txt")
        return

    print(f"Start Ban Round – {len(user_ids)} target ids")

    banned_count = 0
    skipped_count = 0
    no_perm_count = 0

    for guild in bot.guilds:
        print(f"→ Scanning {guild.name} ({guild.id}) – {guild.member_count} Members")

        for user_id in user_ids:
            try:
                member = guild.get_member(user_id)

                if member is None:
                    user = await bot.fetch_user(user_id)
                    await guild.ban(user, reason="Automatic ID Ban list ")
                    print(f"  BAN (not cached): {user} ({user_id})")
                else:
                    await member.ban(reason="Automatic ID Ban list")
                    print(f"  BAN: {member} ({user_id})")

                banned_count += 1
                await asyncio.sleep(0.7)  

            except discord.Forbidden:
                no_perm_count += 1
            except discord.NotFound:
                pass
            except discord.HTTPException as e:
                if e.status == 429:
                    print("Rate limit! Hold on...")
                    await asyncio.sleep(5)
                else:
                    print(f"  Failed to ban {user_id} at {guild.name}: {e}")
            except Exception as e:
                print(f"  unknown error {user_id} – {guild.name}: {type(e).__name__} {e}")

    print(f"Banned: {banned_count} | Skipped/errors: {skipped_count} | No privilege: {no_perm_count}\n")


try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print("Invalid or Wrong Token!")
except Exception as e:
    print(f"Bot didnt start: {e}")