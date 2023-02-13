# -*- coding: utf-8 -*-
import disnake, asyncio ,os
from disnake.ext import commands
import sqlite3,random

TOKEN = ""

intents = disnake.Intents.default()

sync_cmd = commands.CommandSyncFlags(sync_commands_debug=True)
bot = commands.Bot(command_prefix="!?", intents=intents,command_sync_flags=sync_cmd)

@bot.slash_command()
async def reset(inter):
    conn = sqlite3.connect("./user.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM logined WHERE userid='{}'".format(str(inter.author.id)))
    conn.commit()
    await inter.response.send_message("success",ephemeral=True)


@bot.slash_command(title="login",description="ログインします")
async def login_cmd(inter:disnake.ApplicationCommandInteraction):
    conn = sqlite3.connect("./user.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM logined WHERE userid='{}'".format(str(inter.author.id)))
    get_data = cur.fetchall()
    if get_data != []:
        username = get_data[0][0]
        embed = disnake.Embed(title="エラー",description=f"あなたは`{username}`にすでにログインしています。",color=0xff0000)
        await inter.response.send_message(embed=embed,ephemeral=True)
        return
    
    modal_custom_id = str(random.randint(1111,9999))
    await inter.response.send_modal(
        title=f"ログイン",
        custom_id=modal_custom_id,
        components=[
            disnake.ui.TextInput(
                label=f"UserName",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=14
            ),
            disnake.ui.TextInput(
                label=f"Password",
                custom_id="password",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=35
            )
        ]
    )
    modal_inter: disnake.ModalInteraction = await bot.wait_for(
        "modal_submit",
        check=lambda i: i.custom_id == modal_custom_id and i.author.id == inter.author.id,
        timeout=700
    )
    username = modal_inter.text_values["name"]
    password = modal_inter.text_values["password"]

    cur.execute("SELECT username,password FROM users WHERE username='{}' AND password='{}'".format(username,password))
    #cur.execute("SELECT username,password FROM users WHERE username=? AND password=?",(username,password))
    if cur.fetchall() == []:
        embed = disnake.Embed(title="エラー",description="ユーザー名かパスワードが間違っています。",color=0xff0000)
        await modal_inter.response.send_message(embed=embed,ephemeral=True)
    else:
        cur.execute("INSERT INTO logined VALUES('{}','{}')".format(username,str(inter.author.id)))
        conn.commit()
        embed = disnake.Embed(title="ログイン成功",description=f"`{username}`にログインしました。",color=0x7fffd4)
        await modal_inter.response.send_message(embed=embed,ephemeral=True)

if __name__ == "__main__":
    conn = sqlite3.connect("./user.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(username text unique,password text)")
    cur.execute("CREATE TABLE IF NOT EXISTS logined(username text,userid text unique)")
    try:
        cur.execute("INSERT INTO users VALUES('outaokura','lickmyjohnson')")
        cur.execute("INSERT INTO users VALUES('nyaa','ohnobigpenis')")
    except:
        None
    conn.commit()
    bot.run(TOKEN)
