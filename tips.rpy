init -60 python: 
    from collections import OrderedDict
    tip_list = OrderedDict()
    tip_overlay = python_dict() # Determines if the red border should be shown on the tip
    tip_list["example1"] = "Inline Tips"
    tip_list["example2"] = "Tip Orbs"
    tip_list["A5"] = "The smoke in room A5"
    tip_list["search"] = "A search with no results"
    tip_list["future"] = "Sai's Sekimeiya"
    tip_list["9999"] = "Sai's wristwatch"
    tip_list["grenades"] = "Something small and dark"
    tip_list["mastermind"] = "Atsuki the mastermind"
    tip_list["knife"] = "The knife"
    tip_list["key"] = "The bedroom key"
    tip_list["pendulum"] = "Wrong cause of death"
    tip_list["plan"] = "Sai's plan"
    tip_list["traces"] = "Traces of the Sekimeiya"
    tip_list["camera"] = "Camera(s) disabled"
    tip_list["clash"] = "C and B's clash"
    tip_list["eyes"] = "Blind"
    tip_list["cold2"] = "The cold event room"
    tip_list["smell2"] = "The smell"
    tip_list["tired"] = "Atsuki's injury"
    tip_list["lie"] = "A quick lie"
    tip_list["erina"] = "Erina's hidden actions"
    tip_list["smell"] = "What is the smell?"
    tip_list["c2"] = "Chapter 2's title"
    tip_list["akaro"] = "Akaro's behavior"
    tip_list["suspicion"] = "The suspicion toward Atsuki C"
    tip_list["perspective"] = "Atsuki C's perspective"
    tip_list["hours"] = "Katei's sense of time"
    tip_list["fingerprints"] = "Purposeful fingerprints"
    tip_list["Tanya"] = "Tanya?"
    tip_list["perspective2"] = "Atsuki C's perspective 2"
    tip_list["ad"] = "Altered Dichotomy title"
    tip_list["cold"] = "The cold rule in A"
    tip_list["miiya"] = "Miiya's mind"
    tip_list["floor"] = "Why on the floor?"
    tip_list["dead"] = "Miiya should have died"
    tip_list["note"] = "The object that vanished"
    tip_list["spree"] = "The bloody spree"
    tip_overlay["spree"] = False
    tip_list["early"] = "Before {time=21}?"
    tip_list["larles"] = "Larles"
    tip_list["three"] = "Amount of victims"
    tip_list["roof"] = "Needed roof"
    tip_list["c3"] = "Chapter 3's title"
    tip_list["bootstrap"] = "Why in the bedroom?"
    tip_list["ha"] = "Ha—"
    tip_list["demolition"] = "The tower's demolition"
    tip_list["purse"] = "Isla's purse"
    tip_list["phone"] = "\"No service\" message"
    tip_list["january"] = "Four days ago"
    tip_overlay["january"] = False
    tip_list["keys"] = "The keys on the breakers"
    tip_list["card"] = "XYN's card"
    tip_list["burn2"] = "Where is Shiroya's burn?"
    tip_list["fake"] = "Gone from the cabinet"
    tip_list["gan"] = "Hospitalized"
    tip_list["burn4"] = "Hours of energy"
    tip_list["disappearance"] = "Permanent disappearance"
    tip_list["c4"] = "Chapter 4's title"
    tip_list["burn3"] = "Isla's burn"
    tip_list["injury"] = "Instantly healed"
    tip_list["split"] = "The world switch"
    tip_list["saielevator"] = "The impossible elevator"
    tip_list["virtual"] = "The virtual worlds"
    tip_list["burn1"] = "Where is Atsuki's burn?"
    tip_list["ohnoitdidntwork"] = "Flawed loop"
    tip_list["rush"] = "Paradoxical rush"
    tip_list["force"] = "The driving force"
    
    for key in tip_list.keys():
        if key not in persistent.tip_visibility.keys():
            persistent.tip_visibility[key] = 0

label tip_example1:
    scene bg white3
    with dissolve
    c "While in a tip, saving and search jumps are disabled."
    return

label tip_example2:
    scene bg white3
    with dissolve
    c "An orb is used when an inline tip is not viable."
    c "This could be to explain the setting, the chapter name, and so on."
    return
    
label tip_A5:
    $ SpriteTint("dark")
    show kateim 1a serious
    show bg hallwaya3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In world B, Katei assures the group that the event room, hallway A, and hallway B are the only places where the smoke was released. Despite the confidence behind his words, he misses room A5."
    c "This doesn't happen in world C, as in that one, he had time to look through the crystal floor. In world B, though, after hearing a sound in room B4, Katei was forced to stay with Erina's group."
    c "The reason why he doesn't mention room A5 is something that happened when Xyn was crafting their plan."
    show bg desk
    hide kateim
    nvl clear
    with dissolve
    c "\"Finally, both subordinates understood how serious their boss was and broke into a sweat. As they took off and draped their heavy attire on the back of their chairs, they began to process each step of what they would be performing.\""
    show bg securityroom13
    nvl clear
    show kateil 1a confused
    with dissolve
    c "When Katei was listening to Xyn putting together their plan, Ido eventually took off and leaned against his coat. That prevented Katei from clearly listening to the final part of their plan: the gemstones to be used as a fake out."
    return

label tip_search:
    show bg towermorning
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("naomia200")
    c "Even though the first six floors of the tower were searched through, nobody was found. Not because there was nobody to find, though—Naomi A was in the building."
    c "In addition, she didn't have the attic key, so even though the last floor wasn't inspected, nobody was there. Why wasn't she found?"
    c "During the search, Sai heard the elevator three times. That was Akaro's doing, but there's still an unexplained mystery: the starting position of the elevator.{w} It should've been on floor 5. Akaro knew that, so that's where he sent it in the end. However, before he called it, it was below the third floor."
    nvl clear
    show bg black
    show naomil 1a shocked
    with dissolve
    c "Naomi A was responsible for that. She was aware another self of hers had been murdered, and she wanted to easily escape if she had to. She called it when everyone was on the crystal floor, and soon after that, she accidentally made a noise while trying to understand what the others were doing in the event room."
    hide naomil 
    show bg elevator
    with dissolve
    c "That caused a search on the crystal floor, which Naomi A escaped by using the elevator so that she wouldn't be seen on the stairs. The elevator isn't very fast, so she took it to the second floor, where she waited to see if she'd be followed."
    show bg towermorning
    with dissolve
    c "Not long after that, the group went up to inspect the whole building, and they all stayed on different floors. Unable to access the attic, Naomi was cornered."
    show bg office3
    with dissolve
    c "She went up a floor every time someone else did. When she saw Akaro staying on the fourth, she stopped. She had seen him gone from the event room when she'd awakened, and she didn't think he had killed her other self. Most importantly, Naomi realized that if she kept going up, she could end up stuck on Katei's floor, and she suspected him of her own murder."
    show bg office49
    with dissolve
    c "Ready to be found by Akaro, Naomi stayed in the partitions of the fourth floor. However, he never came."
    return

label tip_future:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Sai travels to the past, he appears with the Future Sekimeiya in his hip pack. While unaware of this, he hides the fake Sekimeiya from the event room."
    c "Later, once he slips away from Atsuki, he proceeds to hide the Future and Past Sekimeiya. Even later, he obtains the Future Sekimeiya from the cleaning room and puts it in his hip pack."
    c "That is the reason why he had appeared with it before, but if you follow his movements, you will notice that something is odd: Sai got the Future Sekimeiya from the cleaning room because he had appeared with it earlier and had hidden it there. However, he had appeared with it because he would have it in the future, which would only be possible because he had appeared with it."
    c "...Where exactly does this start? When does the Future Sekimeiya enter this cycle?"
    c "There are a handful of similar riddles left to be uncovered, and the answer is often different for each individual case."
    c "When Sai left the attic after Atsuki and Shiroya, he had a plan in mind. He traveled to the past from room B3 and appeared with the Future Sekimeiya on his person. However, due to what his plan entailed, he would've had the Future Sekimeiya in the future if it hadn't appeared in his hip pack."
    return

label tip_9999:
    $ SpriteTint("dark")
    show bg thinking
    show saim 1a neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Every time Sai travels to the past, the date of his watch changes to \"9999-12-31\", and its screen turns blank. This behavior will be one of the toughest questions Atsuki will face."
    c "It seems to contradict the Sekimeiya's mechanics: infinite loops are needed to max out the watch's clock, yet the physical state of the watch doesn't deteriorate. This also happens with other devices such as the voice recorder and the digital clock in Eagle Motel."
    c "What's the reason behind it? Unfortunately, Atsuki didn't come close to the right answer, as it's related to something he never considered."   
    return

label tip_grenades:
    show bg cleaningroom1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "What Shiroya saw next to the Future Sekimeiya were smoke grenades. Not only the one Akaro had left there initially, but all of them."
    c "To conceal evidence, Akaro later brought the handful of grenades to the cleaning cart, and the moment that Shiroya made it disappear, they disappeared as well."
    c "You might be wondering what happened in world C, where the cart never disappeared but no grenades were found."
    c "In that world, Akaro also had the chance to put all the grenades in the cart. Then, they were never found, the same way Ido's set of keys wasn't found."
    return

label tip_mastermind:
    $ SpriteTint("dark")
    show bg thinking3
    show saim 1b smirk at p13
    show akarom 1a frown at p23
    show kateim 1a frown at p33
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("saib200")
    c "In the lower bedroom, Sai had an idea about how he could escape the locked room they had set up. He only needed Katei to be distracted for an instant—he didn't want him to leave."
    c "Sai told him that Atsuki had been threatening them. At first, Katei didn't believe a word of it.{w} However, Akaro quickly realized that Sai might've needed his assistance: Sai was claiming that Akaro had been threatened as well, and he could easily deny it."
    c "When Akaro confirmed it, Katei's look changed.{w} He didn't believe it. He'd seen Akaro's first reaction; they were lying. Most importantly, Akaro was claiming that Atsuki had been behind the attack, and Katei knew who Akaro was.{w} ...Why? Did both of them suspect that Katei was behind Isla's death? Perhaps they wanted to see whether he could accept another version of events—if he denied it without considering it, he might've given himself away."
    hide saim
    hide akarom
    hide kateim
    with dissolve
    c "Katei yelled Atsuki's name as he climbed up, unaware that the door of the bedroom was opening while his shouts concealed the sound."
    return

label tip_knife:
    $ SpriteTint("dark")
    show bg white3
    show saim 1a smirk2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Where did Sai's knife come from?{w} Originally, it belonged to Suripo."
    hide saim
    show bg entrance15
    with dissolve
    c "After his death in world C, Akaro heard a sound coming from hallway A: it was Katei, who had appeared in the security room."
    show bg hallwaya21
    with dissolve
    $ ChartNode("akaroc60")
    c "Akaro entered the hallway and prevented him from seeing the scene in the lobby. However, he hadn't had enough time to get rid of the knife, which he had under his shirt."
    show bg towermorning
    with dissolve
    c "Later, when the group world switched to world A, Akaro finally had the chance to leave it behind after removing his fingerprints. It was there where Sai found it, after Shiroya pulled him to that world. Soon afterward, Sai returned to world B by world switching alone."  
    show bg cfbathroom3
    with dissolve
    c "The knife eventually ended up in Shiroya B's hands, but it vanished from existence when she traveled to December 30th with it in her purse."
    return

label tip_key:
    show bg bedroomkey
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki is able to find the right bedroom's key in the drawer, so had Sai failed to grab it? Had Sai ignored the fact that they could've locked themselves inside that room?"
    c "Sai thought he was still chasing Atsuki A, who had punched him in the face. The moment Atsuki A had run away, Sai had taken both bedroom keys to prevent him from staying inside one."
    c "When the chase shifted to world B, Sai was unaware the world around him had changed. He entered the attic with the attic key from world A, and he didn't take the bedroom keys because he thought he had already taken them."
    c "Later, when he and Shiroya traveled to the attic's bedroom, Sai appeared with both bedroom keys, and they were still the ones from world A."
    nvl clear
    with dissolve
    show bg atticbedroom12
    show saim 1a worried smoke bright at p11
    with dissolve
    sai "By the way, you never reattached the chain, right?"
    c3s "The chain? What are you talking about?"
    sai "Nothing."
    c "Sai had detached the bedroom chains in world A to prevent Atsuki from hiding in one, so that was further confirmation that the world around him had changed."
    return    

label tip_pendulum:
    show sail 1a surprised
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Sai delivers a fatal blow to Shiroya, he stares at her fallen corpse. Something doesn't seem to make sense from his point of view."
    c "He had already stated it as fact before—Shiroya would die. He had seen her corpse in world A, so he was certain that death was her inevitable fate."
    c "The reason behind Sai's sudden confusion lies behind Shiroya's cause of death. When he saw her corpse in the lobby, he didn't see any physical wound. However, he'd just sliced the knife across her chest."
    c "That causes Sai's momentary puzzlement, but he is able to instantly shrug it off and move on to his second victim."      
    return

label tip_plan:
    $ SpriteTint("dark")
    show bg sekimeiyaroom14
    show saim 1a frown2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("saib300")
    c "Sai couldn't explain his recent experiences, but he was sure that something had happened to the world. The Atsuki who had punched him wasn't the same one he was speaking with, and the green lights on the cameras indicated that the state of the world was changing."
    c "He recognized that the Atsuki in front of him was the same person he'd been with since that morning, and by hearing what he said, Sai began to slightly comprehend what had happened."
    c "The first time the world had changed had been when both Sekimeiya had disappeared in room B6. Curious, Sai asked if that was where Atsuki and Shiroya had found the Sekimeiya, and upon having that confirmed, he learned something important.{w} Both Sekimeiya had been left behind there, and Atsuki and Shiroya had activated the one outside the drawer. That told Sai not only that they had gone to the future, but that when they had returned, someone had taken it."
    c "However, they thought that the Sekimeiya had teleported to the drawer, when in truth, that one had also been there all along. Sai knew that the Sekimeiya in the event room was the past one and that he needed to use it in order to put together a plan he quickly came up with to take advantage of Atsuki's and Shiroya's story."
    return

