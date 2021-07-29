from flask import Flask, render_template
from flask import send_from_directory
from flask import request
import os,re
from io import BytesIO
import base64
import random
from PIL import Image, ImageDraw, ImageChops
import time

app = Flask(__name__)

#RGB値からimageオブジェクトを生成して返す関数
def getGraph(r,g,b):
    width = 100
    height = 100
    graph = Image.new("RGB", (width, height), (r,g,b)) # 画像オブジェクトの生成

    return graph

#imageオブジェクトをBase64形式に変換する関数
def encodeBase64(graph):
    draw = ImageDraw.Draw(graph) # 画像オブジェクトの編集用インスタンスの生成

    # ここでdrawインスタンスを用いてgraph上に文字を書いたりして編集します
    # わたしは、データベースから読み出したタスク情報の文字列を書いたりしました

    buffer = BytesIO() # メモリ上への仮保管先を生成
    graph.save(buffer, format="PNG") # pillowのImage.saveメソッドで仮保管先へ保存

    # 保存したデータをbase64encodeメソッド読み込み
    # -> byte型からstr型に変換
    # -> 余分な区切り文字(　'　)を削除
    base64Img = base64.b64encode(buffer.getvalue()).decode().replace("'", "")

    return base64Img

#乱数からカラーコード、RGB、画像を生成して返す関数
def createColorCode():
    radio = request.args.get("radio", type=str, default="False")
    if radio == "cb5":
        r = int(random.uniform(26, 51))
        g = int(random.uniform(26, 51))
        b = int(random.uniform(26, 51))
    elif radio == "cb10":
        r = int(random.uniform(0, 26))
        g = int(random.uniform(0, 26))
        b = int(random.uniform(0, 26))
    else:
        r = int(random.uniform(0, 51))
        g = int(random.uniform(0, 51))
        b = int(random.uniform(0, 51))

    if radio == "cb6":
        rand = int(random.uniform(1,4))
        if rand == 1:
            r=51
        elif rand == 2:
            g=51
        elif rand == 3:
            b=51
    elif radio == "cb7":
        g = int(random.uniform(0, 30))
        b = int(random.uniform(0, 30))
        r = int(random.uniform(max([g,b])+14, 51))
    elif radio == "cb8":
        r = int(random.uniform(0, 30))
        b = int(random.uniform(0, 30))
        g = int(random.uniform(max([r,b])+14, 51))
    elif radio == "cb9":
        g = int(random.uniform(0, 30))
        r = int(random.uniform(0, 30))
        b = int(random.uniform(max([g,r])+14, 51))
    elif radio == "cb11":
        r = int(random.uniform(0, 51))
        g = r
        b = r

    r=r*5
    g=g*5
    b=b*5
    hr = str(hex(r))
    hg = str(hex(g))
    hb = str(hex(b))

    if len(hr) == 3:
        hr = "0" + hr
    if len(hg) == 3:
        hg = "0" + hg
    if len(hb) == 3:
        hb = "0" + hb

    code = "#" + hr + hg + hb
    rgb = "rgb(" + str(r) + "," + str(g) + "," + str(b) + ")"
    code = code.replace("0x","")

    #pillowで画像生成
    img = getGraph(r,g,b)
    return code,rgb,img

def resize(img,perW,perH):
    return img.resize((int(img.width * perW), int(img.height * perH)))

