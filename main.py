import os
import discord
from nextcord.ext import commands
import nextcord
from keep_alive import keep_running
from tinydb import TinyDB, Query
from asyncio import sleep as async_sleep

bot = commands.Bot(help_command=None)
db = TinyDB("people_in_debt.json")
debtors = Query()


@bot.slash_command(guild_ids=[946805252089348157], description="Sign you soul away today!")
async def register(interaction, user=nextcord.SlashOption(required=False)):
    if user is None:
        user = interaction.user
    else:
        try:
            user = await bot.fetch_user(user[2:-1])
            print(user)
        except:
            await interaction.send("`You must mention the user in order to register`")
            return
    if db.search(debtors.id == user.id):
        await interaction.send(
            "User has already been had by the greedy creators of this bot, sorry lol"
        )
        return
    db.insert({"id": user.id, "money": 1000, "canWork": True})
    await interaction.send(
        f"`Sucessfully registered:` {user.mention}! Thank you for signing your soul away!"
    )


@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

class betconfirmation(nextcord.ui.View):
    def __init__(self, plyr1, plyr2):
        super().__init__()
        self.player1 = plyr1
        self.confirm1 = False
        self.confirm2 = False
        self.player2 = plyr2

    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button,interaction: nextcord.Interaction):
        if interaction.user != self.player1 and  interaction.user != self.player2:
            return
        if interaction.user == self.player1:
            self.confirm1 = True
        if interaction.user == self.player2:
            self.confirm2 = True
        if self.confirm1 and self.confirm2:
            self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    
        if interaction.user != self.player1 and interaction.user != self.player2:
            return
        if interaction.user == self.player1:
            self.confirm1 = False
        if interaction.user == self.player2:
            self.confirm2 = False
        self.stop()



class slvview(nextcord.ui.View):
    def __init__(self, player):
        super().__init__()
        self.choseC = None
        self.player = player

    @nextcord.ui.button(label="Citizen", style=nextcord.ButtonStyle.blurple)
    async def citizen(self, button: nextcord.ui.Button,
                      interaction: nextcord.Interaction):
        self.choseC = True
        self.user = interaction.user
        if interaction.user != self.player:
            return
        for i in self.children:
            i.disabled = True
        self.stop()

    @nextcord.ui.button(label="Slave", style=nextcord.ButtonStyle.red)
    async def slave(self, button: nextcord.ui.Button,
                    interaction: nextcord.Interaction):
        self.choseC = False
        self.user = interaction.user
        if interaction.user != self.player:
            return
        for i in self.children:
            i.disabled = True
        self.stop()


class empview(nextcord.ui.View):
    def __init__(self, player):
        super().__init__()
        self.choseC = None
        self.player = player

    @nextcord.ui.button(label="Citizen", style=nextcord.ButtonStyle.blurple)
    async def citizen(self, button: nextcord.ui.Button,
                      interaction: nextcord.Interaction):
        self.choseC = True
        self.user = interaction.user
        if interaction.user != self.player:
            return
        for i in self.children:
            i.disabled = True
        self.stop()

    @nextcord.ui.button(label="Emperor", style=nextcord.ButtonStyle.green)
    async def slave(self, button: nextcord.ui.Button,
                    interaction: nextcord.Interaction):
        self.choseC = False
        self.user = interaction.user
        if interaction.user != self.player:
            return
        for i in self.children:
            i.disabled = True
        self.stop()


def get_players(uOne, uTwo):
    resOne = db.search(debtors.id == uOne.id)
    if len(resOne) == 0:
        return False, False
    resTwo = db.search(debtors.id == uTwo.id)
    if len(resTwo) == 0:
        return False, False
    return resOne[0], resTwo[0]


@bot.slash_command(name="play", guild_ids=[946805252089348157], description="player 1 plays slave and player two plays emperor first")
async def play(interaction, user_one, bet_one, user_two, bet_two):
    if interaction.user == bot.user:  # you don't want to respond to urself
        return
    if user_one == user_two:
        await interaction.send(
            "You can't play against yourself, thats a rigged gamble.")
        return
    try:
        bet_one = int(bet_one)
        bet_two = int(bet_two)
    except:
        await interaction.send("Your bet is not a number.")
        return

    if bet_one < 100 or bet_two < 100:
        await interaction.send(
            "Your bet must be greater than or equal to 100, type /rules to know more"
        )
        return


    # now we know all input is valid
    user_one = await bot.fetch_user(user_one[2:-1])
    user_two = await bot.fetch_user(user_two[2:-1])
    userO, userT = get_players(user_one, user_two)
    if not userO or not userT:
        await interaction.send(
            "Either one of the users in not registered yet, please run /register to register the user."
        )
        return
    if userO["money"] < bet_one or userT["money"] < bet_two:
        await interaction.send(
            "Bruh you can't bet more than you own, what you want more debt???")
        return

    betconf = betconfirmation(user_one, user_two)
    await interaction.send(
        f"Both players please confirm your bets:\n {user_one.name} = ${bet_one} (playing Slave side)\n {user_two.name} = ${bet_two} (playing Emperor side)",
        view=betconf)
    confmsg = await interaction.original_message()
    timeout = await betconf.wait()
    if timeout or (not betconf.confirm1) or (not betconf.confirm2):
        newmsg = await interaction.send(
            "One or both players didn't confirm, please make a new game")
        await async_sleep(1)
        await confmsg.delete()
        await newmsg.delete()
        return

    await confmsg.delete()
    bet_one *= 5
    rounds = 1
    turne = await interaction.send(
        f"`Epic showdown between {user_one.name} and {user_two.name}\nTurn #{rounds}`"
    )
    msg = await interaction.send(
        f"`Playing with bets of {int(bet_one/5)} on slave side and {bet_two} on emperor side....Creating Game`"
    )
    await async_sleep(1)

    A = B = outcome = SlvWin = None

    while rounds < 5:
        view = slvview(user_one)
        viewB = empview(user_two)
        if rounds > 1:
            await turne.edit(f"`Turn #{rounds}`")
        A, B = await turn(msg, user_one, user_two, view, viewB)

        if A and not B:  # A chose citizen, B choses emp
            outcome = f"{user_two.name} WON and got {bet_two + int(bet_one/5)} coins!"
            SlvWin = False
            break
        elif not A and not B:  # Both sides play key cards
            outcome = f"{user_one.name} WON and got {bet_one + bet_two} coins!"
            SlvWin = True
            break
        elif not A and B:  # A chose slave, B chose citizen
            outcome = f"{user_two.name} WON and got {bet_two + int(bet_one/5)} coins!"
            SlvWin = False
            break
        else:
            await msg.edit("`both sides chose Citizen 🟦`")
            await async_sleep(1)
        # if all these conditions are false, then both chose citizen
        rounds += 1

    if rounds >= 5:
        outcome = f"{user_one.name} WON (by default) and got {bet_one + bet_two} coins!"
        SlvWin = True

    choiceA = "Citizen 🟦" if A else "Slave 🟥"
    choiceB = "Citizen 🟦" if B else "Emperor 🟩"
    if SlvWin:
        winnings = userO["money"] + bet_one + bet_two
        losings = userT["money"] - bet_two
        db.update({"money": winnings}, debtors.id == userO["id"])
        db.update({"money": losings}, debtors.id == userT["id"])
    else:
        winnings = userT["money"] + bet_two + int(bet_one / 5)
        losings = userO["money"] - int(bet_one / 5)
        db.update({"money": winnings}, debtors.id == userT["id"])
        db.update({"money": losings}, debtors.id == userO["id"])

    #final message
    await interaction.send(
        f"```{user_one.name} chose {choiceA}\n{user_two.name} chose {choiceB}\n{outcome}```{user_one.mention} {user_two.mention}"
    )