label tip_traces:
    $ SpriteTint("dark")
    show bg sekimeiyaroom6
    show saim 1a neutral2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai is referring to the forum thread that Vaisude had posted in November. Back then, Sai had replied to it in a frivolous way, but it didn't take long for the Sekimeiya event to be announced. By the time that happened, the thread had already been locked."
    c "Something was going to happen on December 15th—Sai knew that, and as proven by worlds A and C, he would've gone to the event even if he hadn't read that forum thread."
    c "However, in world B, the possibility of time travel was in his mind since the start. The moment that Atsuki traveled to the past, two things were confirmed to Sai."
    c "One: at one point during the day, a very large travel would occur. He had to be careful if he didn't want to be sent to November 24th, and he knew that traveling so far to the past would be possible."
    c "Two: the forum poster was somewhere around them. During the twelve hours in the tower, Sai kept wondering who \"7md_ag\" could be."
    return

label tip_camera:
    show bg crystalrooms8
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "At {time=10:04}, Katei had disabled the camera in room B4. He'd hidden both Sekimeiya there, so alongside removing the incriminating footage, he'd surreptitiously shut that camera down so that he could retrieve them later."
    show bg securityroom21
    with dissolve
    c "When Atsuki and Shiroya found Katei's corpse, a message was on the computer: {time=10:04}: Camera(s) disabled and associated footage erased."
    c "It had been there since Erina had attempted to display the footage from room B4. In other words, the message was only addressing that particular camera—none of the others had been disabled, as shown by the presence of the green lights."
    c "Atsuki double-clicked on the camera selected on the list: \"RECAM_12_01\". It was the one Erina had attempted to display, so he was met with the same error."
    c "Miiya noticed something when she world switched to world B. The camera in room B4 didn't have a green light, while all the others did."
    return

label tip_clash:
    $ SpriteTint("dark")
    show saim 1a frown smoke at p12
    show akarom 1b thinking smoke at p22
    show bg hallwayb25
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When worlds C and B meet, neither of their perspectives makes sense to the other. If you recall everything that happened in world C, you will understand the meaning behind all of Sai's and Akaro's words."
    c "Before them, the two bodies that had vanished reappeared: Shiroya and a bloody Erina. In addition, they thought Shiroya had died weeks in the past."
    c "Given the blood on Erina's clothes, what Sai and Akaro instantly assumed was that she was the body that had disappeared from next to the crystal floor stairs."
    c "\"Well, you're not dead after all, but we felt your pulse...\""
    c "And according to Erina, she didn't remember what had happened before she'd been attacked. Even though she was talking about a different attack, that led to Sai's strange statement: \"Not even you have been here since {time=9}!\""
    c "\"Of course, Erina and Isla have been here the whole time, but not you.\" She was not thought to be the same Erina who'd been with them since the morning, as the way she'd come into existence was still a mystery to them."
    return

label tip_eyes:
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Atsuki dashes out of the elevator, his eyes are closed due to the intense pain. That prevents him from seeing the trail of his own blood going from the storeroom toward the stairs."
    c "Later, that helps him mistakenly believe that he altered history, as he never saw a result of his actions after deciding to try to change the past."
    return

label tip_cold2:
    show bg sekimeiyaroom20
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    #this might be an unnecessary tip
    c "Atsuki finds the event room to be cold—the glass of the cabinet isn't properly shut."
    c "It had been open since Erina had taken the Future Sekimeiya out before world switching to world C. After the group's departure, the Sekimeiya fell to the floor, and the glass was not closed."
    c "Two people entered the event room before Atsuki's return: Sai and Atsuki A."
    c "Both of them noticed the cold, but neither of them closed the cabinet. Atsuki A touched the Future Sekimeiya and world switched to world C. Sai, who had locked Shiroya inside a bedroom a second time, arrived after Atsuki's vanishing and took the Sekimeiya from the floor, hiding it in the women's bathroom."
    return       

label tip_smell2:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The smell released by the Sekimeiya as it gathered energy was often perceived in Ashiya Tower. It became the building's scent, and everyone grew used to it subconsciously."
    c "However, numerous times, the intensity of the smell seemed to increase. Why did this occur?"
    c "If the group spent hours in the attic, upon walking down to the crystal floor, if one of the Sekimeiya had been gathering energy there, the smell would seem more prominent.{w} But that's not all. Noticing the smell often indicated something else.{w} A world switch."
    c "When Atsuki and Erina were in world C, both real Sekimeiya were in the attic, so after returning to world B, Atsuki sensed that the smell was strangely strong."
    return

label tip_tired:
    $ SpriteTint("dark")
    show bg hallwayb5
    show atsukim 1b pensive
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Atsuki travels to the past, he notices that blood has stopped coming out of his injury. Additionally, he feels very tired."
    c "The relation between those results is direct: the body he appeared in had lost a lot of blood."
    c "However, he never actually bled all that blood, so why did he appear in a body that had lost it?"
    c "Not only that, but the injury was still there, so why was no more blood coming out of it?"
    c "Before the time he will reach the replicated location in the future, Atsuki will rush to the crystal floor stairs and reopen his wound. To keep blood from flowing, he will bandage his hand with toilet paper."
    c "That might help you answer the second question, but what about the first? When was all that blood lost? There's still a bit of time for you to find that answer."
    return

label tip_lie:
    show bg hallwayc15
    show saim 1a frown smoke at p12
    show atsukim 1b pensive at p22
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai claims to have heard Atsuki's door slam, but that is not the truth. When Atsuki made that noise, Sai was in the process of traveling to the future; Erina's world switch brought him back to the attic's bedroom, where Shiroya had been trapped."
    c "Why did he say that he had heard it, then?{w} He thought that Atsuki was testing him."
    c "He thought that the intent behind that question was to figure out whether he had traveled to the future and whether such a thing was possible. To prevent Atsuki from learning the truth, he claimed to have heard a sound he could only have heard if he'd traveled to the past."
    return

label tip_erina:
    show bg office42
    show erinal 1c sad blood at p11
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Erina's mood seems to have changed since Atsuki left..."
    hide erinal
    show bg sekimeiyaroom7
    with dissolve
    $ ChartNode("erinab300")
    c "When she made Atsuki and Shiroya world switch, to them, it seemed as if the Sekimeiya teleported to its cabinet—a Sekimeiya was there in world C."
    c "It was the fake Sekimeiya that the people of that world had left there before Miiya went to sleep in the attic. However, you might've noticed something strange."
    $ SpriteTint("dark")
    show bg sekimeiyaroom13
    show miiyam 1a neutral at p22
    show atsukim 1b pensive at p12
    with dissolve
    c "Later in that world, when Atsuki and Miiya went down after waiting on the second floor, the cabinet in the event room was empty. ...Who took the fake Sekimeiya?"
    hide miiyam
    hide atsukim
    show bg sekimeiyaroom7
    show erinam 1d frown blood at p33
    with dissolve
    c "Very few people would've had the chance, and it was Erina B who did. When her group arrived in world C, Atsuki went to the staff room to check if the Sekimeiya had disappeared from Ido's locker. He was followed by Shiroya, which gave Erina the perfect opportunity to silently take the fake Sekimeiya from the unlocked cabinet and put it in her purse."
    hide erinam
    show saim 1a frown smoke at p12
    show akarom 1b thinking smoke at p22
    show bg hallwayb25
    with dissolve
    c "She still wanted to travel to the past, so she calmly waited with the others while she thought that the Sekimeiya she had was gathering energy."
    hide saim
    hide akarom
    show bg black
    nvl clear
    with dissolve
    $ Pause(0.4)
    $ SpriteTint("normal")
    show bg office42
    hide saim
    hide akarom
    show erinam 1c frown2 blood at p12
    show atsukim 1b worried at p22
    with dissolve
    c "When she and Atsuki stopped on the third floor and returned to world B, Atsuki took the elevator down, and a future self of his appeared from the partitions, claiming to have traveled to the past and stopped the wound's bleeding.{w} \"Wait... What? There's no way.\" Erina couldn't help but react that way, as she had the Sekimeiya in her purse."
    hide atsukim
    show erinam 1d frown2 blood at p12
    with dissolve
    c "The moment Atsuki left her alone next to the elevator, she reached inside her purse and attempted to travel through time. The Sekimeiya was there, but of course, nothing happened. That disappointment caused Erina's unresponsiveness when Atsuki returned with Sai."
    show bg towernight
    hide erinam
    with dissolve
    c "This also erased the fake Sekimeiya in world C and led to the existence of two in world B. Erina soon got rid of hers, but the one that Akaro A had hidden was still in the building, and it was the one that the police found at {time=21.}"
    return

label tip_smell:
    show miiyal 4a confused at p33
    show bg gemshop5
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Miiya feels as if she recognizes the smell in the gem shop, yet she isn't able to determine what it is... What exactly was in the air?"
    c "The answer is that two different smells were blending together—the smell of gas and the Sekimeiya's scent.{w} Miiya partly recognized the gas in the air, but due to the Sekimeiya's alien smell, she wasn't able to realize what it was."
    c "On December 15th, Miiya and Shiroya were exposed to the Sekimeiya's smell once again, and they almost felt as if they'd smelled it once before."       
    return

label tip_c2:
    show bg white3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Eden is a perfect world that was given to Adam and Eve. In this world, everyone who was trapped in the tower survived, and Shiroya, who was thought to have died, reappeared on her birthday."
    c "It's a world that was given to Atsuki and Miiya, and just like Eden, it might look perfect at first glance; it's exactly what Atsuki and Shiroya wanted in world B."
    c "...But that is far from the case. Eden is a world doomed to fail.{w} Not only that, but it is a single step away from disaster. It only requires the forbidden fruit."
    return

label tip_akaro:
    show bg thinking
    show akarol 1a frustrated 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The way Akaro initially portrays himself is quite different in worlds B and C. In world B, he hurries Naomi to unlock the cabinet."
    show bg nosmokesekimeiyaroom
    hide akarol
    show akarom clean 1a frown at p13
    show naomim clean 1a neutral
    with dissolve
    c "\"We know, and don't need this introduction, so let's move along. You've been praising this find of yours in every advertisement. Let's see how your claims hold up.\""
    c "In world C, however, he does the opposite. He stops Naomi to buy time."
    c "The reason is the same in both cases: the smoke bombs were timed to go off very soon. In world B, he didn't want them to go off before the cabinet unlocked, while in world C, he didn't want them to go off after the cabinet opened so that there was no staining on the Sekimeiya."
    c "What causes the time difference between both worlds is the talk Atsuki and Shiroya have in hallway B before entering the event room. As such a thing doesn't occur in world C, Akaro is forced to take action, and after proving himself knowledgeable about Ashiya, he maintains that image, telling the group about Xyn as soon as they regain consciousness."
    return

label tip_suspicion:
    $ SpriteTint("dark")
    show kateil 1a thinking smoke at p13
    show bg securityroom
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Katei questions out loud if Atsuki could've been the one to power off the computer. Once the conversation ends, he will talk to Miiya privately and tell her that Atsuki is lying to her. A bit later, even Sai will say something similar."
    c "In both cases, the answer relies on Atsuki B, who was also in the building. You might recall that he thought Katei must have seen him when he crossed through floor 2 holding the Sekimeiya."
    c "Aware of the Sekimeiya's powers, Katei could understand that his sighting of Atsuki was related to it. That's why he attempts to push the narrative that Atsuki was behind the computer's shutdown, certain that he was the one to take the fake Sekimeiya from the event room."
    return

label tip_perspective:
    show bg hallwayc8
    show atsukil 1a pensive smoke
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Miiya doesn't notice that the Atsuki she's talking to is a different person than moments prior in the security room. Atsuki C had traveled to the future with Sai, and before his return, Atsuki B had occupied his place."
    show bg hallwayc8
    hide atsukil
    with fastdissolve
    $ ChartNode("atsukic50")
    c "Some time after Sai and Atsuki C had appeared in the future, Sai had noticed that the elevator was open. Once he shut its door, it immediately ascended, as Atsuki had called it while trapped inside the attic."
    $ SpriteTint("dark")
    show atsukim 1a pensive smoke at p22
    show saim 1a neutral2 smoke at p12
    show bg black
    with dissolve
    c "Sai and Atsuki met, but neither of them said that they had traveled through time. When Atsuki saw the time on Sai's watch, the idea that he had traveled to the past was reinforced: before traveling, Sai had disappeared to check if the Sekimeiya he'd hidden in the storeroom had powers as well, so it made sense to find him separated from the group in the past. For Sai, it meant that he had traveled alongside Atsuki when he'd been going back to the event room; he learned that more than one person could travel at once."
    show bg securityroom10
    show atsukim 1a neutral smoke at p33
    show saim 1a neutral smoke at p23
    nvl clear
    with dissolve
    c "When they returned to the security room, both of them believed that they had been gone for mere minutes, and they were not aware that an Atsuki had been with the group since their departure. That's why numerous things that Atsuki C says conflict with what Atsuki B did."
    c "Atsuki B estimated that Atsuki C had traveled twenty minutes through time, but that wasn't that accurate. When Atsuki C gave his version, he said he traveled \"a few minutes\" to the past, aware that it couldn't have been as many as twenty because the attic had been locked."
    nvl clear
    hide atsukim
    hide saim
    show bg black
    with dissolve
    $ SpriteTint("normal")
    show atsukil 1b pensive smoke 
    show bg hallwayc8
    with dissolve
    c "\"Oh, yeah, it was earlier. Sai used it.\" Unaware that they'd talked about the elevator in the security room, Atsuki C affirms that Sai closed it—it's no speculation."
    hide atsukil
    nvl clear
    show bg black
    with dissolve
    $ SpriteTint("dark")
    show bg mechanical
    nvl clear
    show atsukim 1b pensive smoke at p12
    show miiyam 1a neutral smoke at p22
    with dissolve
    c "Later on, Miiya and Atsuki C will be in the mechanical room, and a similar situation will arise with neither of them noticing; Atsuki C doesn't know the theory that Atsuki B brought up regarding the Sekimeiya's power storage and will hear it for the first time from Miiya."
    c "\"We don't know how long it's been here for, so it might not be a good idea.\""
    c "\"What do you mean?\""
    c "\"Well, if the time you travel depends on how long it spends out of the cabinet, you could go really far back.\""
    c "\"Oh... Hm, I see.\""
    return