#サンプルデザインを作成する関数
def createSample(p1,p2,p3,p4):
    #2色サンプル1
    samp2_1 = Image.new('RGB', (p1.width,p1.height))
    samp2_1.paste(resize(p1,1,0.5), (0                       , 0                      ))
    samp2_1.paste(resize(p2,1,0.5), (0                       , resize(p1,1,0.5).height))

    #2色サンプル2
    samp2_2 = Image.new('RGB', (p1.width,p1.height))
    samp2_2.paste(resize(p1,1,0.2), (0                       , 0                      ))
    samp2_2.paste(resize(p2,1,0.8), (0                       , resize(p1,1,0.2).height))

    #2色サンプル3
    samp2_3 = Image.new('RGB', (p1.width,p1.height))
    samp2_3.paste(resize(p1,0.4,0.4), (0                     , 0                      ))
    samp2_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, 0                      ))
    samp2_3.paste(resize(p1,0.4,0.4), (resize(p1,0.6,1).width, 0                      ))
    samp2_3.paste(resize(p2,  1,0.2), (0                     , resize(p1,1,0.4).height))
    samp2_3.paste(resize(p1,0.4,0.4), (0                     , resize(p1,1,0.6).height))
    samp2_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, resize(p1,1,0.6).height))
    samp2_3.paste(resize(p1,0.4,0.4), (resize(p1,0.6,1).width, resize(p1,1,0.6).height))

    #2色サンプル4
    samp2_4 = Image.new('RGB', (p1.width,p1.height))
    samp2_4.paste(resize(p1,0.5,0.5), (0                     , 0                      ))
    samp2_4.paste(resize(p2,0.5,0.5), (resize(p1,0.5,1).width, 0                      ))
    samp2_4.paste(resize(p2,0.5,0.5), (0                     , resize(p1,1,0.5).height))
    samp2_4.paste(resize(p1,0.5,0.5), (resize(p1,0.5,1).width, resize(p1,1,0.5).height))

    #3色サンプル1
    samp3_1 = Image.new('RGB', (p1.width,p1.height))
    samp3_1.paste(resize(p1, 1,0.2), (0                       , 0                      ))
    samp3_1.paste(resize(p2, 1,0.6), (0                       , resize(p1,1,0.2).height))
    samp3_1.paste(resize(p3, 1,0.2), (0                       , resize(p1,1,0.8).height))

    #3色サンプル2
    samp3_2 = Image.new('RGB', (p1.width,p1.height))
    samp3_2.paste(resize(p1,  1,0.2), (0                       , 0                      ))
    samp3_2.paste(resize(p2,0.5,0.8), (0                       , resize(p1,1,0.2).height))
    samp3_2.paste(resize(p3,0.5,0.8), (resize(p1,0.5,0.8).width, resize(p1,1,0.2).height))

    #3色サンプル3
    samp3_3 = Image.new('RGB', (p1.width,p1.height))
    samp3_3.paste(resize(p1,0.4,0.4), (0                     , 0                      ))
    samp3_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, 0                      ))
    samp3_3.paste(resize(p1,0.4,0.4), (resize(p1,0.6,1).width, 0                      ))
    samp3_3.paste(resize(p3,  1,0.2), (0                     , resize(p1,1,0.4).height))
    samp3_3.paste(resize(p1,0.4,0.4), (0                     , resize(p1,1,0.6).height))
    samp3_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, resize(p1,1,0.6).height))
    samp3_3.paste(resize(p1,0.4,0.4), (resize(p1,0.6,1).width, resize(p1,1,0.6).height))

    #3色サンプル4
    samp3_4 = Image.new('RGB', (p1.width,p1.height))
    samp3_4.paste(resize(p1,0.5,0.5), (0                     , 0                      ))
    samp3_4.paste(resize(p2,0.5,0.5), (resize(p1,0.5,1).width, 0                      ))
    samp3_4.paste(resize(p3,0.5,0.5), (0                     , resize(p1,1,0.5).height))
    samp3_4.paste(resize(p1,0.5,0.5), (resize(p1,0.5,1).width, resize(p1,1,0.5).height))


    #4色サンプル1
    samp4_1 = Image.new('RGB', (p1.width,p1.height))
    samp4_1.paste(resize(p1,  1,0.2), (0                       , 0                      ))
    samp4_1.paste(resize(p2,  1,0.3), (0                       , resize(p1,1,0.2).height))
    samp4_1.paste(resize(p3,  1,0.2), (0                       , resize(p1,1,0.5).height))
    samp4_1.paste(resize(p4,  1,0.3), (0                       , resize(p1,1,0.7).height))

    #4色サンプル2
    samp4_2 = Image.new('RGB', (p1.width,p1.height))
    samp4_2.paste(resize(p1,  1,0.2), (0                       , 0                      ))
    samp4_2.paste(resize(p2,0.5,0.6), (0                       , resize(p1,1,0.2).height))
    samp4_2.paste(resize(p3,0.5,0.6), (resize(p1,0.5,0.8).width, resize(p1,1,0.2).height))
    samp4_2.paste(resize(p4,  1,0.2), (0                       , resize(p1,1,0.8).height))
    
    #4色サンプル3
    samp4_3 = Image.new('RGB', (p1.width,p1.height))
    samp4_3.paste(resize(p1,0.4,0.4), (0                     , 0                      ))
    samp4_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, 0                      ))
    samp4_3.paste(resize(p4,0.4,0.4), (resize(p1,0.6,1).width, 0                      ))

    samp4_3.paste(resize(p3,1,0.2), (0                     , resize(p1,1,0.4).height))

    samp4_3.paste(resize(p4,0.4,0.4), (0                     , resize(p1,1,0.6).height))
    samp4_3.paste(resize(p2,0.2,0.4), (resize(p1,0.4,1).width, resize(p1,1,0.6).height))
    samp4_3.paste(resize(p1,0.4,0.4), (resize(p1,0.6,1).width, resize(p1,1,0.6).height))

    #4色サンプル4
    samp4_4 = Image.new('RGB', (p1.width,p1.height))
    samp4_4.paste(resize(p1,0.5,0.5), (0                     , 0                      ))
    samp4_4.paste(resize(p2,0.5,0.5), (resize(p1,0.5,1).width, 0                      ))
    samp4_4.paste(resize(p3,0.5,0.5), (0                     , resize(p1,1,0.5).height))
    samp4_4.paste(resize(p4,0.5,0.5), (resize(p1,0.5,1).width, resize(p1,1,0.5).height))


    return samp2_1,samp2_2,samp2_3,samp2_4,samp3_1,samp3_2,samp3_3,samp3_4,samp4_1,samp4_2,samp4_3,samp4_4

