# インストールした discord.py を読み込む
import discord
import pickle
import asyncio
import re
import config

# 自分のBotのアクセストークンに置き換えてください
TOKEN = config.MY_TOKEN

# 接続に必要なオブジェクトを生成
client = discord.Client()

#--------------------------------------------定義関数--------------------------------------------
#db関連？
        

#勝率順にソートする関数
def sort(svid):
    global member
    beforeList = []
    afterList = []
    for key in member:
        val = member[key]
        x = val.getWinRate(svid)
        beforeList.append([x,val])
    for i in range(len(beforeList)):
        r = beforeList[i]
        if i == 0:
            afterList.append(beforeList[i])
        else:
            k = afterList[0]
            if r[0] >= k[0]:
                afterList.insert(0,beforeList[i]) 
            else:
                afterList.append(beforeList[i])
    return afterList

#win lose dictを空にする関数
def clean(svid):
    global A
    global D
    A = []
    D = []

#memberNamesの値からキーを抽出する関数　（boombot連動!matchにて使用）
def get_key(val):
    for key, value in memberNames.items():
         if val == value:
             return key
 
    return "情報登録がありません !regist で登録してください"

#--------------------------変数置き場-------------------------
memberID = [["kame"]] #重複登録確認用ID置き場[[user.id,serverid,serverid....],[...]]
member = {} #キー=id,値=インスタンス名のdict  
instanceName = [] #インスタンス名の管理用 (表示名で登録 message.author)
memberNames = {} #キー=表示名, 値=id
A = [] #userIDが入る
D = []
serverList = []#各サーバーに対して[[serverid,[A],[D],…]のリスト  


# カスタム絵文字
EmojiA = "🅰️"
EmojiD = "\N{Turtle}"
EmojiOK= "🆗"
EmojiW = "✅"
EmojiL = "❌"
EmojiC = "🚫"

#-----------------------discord.py event-----------------
# ---------------------起動時に動作する処理-----------------
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')



# ------------------メッセージ受信時に動作する処理------------
@client.event
async def on_message(message):
    global serverList
    global A
    global D
    id_list = [] #boombot 連携にて使用　使い方忘れた
    svid = message.guild.id  #どのサーバーから来たか分かるように定義する。
    x = 0  #クラス変数が使えな勝ったので選手の数とする,選手の登録で使用
    channel = client.get_channel(message.channel.id)

    #boombot自動連動!match!b
    if message.content == "!match-b":
        clean(svid)
        content = f""
        #boombotのメッセージを検索する
        msgList = await channel.history(limit=30).flatten()
        for i in msgList:
            match_result = re.match(r"\*\*Attacker Side\*\*", i.content)
            if match_result:
                msgID = i.id
                break
            else:
                continue

        try:
            message = await channel.fetch_message(msgID)
        except(UnboundLocalError):
            await message.channel.send("boombotの情報が読み取れませんでした。!match!b<messeageID>で指定してください。")
            clean(svid)
            return
        #正規表現にてユーザーidを抜き出す
        msg = message.content
        id_list = re.findall(r'@[\S]{1,18}',msg)
        x = round(len(id_list)/2)
        #Attackerに振り分ける処理
        content += "Attacer:\n"
        for i in range(x):
            id = id_list[i]
            name = get_key(id[1:])
            set_A(svid,id[1:])
            content += str(name) +"\n"

        #Defenderに振り分ける処理
        content += "Defender:\n"
        for i in range(x,len(id_list)):
            id = id_list[i]
            name = get_key(id[1:])
            set_D(svid,id[1:])
            content += str(name) + "\n"
        
        content += f"この内容で正しければ{EmojiOK}キャンセルする場合は{EmojiC}を押してください"
        
        msg = await message.channel.send(content)
        await msg.add_reaction(EmojiOK)
        await msg.add_reaction(EmojiC)



    #boombot連動!match ID検索
    if message.content[:8] == "!match-b":
        if len(message.content) == 26:
            clean(svid)
            content = f""
            message = await channel.fetch_message(int(message.content[8:]))

            #正規表現にてユーザーidを抜き出す
            msg = message.content
            id_list = re.findall(r'@[\S]{1,18}',msg)
            x = round(len(id_list)/2)
            #Attackerに振り分ける処理
            content += "Attacer:\n"
            for i in range(x):
                id = id_list[i]
                name = get_key(id[1:])
                set_A(svid,id[1:])
                content += str(name) +"\n"

            #Defenderに振り分ける処理
            content += "Defender:\n"
            for i in range(x,len(id_list)):
                id = id_list[i]
                name = get_key(id[1:])
                set_D(svid,id[1:])
                content += str(name) + "\n"
            
            content += f"この内容で正しければ{EmojiOK}キャンセルする場合は{EmojiC}を押してください"
            
            msg = await message.channel.send(content)
            await msg.add_reaction(EmojiOK)
            await msg.add_reaction(EmojiC)


    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    
    #選手の登録
    check = False #登録処理で使う
    forcheck = False
    tlist = None
    if message.content == "!regist":
        for i in memberID:
            #重複登録をさせないための処理
            if int(message.author.id) == i[0]:
                check = True
                tlist = i
                for j in range(1,len(i)):
                    if svid == int(i[j]):
                        content = "登録済みです"
                        await message.channel.send(content)
                        forcheck = True
                        break
                if forcheck :
                    break
        else:#登録処理
            if check: #サーバーのみ登録する場合
                tlist.append(svid)
                instance = member[str(message.author.id)]
                instance.registServerID(svid)
                content = str(message.author) + "さんをこのサーバーに追加登録しました"
                await message.channel.send(content)
                return
            
            instanceName.append(message.author)
            instanceName[x] = PlayerManager(str(message.author.id),str(message.author),svid)
            member[str(message.author.id)] = instanceName[x]
            memberNames[str(message.author)] = str(message.author.id)
            content = str(message.author) + "さんを登録しました"
            memberID.append([message.author.id,svid])
            await message.channel.send(content)
            x += 1

    #戦績の記録（手動メンションタイプ）
    if message.content == "!match":
          
        content = f"{EmojiA} = Attacker   {EmojiD} = Defender を選択して、完了したら{EmojiOK}を押してください。キャンセルは{EmojiC}"
        msg = await message.channel.send(content)

        await msg.add_reaction(EmojiA)
        await msg.add_reaction(EmojiD)
        await msg.add_reaction(EmojiOK)
        await msg.add_reaction(EmojiC)
        clean(svid)
    
    #戦績の表示
    if message.content == "!score":
        #製品版は勝率順にソートする
        msg = ""
        list = sort(svid)
        x = 1
        for i in list:
            msg += str(x) + "．" + i[1].score(svid) +"\n"
            x += 1
        await message.channel.send(msg)
        
        """for i in member:
            instancename = member[i]
            await message.channel.send(instancename.score())"""

    #help
    if message.content == "!help":
        content = "選手の登録　!regist\n戦績の記録　!match\n戦績の表示　!score\nbotの終了   　!exit\nboombot連動記録 !match-b または !match!b<messege id を指定>"
        await message.channel.send(content)

    #botを終了させるコマンド
    if message.content == "!exit":
        saveVariableFile()
        exit()
    
    #デバック用
    if message.content == "!print":
        print(f"memberID{memberID}, instanceName{instanceName}, x {x}")
        for i in instanceName:
            print(i.print())
    
    #class操作用
    if message.content == "!class":
        for i in memberNames:
            g = memberNames[i]
            print(i + " " + g)
        key = input("操作するIDを選んでください：")
        win = input("勝利数を入力してください：")
        match = input("対戦回数を入力してください：")
        try:
            win = int(win)
            match  = int(match)
        except(ValueError):
            print("無効な入力です。")
        try:
            val = member[str(key)]
        except(KeyError):
            print("見つかりません")
        val.setMatch(match,svid)
        val.setWin(win,svid)
