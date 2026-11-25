# 《The Sekimeiya: Spun Glass》前文引用对照（对应 all_entries.json）

位置一律用 JSON 条目的 `id`（例如 `script_rpy_L028515_1_c47501c5`）。在 all_entries.json 里搜这个 id，或搜「英文可搜索句」。

- **英文相同**：原句和引用处的 `text` 一致（忽略大小写、空白和 `{w}` 等标签）。若英文本身有差别，会分行写出。
- **两边 new**：你这份 JSON 里已填的中文是否一致。不一致时会列出两处译文。
- 旧全文本行号不能用来检索这份 JSON，这里不再作为主键。

## 重点检索

在 all_entries.json 里搜下面的 `id` 或英文片段。英文 `text` 相同的条目，你填的 `new` 里已有 **208 处中文不一致**，完整差异见各表「两边 new」列。

### 1. 第五章复盘引用第一章尾声

- 原话：`script_rpy_L028515_1_c47501c5`　Don't forget what I said... I meant all of it.
- 第一章独白回放：`script_rpy_L028675_1_74a5af90`
- 第五章开篇同一句：`script_rpy_L058606_1_4fe504f3`
- 第五章再次想起：`script_rpy_L058715_1_c4a2d13b`
- 「A month? What kind of joke was that?」第一章 `script_rpy_L028674_1_ffc044ca` ⇔ 第五章 `script_rpy_L058605_1_808ab696`
- 整段倒计时独白：第一章约 `script_rpy_L028673`–`L028686` ⇔ 第五章约 `script_rpy_L058604`–`L058615`

### 2. 第三章偷听第一章

- `Shiroya! Are you there!?`　第一章 `script_rpy_L021783_1_73d7aa21` ⇔ 第三章（远处听见）`script_rpy_L053941_1_6b2ce3f7`
- `...No. I haven't killed anyone.`　第一章 `script_rpy_L023288_1_f65c7c30`（原文无开头省略号）⇔ 第三章 `script_rpy_L054147_1_9269b900`
- `Where did you even get that knife!? Did you kill Katei and Erina?`　第三章 `script_rpy_L054142_1_8aef5065`（对第一章同句）
- `I've seen Katei's and Erina's corpses.`　第三章 `script_rpy_L054152_1_8800b79b`
- `Shiroya! Can you hear me!?`　第三章现身时 `script_rpy_L054317_1_84c09c7b`；此后与第一章后段同一场对话对位，见正文 2.3 节（约一百句）

### 3. 录音笔四处

同一批对白出现在：第一章第一次播放（说话人带 `2`，如 `ak2`/`sai2`/`il2`）、第一章两处闪回、第五章现场「活出」。

| 英文可搜索句 | 第一次播放 | 闪回 | 第五章现场 |
|---|---|---|---|
| Well... what do we do now? | `script_rpy_L012873_1_6aae5348` | — | `script_rpy_L059124_1_fa5faec0` |
| What do you want to do? We might've been here for more than a month | `script_rpy_L012889_1_c9b40567` | — | `script_rpy_L059130_1_d6f75ee0` |
| I don't get it. What the hell happened? | `script_rpy_L012891_1_0e28da3a` | — | `script_rpy_L059136_1_b74e5677` |
| Atsuki, what are you thinking about? | `script_rpy_L012894_1_5ad0c1c3` | `script_rpy_L021619_1_a8e169b2` | `script_rpy_L059142_1_c01ad663` |
| Isla...! What the hell!? | `script_rpy_L012909_1_37d460a2` | — | `script_rpy_L059152_1_6ff11f48` |
| Hey, answer us...! Wh-What are you looking at!? | `script_rpy_L012912_1_b622151b` | — | `script_rpy_L059154_1_f41524ab` |
| ...Where am I...? | `script_rpy_L012913_1_9500163c` | `script_rpy_L018641_1_94078671` | `script_rpy_L059155_1_24b8ea80` |
| Wh-What do you mean? We're still in Ashiya Tower. | `script_rpy_L012914_1_bd262dcc` | `script_rpy_L018642_1_e005ccb1` | `script_rpy_L059156_1_e0404c2c` |
| No, I know. What I mean is... what happened to me? Where am I? | `script_rpy_L012915_1_c49f234b` | `script_rpy_L018643_1_259d9a7d`；叙述再引 `script_rpy_L018647_1_e54e0444` | `script_rpy_L059157_1_6d6653cc` |
| I-Isla, what's gotten into you? | `script_rpy_L012935_1_b6865bc8` | `script_rpy_L021620_1_d237ee43` | `script_rpy_L059163_1_f6474f20` |

另：终章与第三章末「the recording was real / Like I said, the recording was real」几乎整场重复：第三章 `script_rpy_L055306_1_584cb15b` 起 ⇔ 终章 `script_rpy_L068448_1_70e419f7` 起；其中关键句 `script_rpy_L055361_1_3698e58d` ⇔ `script_rpy_L068492_1_0bfb1724`。

---

## 1.1 开篇接续第一章尾声（L18595–18604）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L028674_1_ffc044ca` | `script_rpy_L058605_1_808ab696` | A month? What kind of joke was that? I couldn't bear one more second. | **不一致**<br>原句：一个月？这算什么玩笑？我一秒都熬不下去了。<br>引用：一个月？这算什么玩笑？我连一秒都撑不下去了。 |
| 2 | 逐字重复 | `script_rpy_L028675_1_74a5af90` | `script_rpy_L058606_1_4fe504f3` | Shiroya's words played back in my head. "Don't forget what I said... I meant all of it." | **不一致**<br>原句：Shiroya 的话在脑中回响。『别忘了我说过的话……每一句都是真心的。』<br>引用：Shiroya 的话在我脑中回响。「别忘了我说过的话……那些话，句句都是真心。」 |
| 3 | 逐字重复 | `script_rpy_L028676_1_5f7289f9` | `script_rpy_L058607_1_f847af5f` | I laughed, alone. I didn't know where I was, what anything had become... none of it. Nothing we'd done had any meaning. We'd made it to t… | **不一致**<br>原句：我独自笑了。我不知道自己身在何处，不知道一切都变成了什么样……什么都不知道。我们所做的一切毫无意义。我们熬过了那漫长得不可思议的一天，却什么也没换来。<br>引用：我独自笑了出来。我不知道自己在哪儿，不知道一切变成了什么样……什么都不知道。我们所做的一切毫无意义。熬过那漫长得不像话的一天，到头来全是白费。 |
| 4 | 逐字重复 | `script_rpy_L028677_1_ff009bda` | `script_rpy_L058608_1_8be43db1` | The words Shiroya had abandoned me with... Were they supposed to be reassuring? | 一致 |
| 5 | 逐字重复 | `script_rpy_L028683_1_19a43ca7` | `script_rpy_L058612_1_c4d4669f` | But I couldn't help but despair. I wanted to leave. I wanted to be hit by the icy air and feel released. I wanted to talk to more people,… | **不一致**<br>原句：可我无法不绝望。我想离开这里。我想被冰冷的空气拍在脸上，好让自己松一口气。我想和更多人说话，哪怕对方是警察也好。<br>引用：可我止不住地绝望。我想离开这里。我想被冰冷的空气扑面打醒，得到解脱。我想多和人说说话，哪怕对方是警察也好。 |
| 6 | 逐字重复 | `script_rpy_L028684_1_ac61b76d` | `script_rpy_L058613_1_ae13c443` | And it wouldn't happen. Could we survive an entire month? Of course not...! Shiroya hadn't been mentioned in the recording, so would I no… | **不一致**<br>原句：而这不可能实现。我们能撑过整整一个月吗？当然不能……！录音里没有提到 Shiroya，难道我要好几周都见不到她？<br>引用：而这都不可能了。我们能撑过整整一个月吗？怎么可能……！录音里没有提到 Shiroya，那岂不是几周都见不到她？ |
| 7 | 逐字重复 | `script_rpy_L028685_1_3943501e` | `script_rpy_L058614_1_deede32b` | Would the nightmare persist in the Sekimeiya's domain? It was too horrible of a thought to bear. People had died, and I still didn't know… | **不一致**<br>原句：这场噩梦会在 Sekimeiya 的领域里一直持续下去吗？这念头太可怕，我承受不住。有人死了，而我至今不知道是谁、怎么死的、为什么……<br>引用：这场噩梦会在 Sekimeiya 的领域里一直延续下去吗？光是想到这一点就令人无法承受。有人死了，而我至今不知道死者是谁、怎么死的、为什么死…… |
| 8 | 逐字重复 | `script_rpy_L028686_1_ef7977a7` | `script_rpy_L058615_1_f64f1132` | The lights had gone out, so I followed their example. I closed my eyes, intensifying the darkness, before I felt once again how insignifi… | **不一致**<br>原句：灯已经灭了，我便也照做。我闭上眼睛，让黑暗更深一层，随后再一次感到自己是多么渺小。<br>引用：灯已经灭了，我便也随他们闭上眼。黑暗更浓了几分，我再一次感到自己是多么渺小。 |
| 9 | 稍作改写 | `script_rpy_L028673_1_811c1965` | `script_rpy_L058604_1_b14433db` | My body crumpled down; I couldn't keep going. | **不一致**<br>原句：我双腿一软，再也支撑不住。<br>引用：{w=0.6}我的身体瘫软下去，再也走不动了。 |
| 10 | 稍作改写（两句并成一行） | `script_rpy_L028681_1_8ecbc997` | `script_rpy_L058611_1_74591ad2` | 原句：I tried to continue yelling her name, but my voice broke. She'd known what would happen a…<br>引用：I tried to continue yelling her name, but my voice broke. She'd known what would happen a… | 英文本不完全相同，中文不必逐字一致 |
| 11 | 断续重述（只摘了前半） | `script_rpy_L028515_1_c47501c5` | `script_rpy_L058606_1_4fe504f3`<br>`script_rpy_L028675_1_74a5af90` | 原句：Don't forget what I said... I meant all of it. Now stay here, and don't follow me.<br>引用：Shiroya's words played back in my head. "Don't forget what I said... I meant all of it." | 英文本不完全相同，中文不必逐字一致 |
| 12 | 断续重述 | `script_rpy_L028515_1_c47501c5` | `script_rpy_L058715_1_c4a2d13b` | 原句：Don't forget what I said... I meant all of it. Now stay here, and don't follow me.<br>引用："Don't forget what I said... I meant all of it." If she's not here anymore, then who did … | 英文本不完全相同，中文不必逐字一致 |

## 1.2 当场「活出」第一章里播过的录音（L18836–18854）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L012873_1_6aae5348` | `script_rpy_L059124_1_fa5faec0` | Well... what do we do now? | **不一致**<br>原句：那么……现在怎么办？<br>引用：那……现在怎么办？ |
| 2 | 逐字重复 | `script_rpy_L012889_1_c9b40567` | `script_rpy_L059130_1_d6f75ee0` | What do you want to do? We might've been here for more than a month and the exit's not open. Unless you wanna take down the shutter by ha… | **不一致**<br>原句：你想怎么办？我们可能已经在这儿待了一个多月，出口还是没开。除非你想徒手把卷帘门拆下来，否则只能继续等。<br>引用：你想怎么办？我们在这里怕是待了一个多月，出口却始终没开。除非你打算徒手把卷帘门拆下来，否则只能继续等。 |
| 3 | 逐字重复 | `script_rpy_L012891_1_0e28da3a` | `script_rpy_L059136_1_b74e5677` | I don't get it. What the hell happened? Did Ashiya just abandon their own building with us inside...? And we thought we'd be free after t… | **不一致**<br>原句：我不明白。到底出了什么事？Ashiya 就这么把自己楼里的人丢下不管了……？我们还以为熬过十二小时就能出去……<br>引用：我不明白。到底出了什么事？芦屋难道就把我们丢在自己的楼里不管了……？明明说好十二小时后就放我们出去的…… |
| 4 | 逐字重复 | `script_rpy_L012894_1_5ad0c1c3` | `script_rpy_L059142_1_c01ad663` | Atsuki, what are you thinking about? Do you have any more ideas...? And hey, Erina, what's with that face? | **不一致**<br>原句：Atsuki，你在想什么？还有什么主意吗……？还有，Erina，你那是什么表情？<br>引用：Atsuki，你在想什么？还有什么主意吗……？喂，Erina，你那张脸是怎么回事？ |
| 5 | 逐字重复 | `script_rpy_L012907_1_27911589` | `script_rpy_L059144_1_dd19c96d` | What, not going to answer? | 一致 |
| 6 | 逐字重复 | `script_rpy_L012909_1_37d460a2` | `script_rpy_L059152_1_6ff11f48` | Isla...! What the hell!? | **不一致**<br>原句：Isla……！搞什么鬼！？<br>引用：Isla……！这到底是怎么回事！？ |
| 7 | 逐字重复 | `script_rpy_L012912_1_b622151b` | `script_rpy_L059154_1_f41524ab` | Hey, answer us...! Wh-What are you looking at!? | **不一致**<br>原句：喂，回答我们啊……！你、你在看什么！？<br>引用：喂，你倒是说话啊……！你、你在看什么！？ |
| 8 | 逐字重复 | `script_rpy_L012914_1_bd262dcc` | `script_rpy_L059156_1_e0404c2c` | Wh-What do you mean? We're still in Ashiya Tower. Do you not remember? | **不一致**<br>原句：你、你说什么？我们还在芦屋塔里啊。你不记得了？<br>引用：你、你说什么？我们还在芦屋塔啊，你不记得了？ |
| 9 | 逐字重复 | `script_rpy_L012915_1_c49f234b` | `script_rpy_L059157_1_6d6653cc` | No, I know. What I mean is... what happened to me? Where am I? | **不一致**<br>原句：不，我知道。我是说……我到底怎么了？我在哪儿？<br>引用：不，我知道。我是说……我到底怎么了？我这是在哪儿？ |
| 10 | 逐字重复 | `script_rpy_L012935_1_b6865bc8` | `script_rpy_L059163_1_f6474f20` | I-Isla, what's gotten into you? ...What are you holding? And Erina, why aren't you doing anything!? | **不一致**<br>原句：Isla，你、你这是怎么了？……你手里拿的是什么？{w} 还有 Erina，你怎么什么都不做！？<br>引用：I、Isla，你怎么了？……你手里拿着什么？{w}还有 Erina，你怎么一点反应都没有！？ |