#16進カラーコードからimageオブジェクト生成する関数
def codetoImg(code):
    code = code.replace("#","")
    r = int(code[0:2],16)
    g = int(code[2:4],16)
    b = int(code[4:6],16)

    return getGraph(r,g,b)

#16進カラーコードからRGB値を返す関数
def codetoRGB(code):
    code = code.replace("#","")
    r = int(code[0:2],16)
    g = int(code[2:4],16)
    b = int(code[4:6],16)

    return r,g,b

#整数のRGB値から16進カラーコードを生成する関数
def rgbtoCode(r,g,b):
    return "#" + str(hex(r))[2:4] + str(hex(g))[2:4] + str(hex(b))[2:4]

#css反映のための関数
@app.context_processor
def add_staticfile():
    def staticfile_cp(fname):
        path = os.path.join(app.root_path, 'static', fname)
        mtime =  str(int(os.stat(path).st_mtime))
        return './static/' + fname + '?v=' + str(mtime)
    return dict(staticfile=staticfile_cp)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/'), 'favicon.ico', )

@app.route('/')
def index():

    cb1 = request.args.get("cb1", type=str, default="False")
    cb2 = request.args.get("cb2", type=str, default="False")
    cb3 = request.args.get("cb3", type=str, default="False")
    cb4 = request.args.get("cb4", type=str, default="False")
    radio = request.args.get("radio", type=str, default="")

    c1,rgb1,img1 = createColorCode()
    c2,rgb2,img2 = createColorCode()
    c3,rgb3,img3 = createColorCode()
    c4,rgb4,img4 = createColorCode()

    checked1 = ""
    checked2 = ""
    checked3 = ""
    checked4 = ""
    checked5 = ""
    checked6 = ""
    checked7 = ""
    checked8 = ""
    checked9 = ""
    checked10 = ""  
    checked11 = ""
    if cb1 != "False":
        checked1 = "checked"
        c1,rgb1 = cb1.split("+")
        img1 = codetoImg(c1)
    if cb2 != "False":
        checked2 = "checked"
        c2,rgb2 = cb2.split("+")
        img2 = codetoImg(c2)
    if cb3 != "False":
        checked3 = "checked"
        c3,rgb3 = cb3.split("+")
        img3 = codetoImg(c3)
    if cb4 != "False":
        checked4 = "checked"
        c4,rgb4 = cb4.split("+")
        img4 = codetoImg(c4)
    if radio == "cb5":
        checked5 = "checked"
    if radio == "cb6":
        checked6 = "checked"
    if radio == "cb7":
        checked7 = "checked"
    if radio == "cb8":
        checked8 = "checked"
    if radio == "cb9":
        checked9 = "checked"
    if radio == "cb10":
        checked10 = "checked"
    if radio == "cb11":
        checked11 = "checked"

    #thumb.png作成
    img = Image.new('RGB', (img1.width,img1.height*4))
    img.paste(img1, (0, 0))
    img.paste(img2, (0, img1.height))
    img.paste(img3, (0, img1.height*2))
    img.paste(img4, (0, img1.height*3))
    #img.save("./static/thumb.png",format="PNG")

    samp2_1,samp2_2,samp2_3,samp2_4,samp3_1,samp3_2,samp3_3,samp3_4,samp4_1,samp4_2,samp4_3,samp4_4 = createSample(img1,img2,img3,img4)

    #送信データ
    colors = {"c1":c1,"c2":c2,"c3":c3,"c4":c4}
    rgbs = {"rgb1":rgb1,"rgb2":rgb2,"rgb3":rgb3,"rgb4":rgb4}
    check = {"cb1":checked1,"cb2":checked2,"cb3":checked3,"cb4":checked4,"cb5":checked5,
             "cb6":checked6,"cb7":checked7,"cb8":checked8,"cb9":checked9,"cb10":checked10,"cb11":checked11}
    imgs = {"samp2_1":encodeBase64(samp2_1),"samp2_2":encodeBase64(samp2_2),"samp2_3":encodeBase64(samp2_3),"samp2_4":encodeBase64(samp2_4),
            "samp3_1":encodeBase64(samp3_1),"samp3_2":encodeBase64(samp3_2),"samp3_3":encodeBase64(samp3_3),"samp3_4":encodeBase64(samp3_4),
            "samp4_1":encodeBase64(samp4_1),"samp4_2":encodeBase64(samp4_2),"samp4_3":encodeBase64(samp4_3),"samp4_4":encodeBase64(samp4_4)}
    
    metatags = {"description":"ランダムに配色パターンを生成するジェネレーターサイト。アイデア出しにご活用ください。",
                "keywords":"配色,配色パターン,配色パターン 4色,配色ジェネレーター,配色 デザイン"}

    #ツイートボタン作成
    tweet = "今日の配色はこれ！\n" + rgb1 + " " + c1 + "\n" + rgb2 + " " + c2 + "\n" + rgb3 + " " + c3 +"\n" + rgb4 + " " + c4 +"\n\n"
    tweetbtn = "\
    <div class='twitter'>\
    <a href='//twitter.com/share' class='twitter-share-button' data-text='" + tweet + "'  data-lang='ja'>\
        入力内容を呟く\
    </a>\
    </div>\
    <script async src='https://platform.twitter.com/widgets.js' charset='utf-8'></script>"  

    return render_template('main.html', title="ランダムに配色パターンを生成するジェネレーターサイト - ランダムカラーズ",metatags=metatags,colors=colors,rgbs=rgbs,check=check,tweetbtn=tweetbtn,imgs=imgs)