label tip_hours:
    $ SpriteTint("dark")
    show kateil 1a pensive clean
    show bg thinking3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai raises a good point: how is Katei able to know that he was missing for three hours?"
    c "Even though Sai accuses him of having left the building, the truth is that he had traveled to the future with Suripo. That doesn't answer the question, though. How is he able to tell how long he's been absent for?"
    c "The past location that was replicated was from the time Suripo was in the lobby. At that time, Katei was in the security room, so that's where he appeared."
    c "What he immediately saw was the BIOS screen that Atsuki and Miiya had left behind, which displayed the current time and revealed to him that he had traveled to the future."      
    return

label tip_fingerprints:
    show akarom 1a frown
    show bg entrance15
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The reason why Akaro takes the walkie-talkie is not to try to repair it. What he wants is to justify the fingerprints that the police would have found on its surface."
    hide akarom
    show kateim 1a confused
    show bg black
    with dissolve
    c "Something similar happened in world B, although it was Katei who thought of it."
    hide kateim
    nvl clear
    show bg hallwayc12
    with dissolve
    $ Pause(1.0)
    show bg hallwayc13
    with dissolve
    $ Pause(0.7)
    c "Before Naomi A's body was found, he brought the suitcase from hallway C to the security room; he realized that he hadn't touched it when they'd found it, so he wanted everyone to see him touching it and leaving fingerprints."       
    return

label tip_Tanya:
    show shiroyal 1ap2 neutral at p13 
    show miiyal 1a smile at p33 
    with dissolve
    c "Why does Isla call Miiya \"Tanya\"? Wasn't that Shiroya's nickname?"
    c "On November 30th, Atsuki bought both girls matching pendants. Even though they weren't real tanzanite, they were a convincing fake."
    c "Miiya and Shiroya were wearing the pendant in their respective worlds, so Isla came up with the nickname \"Tanya\" for both of them."
    return

label tip_perspective2:
    $ SpriteTint("dark")
    show bg thinking3
    show atsukil 1a
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In room A1, Atsuki C met with Atsuki B, who took over the search and temporarily acted like Atsuki C. Minutes after that, Atsuki C timidly approached the storeroom and found everyone beside the secret door. There, he learned that he had completed the whole search without finding anything."
    c "That was all the information he had, so every time he was accused of having ignored something on purpose, he couldn't directly reference the search, as he wasn't sure about how it had unfolded. That's why he asks Miiya if she knows where the Sekimeiya could be, just in case she is aware of a potential hole in a search he didn't witness."
    return

label tip_ad:
    $ SpriteTint("dark")
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "How many dichotomies were altered in this scenario?"
    show saim 1a neutral3
    with fastdissolve
    c "Sai claimed that the Sekimeiya's main two powers, traveling to the past and future, were but a fraction of their capabilities."
    hide saim
    show shiroyam 1ap1 neutral
    with fastdissolve
    c "Miiya stopped existing and Shiroya took her place."
    hide shiroyam
    show bg towernight2
    with dissolve
    c "Neither Ashiya nor Xyn ended up in possession of the real Sekimeiya. In this case, it was Sai who was able to keep both of them."
    c "There was one more dichotomy that was altered, and knowing it will help you figure out Sai's tricks."
    show bg sekimeiya
    with dissolve
    c "To achieve what he wanted, he altered the dichotomy between real and fake Sekimeiya."
    return

label tip_cold:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In world A, before Akaro knocked out Naomi, she told him that the Sekimeiya must always remain in a cold place and that they could break if they remained outside their cabinet. He'd already heard that from Ido, but Naomi's tone of voice made it sound much more important."
    c "That scared Akaro. Would both real Sekimeiya break if he kept them in the cleaning cart? Unaware that they were no longer there, Akaro concluded that he had to move them; he didn't know how long the shutter would stay there for, but he knew Ashiya Tower very well. Other cabinets with temperature functions existed."
    c "Thanks to the security room key that he had found and Naomi's keyring, Akaro went to the attic. There, he found both real Sekimeiya and traveled through time."
    nvl clear
    with dissolve
    c "As soon as he understood what happened, he created a plan and executed it. At the end of the plan, he put the Future Sekimeiya in the refrigerator, moved the suitcase, rejoined the group holding the Past Sekimeiya, and managed to keep it in a cold cabinet in B4 where everyone stayed for a long time."
    c "However, both times, Akaro made a mistake. He wasn't aware of how cold the temperature had to be, as above 0 ºC, the Sekimeiya would always gather energy.{w} Unlike Atsuki, he didn't tamper with the temperature setting, and in room B4, he set the cabinet to 5 ºC. During the time the Sekimeiya spent under those conditions, both of them gathered energy at a slow rate."
    nvl clear
    show bg elevator
    with dissolve
    c "Eventually, Sai left room B4 and started exploring the tower. At that point, the elevator was on floor 6, so he was able to see the hidden bodies and reach the attic."
    show bg sekimeiya
    with dissolve
    c "Up there, he found the Future Sekimeiya in the refrigerator. The instant he touched it, he was split in half by the door of room B4."
    c "Before his body appeared in the future, however, the door of the refrigerator was left open, which made Atsuki C notice that it was strangely cold in the attic. It was Katei C who found the Future Sekimeiya in the refrigerator, and he quickly hid it in a bedroom, where Miiya would soon activate it."
    return

label tip_miiya: #don't know what to do with this tip
    show bg thinking3
    show miiyal 1a neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The entire day, Miiya's thoughts carried mystery and ambiguity, rarely being organized or complete."
    $ Pause(0.3)
    show bg office47
    hide miiyal
    show overlay_flashback onlayer master_overlay
    with dissolve
    c "\"How much longer would I have to play along for? Ever since she'd exited our lives, I'd kept telling myself that it would all eventually go back to how it was at the beginning.\""
    show bg entrance15
    with dissolve
    c "\"Regardless, I had to put on the same appearance, and it came naturally after the previous two weeks.\""
    c "Unlike Shiroya, she didn't fall into a coma, so she had been living with Atsuki for two weeks."
    show bg elevator11
    with dissolve
    c "\"She really was here, but...\""
    show bg black
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "There was often something important to infer from her thoughts, especially after she murdered Erina."
    nvl clear
    show miiyal 1a neutral
    with dissolve
    c "She had killed a person. She'd wondered many times what that would be like, and she finally knew. Until {time=21}, her mind kept going back to that moment, ever-present in her thoughts, trying to make sense of what had really happened at the time."
    show bg crystalrooms42
    hide miiyal
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    c "\"She was there, casually leaning against the line of cabinets. I could hardly believe what I was seeing, but there was no wariness in her eyes and not even a trace of blood near her.\""
    show bg camera3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "When Miiya world switched to world B, she saw that the cameras' green lights had returned."
    c "\"...The computer. It reenabled the cameras. This really must mean that they weren't recording until now, right...?\""
    c "\"Hopeful, I entered one of the rooms.\""
    c "Could that mean that her murder hadn't been recorded? Just as she was trying to rationalize that, Erina appeared in hallway B."
    show bg hallwayb25
    show erinal 1d worried blood at p11
    show overlay_flashback onlayer master_overlay
    with dissolve
    c "Her clothes were caked in dried blood, and the wariness in her voice was back. In response, Miiya started to ask a question that she never finished."
    c "\"A-Are you...?\"{w}—\"the Erina that I already killed?\""
    $ Pause(0.5)
    nvl clear
    hide erinal
    show bg sekimeiyaroom20
    with dissolve
    $ Pause(0.7)
    c "A lot more happened until {time=21.} Miiya saw another Atsuki and was told that Shiroya would come back to life. Although her mind was pulled from many different sides, in the event room, shortly before the shutter opened, she couldn't help but think about her own grim future."
    c "\"I didn't think anything good could come of it. After all, there was a killer in the room.\""
    c "\"Despite that, as the seconds ticked along, the answers I tried to reach changed more and more.{w} What would happen to me? ...I looked up to try to believe that nothing would, but I had no way to know.\""
    c "She looked up at the single camera in the room. The green light on it was no longer visible, but she had no way to know what that meant for her. As the final seconds passed by, Miiya continued to wonder if anyone would ever see the time she had pushed Erina off the stairs on the second floor."
    hide overlay_flashback onlayer master_overlay
    show bg black
    nvl clear
    with dissolve
    return       

label tip_floor:
    show bg cg11-3
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Why does Atsuki B request that they leave the Sekimeiya on the ground on the second floor?"
    c "It's the Future Sekimeiya, and very soon, Shiroya B will travel all the way to November 30th. Since she is in the attic, what Atsuki wants is to prevent the range of the Future Sekimeiya from reaching Shiroya and causing a world switch."
    c "He recalls the events that he lived through: he knows that a group of people is next to the elevator on the crystal floor. That's why the ground on the second floor is the best place to keep the Future Sekimeiya."
    return

label tip_dead:
    show miiyal 1a deadpan at p33
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("miiyac19")
    c "Miiya agrees that she should be dead. From her point of view, she should have died."
    hide miiyal
    show bg gemshop6
    with dissolve
    c "On November 30th, she fell unconscious where a deadly explosion took place. However, when she woke up, her body had moved."
    c "She had no idea what had happened—she'd begun to wonder if she was mistaken about the exact place she had fallen unconscious. Despite that... she should've died. To her, it didn't make sense that she was alive."
    return

label tip_note:
    show miiyal 1a shocked at p34
    show bg red2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Something disappeared from Miiya's purse. The proof that Shiroya had died was no longer there."
    c "It was a note that Atsuki C had written days before December 15th, which Miiya had been careful not to reveal that she had in her purse."
    c "So, when did it vanish? Despite Miiya's speculation, it wasn't a change in history that got rid of it."
    hide miiyal
    show bg black
    with dissolve
    $ SpriteTint("dark")    
    show erinal 1a serious blood bright at p11
    show overlay_flashback onlayer master_overlay
    show bg crystalrooms5
    with dissolve
    c "When Miiya and Erina were together in room A5 in world B, Erina grabbed Miiya's set of keys from her purse with a quick motion. After that, Miiya dashed out of the room when she heard Atsuki calling Shiroya's name."
    show erinam 1a surprised blood at p11
    hide erinal
    show bg sekimeiyaroom24
    with dissolve
    c "That caused the note to fall to the floor, and Erina picked it up. Minutes later, in the event room, she gave it to Atsuki B, which is how he obtained it originally, as it wasn't the same note that he'd already left behind a handrail."
    nvl clear
    show bg white3
    hide overlay_flashback onlayer master_overlay
    hide erinam
    with dissolve
    c "If you follow the movements of the note, though, you might notice that something is off."
    c "It only entered the tower in world C in Miiya's purse. Late into the day, when she went to world B, she dropped it and Erina picked it up."
    c "Erina gave it to Atsuki B before the future location of one of his travels, which let him have it in the past."
    c "He first saw it in the staff room and immediately tossed it behind one of the hallway B handrails, where the police of that world found it."
    c "There's one last key to understanding this puzzle. Before Miiya dropped the note for Erina to obtain it, she had traveled back in time."
    nvl clear
    show bg staffroom1
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    i "\"I looked up and saw three slits in the door. Despite the darkness that should've existed behind them, I discerned a glow.\""
    i "\"It could only have been one thing. Despite being filled with questions, my mind was blank. My hand was drawn to the shape that had begun to take form behind the dark lines, and through the narrow space, I made contact, hoping with all my might that I would be brought to the awaited time.\""
    #"hoping it'd be taken to the awaited time." this is miiya hoping the sekimeiya will send her to the future, past 9pm, since she did realize the last time that's what had happened
    show bg hallwaya26
    nvl clear
    $ Pause(0.7)
    i "\"However, hallway A was my next sight.\""
    play sound "sounds/falling.wav" noloop
    $ Pause(0.2)
    show bg hallwaya44:
        truecenter zoom 1.05 subpixel True ## To hide the vpunch borders
    with vpunch
    i "{w=1.0}\"Then, I fell to the floor immediately after appearing.\""
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg towernight
    with dissolve
    c "She appeared in hallway A, dropped the note next to Erina in room A5, and then the replicated location took place. In world C, she and Atsuki ran to the crystal floor after Akaro. Since they were ahead, they didn't notice her pick up the note. Afterwards, she ran to catch up with Atsuki, which is why she had appeared in hallway A in world B and immediately fallen to the floor."
    c "So there's a large inconsistency. If she dropped the note before the replicated location, why did she have it when she appeared in hallway A? She must've had it, or else she couldn't have dropped it in room A5."
    c "Do you remember something Atsuki B thought regarding the note?"    
    nvl clear
    show bg attickitchen1
    show overlay_flashback onlayer master_overlay
    with dissolve
    i "\"I put my hand in my pocket, but the note wasn't there. It had disappeared at some point.\""
    nm "Right. The next time I traveled to the past, I didn't appear with it.{w} But... why? I should have."
    nm "Oh, it's like I thought earlier. I had the note when I traveled to the past. From the staff room, I appeared in hallway B and then slammed the storeroom door to create a new noise. After that, I waited in the bathroom on the second floor.{w} There, I put my hand in my pocket because I wanted to flush the note away. However, it wasn't there.{w} That's why I didn't appear with it. I wanted to flush it away, so if I had, I wouldn't have held the note in the future, and I never could've appeared with it."
    c "What he thinks happened makes sense, and it would've happened if not for something he didn't realize. By the time he traveled from the staff room, he had already dropped the note Erina had given him in the event room."
    show bg hallwayc22
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve    
    i "\"Sai was the least of my concerns. I barely put any thought into punching him, but before I did, I saw a conspicuous smile all over his face. It only faded momentarily, returning right after the blow.\""
    c "Atsuki had an altercation with Sai C near the elevator after Shiroya left them behind. At that time, the note fell from his pocket."
    c "And someone found it just minutes later. None other than Miiya herself."
    show bg fromstairs1
    nvl clear
    with dissolve    
    i "\"We ran behind Akaro. I looked down and saw that there was still no blood on the floor or the staircase.\""
    show bg hallwaya26
    with dissolve
    n "What...!?"
    show bg hallwayc8
    with dissolve
    i "\"On the floor, below the elevator panel, there was a folded piece of paper. Atsuki and Akaro were ahead of me, so they didn't see me grabbing it and putting it in my purse.\""
    n "Did it... not disappear after all?"
    show bg hallwaya26
    with dissolve
    i "\"Akaro was in the storeroom, but I just followed behind Atsuki, completely lost for words. How the hell had that made it there?\""
    show bg towernight
    with dissolve
    c "Right before she ran through hallway A to satisfy her previous travel, she reobtained the note."
    show bg towernight2
    with dissolve
    $ SpriteTint("normal")
    c "And at {time=21}, the police didn't find it in her shoe, where she had stored it as a last-ditch effort. So, even though only one note entered the tower in the morning, a copy of it reached the end of worlds B and C."       
    return
    