## 1.3 重历第三章「突然出现在事件起点」（L19010–19113 ⇔ 第三章 L15929–16060）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L051012_1_64b97dc8` | `script_rpy_L059703_1_f61ec239` | A-Are you Shiroya...? | 一致 |
| 2 | 逐字重复 | `script_rpy_L051013_1_58aa19b2` | `script_rpy_L059708_1_d4b14eeb` | What? Y-Yes. Where are we? I just appeared here. | **不一致**<br>原句：什么？是、是我。这是什么地方？我刚才突然就出现在这儿了。<br>引用：什么？是、是我。这是哪儿？我刚才突然就出现在这里了。 |
| 3 | 逐字重复 | `script_rpy_L051029_1_6683b29d` | `script_rpy_L059723_1_36205f63` | Y-Yes, but doesn't it look different? | **不一致**<br>原句：是、是的，可你不觉得样子不太一样吗？<br>引用：是、是的，可看起来不太一样吧？ |
| 4 | 逐字重复 | `script_rpy_L051035_1_f1d07a61` | `script_rpy_L059729_1_624807a4` | I'm not sure where we are. I just appeared here too. | **不一致**<br>原句：我也不清楚这是哪儿。我也是突然出现在这里的。<br>引用：我也不清楚这是哪儿。我也是突然就出现在这里的。 |
| 5 | 逐字重复 | `script_rpy_L051052_1_d8c3f8c1` | `script_rpy_L059739_1_4d485b8b` | Oh, fuck. Don't breathe. | **不一致**<br>原句：操。别吸气。<br>引用：该死。别吸气。 |
| 6 | 逐字重复 | `script_rpy_L051061_1_c34134e1` | `script_rpy_L059748_1_c7353235` | A-Are we on the morning of the 15th? | **不一致**<br>原句：我、我们是在15日的早上？<br>引用：现、现在是15号的早上吗？ |
| 7 | 逐字重复 | `script_rpy_L051068_1_af034e6d` | `script_rpy_L059750_1_45c64ced` | ...Are you really Shiroya? The real one? | **不一致**<br>原句：……你真的是 Shiroya？本人？<br>引用：……你真的是 Shiroya？真正的那个？ |
| 8 | 逐字重复 | `script_rpy_L051069_1_7c850ef0` | `script_rpy_L059755_1_4bcc7fb0` | What does that mean...!? Who else would I be? | 一致 |
| 9 | 逐字重复 | `script_rpy_L051074_1_24916ca8` | `script_rpy_L059756_1_06e7efac` | ...What do you remember? Please, tell me everything. | **不一致**<br>原句：……你记得些什么？拜托，全都告诉我。<br>引用：……你都记得什么？拜托，全都告诉我。 |
| 10 | 逐字重复 | `script_rpy_L051075_1_397120d3` | `script_rpy_L059761_1_90f7112d` | What!? I-I don't know what you mean! We got trapped here, and a bunch of things happened! | **不一致**<br>原句：什么！？我、我不明白你在说什么！我们被困在这儿，出了好多事！<br>引用：什么！？我、我不明白你在说什么！我们被困在这里，还发生了那么多事！ |
| 11 | 逐字重复 | `script_rpy_L051076_1_467879b9` | `script_rpy_L059762_1_1604682d` | What happened? How did you end up here? | **不一致**<br>原句：出了什么事？你怎么会到这儿来？<br>引用：发生什么了？你怎么会到这里来？ |
| 12 | 逐字重复 | `script_rpy_L051077_1_db9d9f43` | `script_rpy_L059763_1_17247835` | H-Huh? A lot of things! Do you remember everything? Late into the day, we were in the lobby, and I went to the bathroom. There, I activat… | **不一致**<br>原句：啊？很、很多事！你全都记得吗？那天很晚了，我们在大厅，我去了洗手间。就在那儿，我启动了 Sekimeiya，出现在11月30日，那家宝石店的下方。{w}然后……<br>引用：咦、咦？说来话长！你什么都记得吗？那天快到傍晚的时候，我们在大厅，我去了洗手间。就在那里，我启动了 Sekimeiya，然后出现在 11 月 30 日，那家宝… |

