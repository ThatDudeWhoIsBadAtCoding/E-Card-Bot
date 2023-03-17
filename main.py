import os
from nextcord.ext import commands
import nextcord
from keep_alive import keep_running
from tinydb import TinyDB, Query
import random
from asyncio import sleep as async_sleep

bot = commands.Bot(help_command=None)
db = TinyDB("people_in_debt.json")
debtors = Query()

mod_ids = [864736437710487583]


@bot.slash_command(guild_ids=[1033032849269465128, 946805252089348157],
                   description="Just nostalgia...")
async def nostalgia(interaction,
                    romanji: bool = nextcord.SlashOption(required=False)):
    if romanji is not None and romanji:
        await interaction.send(
            '''tsuki ga sora ni haritsuitera  gingami no hoshi ga yuretera
dare mo ga poketto no naka ni  kodoko o kakushi-motteiru
amari ni mo totsuzen ni   kinou wa kudakete-yuku
sore naraba ima koko de  bokura nanika o hajimeyou

ikiteiru koto ga daisuki de   imi mo naku koufun shiteru
ichido ni subete o nozonde  mahha gojuu de kake-nukeru
kudaranai yo no naka da  shonben kakte-yarou
uchi-nomesareru mae ni  boku ga uchi-nomeshite-yarou

MIRAI WA BOKURA NO TE NO NAKA!!

dareka no ruuru wa iranai  dareka no moraru wa iranai
gakkou mo juku mo iranai  shinjitsu o nigirishimetai

bokura wa naku tame ni  umareta wake janai yo
bokura wa makeru tame ni  umarete kita wake janai yo 
      ''')
        return
    await interaction.send('''月が空にはりついてら 銀紙の星が揺れてら
誰もがポケットの中に 孤独を隠し持っている
あまりにも突然に 昨日は砕けてゆく
それならば今ここで 僕等何かをはじめよう

生きてることが大好きで 意味もなく興奮してる
一度に全てを望んで マッハ50で駆け抜ける
くだらない世の中だ ションベンかけてやろう
打ちのめされる前に 僕が打ちのめしてやろう

未来は僕等の手の中！！

誰かのルールはいらない 誰かのモラルはいらない
学校もジュクもいらない 真実を握りしめたい

僕等は泣くために 生まれたわけじゃないよ
僕等は負けるために 生まれてきたわけじゃないよ

''')


@bot.slash_command(guild_ids=[1033032849269465128, 946805252089348157],
                   description="Sign you soul away today!")
async def register(interaction, user=nextcord.SlashOption(required=False)):
    if user is None:
        user = interaction.user
    else:
        try:
            user = await bot.fetch_user(user[2:-1])
            print(user)
        except:
            await interaction.send(
                "`You must mention the user in order to register`")
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


@bot.slash_command(
    guild_ids=[1033032849269465128, 946805252089348157],
    description=
    "(Can only be used by mods) Give or take money from someone's account")
async def give(interaction,
               target_user=nextcord.SlashOption(),
               amount: int = nextcord.SlashOption()):

    user = await bot.fetch_user(target_user[2:-1])
    if interaction.user.id not in mod_ids:
        await interaction.send("Command can only be used by mods")
        return
    user_id = db.search(debtors.id == user.id)[0]
    if not user_id:
        await interaction.send("User is not registered")
        return
    new_balance = int(user_id["money"]) + int(amount)
    db.update({"money": new_balance}, debtors.id == user_id["id"])
    await interaction.send(
        f"Succesfully updated the account balance of {user.mention}\n" +
        f"New account balance = ${new_balance}")


class betconfirmation(nextcord.ui.View):
    def __init__(self, plyr1, plyr2):
        super().__init__()
        self.player1 = plyr1
        self.confirm1 = False
        self.confirm2 = False
        self.player2 = plyr2

    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button,
                      interaction: nextcord.Interaction):
        if interaction.user != self.player1 and interaction.user != self.player2:
            return
        if interaction.user == self.player1:
            self.confirm1 = True
        if interaction.user == self.player2:
            self.confirm2 = True
        if self.confirm1 and self.confirm2:
            self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button,
                     interaction: nextcord.Interaction):

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


@bot.slash_command(
    name="play",
    guild_ids=[1033032849269465128, 946805252089348157],
    description="player 1 plays slave and player two plays emperor first")