label tip_spree:
    show bg towernight
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In the hour before the tower unlocked, the scent of death enveloped Ashiya Tower. Everyone reached the last stretch of their imprisonment just to fall victim to a sudden, gruesome massacre."
    c "...But what really took place inside the giant building? What was the cause behind the last second turn of events? Here are the facts you already know about:"
    c "1. When the police entered the tower, nobody was alive inside it."
    c "2. All the deaths were instant, and two people couldn't have killed each other simultaneously."
    c "3. No one committed suicide. Every single person who was trapped in the morning was attacked by another person."
    nvl clear
    with dissolve
    c "Those points alone raise a serious question: who killed the last person? Everyone who died was instantly killed by someone, so what happened to the last victim to fall dead?{w} Let's look at more facts surrounding the case:"
    c "4. The police found and unlocked the hidden door in the storeroom. By doing so, they removed Sai's mark. In other words, that door hadn't been opened since Sai had marked it more than six hours earlier."
    c "5. The police found one of the Sekimeiya gray and on the floor in the event room."
    c "6. Everyone who died was killed by someone from their own world, and no killer world switched to another world. They all died in their own world, C, where they were found dead."
    c "7. Everyone who died was pierced by the same screwdriver. When the last person died, their killer threw it away, and the police found it next to the crystal floor stairs.{w} If you're curious, when the police analyzed it, they found two different sets of fingerprints on its handle."
    c "One set of prints matched with Miiya's records. Do you know who else had wielded that screwdriver?"
    nvl clear
    with dissolve
    $ ShowQuestion("char screwdriver")
    window auto show
    with dissolve
    $ Pause(0.5)
    c "A handful of fingerprints belonging to Naomi C overlapped those from Miiya. Does that make sense, though? Wasn't Naomi lying on the floor in the lobby?{w} What really happened when the police raided the building?"
    show bg towernight2
    show overlay_flashback onlayer master_overlay
    nvl clear
    with dissolve
    c "\"In the lobby was the first indication of the bloodbath that had transpired. Dead eyes watched the officers from the floor, inviting them to a hell of corridors and blood.\""
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c "They were Suripo's eyes—Naomi wasn't there."
    c "She wasn't anywhere. As you know, the moment the first police officer took a step into the building, no speck of life dwelled anywhere."
    c "But that's hardly a problem, is it? The gray Sekimeiya that the police found indicates that someone activated it shortly before the shutters rose. It was the Future Sekimeiya, which had previously failed to let Katei escape from his pursuer. Whoever activated it would not have been present when the police entered the building."
    c "Let me refresh your memory of something you were once told."
    nvl clear
    show overlay_flashback onlayer master_overlay
    show bg entrance11
    with dissolve
    c "\"Fortunately, everyone was able to leave safely. That included Naomi, who was woken up by the loud noise of the shutter.\""
    c "\"However, a single decision nearly sent everything spiraling into destruction.\""
    show bg towernight3
    with dissolve
    c "\"Instead of the shutter, yells of pain that would've woken Naomi up before that time were almost let out. Disastrous yells that would've shattered everything that had been needed to get there.\""
    show bg towernight2
    with slowdissolve
    $ Pause(0.5)
    c "\"They were yells that, in reality, nobody ever heard. At {time=21:04}, the police entered the building.{w} Even though everyone was alive, Suripo was dead on the floor. The officers could hardly believe their eyes while the survivors emerged.\""
    $ Pause(0.5)
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg towernight
    with dissolve
    $ Pause(0.5)
    c "So, let's put together a plausible set of events."
    show bg entrance25
    with dissolve
    c "In world C, Naomi wasn't actually dead. The loud motion of the shutter woke her up at {time=21:04}, but in this imaginary world, Erina's and Isla's yells did so ahead of time."
    show bg hallwayc19off
    with dissolve
    c "In a groggy state, she saw the killer finishing off Katei in hallway C, and the only thing she could do was dash at them and use their own weapon to seek instant vengeance."
    show bg towernight
    with dissolve
    c "Naomi roamed around the tower and witnessed the five other corpses, the scent of blood mingling with the smell of the Sekimeiya to create an odor unlike anything she'd ever smelled before. When she entered the event room, the Future Sekimeiya, which Katei had activated, had already powered back on. She ran to it to put it inside its cabinet, but she traveled to the future the moment she contacted the gemstone."
    show bg towernight2
    with dissolve
    c "When the police entered the building, no one was alive inside until Naomi reappeared. Everyone had been killed by someone else. The killer hadn't escaped through the storeroom or to another world. Everyone who had died was killed by someone from their own world. Every single person who had gotten trapped in the morning was attacked by another person—even Naomi, who was attacked and severely injured in world A by Akaro."
    nvl clear
    with dissolve
    c "This seems to answer most questions, but of course, what about all the other murders? What happened before Naomi's reawakening?"
    c "The truth is something that wouldn't be theorized even once by the police or anyone who dared tackle the case. In their world, that is."
    show bg sekimeiyaroom20
    nvl clear
    with dissolve
    c "You know about the time where everyone waited in the event room, calmly spending the last few minutes of the day-long countdown. No one present had any idea of what it had taken for that young, red-haired girl to be sitting there against a wall, staring indifferently at the walls and approaching her long-awaited release."
    c "At that time, the thought of killing anyone was nowhere in her mind, and that didn't change when an impulse drew her out of the room. It was all she could do to obstruct the predictions that a mysterious Atsuki had made, but she had no intention to go any further than that. She had already abandoned the thoughts of death."
    c "After all, she had already killed once. In world A, she had killed Erina, and repeating that act was not something she had even considered. While waiting in the event room, most of Miiya's thoughts were directed to her own well-being. The sight of the camera and not knowing whether her action had been recorded unnerved her."
    c "So that begs the question that everyone would ask themselves. What drove someone to kill that many times mere minutes before their release? Completely ignorant to what she was doing, the moment Miiya rushed out of the event room, she created a world with only one survivor."    
    return

label tip_early:
    $ SpriteTint("dark")
    show bg outside2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In this world, the shutter seems to unlock a few minutes before {time=21}, but that's merely a misunderstanding with Sai's wristwatch."
    show bg thinking
    show sail 1b thinking
    with dissolve
    c "Earlier in the day, Sai traveled to the future alongside Atsuki. However, both of them thought they had traveled to the past, so Sai never believed that the time on his watch was incorrect."
    c "It was several minutes ahead of the real time, but the computer had stopped working, and when they world switched to A, the security room was locked. The first time he thought that it might've been wrong was when he heard the shutter opening."
    return

label tip_larles:
    show bg outside1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Suripo speaks with Larles, a seemingly idiosyncratic individual who was ushered away in the commotion. Though, not by a phone call, like she claimed."
    c "Observers witnessing her were quick to spot something like a second set of arms rummaging in her coat, but most brushed it off as cosplay. There were no records regarding her existence anywhere on Earth."
    c "From the Doctor Who spin-off \"Cwej: The Series\". As per Kickstarter reward: Cameo Scene."
    return

label tip_three:
    show bg towernight2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The initial reports say that three people are missing, but the real number is four: Atsuki, Erina, Sai, and Akaro. The reason behind this misunderstanding is Naomi A's body."
    c "The police believed that at least eight people had been trapped, so when they found four dead bodies and Shiroya, they thought that only three people were unaccounted for."
    c "Two of the dead bodies belonged to Naomi, so with a little more investigation, those numbers would be doubted."      
    return

label tip_roof:
    show bg snow13
    $ Snow(1, fast=True)
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki tells Shiroya to appear below a stone roof, but he doesn't have enough time to fully explain why."
    c "If Shiroya had appeared wide in the open, her body would've collided with the falling snow, but that's not all. The roof would've been needed even if no snow had been falling at the moment she appeared."
    show bg footprints
    with dissolve
    c "That's due to the snow on the ground. If there had been any, Shiroya's future location would've been slightly sunk into it, in her own footprints. Those would not yet have existed in the past, so Shiroya's feet would've collided with an even layer of snow, and she would have lost the bottom portions of her feet, bleeding profusely."
    return

label tip_c3:
    show bg cg1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The third chapter is called \"Peripheral\". The main story of this chapter happens outside of Ashiya Tower—it's the periphery of the story. Not only that, but its main goal resembles that of a computer peripheral."
    c "An external part of the computer essential for the entire machine to work. If Shiroya hadn't been there to relay the group from Chapter 1 to Chapter 5, the entire structure would've collapsed."
    c "Lastly, it references \"peripheral vision\", as this view is essential to solve the mysteries of this part of the story."
    c "Shiroya's narrow field of view prevented her from noticing the truth around her, but if she had widened it ever so slightly, she would've taken notice of everything she was missing. Similarly, if your approach for this chapter had been different, your perception of it would've changed drastically."
    return

label tip_bootstrap:
    show bg atticbedroom
    show saim 1a confused at p33
    show shiroyam 1ap1 upset at p13
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Sai and Shiroya appear in the right bedroom of the attic, but the reason for that seems to be that they appeared inside it. After all, that's what lets them stay there until the time of the future location."
    c "There are other instances where you might ask yourself similar questions. This seems like a paradox that appeared out of thin air."
    c "However, be certain that they all share something that makes them decipherable. There is no effect without a distinct cause."      
    return

label tip_ha:
    show bg fireworks
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Happy New Year!"
    return

label tip_demolition:
    show bg whitesky
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In this imaginary world... the real story converged with your request. Shiroya never returned to the tower on January 5th, leading to many changes."
    c "She wasn't there to save the lives of everyone who had activated a chain of future travels at the end of December 15th. Because she didn't go to the tower on January 5th, her future self didn't exist on December 15th; Shiroya wasn't there at the end of the day to prevent Atsuki from unplugging the cabinet. As a result, he ended up traveling to the future, and the two fake Sekimeiya the police put in the cabinet at {time=21} never ended up breaking."
    show bg snow92
    with dissolve
    c "On January 1st, when Atsuki found Shiroya, he ran behind her without thinking, causing the final accident that would forever change her life."
    c "At the scene, a police officer approached her to ask for her name. As he'd thought, she was one of the people who should've been in the tower on December 15th, so she was taken into a car."
    nvl clear
    show bg towernight2
    with dissolve
    c "The rest of the missing people, however, were not found, which eventually put an end to Ashiya's desperate claims."
    show bg whitesky
    nvl clear
    with dissolve
    c "Months passed. In this world, the storeroom's secret was never found—Katei had escaped in the morning, and the door was always unlocked. That's why Shiroya never attempted to reenter the tower once she was freed. Despite all of those changes, however, the chain of future travels still took place. You might be able to figure out why."
    $ Pause(0.5)
    show bg tv2
    nvl clear
    with dissolve
    c "And on October 4th, the tower was demolished, destroying the Future Sekimeiya. When the missing people appeared, their bodies collided with the fallen debris, killing them instantly. Days later, when the debris was being cleaned, the gruesome fate of the three missing people was finally known to all. Erina was discovered last, as she had appeared where the mechanical room had once been." 
    return

label tip_purse:
    $ SpriteTint("dark")
    show islam 1b surprised
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    $ ChartNode("islaa200")
    c "On December 15th, Isla A world switched to world B. There, she went many days into the past. When she touched the Sekimeiya, she was holding the purse she'd had in world A. Then, on November 24th, which purse did she appear with?"
    c "Interestingly, she appeared with the purse from world B.{w} It had the voice recorder inside, and there were no tickets for the event.{w} It's strange, though, isn't it? Why did she not appear with the purse from world A, which she'd been holding?"
    c "While the two Islas tried to keep her identity hidden, the purses were swapped. Before going to the tower, Erina realized the tickets they'd bought weren't in the purse's pocket, so they printed them again. That's how the purse with the recorder was brought to the tower."
    c "Meanwhile, Isla A was left home with the original purse from world B. Inside were the tickets that Erina B had originally printed, but before January 5th, Shiroya took them."
    c "That's why, when Isla A reentered the tower, she was holding the empty purse from world B. It's why, when she arrived in the past, the purse she had was world B's, and the recorder was inside."
    c "In other words, although two purses existed, they were the very same, as the Sekimeiya had joined them together."
    return

label tip_phone:
    show bg phone
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Shiroya's phone says \"No service\", and she's unable to connect to her mother when she attempts to call her. The reason is the existence of a duplicate phone of hers."
    $ SpriteTint("dark")
    show bg outside2
    show shiroya2l 1c deadpan clean bright at p23
    with dissolve
    c "In this world, when December 15th came to an end, Shiroya was the only person found in Ashiya Tower; she was the version of Shiroya that had saved Miiya in world C."
    show bg whitesky
    hide shiroya2l
    with dissolve
    $ SpriteTint("normal")
    c "Soon after being taken in by the police, she was released and went to temporarily live in Atsuki's house to take care of his pets. She reobtained the phone she had left outside the tower on the morning of the 15th, so when Shiroya's mother called her number, both her original and copied phone received the call."
    show bg phone
    with dissolve
    c "Depending on implementation, some phone services allow the use of the same phone number on multiple devices when notified beforehand. Shiroya's service provider noticed that two devices were receiving calls from the same source and terminated her phone's connection to prevent fraudulent use of the line, whether through her own fault or a third party's."
    c "Of course, they wouldn't terminate her service without notifying her by mail, but mail takes a few days to arrive."
    return