#---------------------リアクションがついた時の動作----------------------
@client.event
async def on_reaction_add(reaction, user):
    global serverList
    channel = client.get_channel(reaction.message.channel.id)
    svid = reaction.message.guild.id
    if user.bot: #botの場合無視する
        return
    emoji =  reaction.emoji
    A = serch_server(svid)[1]
    D = serch_server(svid)[2]

#選手の振り分け  (リアクションタイプ)
    #Attackerへの振り分け
    if emoji == EmojiA:
        for i in A:
                if i  == user.id: 
                    content = "技術不足により一度登録したリアクションをキャンセル出来ません　!matchからやり直してください"
                    clean(svid)
                    await channel.send(content)
                    break

        for i in D:
            if i  == user.id: 
                content = "重複登録を検知し、キャンセルしました !matchからやり直してください"
                clean(svid)
                await channel.send(content)
                break      

        A.append(user.id)
    #Defenderへの振り分け
    if emoji == EmojiD:
        for i in D:
                if i  == user.id: 
                    content = "技術不足により一度登録したリアクションをキャンセル出来ません　!matchからやり直してください"
                    clean(svid)
                    await channel.send(content)
                    break

        for i in A:
            if i  == user.id: 
                content = "重複登録を検知し、キャンセルしました　!matchからやり直してください"
                clean(svid)
                await channel.send(content)
                break

        D.append(user.id)

    #完了した時の処理
    if emoji == EmojiOK:
        content = f"どっちが勝ちましたか?\n Attackerが勝った場合{EmojiW}　負けた場合{EmojiL}を押してください キャンセルは{EmojiC}"
        msg = await channel.send(content)
        await msg.add_reaction(EmojiW)
        await msg.add_reaction(EmojiL)
        await msg.add_reaction(EmojiC)
        
#勝敗登録  
    if emoji == EmojiW:
        for i in A:
            instance = await memberCheck(channel,i)
            try:
                instance.winMatch(svid)
            except:
                pass
        for i in D:
            instance = await memberCheck(channel,i)
            try:
                instance.loseMatch(svid)
            except:
                pass
        await channel.send('Attackerが勝ちとして記録しました。戦績を見る場合は!score')
        saveVariableFile()
    
    if emoji == EmojiL:
        for i in D:
            instance = await memberCheck(channel,i)
            try:
                instance.winMatch(svid)
            except:
                pass
        for i in A:
            instance = await memberCheck(channel,i)
            try:
                instance.loseMatch(svid)
            except:
                pass
        await channel.send("Defenderが勝ちとして記録しました。戦績を見る場合は!score")
        saveVariableFile()

    if emoji == EmojiC:
        content = "キャンセルしました　!matchからやり直してください"
        await channel.send(content)
        clean(svid)

#リアクションを消した時の動作 #わからん動かん
@client.event
async def on_reaction_remove(reaction, user):
    emoji =  reaction.emoji
    if emoji == EmojiA:
        A.remove(user.id)
        print("kamesan")
    if emoji == EmojiD:
        D.remove(user.id)
        print("kamekame")
    
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)