def select_four(imgs):
    new_imgs = imgs[:]
    returns = []
    if len(new_imgs) >= 4:
        for i in range(0,4,1):
            n = int(random.uniform(0, len(new_imgs)))
            returns.append(new_imgs.pop(n))
        return returns[0],returns[1],returns[2],returns[3]
    else:
        return

@app.route('/start')
def start():
    num = "<p>遊び方</p>\
            <ol style='text-align:left'>\
                <li>[脳トレを始める]ボタンを押すと見本と9つの画像が表示されます。</li>\
                <li>見本と同じ画像をクリックしてください。</li>\
                <li>全5問で終了します。</li>\
                <li>全問正解するとクリアタイムが表示されます。</li>\
            </ol>"
    num = "<p>遊び方</p>\
                <div class='left'>\
                <p>①[脳トレを始める]ボタンを押すと見本と9つの画像が表示されます。</p><p></p>\
                <p>②見本と同じ画像をクリックしてください。</p><p></p>\
                <p>③全5問で終了します。</p><p></p>\
                <p>④全問正解するとクリアタイムが表示されます。</p>\
                </div>"

    metatags = {"description":"色を使った脳トレゲーム。無料で遊べます。","keywords":"脳トレゲーム,脳トレゲーム 無料"}
    return render_template('start.html',title="脳トレゲーム - ランダムカラーズ",metatags=metatags,btn_title="脳トレを始める",num=num)