## 1.4 推理中回放的第一章对白与场景

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L026043_1_7b6764cb` | `script_rpy_L060787_1_1afb137b` | Of course, I'm assuming Miiya's in on it as well. | **不一致**<br>原句：当然，我猜 Miiya 也有份。<br>引用：当然，我假定 Miiya 也参与其中。 |
| 2 | 逐字重复 | `script_rpy_L026060_1_1e948f5d` | `script_rpy_L060793_1_42fdfeb0` | ...Okay, I'll ask. How do you know about Miiya? | **不一致**<br>原句：……好吧，我问。你怎么知道 Miiya 的事？<br>引用：……好，我问一句。你怎么知道 Miiya 的事？ |
| 3 | 逐字重复 | `script_rpy_L026061_1_06f21016` | `script_rpy_L060794_1_5fb64e03` | What? She's been here— | **不一致**<br>原句：什么？她一直就在这里——<br>引用：什么？她一直在这儿—— |
| 4 | 逐字重复 | `script_rpy_L026062_1_231b72b5` | `script_rpy_L060795_1_04d86dfc` | That's it, ignore him from now on. He can't get out of the corner he's backed himself into. | **不一致**<br>原句：行了，从现在起别理他。他已经把自己逼进死角，出不来了。<br>引用：够了，从现在起别理他。他自己把自己逼进了死角，出不来了。 |
| 5 | 逐字重复 | `script_rpy_L019732_1_b0c73dcd` | `script_rpy_L061806_1_afaf5716` | 原句：Depending on how it works, the possibilities could be limitless. There's even a higher st…<br>引用："Depending on how it works, the possibilities could be limitless. There's even a higher s… | 英文本不完全相同，中文不必逐字一致 |
| 6 | 逐字重复 | `script_rpy_L019734_1_fd08534c` | `script_rpy_L061808_1_db1b5a2b` | 原句：Out of the countless examples, could you go back in time, trade information with someone,…<br>引用："Out of the countless examples, could you go back in time, trade information with someone… | 英文本不完全相同，中文不必逐字一致 |
| 7 | 逐字重复 | `script_rpy_L019735_1_7d9e3b25` | `script_rpy_L061809_1_474bb066` | 原句：You'd read the note and go back to the past. However, since you would already know the co…<br>引用："You'd read the note and go back to the past. However, since you would already know the c… | 英文本不完全相同，中文不必逐字一致 |
| 8 | 逐字重复 | `script_rpy_L019736_1_f4a24756` | `script_rpy_L061810_1_4fdcc723` | 原句：The note itself would be a paradox that you caused, but was the past truly changed? Was a…<br>引用："The note itself would be a paradox that you caused, but was the past truly changed? Was … | 英文本不完全相同，中文不必逐字一致 |
| 9 | 逐字重复 | `script_rpy_L019737_1_68a223a1` | `script_rpy_L061811_1_9b8faf03` | 原句：...If Sai's watch got to "9999-12-31" by spending infinite time in a loop, did the pasts …<br>引用："...If Sai's watch got to "9999-12-31" by spending infinite time in a loop, did the pasts… | 英文本不完全相同，中文不必逐字一致 |
| 10 | 逐字重复 | `script_rpy_L023918_1_a3c98943` | `script_rpy_L062555_1_e9385c78` | You perfectly remember when we went up to the attic to get the lithium battery, right? | **不一致**<br>原句：我们上阁楼去拿锂电池那件事，你记得一清二楚，对吧？<br>引用：我们上阁楼拿锂电池的时候，你记得很清楚，对吧？ |
| 11 | 逐字重复 | `script_rpy_L023924_1_c9ad6e20` | `script_rpy_L062561_1_f129ebc4` | How did you do that? | 一致 |
| 12 | 逐字重复 | `script_rpy_L023925_1_ef08fb88` | `script_rpy_L062562_1_3907c322` | I said you're incompetent, but at least you're doing your best, unlike the others. | **不一致**<br>原句：我说过你没本事，不过至少你还在尽力，不像其他人。<br>引用：我说过你无能，但至少你还在尽力，不像其他人。 |
| 13 | 逐字重复 | `script_rpy_L023927_1_6ced1e0b` | `script_rpy_L062564_1_5991e7eb` | That's my answer. I suppose it just appeared impressive from your point of view. | **不一致**<br>原句：这就是我的回答。大概只是从你的角度看，才显得了不起吧。<br>引用：这就是我的回答。大概只是从你的角度看来，才显得了不起罢了。 |
| 14 | 逐字重复 | `script_rpy_L015005_1_4f56c169` | `script_rpy_L062579_1_68b4552a` | Yes. He was leading the conversation, telling everyone not to follow us down. Akaro was there too, and he confirmed that he saw us. Sai t… | **不一致**<br>原句：是的。他在引导大家，叫他们不要跟着我们下去。Akaro 也在，还确认他看见了我们。Sai 让他们都等着我们，因为我们是自己擅自离开的，之后发生什么事都由我们负…<br>引用：嗯。当时是他在主导话题，让所有人都不要跟下来找我们。Akaro 也在场，还确认说看见过我们。Sai 让大家等我们回来，因为我们是自愿离开的，之后出了什么事都由… |
| 15 | 逐字重复 | `script_rpy_L015006_1_25048458` | `script_rpy_L062580_1_5f4008c4` | ...I see. So he wanted the others not to come down. | **不一致**<br>原句：……我明白了。所以他想让其他人别下来。<br>引用：……原来如此。所以他是想让其他人别下来。 |
| 16 | 逐字重复 | `script_rpy_L015007_1_e58fb206` | `script_rpy_L062581_1_e142c163` | He kept saying it. He never left, and the elevator was still there with the door open. The conversation started winding down, and when th… | **不一致**<br>原句：他反复这么说。他一直没离开，电梯也还停在那里，门开着。谈话渐渐接近尾声，他们提到要去洗手间时，我立刻离开，免得被人看见。{w}我关着门在客厅里待了几分钟，但我…<br>引用：他一直在强调这一点。他始终没离开，电梯也一直停在那里，门开着。谈话渐渐接近尾声，当他们提到要去洗手间时，我立刻离开，免得被人看见。{w} 我在客厅里关着门待了… |
| 17 | 稍作改写 | `script_rpy_L015813_1_a914403f` | `script_rpy_L062700_1_370ba8dd` | 原句：We were used to looking at the footprints in front of the door, but that was no longer po…<br>引用："We were used to looking at the footprints in front of the door, but that was no longer p… | 英文本不完全相同，中文不必逐字一致 |
| 18 | 稍作改写 | `script_rpy_L015814_1_f07740aa` | `script_rpy_L062701_1_e34ac230` | We must have. This means that the group already left, though. | **不一致**<br>原句：应该是吧。不过这也说明，那群人已经先离开了。<br>引用：应该是我们。不过这样说来，其他人已经走了。 |
| 19 | 稍作改写 | `script_rpy_L015815_1_48324549` | `script_rpy_L062702_1_31aad71d` | 原句：Even though the motion of the door wiped out the nearby marks, there were many around the…<br>引用："Even though the motion of the door wiped out the nearby marks, there were many around th… | 英文本不完全相同，中文不必逐字一致 |
| 20 | 逐字重复 | `script_rpy_L016298_1_0ff25c3f` | `script_rpy_L062742_1_1d0a30e6` | 原句：Sai, showing the strongest reaction, approached the room while letting out a conspicuous …<br>引用："Sai, showing the strongest reaction, approached the room while letting out a conspicuous… | 英文本不完全相同，中文不必逐字一致 |
| 21 | 逐字重复 | `script_rpy_L015445_1_e7839474` | `script_rpy_L062788_1_89eba22c` | 原句：I wasn't sure what Sai planned to do, but we'd seen him standing in front of the door. Sh…<br>引用："I wasn't sure what Sai planned to do, but we'd seen him standing in front of the door. S… | 英文本不完全相同，中文不必逐字一致 |
| 22 | 逐字重复 | `script_rpy_L016539_1_8b30275c` | `script_rpy_L062818_1_9674b649` | Where did you go...? We searched for you. | 一致 |
| 23 | 逐字重复 | `script_rpy_L016540_1_1e16ed8d` | `script_rpy_L062819_1_27652509` | 原句：Sai shot the first question, and an immediate answer came that left the three of them uns…<br>引用："Sai shot the first question, and an immediate answer came that left the three of them un… | 英文本不完全相同，中文不必逐字一致 |
| 24 | 逐字重复 | `script_rpy_L016541_1_0e0685bf` | `script_rpy_L062824_1_d5e114d5` | I don't know. I think I experienced what Atsuki said... That teleportation. I've been searching for you. | **不一致**<br>原句：我不知道。我大概经历了 Atsuki 说的那件事……那个传送。我一直在找你们。<br>引用：我不知道。我想我也经历了 Atsuki 说的那件事……那次传送。我一直在找你们。 |
| 25 | 逐字重复 | `script_rpy_L016778_1_94b075c2` | `script_rpy_L062841_1_6d6734f6` | Understand that what you've told us is that you two spent all this time asleep in the attic. Despite this, you weren't found. | **不一致**<br>原句：你要清楚，按你的说法，你们俩这段时间一直在阁楼里睡觉。可即便如此，你们却没被找到。<br>引用：你这话的意思，就是你们俩这段时间一直睡在阁楼。可即便如此，你们却没被找到。 |
| 26 | 逐字重复 | `script_rpy_L016779_1_d9e3edee` | `script_rpy_L062842_1_33f95b38` | ...You didn't find Katei either, so you obviously didn't do a great job. And you were in a rush, so you kept yelling Isla's name while qu… | **不一致**<br>原句：……你们不也没找到 Katei 吗？可见搜得也不怎么样。而且你们当时急匆匆的，一边喊着 Isla 的名字一边草草查看。我敢说，你们根本没看卧室上层——我们就待…<br>引用：……你们不也没找到 Katei 吗，可见搜得也不怎么样。你们当时心急，一边喊着 Isla 的名字一边匆匆地看。我敢说你们根本没看卧室的上层，我们就待在那儿；我… |
| 27 | 逐字重复 | `script_rpy_L027699_1_f57ee93f` | `script_rpy_L063062_1_6e6aa2a3` | ...We still haven't searched the whole floor. I'll go leave the Sekimeiya in the event room, and we won't move it again. | **不一致**<br>原句：……{w}这一层还没搜完。我去把 Sekimeiya 放到活动室，之后谁都不再动它。<br>引用：……{w}我们还没搜完整层。我去把这台 Sekimeiya 放到活动室，之后我们也不会再动它。 |
| 28 | 逐字重复 | `script_rpy_L027705_1_c43ce4cd` | `script_rpy_L063067_1_3f2c1c8e` | ...There's nothing else to find, is there? Do you seriously believe Shiroya will be here? We've already found the Sekimeiya. | **不一致**<br>原句：……已经没什么可找的了吧？你真觉得 Shiroya 会在这里？Sekimeiya 都已经找到了。<br>引用：……已经没别的可找了吧？你真觉得 Shiroya 会在这里？Sekimeiya 都已经找到了。 |
| 29 | 稍作改写 | `script_rpy_L027706_1_07e2e3b3` | `script_rpy_L063068_1_23482d0d` | 原句：I stared at Sai's eyes, a little disconcerted. His voice sounded noticeably more nervous …<br>引用："I stared at Sai's eyes, a little disconcerted. His voice sounded noticeably more nervous… | 英文本不完全相同，中文不必逐字一致 |
| 30 | 逐字重复 | `script_rpy_L027707_1_11c43026` | `script_rpy_L063069_1_e794b8b6` | ...Is there something else to find here? | 一致 |
| 31 | 逐字重复 | `script_rpy_L027712_1_0573fab7` | `script_rpy_L063070_1_0b4fa0b1` | Hm? What would that be? | **不一致**<br>原句：嗯？还能有什么？<br>引用：嗯？你指什么？ |
| 32 | 逐字重复 | `script_rpy_L028243_1_51352b96` | `script_rpy_L063103_1_98e8299b` | 原句：I noticed the brief instant in which Erina's expression showed surprise. She was still in…<br>引用："I noticed the brief instant in which Erina's expression showed surprise. She was still i… | 英文本不完全相同，中文不必逐字一致 |
| 33 | 逐字重复 | `script_rpy_L028244_1_7d99cd1c` | `script_rpy_L063104_1_97d449c3` | Did you see something? | 一致 |
| 34 | 稍作改写 | `script_rpy_L028253_1_c931337c` | `script_rpy_L063110_1_fc48000a` | 原句：I walked up to her, but I found nothing that stood out in the hallway.<br>引用："I walked up to her, but I found nothing that stood out in the hallway." | 英文本不完全相同，中文不必逐字一致 |
| 35 | 逐字重复 | `script_rpy_L028264_1_af1593bd` | `script_rpy_L063120_1_e1cdf43e` | Or do we use these last minutes to find Sai and the Sekimeiya? If he took it, he must have something in mind, and as much as I want to ge… | **不一致**<br>原句：还是说，用这最后几分钟去找 Sai 和 Sekimeiya？若是他拿走的，那他一定另有打算——我虽然一心想出去，却也不愿任由他为所欲为。<br>引用：「还是说，我们用最后这几分钟去找 Sai 和 Sekimeiya？如果他拿走了它，肯定有他的打算。虽然我很想出去，但也不想由着他乱来。」 |
| 36 | 逐字重复 | `script_rpy_L028269_1_c0ea7bef` | `script_rpy_L063125_1_0d002a5f` | Y-Yes... Maybe we should search for him. | **不一致**<br>原句：是、是啊……也许该去找找他。<br>引用：「是、是啊……也许我们该去找找他。」 |
| 37 | 逐字重复 | `script_rpy_L028275_1_832a48bf` | `script_rpy_L063133_1_7b1caa52` | Search complete. You all did an amazing job this time. | **不一致**<br>原句：搜查结束。这次各位都干得很出色。<br>引用：「搜索完毕。各位这次干得漂亮。」 |
| 38 | 稍作改写 | `script_rpy_L020720_1_54cf60f3` | `script_rpy_L063338_1_4e4d5313` | 原句：We heard an indistinct sound coming from hallway A, made by a door.<br>引用："We heard an indistinct sound coming from hallway A, made by a door." | 英文本不完全相同，中文不必逐字一致 |
| 39 | 逐字重复 | `script_rpy_L020721_1_cca9aea6` | `script_rpy_L063339_1_742319f7` | That's us. We just entered the event room. | **不一致**<br>原句：是我们。我们刚进活动室。<br>引用：就是我们。我们刚走进活动室。 |
| 40 | 逐字重复 | `script_rpy_L020724_1_797fbe51` | `script_rpy_L063340_1_1239ccda` | 原句：We waited, and seconds later, the same sound came from hallway B. Unmistakably, a closing…<br>引用："We waited, and seconds later, the same sound came from hallway B. Unmistakably, a closin… | 英文本不完全相同，中文不必逐字一致 |
| 41 | 逐字重复 | `script_rpy_L023815_1_03c448fd` | `script_rpy_L063692_1_02a68f87` | I thought you'd overstepped, but it seems I was the one who had. | **不一致**<br>原句：我本以为是你越界了，看来越界的是我。<br>引用：我原以为是你越界了，看来越界的人是我。 |
| 42 | 稍作改写 | `script_rpy_L033844_1_3d470dd8` | `script_rpy_L063693_1_d11fdcd2` | 原句：Shut up. What the fuck did that even mean?<br>引用：What the fuck did that even mean? | 英文本不完全相同，中文不必逐字一致 |
| 43 | 逐字重复 | `script_rpy_L023671_1_cf90f63a` | `script_rpy_L063749_1_6270d322` | I also just said what my plan relies on: I must go back to the past, but I don't need to go too far. If I had another Sekimeiya hidden, w… | **不一致**<br>原句：我也刚说过我的计划靠的是什么：我必须回到过去，但不用回得太远。如果我另藏了一件Sekimeiya，那还用这一件做什么？直接拿手上那件回去不就行了？<br>引用：我刚才也说了，我的计划建立在什么之上：我必须回到过去，但不需要回到太久以前。如果我另外藏着一台 Sekimeiya，那还用这一台做什么？直接用手上另一台回到过… |
| 44 | 逐字重复 | `script_rpy_L023677_1_b937f20c` | `script_rpy_L063755_1_93e219bb` | This is an actual question. If I know where another Sekimeiya is like you say, why would I not simply use that one? | **不一致**<br>原句：我是认真在问。如果真像你说的，我知道另一件Sekimeiya在哪儿，那我为什么不干脆用那一件？<br>引用：我这是认真在问。如果真像你说的那样，我知道另一台 Sekimeiya 在哪里，那我为什么不直接用那一台？ |
| 45 | 逐字重复 | `script_rpy_L054681_1_25b9fdcb` | `script_rpy_L063783_1_5b57e96a` | Oh, right, I'd forgotten about this too. | **不一致**<br>原句：哦，对，这事我也忘了。<br>引用：啊，对了，我也忘了这回事。 |
| 46 | 稍作改写 | `script_rpy_L025275_1_3bd9b68a` | `script_rpy_L063784_1_b585791c` | 原句：Still sounding groggy, she traced my gaze up to her purse and took out a small piece of p…<br>引用："Still sounding groggy, she traced my gaze up to her purse and took out a small piece of … | 英文本不完全相同，中文不必逐字一致 |
| 47 | 逐字重复 （另见 第三章 L17318） | `script_rpy_L025280_1_a372a125` | `script_rpy_L063789_1_c12cfb8e` | I found this just now. I tried to read it, but my head hurt a lot. Do you know what it is? | **不一致**<br>原句：这是我刚捡到的。我想读，可头疼得厉害。你知道这是什么吗？<br>引用：这是我刚才找到的。我想看看上面写了什么，可头很疼。你知道这是什么吗？ |
| 48 | 稍作改写 | `script_rpy_L025287_1_371060ad` | `script_rpy_L063794_1_ae02bf41` | 原句：She handed it to me, and I snatched it away, gripping it tightly. My hands started trembl…<br>引用："She handed it to me, and I snatched it away, gripping it tightly. My hands started tremb… | 英文本不完全相同，中文不必逐字一致 |
| 49 | 逐字重复 | `script_rpy_L003762_1_f1d4d717` | `script_rpy_L064598_1_62456a39` | Eventually, up that mountain is a small field that's pretty well-hidden. It's not easy to spot, and you have to deviate onto a smaller pa… | **不一致**<br>原句：沿山而上，最后会到一小片相当隐蔽的平地。那里不容易发现，得岔到一条更窄的小路上去。我得到的说法只是，那地方藏得很深。<br>引用：沿那座山一直往上，最后会有一小片空地，藏得相当隐蔽。很不容易发现，而且要拐上一条更窄的小路。我听到的说法也只是说那里相当僻静。 |
| 50 | 逐字重复 | `script_rpy_L003767_1_0df45551` | `script_rpy_L064605_1_3b1660cb` | That's where this was found. | **不一致**<br>原句：这东西就是在那儿被发现的。<br>引用：那东西就是在那儿被发现的。 |

## 1.5 潜入 B 世界，跟听／跟看第二章行程（`c5continue` L21017–21527）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 断续重述 | `script_rpy_L029779_1_7aa6f889` | `script_rpy_L065264_1_d850e34b` | 原句：Are you okay? I'm sorry I made you come here.<br>引用：...ou okay? I'm so— | 英文本不完全相同，中文不必逐字一致 |
| 2 | 断续重述 | `script_rpy_L029784_1_3dd15c26` | `script_rpy_L065268_1_e8acc695` | 原句：No... Don't worry. None of this is your fault.<br>引用：Don't worry. No— ...our fault. | 英文本不完全相同，中文不必逐字一致 |
| 3 | 逐字重复 | （无独立原句 id） | `script_rpy_L065287_1_d501586c` | ...There's a reason why I believe Naomi hid upstairs if she's part of this, like I suspect. Above us are five desolate floors full of off… | （仅引用处） |
| 4 | 断续重述 | `script_rpy_L029779_1_7aa6f889` | `script_rpy_L065264_1_d850e34b` | 原句：Are you okay? I'm sorry I made you come here.<br>引用：...ou okay? I'm so— | 英文本不完全相同，中文不必逐字一致 |

## 1.6 补叙 `c2explained`（L21528–21827）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复（加了引号） | `script_rpy_L038871_1_455cfbe4` | `script_rpy_L067073_1_da6ab799` | 原句：With what we'd talked about, could Erina's killer be identified? I didn't think so, but t…<br>引用："With what we'd talked about, could Erina's killer be identified? I didn't think so, but … | 英文本不完全相同，中文不必逐字一致 |
| 2 | 稍作改写 | `script_rpy_L038312_1_f58f3273` | `script_rpy_L067067_1_429c1dbb` | 原句：My heavy breathing was interrupting my words, and I didn't let my gaze stray from Erina. …<br>引用："My heavy breathing was interrupting my words, and I didn't let my gaze stray from Erina.… | 英文本不完全相同，中文不必逐字一致 |
| 3 | 逐字重复 | `script_rpy_L038942_1_1a18bd7a` | `script_rpy_L067081_1_0e1f63db` | 原句：She was there, casually leaning against the line of cabinets. I could hardly believe what…<br>引用："She was there, casually leaning against the line of cabinets. I could hardly believe wha… | 英文本不完全相同，中文不必逐字一致 |
| 4 | 逐字重复 | `script_rpy_L038310_1_d554b8ff` | `script_rpy_L067150_1_9caaa05c` | It's not possible for us to take the elevator, so let's walk up. We should come across someone. | **不一致**<br>原句：电梯是坐不成了，我们走上去吧。总会碰上人的。<br>引用：我们没法坐电梯，那就走上去吧。总能碰上人的。 |
| 5 | 逐字重复 | `script_rpy_L038346_1_0d447d5f` | `script_rpy_L067158_1_91ad0269` | 原句：I stared at the floor's footprints—the proof that the past had changed. I had no idea how…<br>引用："I stared at the floor's footprints—the proof that the past had changed. I had no idea ho… | 英文本不完全相同，中文不必逐字一致 |

## 1.7 终章补叙：与第三章末「录音是真的」对谈重复

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L055306_1_584cb15b` | `script_rpy_L068448_1_70e419f7` | There you are... You did come. I'd forgotten you had the key to the attic. | **不一致**<br>原句：你果然来了……真的来了。{w}我都忘了，阁楼的钥匙在你手上。<br>引用：你来了……你真的来了。{w}我都忘了，阁楼的钥匙在你手上。 |
| 2 | 逐字重复 | `script_rpy_L055307_1_3c7316d8` | `script_rpy_L068453_1_1b739c43` | Are you... the Atsuki from this morning? | 一致 |
| 3 | 逐字重复 | `script_rpy_L055313_1_10667d8a` | `script_rpy_L068455_1_e6ae6058` | Y-You knew I would be here, right? You remembered what happened. | **不一致**<br>原句：你、你知道我会来，对吧？你还记得发生过的事。<br>引用：你、你早就知道我会在这儿吧？你记得发生过什么。 |
| 4 | 逐字重复 | `script_rpy_L055319_1_197392cd` | `script_rpy_L068462_1_d745151e` | Have you been here all this time? When you disappeared this morning, I tried to find you, but I was in another world, right? | **不一致**<br>原句：你一直待在这里吗？今天早上你消失之后，我想去找你，可那时我已经在另一个世界了，对吧？<br>引用：你一直都待在这里吗？今天早上你消失之后，我到处找你，可那时我已经在另一个世界了，对吧？ |
| 5 | 逐字重复 | `script_rpy_L055324_1_5ed7d39c` | `script_rpy_L068464_1_4aad374b` | I... think so. I learned a lot of things. It's been longer than you think since I saw you. | **不一致**<br>原句：我……想是吧。我弄清了很多事。我上次见你，已经是很久以前的事了，比你想象的要久得多。<br>引用：我……应该是。我知道了很多事。距离我上次见你，已经比你想象的要久了。 |
| 6 | 逐字重复 | `script_rpy_L055325_1_94577ee7` | `script_rpy_L068469_1_2dda9119` | What do you mean? You said the recording was real, right? What happened at ? And why did both of us appear at the start of today? | **不一致**<br>原句：什么意思？你说过那段录音是真的，对吧？{time=21} 到底发生了什么？还有，为什么我们两个都出现在今天开始的时候？<br>引用：你是什么意思？你说过那段录音是真的，对吧？{time=21} 究竟发生了什么？还有，我们两个为什么都出现在今天刚开始的时候？ |
| 7 | 逐字重复 | `script_rpy_L055330_1_d52c6f27` | `script_rpy_L068470_1_af706493` | ...Why did we travel to this morning? I know the answer now. | 一致 |
| 8 | 逐字重复 | `script_rpy_L055336_1_61bd06ff` | `script_rpy_L068472_1_792060a3` | I remember what you told me. You said you traveled to the 30th of November, and that a few days later, you touched the Sekimeiya in the t… | **不一致**<br>原句：我记得你跟我说过的话。你说你穿越到了 11 月 30 日，几天之后，在塔里碰了 Sekimeiya。是这样吧？<br>引用：我记得你告诉过我的话。你说你穿越到了 11 月 30 日，几天之后，你在塔里碰到了 Sekimeiya。是这样吧？ |
| 9 | 逐字重复 | `script_rpy_L055337_1_15d85d49` | `script_rpy_L068473_1_2581ca51` | Y-Yes. That's when I appeared with you in the lobby. | **不一致**<br>原句：是、是的。我就是在那时和你一起出现在大厅的。<br>引用：对、对。就是那时候，我和你一起出现在了大厅。 |
| 10 | 逐字重复 | `script_rpy_L055342_1_8102c727` | `script_rpy_L068474_1_e39171f8` | No, that's wrong. I know what happened to you. | 一致 |
| 11 | 逐字重复 | `script_rpy_L055344_1_dc33413e` | `script_rpy_L068480_1_612dc590` | You didn't go to November... You went to the future. | **不一致**<br>原句：你没有去 11 月……你去的是未来。<br>引用：你不是去了十一月……你去的是未来。 |
| 12 | 逐字重复 | `script_rpy_L055349_1_fe77f10c` | `script_rpy_L068485_1_0262e254` | ...Wh-What? No I didn't. I went two weeks to the past. | **不一致**<br>原句：……什、什么？不可能。我是往过去走了两周。<br>引用：……什、什么？不可能。我是回到了两周前。 |
| 13 | 逐字重复 | `script_rpy_L055354_1_ca15b6fe` | `script_rpy_L068486_1_4884369b` | I don't know why you think that, but I believe you went to the future. You said that you entered the tower in early December. I believe t… | **不一致**<br>原句：我不知道你为什么会这么想，但我相信你去的是未来。{w}你说过，你是在 12 月初进入塔里的。我认为那其实是 1 月 5 日。<br>引用：我不知道你为什么会这么想，但我认为你去的是未来。{w}你说你是在十二月初进入塔里的。我认为那其实是 1 月 5 日。 |
| 14 | 逐字重复 | `script_rpy_L055361_1_3698e58d` | `script_rpy_L068492_1_0bfb1724` | Like I said, the recording was real. On the 5th of January, we were in the tower. That's why I appeared with you in the lobby when you to… | **不一致**<br>原句：我说过了，录音是真的。一月五日那天，我们就在塔里。所以你碰到 Sekimeiya 的时候，我才会和你一起出现在大厅。<br>引用：我说过了，录音是真的。1 月 5 日那天，我们就在塔里。所以当你碰到 Sekimeiya 时，我才会和你一起出现在大厅。 |
| 15 | 逐字重复 | `script_rpy_L055362_1_b3d86fa2` | `script_rpy_L068493_1_e374459d` | N-No. No. How would I have gone to the future? There's no way. | **不一致**<br>原句：不、不会的。不可能。我怎么可能去到未来？绝无可能。<br>引用：不、不会的。不会的。我怎么可能去到未来？绝无可能。 |
| 16 | 逐字重复 | `script_rpy_L055363_1_c6c7e4b4` | `script_rpy_L068494_1_fe068972` | With the Sekimeiya. There were two of them. | **不一致**<br>原句：靠的是 Sekimeiya。当时有两个。<br>引用：靠 Sekimeiya。当时有两个。 |
| 17 | 逐字重复 | `script_rpy_L055366_1_0056a597` | `script_rpy_L068501_1_63ef187d` | I... know. I saw that too. What do you mean, though? | **不一致**<br>原句：我……知道。那个我也看见了。可你这话是什么意思？<br>引用：我……知道。我也看见了。可你这话是什么意思？ |
| 18 | 逐字重复 | `script_rpy_L055371_1_cc94ae3e` | `script_rpy_L068502_1_93182551` | I've thought about everything that happened. There always were two Sekimeiya, but only one of them made us go to the past. The other one … | **不一致**<br>原句：发生过的每件事我都想过了。始终有两个 Sekimeiya，但把我们送往过去的只有一个。另一个，则把我们送去了未来。<br>引用：发生过的事，我全都想了一遍。Sekimeiya 一直都有两个，但把我们送回过去的只有一个。另一个则把我们送去了未来。 |
| 19 | 逐字重复 | `script_rpy_L055377_1_4ecba2a5` | `script_rpy_L068504_1_f4082571` | The one in the water tank sent you to the future, but that wasn't the first time. ...It wasn't the first time you'd traveled forward in t… | **不一致**<br>原句：水箱里的那个把你送到了未来，但那并不是第一次。……你并非第一次穿越到未来。之前还有过好几次。<br>引用：水箱里的那一个把你送到了未来，可那已经不是第一次了。……你以前就穿越到过未来。还有另外几次。 |