label tip_january:
    with dissolve
    $ pre_tip_song = renpy.music.get_playing(channel='music')
    $ pre_tip_bgm_name = store.bgm_name
    $ StopMusic(fadeout=3)
    $ Pause(4)
    window auto show
    with Dissolve(0.1)
    show bg atsukis3
    with dissolve
    $ Pause(1)
    $ PlayMusic("twodaysofrain", fadein=1)
    $ Pause(1)
    $ ChartNode("shiroyab300")
    c3s "...{w}Don't worry, he'll come back soon."
    $ Pause(1)
    $ SpriteTint("normal")
    i "...He didn't react. Maxi had been staring at me in silence for hours. It must have been strange for him to see me in Atsuki's house for so long."
    i "Much like him, all I could do was stare at the clock. January 1st was slowly coming to an end."
    i "After ignoring me, Maxi approached the front door."
    c3s "You'll get to see him again in just four days. Even if you went to look for him, you wouldn't find him anywhere right now."
    i "..."
    $ Pause(0.7)
    nvl clear
    with dissolve
    i "Because he was traveling to the future... It was insane to think about it so casually, but I was certain that Atsuki was nowhere in the world at that moment."
    i "Seventeen days had passed since December 15th. Before that, I'd been in Eagle Motel for fifteen days. That had been after spending five days in January, immediately after those initial twelve hours..."
    i "I was confident I was finally at the exit of the sprawling labyrinth, and during the past few days, I'd had a lot of time to ruminate on many of the things that had happened."
    n "That time I entered the tower from the storeroom, after spending hours in front of the tower and under the unchanging sky... That'll happen in four days."
    i "Most of my thoughts had been directed to the brief interlude where I'd been in January by myself. Atsuki had told me that I'd gone to the future instead of the past, but that was all the information I had from him."
    nvl clear
    with dissolve
    show overlay_flashback onlayer master_overlay
    show bg tunnel
    with dissolve
    n "I touched the Sekimeiya in the bathroom and appeared under the gem shop. I first thought that I'd gone to November because I accessed the date settings on my phone and read November 30th. The time was {time=21:10.}"
    n "I realized something important a while ago. My phone was from November 30th. Not only that, but I was wearing the clothes from that day, and my whole body was wracked with pain because it had just fallen from the shop. However, I appeared on December 30th."
    n "And not on December 31st—on December 30th. Even though I heard fireworks welcoming the new year when I went home, I don't think I appeared in the past just a few hours earlier. After reading {time=21:10} and November 30th on my phone, I fell unconscious, and when I woke up, I felt as if I'd been there for an eternity. But according to the time, it had been less than half an hour.{w} There's no way. I was there for over a day. The body I'd appeared in had just fallen through the shop's floor, and I was unconscious until the next day, when I went home. I dreamed about many parts of my life for so long..."
    nvl clear
    with dissolve
    n "November 30th and December 30th are both fifteen days apart from December 15th. On December 30th, the body I appeared in was the one from November 30th, which is why my phone displayed that date. That's how Atsuki said the Sekimeiya worked.{w} In the bathroom, I touched the Sekimeiya at about {time=20:30.} Since the body I appeared in was from November 30th at {time=21:00}, what that must mean is that the real time on December 30th was {time=20:00.} The time on my phone was always about one hour ahead."
    n "I remember when I first woke up underground. As opposed to every other time, instead of instantly appearing there, I woke up, as if something had been in between my travel and my awakening."
    n "I don't think I fully understand yet how the Sekimeiya functioned, but I might know why this happened. In this case, the body that was replicated was from after I'd fallen through the gem shop's floor. That means that it was already in a coma. When my future consciousness was placed within it, my body woke up."
    show bg cg1
    nvl clear
    with dissolve
    n "I've had time to notice a few things I didn't realize at the time. When I walked out of that tunnel, no snow was falling—it was not November 30th. The moon phase that I saw didn't match with that day either."
    show bg snow13
    with dissolve
    n "I was really tired, so I don't know if that contributed to everything that I missed, but my first destination was the gem shop where I thought I'd just been. I saw the owner there, who might've been handling the repairs of his store or something, but I only recognized him when I saw his face...{w} because he was no longer wearing the shirt from that day, which had the shop's logo on both sides."
    nvl clear
    show bg c3entrance
    with dissolve
    n "So I just went home, where everything looked like it had on November 30th. That's because after waking up from the coma, I was only there for one day before going to live with Atsuki."
    show bg bedroomnight1
    with dissolve
    n "I thought I had two weeks to change the past, and being free in those icy streets had made for an immense contrast."
    show bg fireworks
    with dissolve
    n "I fell asleep in no time, but I was woken up by the sound of fireworks. Although my phone displayed {time=1}, midnight had just hit, and the fireworks were marking the start of the new year. ...I saw them again last night, once more by myself."
    n "It was 2012. My past self wasn't in a coma, and Atsuki wasn't secluded in his house. However, those beliefs let me feel temporarily at peace."
    show bg whitesky
    with dissolve
    n "The next day was today. I didn't even think that the cereal bars I'd brought to Atsuki's house should've still been in the kitchen. I just ate some mixed nuts and went outside, where I ended up at Ina Café after wandering through the white streets."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg ina
    with dissolve
    d "Hello."
    i "He suddenly turned around."
    show darfeem 1b smile at p11
    with fastdissolve
    d "Ha—"
    show darfeem 1b surprised at p11
    with fastdissolve
    d "Shiroya...!"
    c3s "Yeah. It's been a while."
    show darfeem 1a surprised at p11
    with fastdissolve
    d "Oh my God! Y-You're all right!"
    c3s "...So you know what happened. I am, yes."
    show darfeem 1a concern at p11
    with fastdissolve
    d "Of course! You were in the news!"
    i "\"I managed a bitter smile in response to his relieved expression.\""
    n "He wasn't talking about the incident on November 30th... He was talking about the attack that had taken place in Ashiya Tower; the news about it reached everywhere."
    show darfeem 1a smile at p11
    with fastdissolve
    d "I'm so glad you were released so quickly! How are you?"
    c3s "I'm okay. I was released yesterday. Fortunately, nothing major happened to me." 
    $ Pause(0.3)
    nvl clear
    show bg towernight2
    hide darfeem
    with dissolve
    n "At {time=21}, a team of policemen raided the building, and they only found me. I was thoroughly interrogated, but they released me pretty quickly."
    show bg ina
    show darfeem 1a smile at p11
    with dissolve
    d "That's really good to hear. If you came to relax and try to forget about it, we don't have to talk about it."
    c3s "...It's fine. You don't have to worry."
    show darfeem 1a concern at p11
    with fastdissolve
    d "Are you sure? I can't imagine what it must be like to lose someone close to you at your age. I'm so sorry."
    n "Darfee knew that Atsuki hadn't been found when the tower unlocked. I've read many of the articles that reported the news, and due to all the deaths and the impossibility that the missing people escaped, the worst was assumed by almost everyone."
    c3s "...{w}Thank you."
    d "Do you have any idea what happened? A lot of details weren't published." 
    c3s "Unfortunately, no. It all happened suddenly, and we were just caught up in it."
    i "\"He looked down, very clearly pitying me.\""
    nvl clear
    with dissolve
    $ Pause(0.5)
    hide darfeem
    with fastdissolve
    n "As I was drinking my coffee, I saw a newspaper close to me."
    show bg abc
    with dissolve
    n "It was the latest Yushinews edition. Naturally, the first thing I did was look at the date.{w} It said 12-01..."
    n "...{w}The Japanese date format is year-month-day, but I approached the newspaper intending to read the day's date. It didn't come to mind that Yushinews is a monthly newspaper."
    #to be fair this doesn't work that well because the japanese always have the symbols for year/month/day after the numbers
    n "I saw 12-01: 2012-January, as it was that month's edition. Instead, I interpreted it as December 1st."
    n "And when I flipped back the pages, I ended up at the \"November\" section. In chronological order, every edition begins with the previous month's most important news. That's where I read about the gas explosion and the escape from a prison cell."
    $ Pause(0.4)
    show bg ina
    show darfeem 1b smile at p11
    with dissolve
    n "Before leaving, Darfee told me that it was Sunday. It was the truth, and it was an immense contradiction with what I believed...{w} That even made me think later that Miiya had died on a Saturday, which wasn't the case. After waking up in the hospital, I spent the days secluded from the world, and the case wasn't too different before November 30th. The days of the week meant nothing to me at the time."
    nvl clear
    show bg snow28
    hide darfeem
    with dissolve
    n "On the way back, I ended up next to this house. Silently, I walked to the gate and looked up, where I saw light behind a window."
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    i "...I looked up at the ceiling light. I'd been living at Atsuki's house since I'd been released by the police so that I could take care of his pets."
    c3s "You saw me outside this morning, right?"
    $ Pause(0.4)
    i "Maxi didn't react to my question, but I knew he hadn't been in the living room for most of the day. I recalled the moment I'd seen him by the gate, long ago."
    show overlay_flashback onlayer master_overlay
    show bg snow28
    with dissolve
    i "\"I got startled as soon as I peeked through the bars of his front gate. I hadn't seen Maxi sitting in front of the wooden door, where there was no snow.\""
    i "\"He seemed afraid for an instant when he saw me, but then he ran to me, squeezing his head through the bars.\""
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    c3s "Did seeing me scare you? You knew I was here, so it must've looked like I teleported out."
    n "Curious to see me outside, he approached the gate but couldn't stop me from leaving. I found him waiting by the door, which is all he's done since I started living here. I think he's just waiting for Atsuki to come back."
    $ Pause(0.5)
    nvl clear
    with dissolve
    show bg snow85
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "After that, I walked to my apartment. I noticed that people were looking at me, and I don't think that was just my imagination. One of the reasons I've stayed here is because most people recognize me as the only survivor of the 15th."
    show bg daylightonemptytable
    with dissolve
    n "...When I got home, I decided to change the past by calling my mom."
    ns "Shiroya...! How are you!?{w} I'm so glad you called! We were so worried!"
    ns "Hello...! Are you there? What happened? You're okay, right?"
    n "I didn't want to speak, so I cut the line, my mom's voice leaving me still. Immediately, my phone received a call from her, which I waited out.{w} After that, it took a while until I received another one, but that was the last time she called me."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    i "I knew what had happened. Earlier that day, I had finally talked to my mom, calming her down.{w} When the police had released me, the phone I'd left outside the tower on the 15th had been returned to me. In the future, when my mother had called me, both existing phones had received the call, and I'd picked it up from Atsuki's house."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg daylightonwithmeat
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "After going over all that I'd experienced, I cooked a slice of meat. It was disgusting. I can't believe I didn't realize it tasted awful due to being in the fridge for more than a month."
    show bg livingroomceiling
    with dissolve
    n "And when the sun began to set, my phone showed {time=18.} Strangely, I was exhausted, so I didn't wait long before going to bed."
    nvl clear
    with dissolve
    $ Pause(0.7)
    show bg bedroomday3
    with dissolve
    n "I woke up tomorrow, on January 2nd."
    show bg phone
    with dissolve
    n "That's when I found that thread from November 24th, long since locked.{w} I was so close to discovering the truth there. I wanted to find the first ever mention of the word \"Sekimeiya\" to learn where it had been before Ashiya's announcement, so I sorted the results by oldest first. That made me miss all the articles reporting on what had happened on the 15th."       
    n "...But thanks to an attached picture, I was still able to reach Vaisude's apartment."
    show bg whitesky
    with dissolve
    n "On the way, I saw that there was no light behind the windows in Ashiya Tower. It made sense to me because Katei had said that nobody had been recently working on the office floors, but that was a mistake, since they were lit up on the 15th."
    show vaisudel clean 1a smile
    show bg vaisude2
    with dissolve
    n "It had been more than a month since Vaisude had traveled to the past. He would go live with his parents, where he had appeared on the 24th of November..."
    n "And I, the only person to have been found in the tower, visited him. He thought it was due to his forum thread, and he was surprised when I left without saying a word."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg snow87
    hide vaisudel
    with dissolve
    n "Outside, I constantly felt eyes on me. What did Yushibana know about me? Slowly, I walked to its outskirts."
    show bg snow36
    with dissolve
    n "Next to my school, everything was silent. No classes were happening on a Monday, as it was during the winter holidays."
    show bg snow43
    with dissolve
    n "...And that's where I felt a presence behind me—where I saw footprints running away."
    n "Who was it? That's something I'm not sure of yet. Who would've followed me in January? It could've been anyone who knew I was the only survivor of the attack."
    show bg tableemptydaylightoff
    with dissolve
    n "But thankfully, nothing happened to me. I went home and tried to loosen up by cooking the food I'd bought.{w} Later that day, I received a call from an unknown number. Remembering the words Vaisude and I exchanged is pretty interesting."
    nvl clear
    with dissolve
    show bg daylightoffemptytable
    with dissolve
    c3s "...Hello?"
    v "O-Oh, you picked up. Good.{w} Hey there.{w} Are you Shiroya...?"
    c3s "Huh? Yes. ...Who are you?"
    v "You were at my place earlier, remember? My name's Vaisude.{w} I just need to ask this first. You were in Ashiya Tower during the terrorist attack on December 15th, right?" 
    c3s "...{w}December 15th? What are you talking about?"
    v "Wh-What? You know all about it, right? That's why you came to my place."
    c3s "...{w}I do, yeah. I was there."
    v "I see. I knew I wasn't wrong."
    n "Both of us referred to the 15th like it had already happened, and I thought it was because we had traveled to the past from that day, not because I was in the future..."
    nvl clear
    with dissolve
    v "There's a reason why I'm calling you. ...I don't know how this will sound, though."
    c3s "...What is it?"
    v "...Do you know... what I experienced? You read my thread from November, didn't you? That's how you found my apartment."
    c3s "What did you experience?"
    v "Exactly what I wrote about...! From the 15th of December, I suddenly appeared on the 24th of November!"
    c3s "...I see. You're right. I also traveled back in time."
    v "Wh— R-Really...!? So that is what happened! How, though!?{w} A lot more people had to have come with me, right?{w} Then what will happen in two weeks? Do you think it will repeat?"
    c3s "It's very possible, but I'm not sure everything will be identical."
    v "Yeah, that wouldn't make sense. I have no idea how it'll come to occur, but it'll happen again. People will travel to the past. I can't believe it."
    c3s "...I'm as confused as you are."
    nvl clear
    with dissolve
    n "\"Then what will happen in two weeks? Do you think it will repeat?\" I'm pretty sure I know why he said that."
    n "On the 15th, the dead bodies were found by the police, and in Isla's purse, the voice recorder we played was found too."
    n "Its contents were summarized publicly, and I've read speculation regarding what it all means. Most people ignored the recording because it stated that the shutter wouldn't unlock when it clearly did."
    n "But Vaisude must have known not to dismiss it—something else was hidden behind that audio. So, on January 2nd, something was still set to happen within two weeks. Perhaps the incident would repeat and someone would go to the past again to leave the recorder on December 15th."
    n "...The conversation between the two of us kept going and going, but neither of us realized how different the other's perspective was."
    nvl clear
    with dissolve
    $ Pause(1)
    show bg bedroomnight4
    with dissolve
    n "I woke up pretty early on January 3rd. My phone showed {time=7:45}, but no light was making it through the gaps in the blinds."
    show bg snow84
    $ Snow(1, fast=True)
    with dissolve
    n "I felt the need to go out again, and when I opened the front door, I saw the sun rising from behind the mountains. ...It was an hour earlier than I thought, and light snow was starting to fall."
    show bg snow46-5
    $ RandomizeSnow()
    with dissolve
    n "That was the reason behind that foggy and soulless Yushibana. It culminated when I saw Ina Café closed, but when it was really {time=7:30}, the shutter rose."
    nvl clear
    show bg ina3
    $ Snow(0, fast=True)
    show darfeem 1a neutral at p33
    with dissolve
    d "So what have you been doing these last couple of days?"
    c3s "...{w}Not much. I went to Atsuki's house yesterday, and I was there for a while."
    show darfeem 1a concern at p33
    with fastdissolve
    d "Atsuki's house? You think being there helps you?"
    c3s "...I think so, yeah."
    d "I see."
    show bg ina4
    hide darfeem
    with dissolve
    n "I could finally rest inside, and I did so for longer than I'd expected. I was only drawn out hours later when I saw someone I recognized in the distance."
    show bg snow87
    $ Snow(1, fast=True)
    with dissolve
    n "It was Isla's friend, the Isla from the world I later ended up in. She had traveled from December 15th to November 24th, and for her, it had been a very long time since nobody had come back from the tower."
    show bg snow73
    $ RandomizeSnow()
    with dissolve
    n "I followed her footprints up to her house, but I wasn't yet certain I wanted to change the past. When I felt a presence watching behind me again, I distanced myself from that place."
    show bg cg1-4
    $ Snow(2, fast=True)
    with dissolve
    n "And I ended up high on that mountain, where I finally made the decision to change the past and do all I could to save everyone."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg snow80
    $ RandomizeSnow()
    with dissolve
    n "On the way back, I felt like the same person was following me, and that time, the police were ready to intercept them."
    n "...{w}Hm, thinking about it, I might actually be able to find out who it was."
    show bg snow90
    $ RandomizeSnow()
    with dissolve
    c3s "S-Sorry, did you just arrest someone?"
    ns "Hm? Yes. What's the matter?"
    c3s "I... was feeling like someone was following me just now. Could it have been this person?"
    i "\"The man frowned and took out a tiny scrapbook."
    nvl clear
    with dissolve
    ns "What's your name?"
    c3s "Mine...?{w} ...It's Shiroya Mirana."
    i "\"He looked at me and silently wrote on the paper.{w} Then, he suddenly smiled, completely shifting his expression.\""
    ns "I see. You can stop worrying, then. If you think you were being followed, there's nothing to be afraid of."
    n "At the time, I thought his smile was a bit strange, but he also recognized me as the only survivor. He had just caught the person believed to be behind the attack, so he told me that I could stop worrying."
    nvl clear
    with dissolve
    $ Pause(0.5)
    show bg atsukis3
    $ Snow(0, fast=True)
    hide overlay_flashback onlayer master_overlay
    with dissolve
    n "There's a reason why the police released me without further complications. Right now, there's one person believed to have orchestrated the attack—Akaro, even though the police haven't released his name.{w} That's because a recording was found on the computer in the tower, one which showed Akaro's and Katei's movements during the time the smoke was released. Before {time=21}, Atsuki saved that recording on the computer. He brought it from the world where Miiya was saved."
    #i say the police haven't released akaro's name so that it makes more sense he's still wandering around the town and hasn't escaped
    n "So, if the police believed they had caught a Xyn member, what's most likely is that it was Akaro.{w} I guess that's not all, though."
    n "Atsuki also told me that after Sai and Akaro escaped from the bedroom in the attic, Akaro traveled to the future and appeared on January 5th. He couldn't have been following me on January 3rd.{w} Rather, what it means is that it was the other Akaro. The one who killed me in another world and then arrived in ours with Isla."
    $ Pause(0.4)
    nvl clear
    with dissolve
    n "I traveled fifteen days to the future and appeared in the location where I'd been fifteen days in the past. The rule should be the opposite when you travel to the past. Vaisude appeared in his parents' house on November 24th, and by that amount of time in the future, he moved out to go live with them."
    n "That's gotta be why that Akaro appeared in a cell on November 24th. He would be caught by the police on January 3rd and put in a prison cell. In November, the cell was vacant and unlocked, so he was able to walk right out of it. That's why the image looked the same as in the article when I saw the cell on TV."
    nvl clear
    with dissolve
    $ Pause(0.7)
    show bg snow79-2
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "When the evening of the 3rd came, I stepped out of my apartment again. The place I went to had been constantly in my mind, as it was essential to construct the future I wanted."
    show bg lottery
    with dissolve
    c3s "I came a while ago, but I'd forgotten to check if I'd won anything until now.{w} The number I had was for December 1st, I believe. I wonder, by the way, how long would it be valid for?"
    ns "Oh, it's still valid, don't worry. They last a whole year.{w} Anyway, December 1st? Let me see."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    n "30-05-12-31-15-26. Bonus 24. I still remember it."
    i "There was a small piece of paper on the table containing those numbers. I had bought it in the other world before going to Eagle Motel. However, the winning number had been different."
    i "But that didn't matter. Even though it had been bought in another world, it was immensely valuable in the one I was in."
    nvl clear
    with dissolve
    $ Pause(1.0)
    show bg daylightoffemptytable
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "January 4th was the final day I'd set for myself. It didn't matter anymore, but I did the laundry to pass the time."
    show bg bedroomday1
    with dissolve
    n "I noticed that my favorite blue hoodie was missing. It was among the clothing I'd brought to Atsuki's house on December 9th.{w} Similarly, a shirt that brought bad memories and which I thought I'd left out of the washer was in the bucket. There were two versions of it, as it was the shirt I'd worn on November 30th, and I left it there both on December 8th and on January 1st."
    show bg whitesky2
    with dissolve
    n "...I didn't want to spend the whole day at home, so I went to Ina again."
    nvl clear
    show bg ina2
    with dissolve
    n "That's where I learned that a Xyn member had been arrested for the first time. The latest edition of Yushinews was still there, and it would stay there for the rest of the month."
    n "The news said that the identity of the person they caught was unknown. I wonder if Akaro wasn't his real name..."
    show darfeem 1a concern at p44
    with fastdissolve
    d "Are you thinking about the news?"
    i "\"Darfee addressed me after I'd been in thought for a few minutes.\""
    c3s "A bit. It just threw me off."
    show darfeem 1a neutral at p44
    with fastdissolve
    d "I see. Well, it's good that someone from that group finally got caught."
    c3s "Yeah, I agree."
    nvl clear
    with dissolve
    $ Pause(0.5)    
    c3s "...Do you know about the Sekimeiya?"
    show darfeem 1a confused at p44
    with fastdissolve
    d "Huh? ...What do you mean?"
    c3s "Ashiya's event."
    d "Hm? Yeah, of course."
    c3s "Well, nobody stole the Sekimeiya, right...?"
    show darfeem 1a confused at p44
    with fastdissolve
    d "The Sekimeiya...? N-No. ...As far as I know, at least."
    c3s "All right, I just wanted to make sure since I haven't been paying attention to the news."
    nvl clear
    with dissolve
    $ Pause(0.4)
    hide darfeem
    show bg ina6
    with dissolve
    n "From my perspective, what it all meant was that the past had changed, so I could go to Atsuki's house and prevent him from going to the tower in case something happened to me."
    show bg snow88
    with dissolve
    n "I had to wait for him to leave, which would never happen. As I waited, I realized that I could go back to Isla's house in the meantime."
    show bg snow77
    with dissolve
    n "When I rang the bell, nobody opened the door, and after knocking for some time, I noticed the door wasn't locked."
    n "I'm just speculating, but when Isla traveled from December 15th to November 24th, it's likely she didn't appear with the keys to her house. Since Erina never came back from the tower, Isla would've had to keep the door unlocked when she left so that she could get back in."
    nvl clear
    show bg islasentrance2
    with dissolve
    n "Inside the house, I immediately found her purse. I took two tickets for the event on the 15th, which is pretty strange...{w} because if that was the purse of the Isla who'd traveled from the 15th, I'm not sure why the tickets would've been inside it."
    hide overlay_flashback onlayer master_overlay
    show bg atsukis3
    with dissolve
    n "...The recording was real. On January 5th, everyone who's currently traveling to the future will make it happen.{w} But what about Isla? She'll be there too, and she's not currently traveling through time. ...The Isla from this world died in the cabinet, and the other Isla should currently be alone in her house."
    n "How will that Isla end up inside the tower on January 5th—the exact day that everyone will awaken? I can only think of one thing."
    n "After taking both tickets from her purse, I walked back home. Even though I didn't see anyone, Isla might have been careful about her situation. Maybe she noticed the strange footprints that went in and out of her house."
    n "If she did, and retraced them to my apartment, she had the chance to follow my footprints all the way to the tower. I entered through the storeroom and left the door open, so that's one way she could've been there on the 5th."
    nvl clear
    with dissolve
    n "...That Isla traveled from December 15th to November 24th. She went 21 days to the past.{w} 21 days after December 15th is January 5th. So her location upon appearing on November 24th may have been from January 5th."
    n "If that's correct, it might be how the voice recorder went to the past, although I don't really know any details. What's strange is that if Isla appeared with the recorder on November 24th, the Isla from this world shouldn't have had it in her purse on the 15th."
    n "An answer that explains two questions at once is that the purses were switched at some point before the 15th. That could be why the recorder ended up in the tower and why the tickets were still inside Isla's purse on January 4th.{w} If that's what happened, before going to the tower on December 15th, Isla or Erina must have realized that the tickets were no longer in the lower pocket of the purse and had to print them again."
    nvl clear
    with dissolve
    $ Pause(1.0)
    show bg nightlightoff
    show overlay_flashback onlayer master_overlay
    with dissolve
    n "Back home, I felt the time rapidly passing. I had no idea what would happen the next day, when I would finally visit the tower."
    n "My thoughts were racing, I couldn't get to sleep, and suddenly it was deep in the night. Eventually, it was clear I was just going to stay awake, so I had the thought of leaving anyway because the tower was supposed to open early. I never turned off the heater before leaving, and I never made the connection that it hadn't been turned on when it was December 8th. I'll have to go turn it off on the 5th so I don't waste power."
    show bg outside5
    with dissolve
    n "Anyway, when I arrived, the tower was locked, and nobody seemed to be there."
    show bg streetlight2
    with dissolve
    n "I really thought that the world had stopped moving. For a moment, I believed I would die there."
    n "The tower wouldn't open. It hadn't opened once since December 15th. The time discrepancy with my phone's clock was what made me think that the day wasn't starting."
    n "Something that added to the illusion was my phone saying \"No service\". I'm still not sure what the cause of that was, but the cold definitely didn't let me think properly. The ground in front of the tower was buried in snow, too. Ashiya hadn't been maintaining the plaza like they tended to do."
    nvl clear
    show bg outside7
    with dissolve
    n "I knew the secret of the building, though. I knew that a door probably existed in its left wall, and after feeling around carefully, I found it."
    n "I opened it just by pushing it lightly, which meant that it wasn't locked. I even saw that the handle inside was already taken off."
    n "I bet the door was actually locked on the 15th due to how easily it opened in January. When the police interrogated me, they inquired about that secret area since they had found it open from the inside. They told me that they picked the lock and confirmed the door was really another exit."
    n "Of course, since they didn't have the rusty key, they didn't lock the door again. That's why it was still unlocked on January 5th and not even properly closed. I got it to open just by putting my hand on it."
    nvl clear
    show bg black
    with dissolve
    n "I entered the tower, which was as dark and cold as the outside world, its temperature no longer regulated for visitors. When I set foot in hallway A, I saw the green lights on the cameras. They were still recording.{w} But it's okay—I don't think it mattered. I was in the hallways, security room, lobby, mechanical room, and event room—all places that should've still been covered with smoke or that didn't have cameras in the first place."
    show bg securityroom20
    with dissolve
    n "In the security room, I found Katei's rusty key. His body had already been taken away by the police, and I thought the room was all messy, as if someone had tried to find something."
    show bg black
    with dissolve
    n "Then, above the breakers, I found the attic and Sekimeiya cabinet keys... And not only that."
    nvl clear
    with dissolve
    i "\"I tried to move, but the obstacles in the room didn't make it easy. Could the cabinet have been there? While it seemed like a good place, neither the lobby nor the mechanical room had cameras.\""
    i "\"There were chairs and tables on the floor, so I had to move some aside to get to every part of the room. Even though it was impossible for anyone to be there, I kept trying to be silent and failing as I scattered things that I couldn't see.\""
    n "According to Atsuki, the Sekimeiya that sent us to the future was there. While searching for the cabinet, I moved it accidentally, which stopped the chain of travels and made everyone arrive on that day."
    nvl clear
    with dissolve
    show bg entrance32
    with dissolve
    n "As I was walking to the event room, I saw the reception desk lights flickering in the lobby. I turned around because I felt a presence behind me, and I don't think that was just paranoia."
    n "It had to be Atsuki. He had to be there too since both of us traveled back to the 15th when I touched the Sekimeiya."
    show bg sekimeiyaroom19
    with dissolve
    n "I moved to the event room and felt that it was much colder than the rest of the building. The cabinet wasn't closed..."
    show bg towernight2
    with dissolve
    n "When the police entered the building on the 15th, only the Sekimeiya that sent us to the past was in the cabinet. Ashiya said that the Sekimeiya weren't stolen, which means that the police found another one and put it in the cabinet. Of course, it wasn't the one in the mechanical room..."
    n "I remember the rush they were in when they found me. What must have happened is that they didn't close the cabinet, so on January 5th, that Sekimeiya had been gathering energy at an incredibly slow rate. That's why I was able to activate it inside the cabinet."
    show bg sekimeiyaroom19
    with dissolve
    n "But I'm not exactly sure how everything came to happen. There was something else in the cabinet, and I activated the alarm out of nowhere... What matters is that Atsuki and I returned to December 15th."
    nvl clear
    with dissolve
    $ Pause(0.9)
    show bg atsukis3
    hide overlay_flashback onlayer master_overlay
    with dissolve
    i "That was all the time I'd lived in January. The second coming of January 5th was the light at the end of a long tunnel."
    i "I looked at the clock and saw that I was close to entering the second day of the year. After a long yawn, I stood up from the couch. I'd been sleeping in the guest room, just like before the 15th."
    i "I had been there all day, and my body felt weak. As soon as I stood, I noticed a weight in one of my pockets."
    i "I reached my hand inside and took out a rusty key. There was one final use left for it, scheduled to happen in just three days. I gripped it tightly, ready to finally exit the labyrinth that we'd long ago been entrapped by."
    $ Pause(0.8)
    $ StopMusic(fadeout=5)
    nvl clear
    show bg black
    with slowdissolve
    $ Pause(1.5)
    $ Pause(6)
    $ renpy.music.play(pre_tip_song, channel='music', fadein=2)
    $ store.bgm_name = pre_tip_bgm_name
    return