@app.route('/game')
def game():
    metatags = {"description":"色を使った脳トレゲーム。無料で遊べます。","keywords":"脳トレゲーム,脳トレゲーム 無料"}
    
    ans = request.args.get("ans", type=str, default="mis_0_0")
    cnt = str(int(ans.split("_")[1])+1) #問題数のカウント
    num = "第" + cnt + "問目"
    cur = ans.split("_")[2] #正答数のカウント
    if ans.split("_")[0] == "ans":
        cur = str(int(cur)+1)

    if cnt == "6":
        dif = round(time.time() - float(ans.split("_")[3]),2)
        num = cur + "問正解！"
        if cur == "5":
            num = "全問正解！" + "<br>" + "今回の記録は" + str(dif) + "秒"
        num = "<h2>" + num + "</h2>"
        return render_template('start.html',title="脳トレゲーム - ランダムカラーズ",metatags=metatags,num=num,btn_title="再挑戦する")

    if cnt == "1":
        st = str(time.time())
    else:
        st = ans.split("_")[3]

    img1 = createColorCode()[2]
    img2 = createColorCode()[2]
    img3 = createColorCode()[2]
    img4 = createColorCode()[2]
    img5 = createColorCode()[2]
    img6 = createColorCode()[2]
    imgs = [img1,img2,img3,img4,img5,img6]

    samp = []
    for i in range(0,10,1):
        p1,p2,p3,p4 = select_four(imgs)
        samp.append(encodeBase64(createSample(p1,p2,p3,p4)[11]))

    answers = []
    for a in range(1,10,1):
        answers.append("mis_" + cnt + "_" + cur + "_" + st)

    ans = int(random.uniform(1, 9))
    answers[ans] = "ans_" + cnt + "_" + cur + "_" + st


    btn_imgs = {"samp01":samp[1],"samp02":samp[2],"samp03":samp[3],"samp04":samp[4],
                "samp05":samp[5],"samp06":samp[6],"samp07":samp[7],"samp08":samp[8],"samp09":samp[9]}

    return render_template('game.html',title="脳トレゲーム - ランダムカラーズ",metatags=metatags,btn_imgs=btn_imgs,answers=answers,ans_img=samp[ans],num=num)

@app.route('/howto')
def howto():
    metatags = {"description":"配色ジェネレーターの使い方","keywords":"配色,配色パターン,配色パターン 4色,配色ジェネレーター,配色 デザイン"} 
    return render_template('howto.html',title="使い方 - ランダムカラーズ",metatags=metatags)