## 2.1 未现身时听到的台词

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复（远处喊声，她在藏匿处听到） | `script_rpy_L021783_1_73d7aa21` | `script_rpy_L053941_1_6b2ce3f7` | Shiroya! Are you there!? | 一致 |
| 2 | 逐字重复 | `script_rpy_L023278_1_41931c8b` | `script_rpy_L054142_1_8aef5065` | Where did you even get that knife!? Did you kill Katei and Erina? | **不一致**<br>原句：你从哪儿弄来那把刀的！？你杀了 Katei 和 Erina 吗？<br>引用：你那把刀到底是从哪来的！？你杀了 Katei 和 Erina 吗？ |
| 3 | 稍作改写（多了句首省略号） | `script_rpy_L023288_1_f65c7c30` | `script_rpy_L054147_1_9269b900` | 原句：No. I haven't killed anyone.<br>引用：...No. I haven't killed anyone. | 英文本不完全相同，中文不必逐字一致 |
| 4 | 逐字重复 | `script_rpy_L023300_1_eefb6f03` | `script_rpy_L054152_1_8800b79b` | Listen, here's a good question for you. I've seen Katei's and Erina's corpses. If I killed them, how come there's no blood on my clothes? | **不一致**<br>原句：听好，我倒要问你们一个问题。Katei 和 Erina 的尸体我见过。如果是我杀的，那我衣服上怎么一点血都没有？<br>引用：听好了，我问你个有意思的问题。我见过 Katei 和 Erina 的尸体。如果是我杀的，那我衣服上怎么一点血都没有？ |
| 5 | 逐字重复（此后她开始回应，进入 2.3 的会合场） | `script_rpy_L024839_1_a40faa9a` | `script_rpy_L054317_1_84c09c7b` | Shiroya! Can you hear me!? | **不一致**<br>原句：Shiroya！听得见吗！？<br>引用：Shiroya！你听得见吗！？ |

## 2.2 断续或改写的听句／自引

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 稍作改写＋听述（「处理点事」被叙述改写成「处理一些事情」） | `script_rpy_L025262_1_fda4c940`<br>`script_rpy_L054673_1_ee4f4b78` | `script_rpy_L054674_1_c178770c` | 原句：I see, they're definitely an improvement for you. And just ignore me, Atsuki. I was busy …<br>引用："Sorting something out". I couldn't help but react, as I knew he had just locked my past … | 英文本不完全相同，中文不必逐字一致 |
| 2 | 稍作改写（章内自引＋与第一章细节差） | `script_rpy_L054609_1_2125ab6b`<br>`script_rpy_L054928_1_54d1c04c`<br>`script_rpy_L025188_1_52668d06` | `script_rpy_L054949_1_856862b1` | 原句：Erina opened the glass and rolled the Sekimeiya into her purse, not wanting to touch it f…<br>引用："Erina opened the glass and rolled the Sekimeiya into her purse, not wanting to touch it … | 英文本不完全相同，中文不必逐字一致 |
| 3 | 未对上原句（按她自己的推论处理，不必向某句对白看齐） | （无独立原句 id） | `script_rpy_L054104_1_711b4093` | "If I don't intend to change the past, it won't change." As long as that notion was correct, I could peek out from where I was, knowing I… | （仅引用处） |

