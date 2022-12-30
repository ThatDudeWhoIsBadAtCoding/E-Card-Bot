import os
import discord
# from discord_slash import SlashCommand, SlashContext
from nextcord.ext import commands
import nextcord
from keep_alive import keep_running
from tinydb import TinyDB, Query
from asyncio import sleep as async_sleep

bot = commands.Bot(command_prefix='$', help_command = None, intents = discord.Intents.all())
# slash = SlashCommand(bot)
db = TinyDB("people_in_debt.json")
debtors = Query()

@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])

@bot.command()
async def register(ctx, user=None):
  if user is None:
    user = ctx.author
  else:
    try:
      user = await bot.fetch_user(user[3:-1])
    except:
      await ctx.send("`You must mention the user in order to register`")
  if db.search(debtors.id == user.id):
    await ctx.send("User has already been had by the greedy creators of this bot, sorry lol")
    return
  db.insert({"id": user.id, "money": 1000, "canWork": True})
  await ctx.send(f"`Sucessfully registered:` {user.mention}! Thank you for signing your soul away!")


@bot.command()
async def hack(ctx, user= None):
  if user is None:
    user = ctx.author
  db.update({"canWork": True}, debtors.id == user.id)

@bot.event
async def on_ready():
  print(f"logged in as {bot.user}")

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("This commands format is `$play player1 bet1 player2 bet2`....Maybe you made a typo?")

class BetConfirmation(nextcord.ui.View):
  def __init__(self, plyr1, plyr2):
    super().__init__()
    self.player1 = plyr1
    self.confirm1 = False
    self.confirm2 = False
    self.player2 = plyr2

  @nextcord.ui.button(label = "Confirm", style = nextcord.ButtonStyle.green)
  async def Confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if interaction.user == self.player1:
      self.confirm1 = True
    if interaction.user == self.player2:
      self.confirm2 = True
    if self.confirm1 and self.confirm2:
      self.stop()
      
  @nextcord.ui.button(label = "Cancel", style = nextcord.ButtonStyle.red)
  async def Cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if interaction.user == self.player1:
      self.confirm1 = False
    if interaction.user == self.player2:
      self.confirm2 = False
    self.stop()