@app.route('/gradation')
def gradation():
    c1 = request.args.get("c1", type=str, default="#ffffff")
    c2 = "#FFFFFF"
    c3 = "#FFFFFF"
    c4 = "#FFFFFF"
    c5 = request.args.get("c5", type=str, default="#ffffff")

    c1r,c1g,c1b = codetoRGB(c1)
    c5r,c5g,c5b = codetoRGB(c5)
    dr = (c5r - c1r)//4
    dg = (c5g - c1g)//4
    db = (c5b - c1b)//4

    c2r = c1r + (dr*1)
    c2g = c1g + (dg*1)
    c2b = c1b + (db*1)
    c2 = rgbtoCode(c2r,c2g,c2b)
    rgb2 = "rgb(" + str(c2r) + "," + str(c2g) + "," + str(c2b) + ")"

    c3r = c1r + (dr*2)
    c3g = c1g + (dg*2)
    c3b = c1b + (db*2)
    c3 = rgbtoCode(c3r,c3g,c3b)
    rgb3 = "rgb(" + str(c3r) + "," + str(c3g) + "," + str(c3b) + ")"
    
    c4r = c1r + (dr*3)
    c4g = c1g + (dg*3)
    c4b = c1b + (db*3)
    c4 = rgbtoCode(c4r,c4g,c4b)
    rgb4 = "rgb(" + str(c4r) + "," + str(c4g) + "," + str(c4b) + ")"

    colors = {"c1":c1,"c2":c2,"c3":c3,"c4":c4,"c5":c5}
    rgbs = {"rgb2":rgb2,"rgb3":rgb3,"rgb4":rgb4}

    #ツイートボタン作成
    tweet = "今日のグラデーションはこれ！\n"
    tweetbtn = "\
    <div class='twitter'>\
    <a href='//twitter.com/share' class='twitter-share-button' data-text='" + tweet + "'  data-lang='ja'>\
        入力内容を呟く\
    </a>\
    </div>\
    <script async src='https://platform.twitter.com/widgets.js' charset='utf-8'></script>"

    metatags = {"description":"指定した色からグラデーションを作れるジェネレーター","keywords":"配色 グラデーション,グラデーション,グラデーション デザイン,グラデーション WEBデザイン"}  

    return render_template('gradation.html',title="グラデーションジェネレーター - ランダムカラーズ",metatags=metatags,colors=colors,rgbs=rgbs,tweetbtn=tweetbtn)

@app.route('/compcolor')
def compcolor():
    
    c1 = request.args.get("c1", type=str, default="#ffffff")

    c1r,c1g,c1b = codetoRGB(c1)
    rgb1 = "rgb(" + str(c1r) + "," + str(c1g) + "," + str(c1b) + ")"

    sum = max(c1r,c1g,c1b) + min(c1r,c1g,c1b)

    c2r = sum - c1r
    c2g = sum - c1g
    c2b = sum - c1b
    c2 = rgbtoCode(c2r,c2g,c2b)
    rgb2 = "rgb(" + str(c2r) + "," + str(c2g) + "," + str(c2b) + ")"

    colors = {"c1":c1,"c2":c2}
    rgbs = {"rgb2":rgb2}

    #ツイートボタン作成
    tweet = rgb1 + "の補色は" + rgb2
    tweetbtn = "\
    <div class='twitter'>\
    <a href='//twitter.com/share' class='twitter-share-button' data-text='" + tweet + "'  data-lang='ja'>\
        入力内容を呟く\
    </a>\
    </div>\
    <script async src='https://platform.twitter.com/widgets.js' charset='utf-8'></script>"

    metatags = {"description":"補色を生成するツール。カラーコードとRGBを表示","keywords":"補色,補色 ツール,補色とは,補色 カラーコード,補色 組み合わせ"} 

    return render_template('compcolor.html',title="補色生成ツール - ランダムカラーズ",metatags=metatags,colors=colors,rgbs=rgbs,tweetbtn=tweetbtn)

## おまじない
if __name__ == "__main__":
    #app.run(debug=True)
    app.run()