## 2.3 现身之后：与第一章后段同一场对话的对位

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L024839_1_a40faa9a` | `script_rpy_L054317_1_84c09c7b` | Shiroya! Can you hear me!? | **不一致**<br>原句：Shiroya！听得见吗！？<br>引用：Shiroya！你听得见吗！？ |
| 2 | 逐字重复 | `script_rpy_L024846_1_45bafe22` | `script_rpy_L054324_1_a74013a9` | You're okay, right!? If you can hear me, please come out! Say something! | **不一致**<br>原句：你没事吧！？听得见就快出来！说句话啊！<br>引用：你没事吧！？听得见的话，就出来啊！说句话啊！ |
| 3 | 逐字重复 | `script_rpy_L024887_1_9bbb5098` | `script_rpy_L054352_1_6f61f48e` | ...Are you actually Shiroya? | 一致 |
| 4 | 逐字重复 | `script_rpy_L024896_1_357c86cf` | `script_rpy_L054354_1_ba36bd8a` | Wh-Where were you? What's with those clothes? Are you the same person who disappeared with Sai? | **不一致**<br>原句：你、你刚才在哪儿？这身衣服是怎么回事？{w} 你就是和 Sai 一起消失的那个人吗？<br>引用：你、你刚才在哪儿？这身衣服是怎么回事？{w}你还是和 Sai 一起消失的那个人吗？ |
| 5 | 逐字重复 | `script_rpy_L024903_1_6395f553` | `script_rpy_L054357_1_8c5b4b80` | I-I'm sorry... I'm very confused too. ...I-I guess so, though. | **不一致**<br>原句：对、对不起……我自己也乱得很。……不过，大、大概是的。<br>引用：对、对不起……我自己也乱得很。……不、不过，大概算是吧。 |
| 6 | 逐字重复 | `script_rpy_L024904_1_b12db20d` | `script_rpy_L054358_1_c4c38ff3` | You guess so? What do you mean? You remember everything, right? | **不一致**<br>原句：你是猜的？{w} 你什么意思？你什么都记得吧？<br>引用：大概？{w}你这话什么意思？你什么都记得，对吧？ |
| 7 | 逐字重复 | `script_rpy_L024928_1_71396d07` | `script_rpy_L054381_1_9d8dfef8` | I'm glad to see you two are safe. I was a bit worried... Wh-What's with those clothes? You weren't wearing them earlier, were you...? | **不一致**<br>原句：看到你们俩平安无事，我就放心了。我原本还有点担心……{w} 这、这身衣服是怎么回事？你们先前穿的不是这个吧……？<br>引用：看到你们俩平安无事，我就放心了。我刚才还有点担心……{w}你、你这身衣服是怎么回事？刚才你穿的可不是这个吧……？ |
| 8 | 逐字重复 | `script_rpy_L024930_1_09df6ef6` | `script_rpy_L054386_1_d6755d54` | Who the hell are you? Or even you... How can you two exist!? | **不一致**<br>原句：你到底是什么人？还有你……你们俩怎么可能存在！？<br>引用：你到底是谁？还有你……你们两个怎么可能同时存在！？ |
| 9 | 逐字重复 | `script_rpy_L024942_1_fd2b8788` | `script_rpy_L054393_1_fb1052a5` | Where were you? How did you just appear out of nowhere!? | **不一致**<br>原句：你刚才在哪儿？怎么会凭空冒出来！？<br>引用：你刚才在哪儿？怎么会突然就冒出来了！？ |
| 10 | 逐字重复 | `script_rpy_L024949_1_e028d7ce` | `script_rpy_L054399_1_7576d464` | What do you not understand? Did you just pop into existence at some point? | **不一致**<br>原句：你哪里不明白了？你是从某个时候凭空冒出来的吗？<br>引用：你有什么不明白的？难不成你是凭空冒出来的？ |
| 11 | 逐字重复 | `script_rpy_L024954_1_bc947d3c` | `script_rpy_L054404_1_8a7f499f` | No... Why do you think that? | **不一致**<br>原句：不……你为什么这么想？<br>引用：不是……你怎么会这么想？ |
| 12 | 逐字重复 | `script_rpy_L024960_1_f6677e8c` | `script_rpy_L054405_1_1c75d651` | Have you looked at that room? Your body is there. | **不一致**<br>原句：你看过那个房间吗？你的身体就在那儿。<br>引用：你看过那个房间吗？你的身体就躺在那儿。 |
| 13 | 逐字重复 | `script_rpy_L024966_1_68d3eec8` | `script_rpy_L054413_1_4fe999f0` | What...? That one? It... can't be. | **不一致**<br>原句：什么……？那个房间？不……不可能。<br>引用：什么……？那个？不、不可能。 |
| 14 | 逐字重复 | `script_rpy_L024972_1_e4620bf0` | `script_rpy_L054419_1_69c38e5a` | I knew you were lying. I-I can't be here, of course not... | **不一致**<br>原句：我就知道你在说谎。我、我不能待在这里，当然不能……<br>引用：我就知道你在骗我。我、我不可能在这里，当然不可能…… |
| 15 | 逐字重复 | `script_rpy_L024982_1_9f199cab` | `script_rpy_L054420_1_22958f1d` | ...Shiroya, what the hell is happening? Answer my other questions. How can you exist when it shouldn't be possible? Did the same thing ha… | **不一致**<br>原句：……Shiroya，到底出什么事了？先回答我别的问题。按理说根本不可能的事，你怎么会站在这里？Erina 也遇上了一样的事吗？<br>引用：……Shiroya，到底发生了什么？先回答我其他几个问题。你本不该存在，怎么还能站在这里？Erina 也是同样的情况吗？ |
| 16 | 逐字重复 | `script_rpy_L024987_1_3359c720` | `script_rpy_L054421_1_e9271e0d` | To Erina? She should be dead, right? | **不一致**<br>原句：Erina 吗？她应该已经死了，不是吗？<br>引用：Erina 也是？她应该已经死了吧？ |
| 17 | 逐字重复 （另见 第二章 L11926） | `script_rpy_L025003_1_5c0eb6ca` | `script_rpy_L054426_1_3159a855` | About Erina, I think what happened isn't what you think. | **不一致**<br>原句：关于 Erina，我想事情并不像你想的那样。<br>引用：关于 Erina，我想事情不是你想的那样。 |
| 18 | 逐字重复 | `script_rpy_L025004_1_5c51ace5` | `script_rpy_L054427_1_79ad4ceb` | That's probably right. I can't think of anything anymore. | **不一致**<br>原句：大概吧。我已经什么都想不出来了。<br>引用：大概吧。我已经什么都想不明白了。 |
| 19 | 逐字重复 | `script_rpy_L025010_1_d0d64c2b` | `script_rpy_L054428_1_69dab793` | ...Under those stained clothes, there's no wound, right? | **不一致**<br>原句：……那身沾了血的衣服底下，并没有伤口，对吧？<br>引用：……那身染血的衣服底下，并没有伤口吧？ |
| 20 | 逐字重复 | `script_rpy_L025016_1_bbaab0f0` | `script_rpy_L054442_1_90a71462` | There never was one. The body you think disappeared is her. | **不一致**<br>原句：从来就没有什么伤口。你以为消失的那具尸体，就是她。<br>引用：本来就没有。你以为消失不见的那具尸体，就是她本人。 |
| 21 | 逐字重复 | `script_rpy_L025017_1_a4278702` | `script_rpy_L054443_1_e81a5d33` | Do you mean that she never died? | 一致 |
| 22 | 逐字重复 | `script_rpy_L025022_1_3bf91c32` | `script_rpy_L054449_1_d66172db` | A-Are you serious...? Were you playing dead, then? Or just unconscious? It doesn't look like you feel very well. | **不一致**<br>原句：你、你说真的……？{w}那你是在装死？还是只是昏过去了？你的脸色看起来很差。<br>引用：你、你说真的……？{w}那你是在装死？还是只是昏了过去？你的脸色看起来可不太好。 |
| 23 | 逐字重复 （另见 第二章 L11929） | `script_rpy_L025027_1_b2b0aa7d` | `script_rpy_L054454_1_0fb5f433` | I'm not sure... I remember I was drawn to this room, and then I think I blacked out. | **不一致**<br>原句：我也说不清……我记得自己像是被什么引到了这个房间，然后就没了意识。<br>引用：我不太清楚……我记得自己像是被什么引到了这个房间，然后就昏过去了。 |
| 24 | 逐字重复 | `script_rpy_L025033_1_f7699a39` | `script_rpy_L054464_1_9732b7bc` | N-No... Something stronger, but I'm not sure what, exactly. I don't know whose blood this is, but since I woke up, I've felt... groggy an… | **不一致**<br>原句：不、不是……是更强烈的东西，可我也说不准究竟是什么。我不知道这是谁的血，但醒来之后，我一直觉得……昏昏沉沉，浑身发麻。<br>引用：不、不是……是更强烈的东西，但我说不准到底是什么。这些血是谁的，我也不知道。只是醒过来之后，我一直觉得……昏昏沉沉，浑身发麻。 |
| 25 | 逐字重复 | `script_rpy_L025038_1_e41d5e36` | `script_rpy_L054475_1_354a4d20` | Shiroya, do you remember finding her body as well? And you realized what really happened? ...You still haven't explained what you're doin… | **不一致**<br>原句：Shiroya，你也记得自己发现了她的尸体吗？然后就想通了真相？……你还没解释自己为什么会在这里。你就是那个和 Sai 一起从活动室消失的 Shiroya 吗？<br>引用：Shiroya，你还记得发现她尸体的事吗？还有，你当时就明白到底发生了什么？……你还没解释过你为什么会在这里。你就是那个和 Sai 一起从活动室消失的 Shi… |
| 26 | 逐字重复 | `script_rpy_L040774_1_1fa839fd` | `script_rpy_L054476_1_47afd28f` | ...I wish I could explain everything to you, but I still don't really know what happened. But, yes. I'm really glad to see you again. | **不一致**<br>原句：……我也希望能把一切都解释给你听，可我自己也还不太清楚发生了什么。{w}不过，没错。能再见到你，我真的很高兴。<br>引用：……我也想从头到尾跟你解释清楚，可我自己也还没弄明白究竟发生了什么。{w} 不过，是的。能再见到你，我真的很高兴。 |
| 27 | 逐字重复 （另见 第二章 L11934） | `script_rpy_L025046_1_660e91df` | `script_rpy_L054482_1_295bbe4a` | Wh-What's with those clothes, then? Why is the cross not on them? Why did you ignore me when we saw each other in the event room and when… | **不一致**<br>原句：那、那你这身衣服又是怎么回事？为什么上面没有十字？在活动室碰面的时候，还有我拼命喊你名字的时候，你为什么都不理我？<br>引用：那、那你这身衣服又是怎么回事？为什么上面没有十字？我们在活动室碰面的时候，还有我一直喊你名字的时候，你为什么都不理我？ |
| 28 | 逐字重复 （另见 第二章 L11936） | `script_rpy_L025056_1_6c2f8f5a` | `script_rpy_L054488_1_54e2d20c` | Hey... I'm still confused, but I have a question. | **不一致**<br>原句：那个……我还是没搞明白，不过我有个问题。<br>引用：那个……我还是没弄明白，不过我有个问题。 |
| 29 | 逐字重复 | `script_rpy_L025062_1_aa48ea5b` | `script_rpy_L054494_1_13174aaf` | The Sekimeiya... does it really make you travel through time? How does it work? | **不一致**<br>原句：Sekimeiya……它真的能让人穿越时间吗？{w}是怎么做到的？<br>引用：Sekimeiya……真的能让人穿越时间吗？{w} 它是怎么运作的？ |
| 30 | 逐字重复 | `script_rpy_L025070_1_9706fca8` | `script_rpy_L054504_1_f09075a7` | If I understand it... touching it with your skin activates it, right? And you can go far into the past if it's out of the cabinet for a w… | **不一致**<br>原句：如果我没理解错的话……用皮肤碰它就会启动，对吧？而且它离开展示柜越久，就能回到越远的过去。<br>引用：如果我理解得没错……皮肤碰到它就会启动，对吧？而且它离开展示柜一段时间后，就能回到很久以前的过去。 |
| 31 | 逐字重复 | `script_rpy_L025071_1_9adaec93` | `script_rpy_L054509_1_ee8b3839` | That's... what I've been working under, yes. | **不一致**<br>原句：我……一直是这么认为的，没错。<br>引用：我……确实是这么认为的。 |
| 32 | 逐字重复 | `script_rpy_L025081_1_8c3ebedd` | `script_rpy_L054515_1_a6586967` | I was thinking. Why don't I just go back in time to save Isla? | **不一致**<br>原句：我在想，我为什么不干脆回到过去，去救 Isla 呢？<br>引用：我在想……我干脆回到过去，去救 Isla，不就行了？ |
| 33 | 逐字重复 （另见 第二章 L11940） | `script_rpy_L025095_1_b4c346fa` | `script_rpy_L054533_1_cfacebea` | ...A girl? You saw Shiroya? | **不一致**<br>原句：……女孩？你看见 Shiroya 了？<br>引用：……女孩？你看到的是 Shiroya？ |
| 34 | 逐字重复 （另见 第二章 L11941） | `script_rpy_L025100_1_6c809cfb` | `script_rpy_L054538_1_5fe2a648` | Um... I guess it couldn't have been anyone else. ...It must have been Shiroya. | **不一致**<br>原句：嗯……{w}我想那也不可能是别人。{w}……一定是 Shiroya。<br>引用：嗯……{w} 我想除了她也不会是别人。{w} ……一定是 Shiroya。 |
| 35 | 逐字重复 | `script_rpy_L025110_1_e4c64d84` | `script_rpy_L054544_1_ef425d35` | I also saw what happened to Katei... It looked horrible. Did someone do that? | **不一致**<br>原句：我还看见了 Katei 的遭遇……实在惨不忍睹。是有人下的手吗？<br>引用：我还看见发生在 Katei 身上的事……太惨了。是有人干的吗？ |
| 36 | 逐字重复 | `script_rpy_L025111_1_064a18e4` | `script_rpy_L054549_1_3a32aea4` | ...It couldn't have been an accident. But anyway, the Sekimeiya's not in the event room. | **不一致**<br>原句：……那不可能是意外。{w}不过话说回来，Sekimeiya 不在活动室。<br>引用：……那不可能是意外。{w} 总之，Sekimeiya 不在活动室。 |
| 37 | 逐字重复 | `script_rpy_L025113_1_c44e9951` | `script_rpy_L054551_1_14f50fb1` | Are you sure...? Do you know where it could be? I really need to find it. | **不一致**<br>原句：你确定……？{w}你知道它可能在哪儿吗？我真的必须找到它。<br>引用：你确定……？{w} 你知道它可能在哪儿吗？我真的很需要找到它。 |
| 38 | 逐字重复 | `script_rpy_L025114_1_fa83e0cf` | `script_rpy_L054552_1_a73c512d` | No. I suspect Sai or Akaro must've taken it. | **不一致**<br>原句：不知道。我猜是 Sai 或者 Akaro 把它拿走了。<br>引用：不知道。我猜是 Sai 或者 Akaro 拿走了。 |
| 39 | 逐字重复 | `script_rpy_L025121_1_87a05365` | `script_rpy_L054563_1_27a50014` | What? No, I'm not. | **不一致**<br>原句：什么？没有，我没骗你。<br>引用：什么？没有，我没说谎。 |
| 40 | 逐字重复 | `script_rpy_L025127_1_be4a3067` | `script_rpy_L054571_1_b6c3082b` | The way you two reacted. You don't want me to save Isla, do you? | **不一致**<br>原句：看你们俩那反应。你们不想让我去救 Isla，对吧？<br>引用：看你们俩的反应……你们不想让我去救 Isla，对吧？ |
| 41 | 逐字重复 （另见 第二章 L11943） | `script_rpy_L025132_1_f677f706` | `script_rpy_L054572_1_b454e732` | That's not it at all... Remember that Sai and Akaro took the cabinet key. They probably have the Sekimeiya. | **不一致**<br>原句：根本不是这样……你忘了，展示柜的钥匙是 Sai 和 Akaro 拿走的。Sekimeiya 多半在他们手上。<br>引用：不是这么回事……你忘了？展示柜的钥匙被 Sai 和 Akaro 拿走了。Sekimeiya 多半在他们手上。 |
| 42 | 逐字重复 | `script_rpy_L025153_1_e68d4edd` | `script_rpy_L054588_1_ace467f3` | I-I knew it! You were lying... | **不一致**<br>原句：我、我就知道！你在撒谎……<br>引用：我、我就知道！你们在说谎…… |
| 43 | 逐字重复 | `script_rpy_L025159_1_8efccb2f` | `script_rpy_L054590_1_2422d542` | You didn't want me to look at the cabinet! | **不一致**<br>原句：你就是不想让我看那个展示柜！<br>引用：你们就是不想让我看那个展示柜！ |
| 44 | 逐字重复 | `script_rpy_L025211_1_50dc5d96` | `script_rpy_L054630_1_a5243631` | ...What the fuck are you even doing here? Did you succeed with that plan of yours? | **不一致**<br>原句：……你他妈来这儿干什么？你那个计划成了？<br>引用：……你他妈跑来这儿干什么？你那个计划成了？ |
| 45 | 逐字重复 | `script_rpy_L025216_1_9e1edac8` | `script_rpy_L054635_1_96959674` | Oh, not quite, unfortunately. I thought Erina was dead. What's she doing with the Sekimeiya? | **不一致**<br>原句：哦，遗憾，没成。我还以为 Erina 死了。她拿着 Sekimeiya 做什么？<br>引用：哦，不太顺利，很遗憾。我还以为 Erina 死了。她拿着 Sekimeiya 要做什么？ |
| 46 | 逐字重复 | `script_rpy_L025223_1_17b9ce19` | `script_rpy_L054640_1_91b8d52f` | You thought that too? No. I'm going to go to the past to save Isla. | **不一致**<br>原句：你也这么想？不。我要回到过去救 Isla。<br>引用：你也这么想？不对。我要回到过去救 Isla。 |
| 47 | 逐字重复 | `script_rpy_L025228_1_e4874880` | `script_rpy_L054645_1_2de543a8` | Huh. I doubt that. The past can't be changed. | **不一致**<br>原句：哼，我不信。过去是改不了的。<br>引用：是吗。我看未必。过去是改变不了的。 |
| 48 | 逐字重复 | `script_rpy_L025234_1_df02e3a4` | `script_rpy_L054650_1_c5a14aaa` | That's nonsense! I'm going to the past, so I'll prevent Isla from dying. You've used the Sekimeiya before, right? How long do I need to w… | **不一致**<br>原句：胡说！我回到过去，就能阻止 Isla 死去。你以前用过 Sekimeiya 吧？要等多久，才能回到好几个小时之前？<br>引用：荒唐！我要回到过去，阻止 Isla 死掉。你以前用过 Sekimeiya 吧？我得等多久，才能回到足够早的几个小时前？ |
| 49 | 逐字重复 | `script_rpy_L025239_1_db658615` | `script_rpy_L054655_1_d0f447ce` | Um... It should be about fifteen minutes, but I still find it unlikely you'll change anything. | **不一致**<br>原句：嗯……大概十五分钟吧。不过我还是觉得，你什么也改变不了。<br>引用：嗯……大概要十五分钟吧。不过我还是觉得，你改变不了什么。 |
| 50 | 逐字重复 | `script_rpy_L025246_1_3313fbe8` | `script_rpy_L054662_1_9f6515a9` | Sai... where the fuck did you go? Were you in the attic? Do you know where Shiroya went? I saw her disappear with you. | **不一致**<br>原句：Sai……你他妈到底去哪儿了？你在阁楼里？{w}你知道 Shiroya 去哪儿了吗？我看见她和你一起消失了。<br>引用：Sai……你他妈到底跑哪儿去了？刚才在阁楼里？{w}你知道 Shiroya 去哪儿了吗？我亲眼看见她跟你一起消失的。 |
| 51 | 逐字重复 | `script_rpy_L025251_1_e4184dce` | `script_rpy_L054667_1_740210d0` | Isn't she next to you? What's with those clothes, anyway? Aren't they from there? | **不一致**<br>原句：她不是就在你旁边吗？话说那身衣服是怎么回事？不是那儿来的吗？<br>引用：她不是就在你旁边吗？话说你这身衣服是怎么回事？不是那边的吗？ |
| 52 | 逐字重复 | `script_rpy_L025262_1_fda4c940` | `script_rpy_L054673_1_ee4f4b78` | I see, they're definitely an improvement for you. And just ignore me, Atsuki. I was busy sorting something out. | **不一致**<br>原句：原来如此，穿在你身上确实顺眼多了。{w}还有，别管我，Atsuki。我刚才正忙着理清一些事。<br>引用：原来如此，穿在你身上确实算进步了。{w}别管我，Atsuki，我刚才正忙着处理点事情。 |
| 53 | 逐字重复 | `script_rpy_L025274_1_30724b38` | `script_rpy_L054681_1_25b9fdcb` | Oh, right, I'd forgotten about this too. | **不一致**<br>原句：啊，对了，这个我也忘了。<br>引用：哦，对，这事我也忘了。 |
| 54 | 逐字重复 （另见 第五章 L20412） | `script_rpy_L025280_1_a372a125` | `script_rpy_L054690_1_8da26bba` | I found this just now. I tried to read it, but my head hurt a lot. Do you know what it is? | **不一致**<br>原句：这是我刚捡到的。我想读，可头疼得厉害。你知道这是什么吗？<br>引用：这个是我刚才找到的。我试着读了读，可头特别疼。你知道这是什么吗？ |
| 55 | 逐字重复 | `script_rpy_L025300_1_535b05f9` | `script_rpy_L054708_1_14a602b8` | Don't mind me, like you said. | **不一致**<br>原句：就像你说的，别管我。<br>引用：你不是说了吗，别管我。 |
| 56 | 逐字重复 | `script_rpy_L025305_1_09b8066d` | `script_rpy_L054713_1_b2f0da2b` | You look pretty nervous. I saw something written there. You were pretty in control of things when you pulled off that trick with the key … | **不一致**<br>原句：你看起来挺紧张的。我可看见上面写着字。{w}刚才你耍那把钥匙的把戏时，一副胸有成竹的样子，怎么现在倒把你急成这样？你就那么想藏起来？<br>引用：你看着挺紧张的。那上面写了字，我看见了。{w}刚才拿钥匙耍那一手的时候，你可是一副游刃有余的样子，怎么现在这点事就让你慌了？就这么想把它藏起来？ |
| 57 | 逐字重复 | `script_rpy_L025307_1_a7c959c6` | `script_rpy_L054718_1_dfa17d95` | ...It's just a personal paper. It has nothing to do with you or the Sekimeiya. | **不一致**<br>原句：……{w}只是一张私人纸条，和你、和 Sekimeiya 都没有关系。<br>引用：……{w}只是一张私人的纸，跟你和 Sekimeiya 都没有关系。 |
| 58 | 逐字重复 （另见 第二章 L11963） | `script_rpy_L025332_1_5b945732` | `script_rpy_L054737_1_6b57c03c` | So, did any of you see Miiya...? | **不一致**<br>原句：那么，你们有谁看见 Miiya 了吗……？<br>引用：那么，你们有谁见过 Miiya……？ |
| 59 | 逐字重复 （另见 第二章 L11965） | `script_rpy_L025351_1_a432e4d0` | `script_rpy_L054754_1_88011743` | You don't know her, right? I... I knew I wasn't going insane. | **不一致**<br>原句：你们不认识她吧？我……我就知道我没疯。<br>引用：你不认识她，对吧？我……我就知道，我没有发疯。 |
| 60 | 逐字重复 （另见 第二章 L11966） | `script_rpy_L025357_1_35815cf0` | `script_rpy_L054755_1_005435ff` | H-How do you know that name? | **不一致**<br>原句：你、你怎么会知道那个名字？<br>引用：你、你怎么会知道这个名字？ |
| 61 | 逐字重复 （另见 第二章 L11968） | `script_rpy_L025362_1_5320bc81` | `script_rpy_L054761_1_9e85c85c` | She's the person I was with earlier, before I saw you two... It just came back to me. I don't know where she went, though. | **不一致**<br>原句：她就是刚才和我在一起的人，在我看见你们俩之前……我刚刚才想起来。不过我不知道她去了哪里。<br>引用：在遇到你们两个之前，我就是和她待在一起……我刚刚才想起来。不过她去了哪里，我也不知道。 |
| 62 | 稍作改写 | `script_rpy_L025363_1_9483b947` | `script_rpy_L054762_1_8ab36947` | 原句：What... the fuck is going on?<br>引用：What...? What just happened? | 英文本不完全相同，中文不必逐字一致 |
| 63 | 逐字重复 | `script_rpy_L025368_1_8049ec86` | `script_rpy_L054771_1_7b5a55a4` | What's with that reaction? Don't you see she's just delirious? She didn't die, but I have a pretty good idea of what happened to her. Say… | **不一致**<br>原句：你这是什么反应？看不出来她只是在说胡话吗？{w}她没死，不过她身上发生了什么，我大致猜得到。话说回来，你是产生了幻觉，看见了某个人吗？<br>引用：你这是什么反应？没看出来她只是在说胡话吗？{w}她没死，不过她身上出了什么事，我大概猜得到。我说，你是不是幻视出谁来了？ |
| 64 | 逐字重复 | `script_rpy_L025369_1_f31382b3` | `script_rpy_L054776_1_c4ff7712` | That's not it. That's not just some name she made up. | **不一致**<br>原句：不是这样。那不是什么她随口编出来的名字。<br>引用：不是这样。那名字不是她凭空编出来的。 |
| 65 | 逐字重复 | `script_rpy_L025374_1_79aefbdd` | `script_rpy_L054781_1_cb36c2d1` | Do you know this person, then? | **不一致**<br>原句：那你们认识这个人？<br>引用：这么说，你们认识这个人？ |
| 66 | 逐字重复 （另见 第二章 L11973） | `script_rpy_L025380_1_2f46c5c8` | `script_rpy_L054782_1_6895cfe6` | ...We do, but Erina couldn't have seen her. She couldn't be here. | **不一致**<br>原句：……认识。可 Erina 不可能见到她。她不可能在这里。<br>引用：……认识。可 Erina 不可能见过她。她不可能在这里。 |
| 67 | 逐字重复 | `script_rpy_L025381_1_3e1463fd` | `script_rpy_L054783_1_6ed1dc8d` | Are you sure? She could've entered through the storeroom. She could've even traveled from the future since the Sekimeiya's bound to be ex… | **不一致**<br>原句：你确定？她也许是从储藏室进来的。甚至可能是从未来穿越过来的——Sekimeiya 迟早会暴露在外界面前。<br>引用：你确定？她完全可能是从储藏室进来的。甚至可能是从未来穿越过来的——毕竟 Sekimeiya 迟早会暴露给外界。 |
| 68 | 逐字重复 （另见 第二章 L11975） | `script_rpy_L025382_1_02e8d0ae` | `script_rpy_L054788_1_7f4c2c19` | That's not what she means... She's not anywhere right now. | 一致 |
| 69 | 逐字重复 | `script_rpy_L025387_1_47101ec7` | `script_rpy_L054793_1_afb9ccea` | Oh? Is she dead? ...Wait, Miiya, you said...? | **不一致**<br>原句：哦？她死了？{w}……等等，你刚才说 Miiya……？<br>引用：哦？她死了？{w}……等等，你刚才说的是 Miiya……？ |
| 70 | 逐字重复 | `script_rpy_L025394_1_539f6a30` | `script_rpy_L054801_1_5c691adc` | ...No. She's with us. She has red hair, right? | **不一致**<br>原句：……不。她跟我们在一起。她是红头发，对吧？<br>引用：……不。她跟我们在一起。她是一头红发，对吧？ |
| 71 | 逐字重复 | `script_rpy_L025401_1_b7839ed9` | `script_rpy_L054802_1_97f1b51c` | ...Did you actually see her? What did she say? | 一致 |
| 72 | 逐字重复 | `script_rpy_L025411_1_1420f513` | `script_rpy_L054810_1_66dae2bd` | I don't know how to interpret this. Did you all agree to make up this story for when I appeared? | **不一致**<br>原句：我真不知道该怎么理解。你们是不是早就串通好，等我一出现就编出这套说辞？<br>引用：我真不知道怎么理解才好。你们该不会是商量好了，就等我出现的时候编出这套说辞吧？ |
| 73 | 逐字重复 | `script_rpy_L025417_1_634d5eb5` | `script_rpy_L054820_1_c0cbb75c` | Well, I'm trying to figure things out myself and I thought I was close to understanding quite a bit, but now there's a bunch of shit I do… | **不一致**<br>原句：我自己也在琢磨这一切，本来以为已经快要弄明白不少事了，结果现在冒出一堆我搞不懂的鬼东西，感觉可不怎么好。<br>引用：我不过是想自己把事情理清楚。本以为已经快弄明白不少了，结果现在又冒出一堆我搞不懂的破事，这滋味可不太好受。 |
| 74 | 逐字重复 | `script_rpy_L025423_1_de50ca98` | `script_rpy_L054825_1_34d24a54` | You did mean she died, right? Is saving her with the Sekimeiya not an option? | **不一致**<br>原句：你刚才确实是说她死了吧？难道不能用 Sekimeiya 救她？<br>引用：你刚才的意思是她死了，对吧？用 Sekimeiya 救她难道不行吗？ |
| 75 | 逐字重复 | `script_rpy_L025429_1_63109d04` | `script_rpy_L054830_1_87b1a028` | Sai, shut the fuck up. If it was, I promise you that we would've done it. | **不一致**<br>原句：Sai，你他妈给我闭嘴。要是能救，我保证我们早就做了。<br>引用：Sai，你他妈给我闭嘴。要是有办法，我向你保证，我们早就做了。 |
| 76 | 逐字重复 | `script_rpy_L025443_1_ff427e53` | `script_rpy_L054848_1_5f663c21` | It's probably been close to fifteen minutes already, right? | **不一致**<br>原句：差不多快十五分钟了吧？<br>引用：差不多该到十五分钟了吧？ |
| 77 | 逐字重复 （另见 第二章 L11986） | `script_rpy_L025462_1_b353592a` | `script_rpy_L054858_1_d6268f9d` | Are you sure I'll go far enough back? | **不一致**<br>原句：你确定我能回到足够早的时间？<br>引用：你确定我能回到足够早的时间点吗？ |
| 78 | 逐字重复 | `script_rpy_L025468_1_811482e1` | `script_rpy_L054859_1_f917496d` | She died at around , right? It should be enough, yes. | **不一致**<br>原句：她是在 {time=14} 前后死的吧？那应该够了。<br>引用：她是在{time=14}前后死的，对吧？那应该够了。 |
| 79 | 逐字重复 | `script_rpy_L025475_1_f53d5c47` | `script_rpy_L054864_1_2af3c2dd` | ...Okay. I'm going, then. Are all of you coming with me? | **不一致**<br>原句：……好。那我走了。你们都会跟我一起来吗？<br>引用：……好。那我走了。你们都要一起来吗？ |
| 80 | 逐字重复 | `script_rpy_L025476_1_0ef52811` | `script_rpy_L054865_1_5c6d131e` | Don't worry, we're far enough from you. | 一致 |
| 81 | 逐字重复 | `script_rpy_L025485_1_7d1bd6d8` | `script_rpy_L054872_1_7af3cec6` | I understand. Well... goodbye for now. | **不一致**<br>原句：我明白。嗯……暂时再见了。<br>引用：我明白了。那么……先再见了。 |
| 82 | 逐字重复 | `script_rpy_L025533_1_8ca5ae42` | `script_rpy_L054907_1_39a685ff` | Why didn't it work!? Did Sai disappear? Was everything that he said a lie...? | **不一致**<br>原句：为什么没有生效！？Sai 消失了吗？{w} 难道他说的一切都是谎话……？<br>引用：为什么没有用！？Sai消失了？{w} 他说的话，难道全是谎话……？ |
| 83 | 逐字重复 | `script_rpy_L025550_1_433c10da` | `script_rpy_L054913_1_1472437c` | Admit it... Did you ever want me to save Isla? Were you... Were you involved in the first place!? | **不一致**<br>原句：你就承认吧……你到底想没想过要救 Isla？你……你从一开始就掺和进来了吧！？<br>引用：承认吧……你到底有没有想过让我救Isla？你……你难道从一开始就掺和在里面！？ |
| 84 | 逐字重复 （另见 第二章 L11997） | `script_rpy_L025556_1_87242e66` | `script_rpy_L054914_1_7643b33b` | You're wrong. We don't know how the Sekimeiya works, but this shouldn't have happened... | **不一致**<br>原句：你错了。我们确实不知道 Sekimeiya 的原理，但这种事本不该发生……<br>引用：你错了。Sekimeiya的运作方式我们也不清楚，但这种事本来不该发生…… |
| 85 | 逐字重复 | `script_rpy_L040890_1_0f462e1e` | `script_rpy_L054921_1_6580bb23` | ...Wait! Where did it go!? It's not here! | **不一致**<br>原句：……等等！它去哪了！？{w} 不在这里！<br>引用：……等等！它去哪儿了！？{w} 不在这儿了！ |
| 86 | 逐字重复 （另见 第二章 L12006） | `script_rpy_L025607_1_f72a2aa6` | `script_rpy_L054934_1_465c38fa` | Atsuki, tell me... What do I need to do to travel through time? | 一致 |
| 87 | 逐字重复 （另见 第二章 L12007） | `script_rpy_L025608_1_ed69d2af` | `script_rpy_L054939_1_16fe3805` | Exactly what Sai and I told you. I don't know why it didn't work just now. | **不一致**<br>原句：就像我和 Sai 告诉你的那样。刚才为什么没生效，我也不知道。<br>引用：就是我和Sai对你说的那些。刚才为什么没成功，我也不知道。 |
| 88 | 逐字重复 | `script_rpy_L025641_1_1c820e61` | `script_rpy_L054971_1_0bfdd561` | Can I... not save Isla? Why did it not work...? Oh, of course. What was I even thinking? Traveling to the past isn't possible. You lied a… | **不一致**<br>原句：我……救不了 Isla 吗？为什么没有生效……？{w} 啊，当然了。{w} 我到底在想什么？回到过去根本不可能。{w} 你从一开始就在骗我，对不对？所以才会失…<br>引用：我……终究救不了Isla吗？为什么会没有用……？{w} 啊，当然了。{w} 我在想什么啊。回到过去根本不可能。{w} 你从一开始就在骗我，对吧？所以才会没用—… |
| 89 | 逐字重复 | `script_rpy_L025643_1_5f112a1b` | `script_rpy_L054976_1_28c28160` | Just wait here. I'll be back in a second. | **不一致**<br>原句：在这里等我，我马上回来。<br>引用：在这里等着。我马上回来。 |
| 90 | 逐字重复 | `script_rpy_L025687_1_962a2550` | `script_rpy_L055000_1_ff01febe` | Wh-What did you want to do? | **不一致**<br>原句：你、你想做什么？<br>引用：你、你到底想做什么？ |
| 91 | 逐字重复 | `script_rpy_L025688_1_aebb01a3` | `script_rpy_L055005_1_8adcb2c6` | Oh, I'm just wondering about Sai's whereabouts because an extra version of him has existed somewhere in the past. | **不一致**<br>原句：哦，我只是在想 Sai 的下落。毕竟在过去某个时刻，还存在着另一个多出来的他。<br>引用：哦，我只是在想Sai去了哪儿。毕竟在过去的某处，曾多出一个他。 |
| 92 | 逐字重复 | `script_rpy_L025693_1_b2f1364d` | `script_rpy_L055010_1_c0d655f7` | Did we never see him in so many hours? | **不一致**<br>原句：这么多小时里，我们一次都没见到他吗？<br>引用：这么多个小时里，我们一次都没见过他吗？ |
| 93 | 逐字重复 | `script_rpy_L025697_1_60d7516a` | `script_rpy_L055016_1_d33eb868` | ...I'm not sure, but he has to be somewhere. | **不一致**<br>原句：……我不确定，但他总该在某个地方。<br>引用：……不好说，但他总该在某个地方。 |
| 94 | 逐字重复 | `script_rpy_L025710_1_0ee35796` | `script_rpy_L055028_1_be1827b3` | There you are. What were you doing? | **不一致**<br>原句：你在这儿啊。刚才都干什么去了？<br>引用：你在这儿啊。刚才在做什么？ |
| 95 | 逐字重复 | `script_rpy_L025722_1_2e890c56` | `script_rpy_L055038_1_50534e1a` | ...! Wh-Who the fuck are you? How are you here? | 一致 |
| 96 | 逐字重复 | `script_rpy_L025733_1_e04db4af` | `script_rpy_L055049_1_b0777aad` | Whoa! What's this girl doing here!? | **不一致**<br>原句：哇！这女孩怎么会在这里！？<br>引用：哇啊！这女孩怎么跑这儿来了！？ |
| 97 | 逐字重复 | `script_rpy_L025739_1_3db3b8aa` | `script_rpy_L055060_1_1af500bc` | Atsuki! Now you have to answer! Who is she? | **不一致**<br>原句：Atsuki！这下你总该回答了吧！她是谁？<br>引用：Atsuki！现在你总该回答了吧！她是谁？ |
| 98 | 逐字重复 | `script_rpy_L025745_1_5bcefb0f` | `script_rpy_L055061_1_e7a969a1` | ...Are you actually acting as if you don't recognize me? | **不一致**<br>原句：……你们是真打算装作不认识我？<br>引用：……你们真打算装作不认识我？ |
| 99 | 逐字重复 | `script_rpy_L025747_1_b7fa8565` | `script_rpy_L055062_1_c149a6da` | Of course we don't! | **不一致**<br>原句：我们当然不认识！<br>引用：当然不认识！ |
| 100 | 逐字重复 | `script_rpy_L025752_1_e5bdf7f6` | `script_rpy_L055067_1_76f18158` | Well... No. Of course we do. Aren't you... dead? | **不一致**<br>原句：呃……不认识。{w}不对，当然认识。{w}你不是……死了吗？<br>引用：那个……不。{w}当然认识。{w}你不是……死了吗？ |
| 101 | 逐字重复 | `script_rpy_L025761_1_d508a157` | `script_rpy_L055069_1_7795bcbf` | M-Me...? Why would I be dead? | **不一致**<br>原句：我……？我怎么会死？<br>引用：我、我……？我为什么会死？ |
| 102 | 逐字重复 （另见 第五章 L21063） | `script_rpy_L025762_1_76bc70e6` | `script_rpy_L055070_1_077c6d1a` | And you too, Erina! I thought you'd died! | 一致 |
| 103 | 逐字重复 | `script_rpy_L025770_1_f53cf48d` | `script_rpy_L055075_1_fc388e88` | Wh...? Isn't that what you said earlier? | 一致 |
| 104 | 逐字重复 | `script_rpy_L025771_1_a63f8920` | `script_rpy_L055076_1_e5caea8d` | Earlier? What the hell are you talking about? | **不一致**<br>原句：刚才？你在说什么鬼话？<br>引用：刚才？你他妈在说什么？ |
| 105 | 逐字重复 | `script_rpy_L025789_1_37c33911` | `script_rpy_L055093_1_c18deaff` | Why? Did you time travel? | **不一致**<br>原句：怎么？你时间穿越了？<br>引用：为什么？你时间穿越了？ |
| 106 | 逐字重复 | `script_rpy_L025795_1_f0272265` | `script_rpy_L055103_1_63cbd567` | He's right, though. Are you a future version of Erina or something? | **不一致**<br>原句：不过他说得对。你该不会是未来的 Erina 什么的吧？<br>引用：不过他说得对。你是未来版的 Erina 还是什么？ |
| 107 | 逐字重复 | `script_rpy_L025797_1_94c8572b` | `script_rpy_L055105_1_f7e6ee47` | Well, you're not dead after all, but we felt your pulse... In any case, I figured you would've come from the future. What even happened t… | **不一致**<br>原句：你毕竟没死，可我们当时分明摸过你的脉搏……总之，我原以为你是从未来过来的。你到底出了什么事？<br>引用：这个嘛，你毕竟没死，可我们明明探过你的脉搏……不管怎样，我还以为你是从未来来的。你到底出了什么事？ |
| 108 | 逐字重复 | `script_rpy_L025803_1_10338270` | `script_rpy_L055110_1_36c76479` | Um... I can't remember much. I think someone hit my head, and I fell unconscious. I don't know what happened before that. | **不一致**<br>原句：那个……我记不太清了。好像有人打了我头一下，我就昏了过去。在那之前发生了什么，我也不清楚。<br>引用：嗯……我记不太清了。好像有人打了我的头，我就昏过去了。在那之前发生了什么，我也不知道。 |
| 109 | 逐字重复 | `script_rpy_L025808_1_33d3ba7c` | `script_rpy_L055115_1_6738cebb` | Yeah, that's about what we knew too. Sorry that we can't be of more use. | **不一致**<br>原句：嗯，我们知道的也就这些。抱歉，帮不上更多忙。<br>引用：是啊，我们知道的也差不多。抱歉，帮不上更多忙。 |
| 110 | 逐字重复 | `script_rpy_L025814_1_377f6a96` | `script_rpy_L055121_1_8e4d8836` | I don't get it either, but I'm glad you're safe. This means you're not guaranteed to end up dead, but you... What even is your name? How … | **不一致**<br>原句：我也搞不懂，不过你平安就好。这说明你未必一定会死，可你……你到底叫什么名字？又是怎么到这儿来的？<br>引用：我也不明白，不过你没事就好。也就是说，你不见得会死，可你……你到底叫什么名字？又是怎么来到这里的？ |
| 111 | 逐字重复 | `script_rpy_L025821_1_4654221e` | `script_rpy_L055122_1_22ac9af7` | ...I've been here since the start. | 一致 |
| 112 | 逐字重复 | `script_rpy_L025832_1_738bc381` | `script_rpy_L055133_1_b00f57f2` | Hold on, though... Your name... I think I might actually remember that. Shi... roya, was it? My memories are a little foggy. | **不一致**<br>原句：不过，等等……你的名字……我好像还真有印象。{w}Shi……roya，对吧？我的记忆有点模糊。<br>引用：不过等等……你的名字……我好像真有点印象。{w}Shi……roya，对吧？我的记忆有点模糊。 |
| 113 | 逐字重复 | `script_rpy_L025843_1_1e8013af` | `script_rpy_L055139_1_b07de5c3` | I thought so. Like I said... I thought you'd died. | **不一致**<br>原句：果然。就像我说的……我以为你已经死了。<br>引用：我就觉得是这样。就像我刚才说的……我还以为你死了。 |
| 114 | 逐字重复 | `script_rpy_L025849_1_9cfa99f7` | `script_rpy_L055140_1_2715c332` | As you can see, I'm alive. | 一致 |
| 115 | 逐字重复 | `script_rpy_L025854_1_2f6c7676` | `script_rpy_L055141_1_ec7fa0f8` | Do you have a twin, by any chance? | **不一致**<br>原句：你该不会有个双胞胎姐妹吧？<br>引用：你该不会有个双胞胎吧？ |
| 116 | 逐字重复 | `script_rpy_L025860_1_ce55c0eb` | `script_rpy_L055147_1_6ed56761` | But, then... It doesn't make any sense. I'm still really confused... | **不一致**<br>原句：可是，那……这可就说不通了。我还是想不明白……<br>引用：可是，那……这说不通啊。我还是完全搞不懂…… |
| 117 | 逐字重复 | `script_rpy_L025866_1_e497a8ea` | `script_rpy_L055152_1_e034fc16` | What the fuck do you mean you're "confused"!? She just showed up like that! Did you enter through the storeroom? | **不一致**<br>原句：你他妈在说什么「想不明白」！？她就是这么突然冒出来的！你是从储藏室进来的？<br>引用：你他妈说『搞不懂』是什么意思！？她就这样突然冒出来了！你是从储藏室进来的吗？ |
| 118 | 逐字重复 | `script_rpy_L025867_1_f96d4e36` | `script_rpy_L055153_1_c2499f6d` | I've been with you since , Sai. | **不一致**<br>原句：Sai，从 {time=9} 起，我就一直和你们在一起。<br>引用：Sai，我从 {time=9} 起就一直和你们在一起。 |
| 119 | 逐字重复 | `script_rpy_L025872_1_8aafa2da` | `script_rpy_L055158_1_3224520d` | That's a load of crap. Regardless, you'll definitely die. I'm sorry to tell you like that, but you're not making it easy for us. Atsuki, … | **不一致**<br>原句：一派胡言。不管怎样，你肯定会死。很抱歉这样跟你说，可你实在让我们难办。Atsuki，我知道你认识她。<br>引用：一派胡言。不管怎样，你必死无疑。抱歉把话说得这么直接，可你实在让我们难以相信。Atsuki，我知道你认识她。 |
| 120 | 逐字重复 | `script_rpy_L025874_1_9b50bac1` | `script_rpy_L055164_1_cd171302` | ...I do, and she's telling the truth. | **不一致**<br>原句：……{w}我认识，而且她说的是实话。<br>引用：……{w}我认识她，而且她说的是真的。 |
| 121 | 逐字重复 | `script_rpy_L025877_1_5df2c118` | `script_rpy_L055169_1_e7bc3dda` | Are you just fucking with me? What's the point of lying so blatantly? | **不一致**<br>原句：你他妈是在耍我吗？这么明目张胆地撒谎，有什么意义？<br>引用：你他妈是在耍我吗？这么明目张胆地撒谎有什么意义？ |
| 122 | 逐字重复 | `script_rpy_L025884_1_d4466f45` | `script_rpy_L055174_1_aa16a024` | He's... He's telling the truth. Shiroya's been with us the entire time. | **不一致**<br>原句：他……他说的是真的。Shiroya 一直都在我们身边。<br>引用：他……他说的是真的。Shiroya 一直和我们在一起。 |
| 123 | 逐字重复 | `script_rpy_L025889_1_a5c5c30e` | `script_rpy_L055179_1_5e388789` | The entire time? Not even you have been here since ! | **不一致**<br>原句：一直都在？你才不是从 {time=9} 起就在这里的！<br>引用：一直？连你都不是从 {time=9} 起就待在这里的！ |
| 124 | 稍作改写 | `script_rpy_L025900_1_fbbe8302` | `script_rpy_L055189_1_7a26b5ff` | 原句：Well, you get what I mean. You don't remember when you got attacked or where you came fro…<br>引用：Well, you get what I mean. You don't remember when you got attacked or where you came fro… | 英文本不完全相同，中文不必逐字一致 |
| 125 | 逐字重复 | `script_rpy_L025922_1_9324b81f` | `script_rpy_L055215_1_176236f3` | ...Did you notice something? | **不一致**<br>原句：……你发现了什么？<br>引用：……你发现什么了吗？ |
| 126 | 逐字重复 | `script_rpy_L025927_1_4855919e` | `script_rpy_L055224_1_3175aa20` | ...I... need to go somewhere. | 一致 |
| 127 | 逐字重复 | `script_rpy_L025933_1_296653ef` | `script_rpy_L055233_1_68fc2ba8` | I'm sorry, I need to go to the attic. | **不一致**<br>原句：抱歉，我得去阁楼一趟。<br>引用：抱歉，我得去一趟阁楼。 |
| 128 | 逐字重复 | `script_rpy_L025943_1_14caa1a1` | `script_rpy_L055245_1_e6e7bc1a` | Please, don't follow me. | **不一致**<br>原句：请你别跟来。<br>引用：求你，别跟来。 |

## 3.1 角色说「你（们）说过／记得吗」并接着引述旧句

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | L998 逐字；L901 稍作改写 | `script_rpy_L002713_1_27ef1f9e` | `script_rpy_L002920_1_918de076`<br>`script_rpy_L003256_1_7d51225b` | 原句：I guarantee you that everything he's said has been a lie. Don't trust anything he says.<br>引用："I guarantee you that everything he's said has been a lie. Don't trust anything he says." | 英文本不完全相同，中文不必逐字一致 |
| 2 | 断续重述 | `script_rpy_L028515_1_c47501c5` | `script_rpy_L028675_1_74a5af90`<br>`script_rpy_L058606_1_4fe504f3`<br>`script_rpy_L058715_1_c4a2d13b` | 原句：Don't forget what I said... I meant all of it. Now stay here, and don't follow me.<br>引用：Shiroya's words played back in my head. "Don't forget what I said... I meant all of it." | 英文本不完全相同，中文不必逐字一致 |
| 3 | 断续重述 | `script_rpy_L012915_1_c49f234b` | `script_rpy_L018647_1_e54e0444` | 原句：No, I know. What I mean is... what happened to me? Where am I?<br>引用："...What happened to me? Where am I?" I remembered the agonizing way that sounded. | 英文本不完全相同，中文不必逐字一致 |
| 4 | 稍作改写（当场回指） | `script_rpy_L025262_1_fda4c940`<br>`script_rpy_L054673_1_ee4f4b78` | `script_rpy_L054708_1_14a602b8`<br>`script_rpy_L025300_1_535b05f9` | 原句：I see, they're definitely an improvement for you. And just ignore me, Atsuki. I was busy …<br>引用：Don't mind me, like you said. | 英文本不完全相同，中文不必逐字一致 |
| 5 | 改写转述 | `script_rpy_L051077_1_db9d9f43` | `script_rpy_L068472_1_792060a3`<br>`script_rpy_L055336_1_61bd06ff` | 原句：H-Huh? A lot of things! Do you remember everything? Late into the day, we were in the lob…<br>引用：I remember what you told me. You said you traveled to the 30th of November, and that a fe… | 英文本不完全相同，中文不必逐字一致 |
| 6 | 当场回指（跨过一段之后再问） | `script_rpy_L068492_1_0bfb1724`<br>`script_rpy_L055361_1_3698e58d` | `script_rpy_L069080_1_5a8f9f1c` | 原句：Like I said, the recording was real. On the 5th of January, we were in the tower. That's …<br>引用：What? Didn't you say that the recording was real? | 英文本不完全相同，中文不必逐字一致 |

## 3.3 第三章开场＝第一章开场（双视角，不是偷听）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L000102_1_9133929d` | `script_rpy_L043419_1_4b90b640` | ...I think it'll be time soon. | **不一致**<br>原句：……我想，快到时候了。<br>引用：……我想快到时间了。 |
| 2 | 逐字重复 | `script_rpy_L000104_1_0e470075` | `script_rpy_L043424_1_99565c42` | Yeah, probably less than twenty minutes. | **不一致**<br>原句：嗯，大概不到二十分钟。<br>引用：嗯，大概不到二十分钟了。 |
| 3 | 逐字重复 | `script_rpy_L000264_1_c67f9e29` | `script_rpy_L043467_1_924e7a05` | You three are the first group, correct? | **不一致**<br>原句：你们三位就是第一批，对吧？<br>引用：你们三位是第一组，对吗？ |
| 4 | 逐字重复 | `script_rpy_L000269_1_ee650144` | `script_rpy_L043470_1_54e41dc8` | ...All right, then. Please follow me to the event room to be the first to see the Sekimeiya. | **不一致**<br>原句：……好吧。那请随我去活动室，你们会是第一批见到 Sekimeiya 的人。<br>引用：……好。请跟我来活动室，你们将是第一批见到 Sekimeiya 的人。 |
| 5 | 逐字重复 | `script_rpy_L000294_1_c50542f9` | `script_rpy_L043484_1_330c6951` | Are you feeling better? | 一致 |
| 6 | 逐字重复 | `script_rpy_L000299_1_17da12d9` | `script_rpy_L043485_1_56bb7ddf` | Oh... Yeah, I'm fine. Don't worry about it. | **不一致**<br>原句：哦……嗯，我没事。别在意。<br>引用：哦……嗯，我没事。别担心。 |
| 7 | 稍作改写 | `script_rpy_L000306_1_8263260a` | `script_rpy_L043491_1_588d3c09` | ...Do you regret coming? | **不一致**<br>原句：……你后悔来这儿吗？<br>引用：……你后悔来了吗？ |
| 8 | 逐字重复 | `script_rpy_L000312_1_5abc92ce` | `script_rpy_L043501_1_9176f963` | I know how you feel, okay? It's... the same for me. It doesn't help a lot to say it, but I don't want to see you sad. | **不一致**<br>原句：你的心情我明白，好吗？我也……一样。说出来未必有什么用，但我不想看你难过。<br>引用：我明白你的感受，好吗？我也……一样。说出来也起不了多大作用，但我不想看见你难过。 |
| 9 | 逐字重复 | `script_rpy_L000317_1_b0acf6f4` | `script_rpy_L043502_1_bc7cc8dd` | I'm here because I want to be, Atsuki. I'm okay. This is where I need to be right now. Sorry, I must look terrible. | **不一致**<br>原句：Atsuki，我是因为想来才来的。我没事。现在我就该待在这里。抱歉，我这副样子一定很难看。<br>引用：Atsuki，我是因为想来才来的。我没事。现在我就该在这里。抱歉，我这副样子一定很难看。 |
| 10 | 逐字重复 | `script_rpy_L000319_1_87477651` | `script_rpy_L043507_1_a8efc3df` | ...You know this isn't something you need to apologize for. Nothing about this is your fault. | **不一致**<br>原句：……你该知道，这没什么好道歉的。那件事没有一处是你的错。<br>引用：……你知道这不是你该道歉的事。这一切都不是你的错。 |
| 11 | 逐字重复 | `script_rpy_L000324_1_8bc4689e` | `script_rpy_L043508_1_e7685949` | I'm... not so sure. I wish I didn't have to be a drag for you now. | **不一致**<br>原句：我……不太确定。真希望现在不是我拖累你。<br>引用：我……不太确定。真希望现在不用拖累你。 |
| 12 | 逐字重复 | `script_rpy_L000325_1_603ca667` | `script_rpy_L043514_1_a51005a4` | H-Hey, come on. If you want to leave, we still can. Don't feel like you have to push yourself for my sake. | **不一致**<br>原句：喂、喂，别这样。你要是想走，我们现在也能走。别为了我勉强自己。<br>引用：喂、喂，别这样。你想走的话，我们随时可以走。别觉得是为了我才硬撑着。 |
| 13 | 逐字重复 | `script_rpy_L000331_1_8887433b` | `script_rpy_L043515_1_e2504e26` | 原句：It's all right. Thank you. Let's continue, though. I was the one who wanted to do this.<br>引用：It's all right. Thank you. Let's continue, though. I was the one who wanted to come. | 英文本不完全相同，中文不必逐字一致 |
| 14 | 逐字重复 | `script_rpy_L000548_1_4778d7d4` | `script_rpy_L043554_1_8a317d84` | Are y—*cough* *cough* | **不一致**<br>原句：你没——*咳* *咳*<br>引用：你——*咳* *咳* |
| 15 | 逐字重复 | `script_rpy_L000550_1_ffcdbdeb` | `script_rpy_L043557_1_fe294155` | Yes... I think so. *cough* | **不一致**<br>原句：嗯……我想是吧。*咳*<br>引用：是……应该是。*咳* |