label tip_keys:
    show bg mechanical
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "In January, above the breakers, Shiroya finds the attic and Sekimeiya cabinet keys. Why were they there on January 5th, though?"
    show bg atticdoor
    show overlay_flashback onlayer master_overlay
    show saim 1b neutral smoke at p11
    show erinam 1d worried blood at p13
    with dissolve
    c "\"Wait, no. You're definitely lying.\""
    c "\"Me? I don't ever lie.\""
    c "\"You don't have any key on you. That proves you hid them, because you should have the cabinet key.\""
    c "...They were the keys that Sai had hidden after locking Shiroya in the attic's bedroom."     
    return

label tip_card:
    show bg towernight2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "At the end of December 15th, as soon as the shutter unlocked, the police were struck by a very strong smell. There, they saw an unidentifiable gas in the air as its source. It was the lingering range of the Sekimeiya.{w} When they raided the building with protective masks, a sole Sekimeiya was in the cabinet: the Past Sekimeiya. They knew another one had to be found, so they searched until one of the two fake Sekimeiya that existed was spotted in the attic.{w} They put it in the cabinet, but they were in a rush. That's why the glass wasn't properly closed."
    c "As the days passed, the cold temperature led to the effect Xyn had designed: the fake Sekimeiya left behind a card with their name. However, their method also damaged the cabinet's interior."
    show bg sekimeiyaroom19
    nvl clear
    with dissolve
    c "...And when Shiroya tried to open the glass all the way, it had been stuck. As soon as she applied a bit of force, one of the triggers for the alarm went off. However, there was no one for it to alert. Nobody had expected it to go off ever again."
    #i have to say this (that the alarm doesn't reach the police nor ashiya on january 5th) or else the police would enter the building through the storeroom
    return

