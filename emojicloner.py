import discord
import aiohttp
import asyncio
from colorama import Fore, Style, init

init(autoreset=True)

banner = r"""
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████──██████─██████████─██████████████────██████████████─██████──────────██████─██████████████─────────██████─██████████─
─██░░██──██░░██─██░░░░░░██─██░░░░░░░░░░██────██░░░░░░░░░░██─██░░██████████████░░██─██░░░░░░░░░░██─────────██░░██─██░░░░░░██─
─██░░██──██░░██─████░░████─██████░░██████────██░░██████████─██░░░░░░░░░░░░░░░░░░██─██░░██████░░██─────────██░░██─████░░████─
─██░░██──██░░██───██░░██───────██░░██────────██░░██─────────██░░██████░░██████░░██─██░░██──██░░██─────────██░░██───██░░██───
─██░░██████░░██───██░░██───────██░░██────────██░░██████████─██░░██──██░░██──██░░██─██░░██──██░░██─────────██░░██───██░░██───
─██░░░░░░░░░░██───██░░██───────██░░██────────██░░░░░░░░░░██─██░░██──██░░██──██░░██─██░░██──██░░██─────────██░░██───██░░██───
─██░░██████░░██───██░░██───────██░░██────────██░░██████████─██░░██──██████──██░░██─██░░██──██░░██─██████───██░░██───██░░██───
─██░░██──██░░██───██░░██───────██░░██────────██░░██─────────██░░██──────────██░░██─██░░██──██░░██─██░░██───██░░██───██░░██───
─██░░██──██░░██─████░░████─────██░░██────────██░░██████████─██░░██──────────██░░██─██░░██████░░██─██░░██████░░██─████░░████─
─██░░██──██░░██─██░░░░░░██─────██░░██────────██░░░░░░░░░░██─██░░██──────────██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░██─
─██████──██████─██████████─────██████────────██████████████─██████──────────██████─██████████████─██████████████─██████████─
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
"""

print(Fore.MAGENTA + banner + Style.RESET_ALL)

token = input(f'{Fore.CYAN}Token de usuario:\n> {Style.RESET_ALL}')
guild_source_id = input(f'{Fore.CYAN}ID del servidor origen:\n> {Style.RESET_ALL}')
guild_target_id = input(f'{Fore.CYAN}ID del servidor destino:\n> {Style.RESET_ALL}')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

def print_add(msg): print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")
def print_del(msg): print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")
def print_info(msg): print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")
def print_err(msg): print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

@client.event
async def on_ready():
    source = client.get_guild(int(guild_source_id))
    target = client.get_guild(int(guild_target_id))
    if not source or not target:
        print_err("No estoy en uno de los servidores o no tengo permisos.")
        await client.close()
        return

    borrar = input(f"{Fore.YELLOW}¿Quieres borrar todos los emojis actuales del servidor destino antes de clonar? (s/n): {Style.RESET_ALL}").strip().lower()
    if borrar in ["s", "si", "y", "yes"]:
        print_info("Eliminando emojis del servidor destino...")
        for e in target.emojis:
            try:
                await e.delete()
                print_del(f"Eliminado: {e.name}")
                await asyncio.sleep(0.5)
            except:
                print_err(f"No se pudo eliminar: {e.name}")

    total = len(source.emojis)
    if total == 0:
        print_info("No hay emojis para clonar.")
        await client.close()
        return

    max_emojis = 50
    print_info(f"Clonando {total} emojis...")
    async with aiohttp.ClientSession() as session:
        for idx, emoji in enumerate(source.emojis, 1):
            if len(target.emojis) >= max_emojis:
                print_err("Se alcanzó el límite de emojis en el servidor destino.")
                break
            try:
                async with session.get(str(emoji.url)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await target.create_custom_emoji(name=emoji.name, image=data)
                        print_add(f"[{idx}/{total}] Clonado: {emoji.name}")
                        bar_len = 30
                        filled_len = int(bar_len * idx / total)
                        bar = "█" * filled_len + "-" * (bar_len - filled_len)
                        print(f"[{bar}] {idx}/{total} emojis clonado(s)", end="\r")
                        await asyncio.sleep(1)
            except:
                print_err(f"Error clonando {emoji.name}")
    print("\n" + Fore.GREEN + "Clonación completada." + Style.RESET_ALL)
    await client.close()

client.run(token, bot=False)