class SlvView(nextcord.ui.View):
    def __init__(self, player):
        super().__init__()
        self.choseC = None
        self.player = player
      
    @nextcord.ui.button(label = "Citizen", style = nextcord.ButtonStyle.blurple)
    async def citizen(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
      self.choseC = True
      self.user = interaction.user
      if interaction.user != self.player:
        return
      for i in self.children:
        i.disabled = True
      self.stop()
      

    @nextcord.ui.button(label = "Slave", style = nextcord.ButtonStyle.red)
    async def slave(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
      self.choseC = False
      self.user = interaction.user
      if interaction.user != self.player:
        return
      for i in self.children:
        i.disabled = True
      self.stop()


class EmpView(nextcord.ui.View):
    def __init__(self, player):
        super().__init__()
        self.choseC = None
        self.player = player
      
    @nextcord.ui.button(label = "Citizen", style = nextcord.ButtonStyle.blurple)
    async def citizen(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
      self.choseC = True
      self.user = interaction.user
      if interaction.user != self.player:
        return
      for i in self.children:
        i.disabled = True
      self.stop()

    @nextcord.ui.button(label = "Emperor", style = nextcord.ButtonStyle.green)
    async def slave(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
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
  

@bot.command()
async def play(ctx, userOne, betOne, userTwo, betTwo):
  if ctx.author == bot.user: # you don't want to respond to urself
    return
  if userOne == userTwo:
    await ctx.send("You can't play against yourself, thats a rigged gamble.")
    return
  try:
    betOne = int(betOne)
    betTwo = int(betTwo)
  except:
    await ctx.send("Your bet is not a number.")
    return

  if betOne < 100 or betTwo < 100:
    await ctx.send("Your bet must be greater than or equal to 100, $play follows a specefic format, `$play player1 bet1 player2 bet2` Player1 plays the slave side, Player2 plays emperor side, type $rules to know more")
    return
    
  try:
    userOne = await bot.fetch_user(userOne[3:-1])
    userTwo = await bot.fetch_user(userTwo[3:-1])
  except:
    await ctx.send("$play follows a specefic format, `$play player1 bet1 player2 bet2` Player1 plays the slave side, Player2 plays emperor side, type $rules to know more")
    return

  # now we know all input is valid
  userO, userT = get_players(userOne, userTwo)
  if not userO or not userT:
    await ctx.send("Either one of the users in not registered yet, please run $register to register the user.")
    return
  if userO["money"] < betOne or userT["money"] < betTwo:
    await ctx.send("Bruh you can't bet more than you own, what you want more debt???")
    return

  betconf = BetConfirmation(userOne, userTwo)
  confmsg = await ctx.send(f"Both players please confirm your bets:\n {userOne.name} = ${betOne} (playing Slave side)\n {userTwo.name} = ${betTwo} (playing Emperor side)", view=betconf)
  timeout = await betconf.wait()
  if timeout or (not betconf.confirm1) or (not betconf.confirm2):
    newmsg = await ctx.send("One or both players didn't confirm, please make a new game")
    await async_sleep(1)
    await confmsg.delete()
    await newmsg.delete()
    return

  await confmsg.delete()
  betOne *= 5
  rounds = 1
  turne = await ctx.send(f"`Epic showdown between {userOne.name} and {userTwo.name}\nTurn #{rounds}`")
  msg = await ctx.send(f"`Playing with bets of {int(betOne/5)} on slave side and {betTwo} on emperor side....Creating Game`")
  await async_sleep(1)
  
  A = B = outcome = SlvWin = None
  
  while rounds < 5:
    view = SlvView(userOne)
    viewB = EmpView(userTwo)
    if rounds > 1:
      await turne.edit(f"`Turn #{rounds}`")
    A, B = await turn(msg, userOne, userTwo, view, viewB)
    
    if A and not B: # A chose citizen, B choses emp
      outcome = f"{userTwo.name} WON and got {betTwo + int(betOne/5)} coins!"
      SlvWin = False
      break
    elif not A and not B: # Both sides play key cards
      outcome = f"{userOne.name} WON and got {betOne + betTwo} coins!"
      SlvWin = True
      break
    elif not A and B: # A chose slave, B chose citizen
      outcome = f"{userTwo.name} WON and got {betTwo + int(betOne/5)} coins!"
      SlvWin = False
      break
    else:
      await msg.edit("`both sides chose Citizen 🟦`")
      await async_sleep(1)
    # if all these conditions are false, then both chose citizen
    rounds += 1

  if rounds >= 5:
    outcome = f"{userOne.name} WON (by default) and got {betOne + betTwo} coins!"
    SlvWin = True

  choiceA = "Citizen 🟦" if A else "Slave 🟥"
  choiceB = "Citizen 🟦" if B else "Emperor 🟩"
  if SlvWin:
    winnings = userO["money"] + betOne + betTwo
    losings = userT["money"] - betTwo
    db.update({"money": winnings}, debtors.id == userO["id"])
    db.update({"money": losings}, debtors.id == userT["id"])
  else:
    winnings = userT["money"] + betTwo + int(betOne/5)
    losings = userO["money"] - int(betOne/5)
    db.update({"money": winnings}, debtors.id == userT["id"])
    db.update({"money": losings}, debtors.id == userO["id"])

  #final message
  await ctx.send(f"```{userOne.name} chose {choiceA}\n{userTwo.name} chose {choiceB}\n{outcome}```{userOne.mention} {userTwo.mention}")

async def turn(msg, userOne, userTwo, view, viewB):
  
  #Slave side's turn
  await msg.edit(f"`{userOne.name} chooses first...`\n`which card?`", view=view)
  await view.wait()
  await msg.edit(f"`{userOne.name} chose their card`", view = view)

  #Emperor side's turn
  await msg.edit(f"`{userTwo.name} chooses next...`\n`which card?`", view = viewB)
  await viewB.wait()
  await msg.edit(f"`{userTwo.name} chose their card too`", view = viewB)
  return view.choseC, viewB.choseC

#run the bot

@bot.command()
async def help(ctx):
  await ctx.send(
"""
```$help -> displays this message

$rules -> shows the rules of the game

$play -> plays a match (you need to also mention the users participating)
          example [$play @userA betA @userB betB]```""")

@bot.command()
async def rules(ctx):
  await ctx.send(
"""
```E-Card Rules
                 
- Each side gets 5 cards, out of which 4 are Citizen 🟦, and 1 is either Slave 🟥 or Emperor 🟩

- Both sides then have to choose 1 card and play it against the other side every turn (players will lose the card they played, which means the game can only go up to 5 rounds)

- If both sides choose Citizen 🟦, then it is a tie and the next turn is played

- If one side chooses Emperor 🟩 and the other Citizen 🟦, the Emperor side wins the game

- If one side chooses Slave 🟥 and the other Citizen 🟦, the Emperor side (one who chose Citizen 🟦) wins the game

- If one side chooses Slave 🟥 and the other Emperor 🟩, the Slave side wins the game

- If neither side plays a key card by the 5th round, the Slave side wins by default (as the only possible play is Slave 🟥 vs Emperor 🟩)```""")

@bot.command(aliases = ["bal", "urmom", "money"])
async def balance(ctx, user=None):
  if user is None:
    user = ctx.author
  else:
    user = await bot.fetch_user(user[3:-1])
  res = db.search(debtors.id == user.id)
  if len(res) == 0:
    await ctx.send(f"{user.name} has never played an E-card game before")
  else:
    m = res[0]['money']
    await ctx.send(f"`Your current Balance is: ${m}`")

class WorkView(nextcord.ui.View):
  def __init__(self, workdone):
    super().__init__()
    self.workdone = workdone

  @nextcord.ui.button(label = "Shovel", style = nextcord.ButtonStyle.danger)
  async def shovel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    self.workdone += 5
    if (self.workdone >= 100):
      button.disabled = True
    self.stop()
    
    

@bot.command()
async def work(ctx):
  resp = db.search(debtors.id == ctx.author.id)
  if len(resp) == 0:
    await ctx.send("This user has not played a game yet")
    return
  
  resp = resp[0]
  if resp["canWork"]: 
    db.update({"canWork": False}, debtors.id == ctx.author.id)
    winnings = resp["money"] + 500
    view = WorkView(0)
    msg = await ctx.send("`Press 'Shovel' to dig out the dirt`", view=view)
    while view.workdone < 95:
      await view.wait()
      view = WorkView(view.workdone)
      await msg.edit("`Work done: {}%`".format(view.workdone), view=view)
      
    await msg.edit(f"`Good job, you earned 500 coins!`", view=None) 
    db.update({"money" : winnings}, debtors.id == ctx.author.id)
    await async_sleep(600)
    db.update({"canWork": True}, debtors.id == ctx.author.id)
  else:
    await ctx.send("`You are on cooldown. Wait for 10 minutes before you can work again`")

token = os.environ['token']
keep_running()
bot.run(token)