label tip_burn2:
    show shiroyal 4a smile2 at p25 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. The Sekimeiya was immensely hot, so the burn would not have faded by the time the future position took place."
    c "So then, why does Shiroya not appear with a burn mark when she travels from January 5th to December 15th? The number of days traveled is the same."
    c "There's a key difference that prevented a burn from appearing on Shiroya's finger, and it becomes apparent when you track her movements."
    c "After appearing on December 15th, Shiroya will spend many hours in world A until she arrives in world C and once again travels to the past. She will travel to November 30th to save Miiya in that world."
    c "For her to reach January 26th, almost two months will pass. That amount of time is what causes her to appear with no burn mark."
    return

label tip_fake:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Despite Sai's initial reaction to the attack being different in the three worlds, there's something he always did at the start: hide the fake Sekimeiya.{w} Doing that opposed Katei's and Akaro's intentions, as Sai was not yet aware that three different Sekimeiya existed. Although his motives were slightly different in each world, the main goal was always the same."
    c "In world B, Sai took the fake Sekimeiya from the cabinet and hid it in the storeroom, where no cameras recorded him. In world C, when the group was inspecting the office floors, everyone was suddenly separated. That gave Sai the perfect chance to do the same thing."
    c "In this world, A, Naomi C appeared before everyone. Unlike in the other worlds, she wanted to talk to Shiroya in addition to Akaro, as she had seen her world B self on the crystal floor separated from the group and wearing clothes from the attic—two versions of her existed at the same time, and Naomi, who had experienced time travel once, realized that Shiroya might have made contact with the Sekimeiya during the attack."
    c "The three of them didn't return, so eventually, everyone walked to the crystal floor. Sai hurried to the event room, and as he yelled about the Sekimeiya's disappearance, he put it in his hip pack. Soon after, he hid it in room A5, where Atsuki C would find it hours later."
    return

label tip_gan:
    show bg gemshop1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Akaro A says that one person was hospitalized, and he's referring to Atsuki. ...What about Gan, though?{w} The truth is that Gan was only sent to the hospital in world B."
    c "When Akaro A world switched to world B and then traveled to November 24th, he decided to walk away from Xyn's plan. He deeply regretted what he'd done in the tower, and he wished for history not to turn out the same way."
    c "He knew he was in the past—he possessed valuable information. One of the things he did was remove the storeroom's handle. However, the first action he took to alter history came days prior."
    c "On November 30th, he had accidentally killed a young girl. It was the perfect chance to prevent that."
    c "He knew that an explosion had occurred while everyone had been unconscious in the gem shop, so all he had to do was make sure that wouldn't repeat: he called Gan and told him to turn the heater off late on November 30th in order to prevent a disaster."
    c "Akaro was confident he had saved the girl—Gan had told him that he would turn off the gas. However, Akaro was unaware that Gan did no such thing. He didn't put any real stock in such a bizarre phone call."
    nvl clear
    show bg night3
    with dissolve
    c "Afterward, the Sekimeiya were found, and mere days later, it was November 30th. The way events unfolded in world B slightly differed from world A."
    show bg gemshop1
    with dissolve
    c "When Gan went to get the second Sekimeiya, he stopped himself in the middle of the shop. The moment he smelled the gas, the strange call came back to him."
    c "He glanced at the heater and approached it curiously just as dense smoke invaded the whole shop. He fell unconscious closer to the source of the explosion, so due to Akaro A's actions, Gan had to be sent to the hospital alongside Atsuki."
    return

label tip_burn4:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The Past Sekimeiya, which Atsuki touches, has been in the storeroom for numerous hours, so why is it that he doesn't have a burn mark on his finger when he world switches?"
    c "That's because of the temperature in the storeroom's secret corridor—the coldest place in the tower."
    c "When Atsuki touches the Sekimeiya, it has very little energy: the one with the massive range is in room A4, and it will remain undiscovered until June of 2012."
    return

label tip_disappearance:
    show bg japan
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Along with Atsuki, almost a third of Japan disappears from the face of the Earth. Not only that, but they never appear anywhere."
    c "In this world, when the police entered the tower at {time=21}, they found a real Sekimeiya and a fake. As instructed, they made sure both were kept cold."
    c "Atsuki was the only person they were able to find, and since that day, the tower spent many weeks abandoned. Each second that passed, the real Sekimeiya that hadn't been found kept gaining energy."
    c "The day that it was activated, its surface could've melted iron. The method through which that happened is a question of its own, but the effect became humanity's biggest mystery."
    c "The range had been increasing every day, and it ended up taking away a third of Japan's population. The other real Sekimeiya was still refrigerated, so no world switch occurred. Given that the people who vanished didn't reappear anywhere, which Sekimeiya was activated? Did everyone go to the past or to the future?"
    c "If they had gone millennia to the past, they would never have been able to exist in the future location, so they wouldn't have appeared anywhere. If they had gone millennia to the future, they wouldn't have existed in the proportional past, so they wouldn't have appeared anywhere."
    return

label tip_c4:
    show bg mountain4
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Calliants are the flowers that compose the flora of Airun's base. That is what this chapter is."
    c "The base of the mountain, which lets it build all the way to the peak. In addition, this chapter is more grounded than the others."
    c "Even though it's based on a real flower that can be found on snowy mountains, \"calliant\" is a made-up word."
    return

label tip_burn3:
    $ SpriteTint("dark")
    show bg thinking
    show islam 1a sleepy2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. ...Why, though?"
    c "This is one of the clearest indications of an elusive rule of the Sekimeiya."
    c "When someone traveled to the past, they were unable to keep feeling the pain of the burn they had noticed for an instant. The difference in Isla's case is the amount of time she traveled to the past."
    c "When she touched it, the Past Sekimeiya was immensely hot, so normally, a painful burn would've remained on her skin. The amount of days that it took her to reach January 5th from November 24th would not have gotten rid of it. That's why she appeared with it in the first place."
    nvl clear
    with dissolve
    c "In other words, the body she appeared in was that of one loop of her travel."
    c "When she reached January 5th, the burn she'd appeared with had healed considerably, but it was still visible. If that body of hers had been the one to appear on November 24th, an instant chain of infinite loops would've made it impossible for her burn to ever appear."
    c "Of course, that also means that she would've died instantly; she would've aged more than a month per loop and been unable to appear in November."
    c "Instead, she appeared in a body that had undergone a single loop. This behavior can be observed in a number of travels, and it's the answer behind one of the toughest questions Atsuki will face."
    return

label tip_injury:
    $ SpriteTint("dark")
    show bg thinking3
    show atsukil 1b pensive
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Why does Atsuki's injury disappear when he travels forty minutes to the past? That's not what happened the last time he traveled back in time after getting injured."
    c "The first reason is the amount of time it will take him to reach the future location. Even though it's minutes away, many weeks will pass until he returns to January 5th. That amount of time, enough for the injury to heal, is what makes him appear without it."
    c "However, there's another reason why his injury disappears, and it's unrelated to the amount of time that it will take him to return to January 5th. It's the same reason he doesn't appear with a burn mark when he travels all the way to November 24th, but that will be touched on a little later."       
    return

label tip_split:
    show bg sekimeiya
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Certain events in this story have a specific characteristic to them: their origin seems unclear."
    c "The handle of the storeroom's door has been taken off by Akaro A, but the means by which that happened are not straightforward."
    c "Akaro world switched to world B, and in the attic, he was told about the existence of the secret door. Afterward, he traveled to the past and removed the handle from that door. It could be said that he was told about the existence of the door because he had removed its handle."
    c "This is not the only instance where this seeming lack of causality takes place, so where exactly is it coming from?"
    $ Pause(0.3)
    nvl clear
    show bg mainmenu5
    with fade
    c "In world A, Akaro knew Xyn had been outsmarted. An alarm had trapped them in the tower, and the real Sekimeiya had vanished when he had woken up. Not only that, but he thought he had killed two people in order to bring his plan to success."
    c "He hated the way the world had turned out, but altering the reality he'd experienced wasn't possible. However, eventually, he world switched to world B.{w} Someone else originally from world A came with him: Isla."
    c "In world A, Isla never expected that an attack would take place in the tower. She followed the adults and hoped that everything would be resolved quickly. ...A lot of time passed, though, and at one point, her mother had been missing for a while after going to the bathroom."
    c "Isla couldn't bring herself to voice her worry, as that would've meant admitting that something could've happened to her mother. However, she regretted the way she'd acted; she wished she could've told Erina to stay with her."
    c "Akaro and Isla world switched to world B. As soon as they appeared in that world, they shaped it in a way they couldn't change their own."
    nvl clear
    with dissolve
    show bg mainmenu5-2
    with dissolve
    c "Atsuki and Shiroya B were able to save Miiya in world C, but didn't that only happen because she had already been saved?"
    c "This behavior of the world switch defined the relationship between the three worlds, instantly shaping three drastically different sets of events."
    c "And when a two-way world switch happened, someone was pulled backward in the order of switches. In those instances, both worlds balanced each other out accordingly. By working like this, the world switches led into the progression between the three worlds."
    nvl clear
    with dissolve
    c "In world A, only Atsuki made it to {time=21}, and he was accused of the murders that had taken place. Not a lot of time passed before a large portion of Japan suddenly disappeared forever."
    c "World B was a step up, but being between worlds A and C, it was filled with many bittersweet resolutions. Despite a few deaths, some people got out safely. Isla returned, but it wasn't the Isla who had died. Akaro was arrested, but it was the Akaro who most regretted what he'd done. Atsuki and Shiroya left happily, but they would never see Miiya again."
    c "World C existed thanks to world B. Everyone who was trapped got out alive. The people of that world faced numerous hardships, but they were all resolved. Naomi seemed to die, but she returned. Shiroya seemed to die, but she returned. Erina seemed to die, but she returned.{w} ...Then, why is it a world so close to world A?"
    c "A step was taken when world C was created, but what direction did it take? A bit more examination is needed to reach that answer."
    nvl clear
    with dissolve
    $ Pause(0.6)
    show bg mainmenu5-3
    with dissolve
    c "In any case, the labyrinth spawned by the world switches always operated under the inherent progression that it had created. Some people from world A ended up in world B. Some people from world B ended up in world C, but their world A selves pulled them back to world B. Some people from world C visited worlds A and B, but they were able to safely return to world C.{w} Thanks to the recording obtained in world C, Akaro A was arrested in world B. Atsuki A was the only person from his world to momentarily reach world C, but he dropped all the way back to world A when his elevator ride to the top vanished out of nowhere, the exact moment Shiroya B traveled to November to make world C the world it was..."
    c "The labyrinth never stopped spinning, and somewhere, it hid the peak that everyone wanted to reach. There's only one place where it would not have moved."
    $ Pause(0.5)
    return