async def turn(msg, userOne, userTwo, view, viewB):

    #Slave side's turn
    await msg.edit(f"`{userOne.name} chooses first...`\n`which card?`",
                   view=view)
    await view.wait()
    await msg.edit(f"`{userOne.name} chose their card`", view=view)

    #Emperor side's turn
    await msg.edit(f"`{userTwo.name} chooses next...`\n`which card?`",
                   view=viewB)
    await viewB.wait()
    await msg.edit(f"`{userTwo.name} chose their card too`", view=viewB)
    return view.choseC, viewB.choseC


#run the bot


@bot.slash_command(guild_ids=[946805252089348157], description="A quick rules guide to play the game!")
async def rules(interaction):
    await interaction.send("""
```E-Card Rules
                 
- Each side gets 5 cards, out of which 4 are Citizen 🟦, and 1 is either Slave 🟥 or Emperor 🟩

- Both sides then have to choose 1 card and play it against the other side every turn (players will lose the card they played, which means the game can only go up to 5 rounds)

- If both sides choose Citizen 🟦, then it is a tie and the next turn is played

- If one side chooses Emperor 🟩 and the other Citizen 🟦, the Emperor side wins the game

- If one side chooses Slave 🟥 and the other Citizen 🟦, the Emperor side (one who chose Citizen 🟦) wins the game

- If one side chooses Slave 🟥 and the other Emperor 🟩, the Slave side wins the game

- If neither side plays a key card by the 5th round, the Slave side wins by default (as the only possible play is Slave 🟥 vs Emperor 🟩)```"""
                   )


@bot.slash_command(guild_ids=[946805252089348157], description = "Check your balance (we all know ur broke)")
async def balance(interaction, user=nextcord.SlashOption(required=False)):
    if user is None:
        user = interaction.user
    else:
        user = await bot.fetch_user(user[2:-1])
    res = db.search(debtors.id == user.id)
    if len(res) == 0:
        await interaction.send(f"{user.name} has never played an E-card game before, run /register to register")
    else:
        m = res[0]['money']
        await interaction.send(f"`Your current Balance is: ${m}`")


class workview(nextcord.ui.View):
    def __init__(self, workdone):
        super().__init__()
        self.workdone = workdone

    @nextcord.ui.button(label="Shovel", style=nextcord.ButtonStyle.danger)
    async def shovel(self, button: nextcord.ui.Button,
                     interaction: nextcord.Interaction):
        self.workdone += 5
        if (self.workdone >= 100):
            button.disabled = True
        self.stop()


@bot.slash_command(guild_ids=[946805252089348157])
async def work(interaction, description = "Work to get some money!"):
    resp = db.search(debtors.id == interaction.user.id)
    if len(resp) == 0:
        await interaction.send("This user has not played a game yet, run /register to register")
        return

    resp = resp[0]
    if resp["canWork"]:
        db.update({"canWork": False}, debtors.id == interaction.user.id)
        winnings = resp["money"] + 500
        view = workview(0)
        await interaction.send("`Press 'Shovel' to dig out the dirt`", view=view)
        while view.workdone <= 95:
            await view.wait()
            view = workview(view.workdone)
            og_msg = await interaction.original_message()
            await og_msg.edit("`Work done: {}%`".format(view.workdone), view=view)

        await og_msg.edit(f"`Good job, you earned 500 coins!`", view=None)
        db.update({"money": winnings}, debtors.id == interaction.user.id)
        await async_sleep(600)
        db.update({"canWork": True}, debtors.id == interaction.user.id)
    else:
        await interaction.send(
            "`You are on cooldown. Wait for 10 minutes before you can work again`"
        )


token = os.environ['token']
keep_running()
bot.run(token)