## 3.4 阁楼重逢双视角（第一章 L8140 一带 ⇔ 第三章 L13256 一带）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 稍作改写（合并） | `script_rpy_L027018_1_7882b117`<br>`script_rpy_L027020_1_ab1a0f62` | `script_rpy_L044904_1_63595643` | 原句：I... see.<br>引用：I... see. We didn't check Erina's pulse, remember...? | 英文本不完全相同，中文不必逐字一致 |

## 3.5 阿卡罗阁楼发言的事后回想（第三章 L16774–16779 ⇔ 第一章 L5614–5627）

| # | 类型 | 原句 id | 引用处 id | 英文可搜索句 | 两边 new |
|---|---|---|---|---|---|
| 1 | 逐字重复 | `script_rpy_L019073_1_82b78b54` | `script_rpy_L053267_1_33306755` | Sai? I have no idea. He left the room earlier and didn't come back. What are you all even doing here? | **不一致**<br>原句：Sai？我完全不知道。他早些时候出了房间，就没再回来。你们到底在这儿干什么？<br>引用：Sai？我不知道。他之前离开房间就没再回来。你们几个到底来这儿做什么？ |
| 2 | 逐字重复 | `script_rpy_L019093_1_ae0c45e6` | `script_rpy_L053269_1_cb97be38` | I mean... what I said. Why are you all here? | **不一致**<br>原句：我是说……我刚才问的。你们为什么都在这儿？<br>引用：我是说……我刚才问的。你们为什么会在这里？ |
| 3 | 逐字重复 | `script_rpy_L019094_1_afb172cc` | `script_rpy_L053270_1_55a55e38` | We tried to stay put in one place together. Do you not remember that? | **不一致**<br>原句：我们不是一直守在同一处地方吗。你不记得了？<br>引用：我们说好一起待在一个地方不动。你不记得了？ |
| 4 | 逐字重复 | `script_rpy_L019099_1_6e432a4a` | `script_rpy_L053271_1_ea1ad81a` | No, I do. That doesn't answer my question, though. | **不一致**<br>原句：不，我记得。可这没回答我的问题。<br>引用：不，我记得。可这并没有回答我的问题。 |
| 5 | 逐字重复 | `script_rpy_L019100_1_35106c7a` | `script_rpy_L053272_1_842193b3` | How does it not answer your question? You and Sai escaped, and now you came back. | **不一致**<br>原句：怎么没回答？你和 Sai 逃了出去，现在又回来了。<br>引用：这怎么不算回答？你和 Sai 逃了出去，现在又回来了。 |
| 6 | 逐字重复 | `script_rpy_L019105_1_b2895ae3` | `script_rpy_L053273_1_61fa6a1b` | What!? That's not true! I didn't escape. | **不一致**<br>原句：什么！？胡说！我根本没逃出去。<br>引用：什么！？没有的事！我根本没逃。 |

## 统计

- 对照表条目：276
- 英文 `text` 有实质差异（不只是标签或大小写）：41
- 你填的 `new` 中文已不一致：208

下列旧全文本行号是章节或块的起点，不是对白，因此没有 JSON 条目：L8758（第二章起）、L12729（第三章起）、L17758（第四章起）、L18593（第五章起）、L21828（终章起）、L14923（`forsakenrelay`）、L20595（`c5badend`）、L21528（`c2explained`）。