label tip_saielevator:
    show bg thinking
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "I hope you had enough time to think about this mystery.{w} As you might have guessed, the Past Sekimeiya was involved."
    c "Sai traveled to the past and appeared in the locked elevator. Before asking \"why\", though, it's necessary to ask \"how\". Without the Sekimeiya, in the future location of Sai's travel, he wouldn't have been able to enter the elevator. Hence, traveling to the past and appearing inside it seems impossible."
    c "As long as the past and future states align and the events in between are possible, many elaborate setups can be created."
    $ explanation=True
    show bg chart_saielev1
    nvl clear
    with dissolve
    c "Consider this chart depicting one of Sai's possible journeys. Atsuki and Shiroya have trapped themselves in the elevator."
    c "Sai thinks about his next course of action and decides to use the Past Sekimeiya. After allowing it to warm up, he touches it.{w} But how is his past position determined?"
    show bg chart_saielev2
    with dissolve
    c "The answer is that he continues to live virtually, as if he did not time travel. Movements during this time can be natural or driven with clear intent. Let's say he virtually moves until he reaches room B4."
    show bg chart_saielev3
    with dissolve
    c "When he arrives in the past, he will be in room B4. Right now, this new timeline is imaginary. It will become real once the past state matches the future state."
    show bg chart_saielev4
    nvl clear
    with dissolve
    c "Next, he takes out the Past Sekimeiya and allows it to warm up. He touches it and lives virtually until he reaches the floor 4 partitions."
    c "What's important is that the new timeline does not prevent the first travel from occurring."
    c "This means that the Past Sekimeiya must be in the same location and charge state as it was when the first travel happened."
    show bg chart_saielev5
    nvl clear
    with dissolve
    c "This travel creates another imaginary timeline, and Sai now exists before the elevator is stopped."
    show bg chart_saielev6
    with dissolve
    c "Taking this opportunity, he enters it and traps himself between floors."
    c "Isn't this a contradiction, though? In the real timeline, Atsuki and Shiroya are in the elevator, but here, Sai is alone."
    c "Try thinking about what the original Sai sees and hears from his perspective. As long as the circumstances that allowed the first travel to happen are preserved, this is valid."
    c "In any case, this is the power of virtual timelines. The absurdities will soon collapse into a single truth."
    nvl clear
    with dissolve
    c "Notice that the future position of the third timeline no longer matches the second. Sai can no longer go to the 4th floor partitions since he's stuck in the elevator."
    show bg chart_saielev7
    with dissolve
    c "The result is that the future position in the second timeline is updated to match the third. The past position in the third timeline is updated accordingly."
    c "In this latest iteration of the third timeline, Sai appears midair inside the elevator and crashes down. He repeats the process of trapping himself between floors."
    c "The validity of the third timeline is preserved, so let's see what happens if we look farther into the future."
    show bg chart_saielev8
    nvl clear
    with dissolve
    c "The future position of the first timeline is updated to be in the elevator, which updates the past position in the second timeline."
    c "However, this raises an issue."
    c "Sai can no longer perform the second travel since now he appears in the stopped elevator."
    show bg chart_saielev9
    nvl clear
    with dissolve
    c "This destroys the third timeline, but preserves its effect.{w} The future position in the first timeline is inside the elevator after it closed."
    c "After killing Atsuki and Shiroya, Sai's past and future positions finally match. The virtual timeline stabilizes and becomes reality."
    show bg thinking
    nvl clear
    with dissolve
    $ explanation=False
    c "Perhaps you don't like the idea that Atsuki and Shiroya aren't in the elevator in the third timeline."
    c "That's fine. This merely demonstrates the concept."
    c "Another method might involve Sai falling down the elevator shaft in a virtual timeline and entering the elevator from the top."
    c "As long as the goal is achievable within the travel and the user has the will to reach it, the Past Sekimeiya will turn it into reality."
    c "The key is to set the future state to be within the elevator. The exact method is not important as long as there is at least one valid option in the sea of possibilities."
    c "The concept of virtual timelines and iterative updates can be found elsewhere in the story. I wonder what solutions you'll come up with."
    return
    
label tip_virtual:
    show bg thinking2
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "Atsuki obtains an equation for the Sekimeiya's travel times using hypothetical worlds. We'll call these \"virtual worlds\"."
    c "Through countless iterations, he uses his virtual selves to produce a result that's observed in the real world."
    c "While this concept works for him, Atsuki isn't aware of how lucky he is to formulate the plan the way he does."
    $ explanation=True
    show bg chart_virtual1
    nvl clear
    with dissolve
    c "Let's take a look at a simple travel using the Past Sekimeiya. In this example, we'll pay close attention to the age of the user throughout the sequence. The node {b}t{/b} represents the moment at which the Sekimeiya is activated."
    show bg chart_virtual2
    with dissolve
    # Even though they don't time travel, they'd still keep any burns they may have sustained
    c "The Sekimeiya sends the user twenty minutes back in time. In order to determine the user's state in the past, a virtual copy of the user is created that continues to live as if they had not time traveled. After twenty minutes, their final state is used in the past."
    c "Both past and future locations are equidistant from the travel point, which means that in this virtual world, the user will arrive in the past being twenty minutes older than at the moment the Sekimeiya was activated."
    show bg chart_virtual3
    nvl clear
    with dissolve
    c "And when the user makes it to the future copy point of the second virtual world, they will be sixty minutes older than at the moment of the travel."
    c "In this second world, the user is able to update their future state."
    c "The state {b}t+20{/b} does not account for the user's behavior in the past, but {b}t+60{/b} does. This update stage is essential for convergence."
    show bg chart_virtual4
    nvl clear
    with dissolve
    c "The next step is a third virtual world."
    c "Since the previous stage's final position is copied, the user will age by another forty minutes and will be 100 minutes older at the end of the travel."
    c "This stage exists to confirm the loop is stable. The user must have identical positions and possessions at {b}t+60{/b} and {b}t+100{/b}. The ages of the body and possessions will be slightly older, but everything else is identical."
    show bg chart_virtual5
    nvl clear
    with dissolve
    c "If the most recent virtual world was stable, the next step will apply the final result to the real world."
    c "When the user appears in the past, they are sixty minutes older than the moment they touched the Sekimeiya, and in the copy point of the future, they will be 100 minutes older. When a user reaches the future state in reality, they have experienced five times the travel time."
    nvl clear
    with dissolve
    c "This is how infinite aging is avoided. The update stage is required to account for the user's actions in the past, and the final stable loop is frozen and applied to reality. Of course, every stage starts with the memories from the {b}t{/b} point."
    c "A clear example of this kind of sequence is Isla's burn. Touching the Sekimeiya left a burn scar on her finger that this system didn't have enough time to erase. Naturally, however, she didn't age infinitely."
    nvl clear
    $ explanation=False
    show bg thinking2
    with dissolve
    c "Atsuki is able to successfully execute his plan, but he's not fully aware of how the Past Sekimeiya works. His understanding is that Sai's watch displayed the year 9,999 through infinite virtual loops."
    c "However, that's incorrect. If the loops operated like that, Sai would have instantly died in the process, and the watch would've disintegrated."
    c "So let's consider a different way Atsuki could have formulated his plan."
    nvl clear
    with dissolve
    #charts that illustrate this process?
    c "\"If I touch the Sekimeiya when fifteen minutes have passed, I'll go twenty minutes to the past and appear in the hallway holding a notepad. Depending on what it says, I'll do one of three things.\""
    c "\"1: If it has a formula written down, forty minutes later, I'll be holding it, so that's how I will have appeared with it.\""   
    c "\"2: If I don't appear with a notepad, by using the Future Sekimeiya in the kitchen, I'll start working toward finding the formula. Before forty minutes pass, I'll obtain a notepad from the bedrooms, and in the top left corner of the first page, I'll write a \"1\" along with the progress I made in those forty minutes. In the future location, I'll be holding the notepad.\""
    c "\"3: If I find a notepad that doesn't contain the formula, it will have my current progress along with a number in the top left corner of the first page, which will indicate the amount of iterations that have occurred so far.{w} Using the information in the notepad, I'll start working to find the formula. Before the forty minutes pass, I'll write down the updated progress in a notepad from the bedrooms, increase the number I saw in the top left corner by one, and make sure that I'm holding it in the future location.\""
    nvl clear
    with dissolve
    c "The concept is almost the same as the one he actually uses, but there's a very important distinction. In this example, Atsuki doesn't get any information before he travels. Instead, he appears with a notepad after traveling to the past."
    c "According to what Atsuki believes at this point in time, this sequence should've worked too since it's almost identical to what he believes happened to Sai's watch. However, if he had attempted it, it would not have worked."
    nvl clear
    $ explanation=True
    show bg chart_virtual5
    with dissolve
    c "The reason is simple. In the virtual worlds, the location of arrival would not have changed after the update stage. The same mechanism that prevents infinite aging would've prevented the infinite information gathering system. In the real world, Atsuki could only have appeared with a notepad containing sixty minutes' worth of information.{w} Not only that, but the plan contains a glaring contradiction. Points {b}t+60{/b} and {b}t+100{/b} are necessarily identical in every way except age, so appearing with a notepad that contains different information from the one that will be held in the future copy point is conceptually flawed. Even though it's what Atsuki believes happened to Sai's watch, it's fundamentally faulty, as it breaks the rule that past and future points must be identical."
    nvl clear
    with dissolve    
    c "...So why did his original plan work? Where's the loophole that allows him to manifest this infinitely iterated information without aging infinitely?"
    c "Let's refresh our memory on the method through which Atsuki obtains the Sekimeiya's formula."
    nvl clear
    show overlay_flashback onlayer master_overlay
    show bg atticlivingroom4
    $ explanation=False
    with dissolve
    c "\"If I touch the Sekimeiya when fifteen minutes have passed, I'll go twenty minutes to the past.{w} But before I touch it, I'll open the door to the hallway and find a notepad from the bedrooms on the floor. Depending on what it says, I'll do one of three things.\""
    c "\"1: If it has a formula written down, I'll go twenty minutes to the past, obtain the notepad, write the formula down, and leave it in the hallway.\"" 
    c "\"2: If I don't find a notepad, I'll go twenty minutes to the past, and using the Future Sekimeiya in the kitchen, I'll start to work toward finding the formula. Before twenty minutes pass, I'll obtain a notepad from the bedrooms, and in the top left corner of the first page, I'll write a \"1\" along with the progress I made in those twenty minutes. Then, I'll leave it in the hallway.\""
    c "\"3: If I find a notepad that doesn't contain the formula, it will have my current progress along with a number in the top left corner of the first page, which will indicate the amount of iterations that have occurred so far.{w} I'll go back to the past, and using the information I read in the notepad, I'll start working to find the formula. Before the twenty minutes pass, I'll write down the updated progress in a notepad from the bedrooms, increase the number I saw in the top left corner by one, and then leave the notepad in the hallway.\""
    nvl clear
    hide overlay_flashback onlayer master_overlay
    show bg chart_virtual6
    with dissolve
    $ explanation=True
    c "As you might've noticed, the reason behind his success lies in observing the information left by the virtual worlds before touching the Sekimeiya."
    c "The Atsukis in the virtual worlds leave the notepad in the hallway so that the Atsuki before the {b}t{/b} point can see it. In other words, stage 2 feeds information to stage 1."
    nvl clear
    with dissolve
    c "That causes {b}t{/b}'s starting memories to continuously update, and the calculations made at the {b}t+60{/b} point are no longer locked to a state of a single round of calculations."
    c "When the sequence converges and the final result is applied to the real world, Atsuki appears in the past having aged only sixty minutes but having spent infinite time computing. This is thanks to the virtual worlds continuously updating the starting point through real Atsuki's memories."
    $ explanation=False
    return

label tip_burn1:
    $ SpriteTint("dark")
    show bg thinking
    show atsukil 1b neutral
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "When Isla A traveled from December 15th to November 24th, she appeared with a burn mark on her finger. The Sekimeiya was immensely hot, so the burn would not have faded by the time the future location took place."
    show bg streetlight2
    hide atsukil
    with dissolve
    c "So then, why does Atsuki not appear with a burn mark on November 24th? The Sekimeiya was about as hot, and he will spend even fewer days to reach the future position since he will travel forward in time from December 15th to January 5th."
    show bg atsukisbedroom
    with dissolve
    c "The answer lies in what will happen to Atsuki the night he will arrive at the motel. He will travel to the future in order to duplicate his money, but due to a miscalculation, he will replicate his body from November 24th."
    c "That body didn't have a burn, so he never appeared with one."
    return

label tip_ohnoitdidntwork:
    show bg night5
    $ Snow(1, fast=True)
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "The biggest reason why this loop doesn't work for Atsuki is that the box Atase took only contained the Past Sekimeiya."
    return

label tip_rush:
    show atsukim 1a confused
    show bg attickitchen1
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "While he's rushing his actions, Atsuki can't help but feel like that doesn't make sense."
    c "He recalls that he returned to his world at {time=19:30}, which is approaching. That's why he rushes Shiroya to activate the Sekimeiya at that time and make the people in the center of the tower change worlds."
    c "But of course, that's slightly paradoxical. Why did the travel happen at {time=19:30} in the first place? His hurry to take this action only existed because the world switch had been lived through once, so why did it not just happen at a later point?"
    c "There's something Atsuki is mistaken about. Shiroya traveling to November 30th isn't what makes everyone world switch back to world B. It is Atsuki A who causes that when he travels from world B to world C, pulling them back to their world. That's why he has no control over the time at which the world switch takes place."
    hide atsukim
    show bg towernight
    with dissolve
    c "Nonetheless, when Shiroya travels to November, she does cause a world switch. Both immense ranges still overlapped in the middle of the tower, and only one person found themselves there: Atsuki A, cluelessly taking the elevator up. Before his ride ends, Shiroya's touch makes him go back to world A, where no elevator is supporting him, and he falls onto the one below him."
    return

label tip_force:
    $ SpriteTint("dark")
    show bg tunnel
    show shiroyal 4a smile at p35 
    with dissolve
    $ Pause(0.3)
    window auto show
    with Dissolve(0.1)
    c "That burning touch of the Sekimeiya was the catalyst behind the events that unfolded on December 15th. Shiroya traveled to the future and suddenly found herself in her apartment. It was December 19th, and the first thing she did was call Atsuki's phone."
    hide shiroyal
    show bg towermorning
    with dissolve
    c "During the twelve hours of December 15th, Atsuki B vaguely wondered something. He knew he had to make sure that Shiroya's body wouldn't be found in world C so that Miiya could be saved, but that would only work out because her body had already not been found. Atsuki wasn't sure how that detail had originated.{w} Regardless, he instructed Shiroya to keep her world C self hidden from the world. Yet, in the end, she didn't end up causing that: it was Shiroya C herself who was attracted to the Sekimeiya's glow and vanished from the world for weeks."
    show bg night5
    $ Snow(1, fast=True)
    with dissolve
    c "The importance behind that action was even larger than Atsuki had thought. Due to Shiroya's disappearance, Akaro believed that he had killed a young girl, which developed into the attack of December 15th."
    c "And although it was world C's own flow that made that happen, it was thanks to world B's influence that it occurred. Shiroya C avoided falling into a coma because her world B self shielded her while both of them fell through the floor of the gem shop."
    return

label tip_end:
    # This marks the end of tips for the search function
    return