async def play(interaction, slave, slave_bet, emperor, emp_bet):
    if interaction.user == bot.user:  # you don't want to respond to urself
        return
    if slave == emperor:
        await interaction.send(
            "You can't play against yourself, thats a rigged gamble.")
        return
    try:
        slave_bet = int(slave_bet)
        emp_bet = int(emp_bet)
    except:
        await interaction.send("Your bet is not a number.")
        return

    if slave_bet < 100 or emp_bet < 100:
        await interaction.send(
            "Your bet must be greater than or equal to 100, type /rules to know more"
        )
        return

    # now we know all input is valid
    user_slave = await bot.fetch_user(slave[2:-1])
    user_emp = await bot.fetch_user(emperor[2:-1])
    userS, userE = get_players(user_slave, user_emp)
    if not userS or not userE:
        await interaction.send(
            "Either one of the users in not registered yet, please run /register to register the user."
        )
        return
    if userS["money"] < slave_bet or userE["money"] < emp_bet:
        await interaction.send(
            "Bruh you can't bet more than you own, what you want more debt???")
        return

    betconf = betconfirmation(user_slave, user_emp)
    await interaction.send(
        f"Both players please confirm your bets:\n {user_slave.name} = ${slave_bet} (playing Slave side)\n {user_emp.name} = ${emp_bet} (playing Emperor side)",
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
    rounds = 1
    turne = await interaction.send(
        f"`Epic showdown between {user_slave.name} and {user_emp.name}\nTurn #{rounds}`"
    )
    msg = await interaction.send(
        f"`Playing with bets of {slave_bet} on slave side and {emp_bet} on emperor side...Creating Game`"
    )
    await async_sleep(0.25)

    A = B = outcome = SlvWin = None

    while rounds < 5:
        view = slvview(user_slave)
        viewB = empview(user_emp)
        if rounds > 1:
            await turne.edit(f"`Turn #{rounds}`")
        A, B = await turn(msg, user_slave, user_emp, view, viewB)

        if A and not B:  # A chose citizen, B choses emp
            outcome = f"{user_emp.name} WON and got {emp_bet + slave_bet} coins!"
            SlvWin = False
            break
        elif not A and not B:  # Both sides play key cards
            outcome = f"{user_slave.name} WON and got {(slave_bet*5) + emp_bet} coins!"
            SlvWin = True
            break
        elif not A and B:  # A chose slave, B chose citizen
            outcome = f"{user_emp.name} WON and got {emp_bet + slave_bet} coins!"
            SlvWin = False
            break
        else:
            await msg.edit("`both sides chose Citizen 🟦`")
            await async_sleep(1)
        # if all these conditions are false, then both chose citizen
        rounds += 1

    if rounds >= 5:
        outcome = f"{user_slave.name} WON (by default) and got {(slave_bet*5) + emp_bet} coins!"
        SlvWin = True

    choiceA = "Citizen 🟦" if A else "Slave 🟥"
    choiceB = "Citizen 🟦" if B else "Emperor 🟩"

    slave_bal_new = userS['money']
    emp_bal_new = userE['money']

    if SlvWin:
        money_diff = (slave_bet * 5) + emp_bet
        slave_bal_new += money_diff
        emp_bal_new -= money_diff
    else:
        money_diff = slave_bet + emp_bet
        emp_bal_new += money_diff
        slave_bal_new -= money_diff

    db.update({"money": emp_bal_new}, debtors.id == userE["id"])
    db.update({"money": slave_bal_new}, debtors.id == userS["id"])

    #final message
    await interaction.send(
        f"```{user_slave.name} chose {choiceA}\n{user_emp.name} chose {choiceB}\n{outcome}```{user_slave.mention} {user_emp.mention}"
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


@bot.slash_command(guild_ids=[1033032849269465128, 946805252089348157],
                   description="A quick rules guide to play the game!")
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


@bot.slash_command(guild_ids=[1033032849269465128, 946805252089348157], description="Check your balance (we all know ur broke)")
async def balance(interaction, user=nextcord.SlashOption(required=False)):
    if user is None:
        user = interaction.user
    else:
        user = await bot.fetch_user(user[2:-1])
    res = db.search(debtors.id == user.id)
    if len(res) == 0:
        await interaction.send(
            f"{user.name} has never played an E-card game before, run /register to register")
    else:
        m = res[0]['money']
        m = "${}".format(m) if m >= 0 else "-${}".format(abs(m)) 
        if user == interaction.user:
            await interaction.send(f"`Your current Balance is: {m}`")
        else:
            await interaction.send(f"`{user.name}'s current Balance is: {m}`")


class work_view(nextcord.ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.args = []
        self.interaction = interaction
        self.game = random.choice([aim_game_view, shovel_view])
        self.reward = self.game.reward

    async def initiate_game(self):
        interaction = self.interaction
        if self.game.name == "aim_game":
            view = aim_game_view(0)
            game_screen = "```|" + " " * view.pos + "V" + " " * (
                10 - view.pos
            ) + "|\n|" + " " * 11 + "|\n|" + " " * view.target + "O" + " " * (
                10 - view.target) + "|```"

            await interaction.send(
                "`Press 'Shoot' when V and O are lined up`\n" + game_screen)
            og_msg = await interaction.original_message()
            while not view.shot:
                await view.update_pos()
                await async_sleep(0.05)
                game_screen = "```|" + " " * view.pos + "V" + " " * (
                    10 - view.pos
                ) + "|\n|" + " " * 11 + "|\n|" + " " * view.target + "O" + " " * (
                    10 - view.target) + "|```"
                await og_msg.edit(
                    "`Press 'Shoot' when V and O are lined up`\n" +
                    game_screen,
                    view=view)
            if view.win:
                await og_msg.edit("You win! Nice aim, $750 for you!",
                                  view=None)
            else:
                await og_msg.edit("Absolute L you suck, no money >:)",
                                  view=None)
        elif self.game.name == "shovel_game":
            view = shovel_view(0, interaction.user)
            await interaction.send("`Press 'Shovel' to dig out the dirt`",
                                   view=view)
            while view.workdone <= 95:
                await view.wait()
                view = shovel_view(view.workdone, interaction.user)
                og_msg = await interaction.original_message()
                await og_msg.edit("`Work done: {}%`".format(view.workdone),
                                  view=view)

            await og_msg.edit(f"`Good job, you earned $500!`", view=None)


class aim_game_view(nextcord.ui.View):
    name = "aim_game"
    reward = 750

    def __init__(self, pos):
        super().__init__()
        self.target = random.randint(3, 8)
        self.shot = False
        self.pos = pos
        self.moving_right = True
        self.win = False

    async def update_pos(self):
        self.pos += 1 if self.moving_right else -1
        if self.pos == 10:
            self.moving_right = False
        elif self.pos == 0:
            self.moving_right = True

    @nextcord.ui.button(label="Shoot", style=nextcord.ButtonStyle.danger)
    async def shoot(self, button: nextcord.ui.Button,
                    interaction: nextcord.Interaction):
        if abs(self.pos - self.target) <= 1:
            self.win = True
        else:
            self.win = False
        self.shot = True
        self.stop()


class shovel_view(nextcord.ui.View):
    name = "shovel_game"
    reward = 500

    def __init__(self, workdone, worker):
        super().__init__()
        self.workdone = workdone
        self.worker = worker

    @nextcord.ui.button(label="Shovel", style=nextcord.ButtonStyle.danger)
    async def shovel(self, button: nextcord.ui.Button,
                     interaction: nextcord.Interaction):
        self.workdone += 5
        if interaction.user != self.worker:
            return
        if (self.workdone >= 100):
            button.disabled = True
        self.stop()


@bot.slash_command(guild_ids=[1033032849269465128, 946805252089348157],
                   description="Work to get some money!")
async def work(interaction):
    resp = db.search(debtors.id == interaction.user.id)
    if len(resp) == 0:
        await interaction.send(
            "This user has not played a game yet, run /register to register")
        return

    resp = resp[0]
    if resp["canWork"]:
        db.update({"canWork": False}, debtors.id == interaction.user.id)
        game = work_view(interaction)
        await game.initiate_game()
        winnings = resp["money"] + game.reward
        db.update({"money": winnings}, debtors.id == interaction.user.id)
        await async_sleep(60)
        db.update({"canWork": True}, debtors.id == interaction.user.id)
    else:
        await interaction.send(
            "`You are on cooldown. Wait for 1 minute before you can work again`"
        )


token = os.environ['token']
keep_running()
bot.run(token)
