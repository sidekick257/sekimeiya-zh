## @TOOD: Store data until a connection is established
## @TODO: Ship the game with some stats in case the player never connects online. Disclaimer it with the date that data was last updated

init -20 python:
    class PlayerQuestion(python_object):
        def __init__(self,
                name="",
                type="",
                prompt="",
                hint_text="",
                show_timeline=False,
                map_number=1,
                text_bg="",
                choices=python_list(),
                correct_answers=python_list(),
                min_range = 0,
                min_text = "Minimum",
                max_range = 100,
                max_text = "Maximum",
                special_value = None,
                special_text = "",
                ):
            self.name = name
            self.type = type

            self.prompt = prompt
            self.hint_text = hint_text
            self.show_timeline = show_timeline
            self.map_number = map_number
            self.text_bg = text_bg
            self.choices = choices

            if self.type == "rank":
                self.ranking = python_dict()
            if self.type == "num_range":
                self.min_range = min_range
                self.min_text = min_text
                self.max_range = max_range
                self.max_text = max_text
                self.special_value = special_value
                self.special_text = special_text

            self.correct_answers = correct_answers

    from collections import MutableMapping, OrderedDict
    class PlayerQuestionsContainer(MutableMapping):
        def __init__(self, store_answers, store_scores=None, store_times=None):#, *args, **kwargs):
            self.questions = OrderedDict()
            self.store_answers = store_answers
            self.store_scores = store_scores
            self.store_times = store_times
            self.last_answer = None
            self.is_last_answer_correct = False
            #self.update(dict(*args, **kwargs))  # use the free update to set keys

        def __getitem__(self, key):
            return self.questions[key]

        def __setitem__(self, key, value):
            self.questions[key] = value

        def __delitem__(self, key):
            del self.questions[key]

        def __iter__(self):
            return iter(self.questions)

        def __len__(self):
            return len(self.questions)

        def GetQuestion(self, name):
            return self.__getitem__(name)

        def GetAnswer(self, name):
            answer = ""
            if name in self.store_answers:
                answer = self.store_answers[name].upper()

            question_obj = self.GetQuestion(name)
            if question_obj.type == "choice":
                for temp in question_obj.choices:
                    if temp[1]==answer:
                        answer = temp[0]
                        break

            return answer

        def GetAnswerRaw(self, name):
            answer = None
            if name in self.store_answers:
                answer = self.store_answers[name].upper()
                answer = answer or "<blank>"

            return answer

        def GetAnswerFromRaw(self, name, answer):
            rv = ""
            question_obj = self.GetQuestion(name)
            if question_obj.type in ["choice", "rank"]:
                for temp in question_obj.choices:
                    if temp[1]==answer:
                        rv = temp[0]
                        break
            else:
                if answer is not None:
                    rv = answer
                rv = rv or "<blank>"
                rv = rv.title() # Capitalize the string as a title

            return rv

        def IsQuestionSeen(self, name):
            return name in persistent.analytics_logged['c5 answers']

        def IsCorrectAnswer(self, name):
            if name in self.store_scores:
                return self.store_scores[name]

            return False

        def GetCorrectAnswer(self, name):
            question_obj = self.GetQuestion(name)
            answer = ' / '.join(question_obj.correct_answers)

            if question_obj.type == 'choice':
                for temp in question_obj.choices:
                    if temp[1]==answer:
                        answer = temp[0]
                        break

            return answer

        def GetScore(self):
            count = 0
            sum = 0
            for question_name, is_correct in self.store_scores.items():
                if s is not None:
                    count += 1
                    sum += is_correct

            if count == 0:
                percentage_correct = 0
            else:
                percentage_correct = int(100.0*sum/count)

            return count, sum, percentage_correct

        def CreateSingleAnswer(self, name):
            ## Used if there's not a single answer given except your own
            ## Would only be used for the very first player

            rv = dict()
            rv[self.GetAnswerRaw(name)] = 1
            self.ExpandAnswers(rv, name)
            return rv

        def ExpandAnswers(self, rv, name):
            if name not in self.questions:
                return rv

            question_obj = self.questions[name]
            keys = python_list()

            if question_obj.type == 'choice':
                for temp in question_obj.choices:
                    keys.append(temp[1])

            elif question_obj.type == "map":
                room_list = None
                if question_obj.map_number == 1:
                    room_list = ["STOREROOM", "LIVING ROOM", "BATHROOM", "KITCHEN", "BEDROOMS"]
                elif question_obj.map_number == 2:
                    room_list = ["STOREROOM", "MECHANICAL ROOM", "BATHROOM", "HALL B ROOMS"]
                elif question_obj.map_number == 3:
                    room_list = ["STOREROOM", "MECHANICAL ROOM", "BATHROOM", "HALL B ROOMS", "SECURITY ROOM", "EVENT ROOM", "LOBBY", "CLEANING ROOM", "STAFF ROOM"]
                elif question_obj.map_number == 4:
                    room_list = ["F1 STAIRS", "F3 STAIRS", "INSIDE PARTITIONS", "OUTSIDE PARTITIONS"]

                for temp in room_list:
                    keys.append(temp)

            elif question_obj.type in ["character", "text"]:
                keys.append(question_obj.correct_answers[0])

            """
            elif question_obj.type == "character":
                for temp in ['ATSUKI', 'SHIROYA', 'MIIYA', 'SAI', 'AKARO', 'KATEI', 'ERINA', 'ISLA', 'NAOMI']:
                    if question_obj.show_timeline:
                        for suffix in [' A', ' B', ' C']:
                            keys.append(temp+suffix)
                    else:
                        keys.append(temp)
            """

            for key in keys:
                if key not in rv:
                    rv[key] = 0

            return rv

        def ShowQuestion(self, name):
            renpy.sound.play('sounds/sys30.wav')
            if name not in self.questions:
                raise ValueError("Question '{}' not found".format(name))

            question_obj = self.GetQuestion(name)
            start_time = time.time()

            _window_hide(auto=True)

            if question_obj.type == "character":
                renpy.transition(dissolve)
                self.last_answer = renpy.call_screen("CharacterSelect", question_obj.prompt, show_timeline=question_obj.show_timeline, _with_none=False)
            elif question_obj.type == "map":
                renpy.transition(dissolve)
                self.last_answer = renpy.call_screen("MapSelect", question_obj.prompt, number=question_obj.map_number, _with_none=False)
            elif question_obj.type == "text":
                renpy.scene()
                renpy.show(question_obj.text_bg)
                renpy.transition(dissolve)
                initial_text = ""
                if name in self.store_answers:
                    initial_text = self.store_answers[name]
                answer = renpy.call_screen("input", prompt="", initial_text=initial_text, hint_text=question_obj.hint_text, _with_none=False)
                renpy.sound.play('sounds/sys23.wav')
                self.last_answer = answer or "<blank>"
            elif question_obj.type == "choice":
                renpy.transition(dissolve)
                if len(question_obj.choices)>=7:
                    self.last_answer = renpy.display_menu(question_obj.choices, scope={'spacing':9})
                else:
                    self.last_answer = renpy.display_menu(question_obj.choices)

            time_taken = int(time.time() - start_time)
            self.last_answer = self.last_answer.upper()
            self.is_last_answer_correct = self.last_answer in question_obj.correct_answers
            self.UpdateScore(name, self.last_answer, int(self.is_last_answer_correct), time_taken)

        def UpdateScore(self, question, answer, score, time_taken=0):
            if self.IsQuestionSeen(question):
                return
            if question not in persistent.analytics_logged['c5 answers']:
                self.store_scores[question] = score
                self.store_answers[question] = answer
                self.store_times[question] = time_taken

                renpy.invoke_in_thread(analytics.SendC5Answer, question, answer, time_taken)
            elif question=="choice shiroya c3":
                pass
            else:
                if self.store_scores[question]==0 and score==1 and not persistent.save_scum_detected:
                    #current_bg = ' '.join(renpy.game.contexts[0].scene_lists.layers["master"][0].name)
                    renpy.scene()
                    renpy.scene('master_overlay')
                    renpy.show("bg white3")
                    nvl_clear()
                    renpy.with_statement(dissolve)
                    c("Nice try, but you and I know how you answered this question the first time.")
                    c("In any case, I'll let you see the result of your new choice.")
                    nvl_clear()
                    #renpy.show(current_bg)
                    #renpy.with_statement(dissolve)
                    persistent.save_scum_detected = True

        def GetPreferenceData(self, name):
            if name not in self.questions:
                return

            if name in persistent.analytics_retrieved["prefs"]:
                data = persistent.analytics_retrieved["prefs"][name]
            else:
                data = {"0":1}

            q_obj = self.questions[name]
            if q_obj.type == "num_range":
                temp_dict = {'0':0, '1':0, '2':0, '3':0, '4':0}
                if q_obj.special_value is not None:
                    temp_dict['special'] = 0

                for d_key, d_val in data.items():
                    d_idx = int(d_key)
                    if d_idx == q_obj.special_value:
                        temp_dict['special'] = d_val
                        continue
                    # Map value between 0.0 and 1.0
                    d_idx = (1.0*d_idx - q_obj.min_range)/(q_obj.max_range-q_obj.min_range)

                    if d_idx < 0.2:
                        temp_dict['0'] += d_val
                    elif d_idx < 0.4:
                        temp_dict['1'] += d_val
                    elif d_idx < 0.6:
                        temp_dict['2'] += d_val
                    elif d_idx < 0.8:
                        temp_dict['3'] += d_val
                    else:
                        temp_dict['4'] += d_val

                rv = OrderedDict()
                rv[q_obj.min_text] = temp_dict['0']
                rv[' '] = temp_dict['1']
                rv['  '] = temp_dict['2']
                rv['   '] = temp_dict['3']
                rv[q_obj.max_text] = temp_dict['4']
                if 'special' in temp_dict:
                    rv[q_obj.special_text] = temp_dict['special']
                data = rv

            return data

        def GetSelectedPreference(self, name):
            return ""

    ####################
    ## Chapter 5 Answers
    ####################

    c5_answers = PlayerQuestionsContainer(persistent.c5_answers, persistent.c5_score, persistent.c5_times)

    c5_answers["choice shiroya c3"] = PlayerQuestion(
        type="choice",
        prompt="Where did Shiroya travel?",
        choices=(
            ("To the past.", "PAST"),
            ("To the future.", "FUTURE"),
            ),
        correct_answers=("FUTURE",),
        )

    c5_answers["char akaro voice"] = PlayerQuestion(
        type="character",
        prompt="That voice belonged to...",
        show_timeline=False,
        correct_answers=("AKARO",),
        )

    c5_answers["map kitchen clue"] = PlayerQuestion(
        type="map",
        prompt="Where was the biggest clue?",
        show_timeline=False,
        correct_answers=("KITCHEN",),
        )

    c5_answers["text jan 5 date"] = PlayerQuestion(
        type="text",
        prompt="The date that Isla said was...",
        hint_text="MM-DD-YYYY",
        text_bg="bg text1",
        correct_answers=("01-05-2012", "1-5-2012", "01/05/2012", "1/5/2012","01.05.2012", "1.5.2012", "1052012"),
        )

    #c5_answers["text isla fist"] = PlayerQuestion(
    #    type="text",
    #    prompt="Isla's clenched fist had been hiding a ____.",
    #    hint_text="4 letters",
    #    text_bg="bg text2",
    #    correct_answers=("BURN", "SCAR", "MARK"),
    #    )

    c5_answers["choice jan 5 event"] = PlayerQuestion(
        type="choice",
        #prompt="Someone had been there right as the group had appeared on January 5th. Atsuki knew that thanks to the last time he'd been in...",
        prompt="Clues of a tower visit on Jan 5th were found in...",
        choices=[
            ("The lobby.", "LOBBY"),
            ("The crystal floor hallways.", "HALLWAYS"),
            ("The event room.", "EVENT ROOM"),
            ("The attic.", "ATTIC"),
            ],
        correct_answers=("EVENT ROOM",),
        )

    c5_answers["choice jan5 charge"] = PlayerQuestion(
        type="choice",
        prompt="I need to leave the Sekimeiya here...",
        choices=[
            ("For approximately 10 minutes.", "10 MINUTES"),
            ("For approximately 15 minutes.", "15 MINUTES"),
            ("For approximately 20 minutes.", "20 MINUTES"),
            ("For approximately 25 minutes.", "25 MINUTES"),
            ("For approximately 35 minutes.", "35 MINUTES"),
            ],
        correct_answers=("25 MINUTES",),
        )

    #c5_answers["choice atsukis injury"] = PlayerQuestion(
    #    type="choice",
        #prompt="I looked at my hand, where I'd suffered a painful injury in the elevator.",
    #    prompt="I looked at the hand injury I got in the elevator.",
    #    choices=(
    #        ("The injury was still there.", "STILL THERE"),
    #        ("The injury wasn't there anymore.", "NOT THERE"),
    #        ),
    #    correct_answers=("NOT THERE",),
    #    )

    c5_answers["choice shiroya naomi switch"] = PlayerQuestion(
        type="choice",
        prompt="At the top of attic stairs, Shiroya turned to me...",
        choices=(
            ("But before she could face me, my surroundings shifted.", "MY SURROUNDINGS SHIFTED"),
            ("But before she could face me, she disappeared.", "SHE DISAPPEARED"),
            ),
        correct_answers=("SHE DISAPPEARED",),
        )

    c5_answers["text suitcase"] = PlayerQuestion(
        type="text",
        prompt="With them, the ________ had also disappeared.",
        text_bg="bg text3",
        correct_answers=("SUITCASE", "BRIEFCASE"),
        )

    c5_answers["choice storeroom handle"] = PlayerQuestion(
        type="choice",
        prompt="In the dark, I felt the door for its handle...",
        choices=(
            ("It was there.", "THERE"),
            ("It wasn't there.", "NOT THERE"),
            ),
        correct_answers=("THERE",),
        )

    c5_answers["char miiya voice"] = PlayerQuestion(
        type="character",
        prompt="It had belonged to...",
        show_timeline=False,
        correct_answers=("MIIYA",),
        )

    c5_answers["text sekimeiya1"] = PlayerQuestion(
        type="text",
        prompt="It was a...",
        text_bg="bg text5",
        correct_answers=("SEKIMEIYA",),
        )

    c5_answers["choice sekimeiya off"] = PlayerQuestion(
        type="choice",
        prompt="That doesn't make sense...",
        choices=(
            ("Because they would have come back here after appearing in the past.", "APPEAR IN PAST"),
            ("Because the Sekimeiya shouldn't have worked.", "SHOULDN'T WORK"),
            ("Because of its color.", "COLOR"),
            ("Because the Sekimeiya would have teleported.", "TELEPORTED"),
            ),
        correct_answers=("COLOR",),
        )

    c5_answers["text sekimeiya2"] = PlayerQuestion(
        type="text",
        prompt="It was a...",
        text_bg="bg text5",
        correct_answers=("SEKIMEIYA",),
        )

    c5_answers["choice tower empty"] = PlayerQuestion(
        type="choice",
        prompt="Atsuki suspected that perhaps...",
        choices=(
            ("The others had appeared outside the tower.", "OUTSIDE TOWER"),
            ("The others had traveled to the future.", "TRAVEL TO FUTURE"),
            ("The others were no longer in that world.", "NOT IN THAT WORLD"),
            ),
        correct_answers=("NOT IN THAT WORLD",),
        )

    c5_answers["choice miiyas existence"] = PlayerQuestion(
        type="choice",
        prompt="What Atsuki recognized from this world was...",
        choices=(
            ("Miiya's existence.", "MIIYAS EXISTENCE"),
            ("The storeroom's handle.", "STOREROOM HANDLE"),
            ("The empty tower.", "EMPTY TOWER"),
            ),
        correct_answers=("MIIYAS EXISTENCE",),
        )

    c5_answers["choice miiya existence normalized"] = PlayerQuestion(
        type="choice",
        #prompt="When did Miiya's existence become normal for the world?",
        prompt="When did Miiya's existence become normal?",
        choices=(
            ("When Erina touched the Sekimeiya in the event room.", "ERINA TOUCHED SEKIMEIYA"),
            ("When Atsuki touched the Sekimeiya in room B6.", "ATSUKI SEKIMEIYA HALLWAY B"),
            ("When Atsuki touched the Sekimeiya in the staff room.", "ATSUKI SEKIMEIYA STAFF ROOM"),
            ),
        correct_answers=("ERINA TOUCHED SEKIMEIYA",),
        )

    c5_answers["choice shiroyas existence"] = PlayerQuestion(
        prompt="There was another major change.",
        type="choice",
        choices=(
            ("Katei's existence.", "KATEIS EXISTENCE"),
            ("The Sekimeiya's existence.", "SEKIMEIYAS EXISTENCE"),
            ("Shiroya's existence.", "SHIROYAS EXISTENCE"),
            ),
        correct_answers=("SHIROYAS EXISTENCE",),
        )

    c5_answers["choice event room second sekimeiya"] = PlayerQuestion(
        type="choice",
        #prompt="Why did Erina, Shiroya, and I not travel, but Sai did? Why did the Sekimeiya teleport instantly back to its cabinet?",
        prompt="What factor was involved in that strange travel?",
        choices=(
            ("Miiya's existence.", "MIIYAS EXISTENCE"),
            ("Traveling to the future.", "TRAVEL TO FUTURE"),
            ("The second Sekimeiya.", "SECOND SEKIMEIYA"),
            ),
        correct_answers=("SECOND SEKIMEIYA",),
        )

    c5_answers["choice different sekimeiya"] = PlayerQuestion(
        type="choice",
        prompt="The Sekimeiya didn't teleport. The reality was...",
        choices=(
            ("Someone had moved it there.", "SOMEONE MOVED IT"),
            ("It had teleported to the cabinet.", "TELEPORTED TO CABINET"),
            ("It was not the same Sekimeiya.", "DIFFERENT SEKIMEIYA"),
            ),
        correct_answers=("DIFFERENT SEKIMEIYA",),
        )

    c5_answers["choice world switch cause"] = PlayerQuestion(
        type="choice",
        #prompt="What was the key to the occurrences in the event room?",
        prompt="The key to the event room occurrences was...",
        choices=(
            ("Who touched the Sekimeiya.", "WHO ACTIVATED"),
            ("Which Sekimeiya was activated.", "WHICH ACTIVATED"),
            ("The location of both Sekimeiya.", "SEKIMEIYA POSITIONS"),
            ("The number of people within range.", "NUMBER OF PEOPLE"),
            ),
        correct_answers=("SEKIMEIYA POSITIONS",),
        )

    c5_answers["choice naomi c death"] = PlayerQuestion(
        type="choice",
        #prompt="The Naomi that Shiroya disappeared with was one of the two bodies that we found dead.",
        prompt="That Naomi was one of the two bodies we found.",
        choices=(
            ("Correct.", "CORRECT"),
            ("Incorrect.", "INCORRECT"),
            ),
        correct_answers=("INCORRECT",),
        )

    c5_answers["choice another world"] = PlayerQuestion(
        type="choice",
        prompt="Why did Akaro have different memories?",
        choices=(
            ("There was a change to the past.", "CHANGED PAST"),
            ("Akaro lied.", "AKARO LIED"),
            ("He was from another world.", "ANOTHER WORLD"),
            ("His memories were erased.", "ERASED MEMORIES"),
            ),
        correct_answers=("ANOTHER WORLD",),
        )

    c5_answers["text number worlds"] = PlayerQuestion(
        type="text",
        prompt="How many worlds are there?",
        text_bg="bg text7",
        correct_answers=("THREE", "3", "III", "11"),
        )

    c5_answers["text why three"] = PlayerQuestion(
        type="text",
        prompt="Because the three worlds ____.",
        text_bg="bg text8",
        correct_answers=("LOOP", "SPIN", "SPUN", "GYRE"),
        )

    c5_answers["choice world c"] = PlayerQuestion(
        type="choice",
        prompt="The world where everyone survived...",
        choices=(
            ("Is B.", "B"),
            ("Is C.", "C"),
            ),
        correct_answers=("C",),
        )

    c5_answers["choice world b"] = PlayerQuestion(
        type="choice",
        prompt="World switching from world A brought people to...",
        choices=(
            ("World B.", "B"),
            ("World C.", "C"),
            ),
        correct_answers=("B",),
        )

    c5_answers["choice timeline order"] = PlayerQuestion(
        type="choice",
        prompt="The order is A - B - C - A.",
        choices=(
            ("...There is a problem with this order.", "PROBLEM"),
            ("...There is no problem with this order.", "NO PROBLEM"),
            ),
        correct_answers=("PROBLEM",),
        )

    c5_answers["choice world a difference"] = PlayerQuestion(
        type="choice",
        prompt="The major difference in world A...",
        choices=(
            ("Was the lack of deaths.", "NO DEATHS"),
            ("Was Katei's absence.", "KATEIS ABSENCE"),
            ("Was the second Naomi.", "SECOND NAOMI"),
            ),
        correct_answers=("KATEIS ABSENCE",),
        )

    c5_answers["choice katei dropped key"] = PlayerQuestion(
        type="choice",
        #prompt="Katei tripped in the staircase leading to the fourth floor without realizing he dropped another key, which was...",
        prompt="Katei tripped and dropped another key, which was...",
        choices=(
            ("The security room's.", "SECURITY ROOM KEY"),
            ("The Sekimeiya cabinet's.", "SEKIMEIYA CABINET KEY"),
            ("The rusty key.", "RUSTY KEY"),
            ),
        correct_answers=("SECURITY ROOM KEY",),
        )

    c5_answers["choice security key b"] = PlayerQuestion(
        type="choice",
        prompt="What happened to the security room key in world B?",
        choices=(
            ("Katei didn't drop it.", "DIDNT DROP IT"),
            ("Katei immediately realized he'd dropped it.", "REALIZED HE DROPPED IT"),
            ("Someone didn't mention they'd found it.", "SOMEONE FOUND IT"),
            ),
        correct_answers=("DIDNT DROP IT",),
        )

    c5_answers["choice only occurred in b"] = PlayerQuestion(
        type="choice",
        #prompt="Katei didn't drop the key. The answer is tied to something else that only occurred in B.",
        prompt="The key was something that only occurred in world B.",
        choices=(
            ("The handle's removal.", "HANDLE REMOVAL"),
            ("The alarm's effects.", "ALARM EFFECTS"),
            ("The call with Suripo.", "SURIPO CALL"),
            ),
        correct_answers=("HANDLE REMOVAL",),
        )

    c5_answers["char remove handle"] = PlayerQuestion(
        type="character",
        prompt="Who took the handle off in world B?",
        show_timeline=True,
        correct_answers=("AKARO A",),
        )

    c5_answers["choice relation between world changes"] = PlayerQuestion(
        type="choice",
        prompt="What is the relation between all these changes?",
        choices=(
            ("There is no correlation.", "NO CORRELATION"),
            ("Someone from another world caused them.", "ANOTHER WORLD CAUSE"),
            ("They had no real origin.", "UNINTENTIONAL"),
            ),
        correct_answers=("ANOTHER WORLD CAUSE",),
        )

    c5_answers["text device 4:15"] = PlayerQuestion(
        type="text",
        prompt="And the time on the screen was...",
        hint_text="mm:ss",
        text_bg="bg text10",
        correct_answers=("4:15", "04:15", "04 15", "4 15", "415", "0415", "4：15", "04：15"),
        )

    c5_answers["choice device timeless"] = PlayerQuestion(
        type="choice",
        #prompt="The oven's timer was at 2:25, so I hurried to look at the voice recorder.",
        prompt="The oven's timer read 2:25. On the voice recorder...",
        choices=(
            ("The time displayed was 2:25.", "2:25"),
            ("The time displayed was 2:35.", "2:35"),
            ("The time displayed was 2:44.", "2:45"),
            ("The time displayed was 2:53.", "2:53"),
            ("There was no time displayed.", "NO TIME"),
            ),
        correct_answers=("NO TIME",),
        )

    c5_answers["text shiroyas phone gone"] = PlayerQuestion(
        type="choice",
        prompt="Erased due to not possessing it in the future",
        choices=(
            ("This is what happened to the knife.", "KNIFE"),
            ("This is what happened to the cleaning cart.", "CART"),
            ("This is what happened to Shiroya's phone.", "PHONE"),
            ),
        correct_answers=("PHONE",),
        )

    c5_answers["choice sekimeiya traveled"] = PlayerQuestion(
        type="choice",
        prompt="After traveling to the future, I looked at my hands...",
        # prompt="I appeared in the kitchen nine seconds in the future. Then, I glanced at my hands.",
        choices=(
            ("The Past Sekimeiya was there.", "THERE"),
            ("The Past Sekimeiya was not there.", "NOT THERE"),
            ),
        correct_answers=("THERE",),
        )

    c5_answers["choice sekimeiya didnt travel"] = PlayerQuestion(
        type="choice",
        #prompt="Why didn't the disabled Future Sekimeiya travel to the past?",
        prompt="Why didn't the disabled Future Sekimeiya travel?",
        choices=(
            ("Sending the Future Sekimeiya to the past would be paradoxical.", "PARADOX"),
            ("Because it is an infinity loop!", "INFINITY LOOP"),
            ("Because it would've caused a world switch.", "WORLD SWITCH"),
            ),
        correct_answers=("PARADOX",),
        )

    c5_answers["char sai a"] = PlayerQuestion(
        type="character",
        prompt="That is what happened to...",
        show_timeline=True,
        correct_answers=("SAI A",),
        )

    c5_answers["text sekimeiya range"] = PlayerQuestion(
        type="text",
        #prompt="Unlike the time component, the _____ of the Sekimeiya increases gradually.",
        prompt="The _____ of the Sekimeiya increases gradually.",
        text_bg="bg text12",
        correct_answers=("RANGE", "REACH", "SPACE", "WIDTH"),
        )

    c5_answers["char computer shutdown b"] = PlayerQuestion(
        type="character",
        prompt="Who shut down the computer in world B?",
        show_timeline=True,
        correct_answers=("KATEI B",),
        )

    c5_answers["char elevator naomi a"] = PlayerQuestion(
        type="character",
        prompt="Who moved the elevator?",
        show_timeline=True,
        correct_answers=("NAOMI A",),
        )

    c5_answers["choice elevator naomi b"] = PlayerQuestion(
        type="choice",
        #prompt="It was soon after when we found Naomi's first corpse in the hallway B crystal room.",
        prompt="We found Naomi's first corpse in room B4.",
        choices=(
            ("That was the Naomi who'd taken the elevator.", "TOOK ELEVATOR"),
            ("That was not the Naomi who'd taken the elevator.", "DIDNT TAKE ELEVATOR"),
            ),
        correct_answers=("DIDNT TAKE ELEVATOR",),
        )

    c5_answers["char naomi b killer"] = PlayerQuestion(
        type="character",
        prompt="Who killed Naomi B?",
        show_timeline=True,
        correct_answers=("KATEI B",),
        )

    c5_answers["char hide storeroom sai b"] = PlayerQuestion(
        type="character",
        prompt="Who hid the Sekimeiya in the storeroom?",
        show_timeline=True,
        correct_answers=("SAI B",),
        )

    c5_answers["choice storeroom hidden culprit"] = PlayerQuestion(
        type="choice",
        prompt="How did the Sekimeiya end up in the storeroom?",
        choices=(
            ("It wasn't the same Sekimeiya.", "DIFFERENT SEKIMEIYA"),
            ("Someone in hallway B worked with someone in hallway A.", "ACCOMPLICE"),
            ("Sai already had it when he entered the storeroom.", "SAI HAD IT"),
            ),
        correct_answers=("DIFFERENT SEKIMEIYA",),
        )

    c5_answers["char hide past sai b"] = PlayerQuestion(
        type="character",
        prompt="Who hid the Past Sekimeiya?",
        show_timeline=True,
        correct_answers=("SAI B",),
        )

    c5_answers["char three elevator trips"] = PlayerQuestion(
        type="character",
        prompt="Who caused the three elevator trips?",
        show_timeline=True,
        correct_answers=("AKARO B",),
        )

    c5_answers["map hide bathroom"] = PlayerQuestion(
        type="map",
        prompt="Then, where did he hide it?",
        map_number=3,
        correct_answers=("BATHROOM",),
        )

    c5_answers["char naomi a killer"] = PlayerQuestion(
        type="character",
        prompt="Who killed Naomi A?",
        show_timeline=True,
        correct_answers=("AKARO B",),
        )

    c5_answers["choice recording dec 15"] = PlayerQuestion(
        type="choice",
        #prompt="How did the recorder from the future end up on December 15th?",
        prompt="How did the future recording end up in December?",
        choices=(
            ("It came from another world.", "ANOTHER WORLD"),
            ("It traveled to the future instead.", "TRAVELED TO FUTURE"),
            ("It happened when someone traveled to the past on December 15th.", "TRAVELED TO PAST DEC 15"),
            ("It happened when someone traveled to the past on January 5th.", "TRAVELED TO PAST JAN 5"),
            ("The device picked up a recording that would occur in the future.", "PICKED UP RECORDING"),
            ),
        correct_answers=("TRAVELED TO PAST DEC 15",),
        )

    c5_answers["choice watch battery attic"] = PlayerQuestion(
        type="choice",
        prompt="Why didn't the watch work?",
        choices=(
            ("Sai traveled to the past a second time.", "TRAVELED AGAIN"),
            ("Sai changed the battery back to the one that didn't work.", "RETURNED EMPTY BATTERY"),
            ("It was due to the battery in the attic.", "ATTIC BATTERY"),
            ),
        correct_answers=("ATTIC BATTERY",),
        )

    c5_answers["choice cleaning cart past"] = PlayerQuestion(
        type="choice",
        prompt="After we found the Sekimeiya in the cleaning cart...",
        choices=(
            ("We traveled to the past.", "PAST"),
            ("We traveled to the future.", "FUTURE"),
            ),
        correct_answers=("FUTURE",),
        )

    c5_answers["choice future sekimeiya cart"] = PlayerQuestion(
        type="choice",
        #prompt="What happened to the Future Sekimeiya after we traveled with the cart?",
        prompt="Then what happened to the Future Sekimeiya?",
        choices=(
            ("Katei took it.", "KATEI"),
            ("Sai took it.", "SAI"),
            ("It teleported.", "TELEPORTED"),
            ("It was also there.", "ALSO THERE"),
            ),
        correct_answers=("SAI",),
        )

    c5_answers["choice katei cart disappear"] = PlayerQuestion(
        type="choice",
        #prompt="Where was Katei after we disappeared with the cart?",
        prompt="Where was Katei after we traveled with the cart?",
        choices=(
            ("Katei was in the storeroom's secret corridor.", "KATEI SECRET CORRIDOR"),
            ("The search wasn't optimal, so they missed him.", "BAD SEARCH"),
            ("Katei had traveled to the future as well.", "KATEI FUTURE"),
            ("Katei was in another world.", "KATEI ANOTHER WORLD"),
            ("Someone didn't reveal that they had found Katei.", "UNREPORTED"),
            ),
        correct_answers=("KATEI FUTURE",),
        )

    c5_answers["choice isla death"] = PlayerQuestion(
        type="choice",
        prompt="How did Isla die?",
        choices=(
            ("Isla was killed.", "KILLED"),
            ("Isla suffered an accidental death.", "ACCIDENT"),
            ),
        correct_answers=("ACCIDENT",),
        )

    c5_answers["choice isla cabinet sekimeiya"] = PlayerQuestion(
        type="choice",
        #prompt="The Sekimeiya that appeared next to Isla's dead body was working...",
        prompt="An active Sekimeiya appeared next to Isla's body...",
        choices=(
            ("And it was the Past Sekimeiya.", "PAST"),
            ("And it was the Future Sekimeiya.", "FUTURE"),
            ),
        correct_answers=("PAST",),
        )

    c5_answers["choice culprit hidden partition"] = PlayerQuestion(
        type="choice",
        #prompt="I was certain that secret place had been used by the culprit to escape the multiple searches we did.",
        prompt="The culprit evaded us using the secret partition...",
        choices=(
            ("But that never happened.", "NEVER HAPPENED"),
            ("But it was only used to avoid one.", "AVOID ONE"),
            ("And it was used to avoid two.", "AVOID TWO"),
            ),
        correct_answers=("NEVER HAPPENED",),
        )

    c5_answers["choice arrival in jan 5"] = PlayerQuestion(
        type="choice",
        prompt="How did we make it to January 5th?",
        choices=(
            ("Isla lied about the date.", "ISLA LIED"),
            ("Isla traveled from January 5th to December 15th unknowingly.", "ISLA TRAVELED UNKNOWINGLY"),
            ("All of us had been in the tower on November 24th.", "ALL IN NOV 24"),
            ("We traveled to the future more than once.", "MULTIPLE FUTURE TRAVELS"),
            ("We were knocked out until January 5th.", "KNOCKED OUT TILL JAN 5"),
            ("The fourth effect of the Sekimeiya was activated.", "FOURTH SEKIMEIYA EFFECT"),
            ("We never traveled through time.", "NEVER TRAVELED"),
            ("We were always on January 5th.", "ALWAYS IN JAN 5"),
            ),
            #add consistency in the choices because sometimes they're in 1st person and others in 3rd person. also remove quotation marks between 1st person ones earlier in c5
        correct_answers=("MULTIPLE FUTURE TRAVELS",),
        )

    c5_answers["map future chain activation"] = PlayerQuestion(
        type="map",
        prompt="Where was the Future Sekimeiya activated?",
        map_number=3,
        correct_answers=("MECHANICAL ROOM",),
        )

    c5_answers["choice isla a past travel"] = PlayerQuestion(
        type="choice",
        #prompt="The reason she was able to go many days back was...",
        prompt="The reason she was sent back many days was...",
        choices=(
            ("Someone took the Past Sekimeiya out of the cabinet before the group locked themselves up.", "TAKEN OUT EARLY"),
            ("Due to a bed sheet.", "BED SHEET"),
            ("When Atsuki and Shiroya left the bedroom, Isla hadn't traveled to the past yet.", "HADNT TRAVELED YET"),
            ("Isla world switched when Akaro went to the future.", "WORLD SWITCH"),
            ),
        correct_answers=("BED SHEET",),
        )

    c5_answers["char took fake sekimeiya akaro"] = PlayerQuestion(
        type="character",
        prompt="Who took the fake Sekimeiya?",
        show_timeline=True,
        correct_answers=("AKARO A",),
        )

    c5_answers["choice b6 future travel"] = PlayerQuestion(
        type="choice",
        prompt="We found a Sekimeiya on the floor of room B6.",
        choices=(
            ("We touched it and went to the past.", "PAST"),
            ("We touched it and went to the future.", "FUTURE"),
            ),
        correct_answers=("FUTURE",),
        )

    c5_answers["char heard erina hallway"] = PlayerQuestion(
        type="character",
        prompt="Who did they hear in the hallways?",
        show_timeline=True,
        correct_answers=("ERINA B",),
        )

    c5_answers["choice bad end c1 people"] = PlayerQuestion(
        type="choice",
        prompt="Before he died, Atsuki saw 4 people he recognized.",
        choices=(
            ("Ido, Shiroya, Erina, and Suripo.", "ISES"),
            ("Ido, Shiroya, Katei, and Isla.", "ISKI"),
            ("Ido, Shiroya, Suripo, and himself.", "ISSH"),
            ),
        correct_answers=("ISES",),
        )

    c5_answers["choice bad end c1 impossible"] = PlayerQuestion(
        type="choice",
        #prompt="Two impossibilities prevented this from happening. One was the butterfly effect.",
        prompt="The butterfly effect prevented this from happening.",
        choices=(
            ("The other was Atsuki's death.", "ATSUKIS DEATH"),
            ("The other was the lack of a world switch.", "NO WORLD SWITCH"),
            ("The other was Shiroya's existence.", "SHIROYAS EXISTENCE"),
            ),
        correct_answers=("ATSUKIS DEATH",),
        )

    c5_answers["char katei b killer"] = PlayerQuestion(
        type="character",
        prompt="Who killed Katei B?",
        show_timeline=True,
        correct_answers=("ERINA B",),
        )

    c5_answers["choice sai stop attack"] = PlayerQuestion(
        type="choice",
        prompt="Sai stopped his attack...",
        choices=(
            ("When he saw the security camera.", "SECURITY CAMERA"),
            ("When he heard a sound.", "HEARD SOUND"),
            ("When he saw Atsuki hadn't cried.", "WHEN HE DOESNT CRY"),
            ),
        correct_answers=("SECURITY CAMERA",),
        )

    c5_answers["choice erina atsuki note"] = PlayerQuestion(
        type="choice",
        prompt="What's the origin of the note that Atsuki read?",
        choices=(
            ("Erina gave Atsuki a note with different contents.", "DIFFERENT CONTENTS"),
            ("Erina didn't find the note where Atsuki had thrown it.", "NOTE LOCATION"),
            ("Two identical notes had been written.", "TWO IDENTICAL NOTES"),
            ("Atsuki had the note in his pocket before he traveled to the past.", "PAST TRAVEL"),
            ),
        correct_answers=("NOTE LOCATION",),
        )

    c5_answers["choice sai event room switch"] = PlayerQuestion(
        type="choice",
        #prompt="In the event room, when Erina activated the Sekimeiya, the world around us changed, and Sai was the only one to travel through time.",
        prompt="Sai traveled when Erina caused the world switch.",
        choices=(
            ("He traveled to the past.", "PAST"),
            ("He traveled to the future.", "FUTURE"),
            ),
        correct_answers=("FUTURE",),
        )

    c5_answers["choice shiroya future contradiction"] = PlayerQuestion(
        type="choice",
        #prompt="She had told me that she'd traveled to November 30th, but there's a contradiction.",
        prompt="What contradicts her supposed travel to Nov 30th?",
        choices=(
            ("The number of days she spent in the past.", "DAYS SPENT"),
            ("The place where she stayed.", "PLACE STAYED"),
            ("The location where she appeared.", "APPEARING LOCATION"),
            ),
        correct_answers=("APPEARING LOCATION",),
        )

    c5_answers["text duct tape"] = PlayerQuestion(
        type="text",
        prompt="A USB drive and ____ ____.",
        text_bg="bg text25",
        correct_answers=("DUCT TAPE","TAPE ROLL"),
        )

    c5_answers["choice katei shiroyas name"] = PlayerQuestion(
        type="choice",
        prompt="Katei said Shiroya's name...",
        choices=(
            ("Because on the news, Miiya's face had been above Shiroya's name.", "NEWS"),
            ("Because Miiya was wearing Shiroya's clothes.", "CLOTHES"),
            ("Because of Shiroya's ticket.", "TICKET"),
            ),
        correct_answers=("TICKET",),
        )

    c5_answers["choice katei second bundle"] = PlayerQuestion(
        type="choice",
        #prompt="When Katei was confronted, he showed them a set of keys belonging to Naomi. However, that's when he himself realized something.",
        prompt="When Katei showed them the keys, he realized...",
        choices=(
            ("That the keyring was there.", "HAD BUNDLE"),
            ("That there was a second set of keys under it.", "SECOND BUNDLE"),
            ("That a key was missing from the ring.", "MISSING KEY"),
            ),
        correct_answers=("SECOND BUNDLE",),
        )

    c5_answers["choice elevator enabled c"] = PlayerQuestion(
        type="choice",
        #prompt="Sai tried to call the elevator on the sixth floor, but it didn't come after waiting.",
        prompt="The elevator didn't come when called on F6.",
        choices=(
            ("The elevator was still disabled.", "DISABLED"),
            ("The elevator had already been enabled.", "ENABLED"),
            ),
        correct_answers=("ENABLED",),
        )

    #c5_answers["choice elevator didnt come c"] = PlayerQuestion(
    #    type="choice",
    #    prompt="The elevator didn't come when Sai called the elevator later.",
    #    choices=(
    #        ("It was open on another floor.", "ANOTHER FLOOR"),
    #        ("Sai didn't call it.", "DIDNT CALL IT"),
    #        ("It was already on that floor.", "ALREADY THERE"),
    #        ),
    #    correct_answers=("ALREADY THERE",),
    #    )

    c5_answers["char suripo c killer"] = PlayerQuestion(
        type="character",
        prompt="Who killed Suripo C?",
        show_timeline=True,
        correct_answers=("AKARO C",),
        )

    #c5_answers["choice sai c behavior partition"] = PlayerQuestion(
    #    type="choice",
        #prompt="After discovering the storeroom partition, someone's behavior differed from B's.",
    #    prompt="After the discovery, someone's behavior differed.",
    #    choices=(
    #        ("Sai's.", "SAI"),
    #        ("Katei's.", "KATEI"),
    #        ("Akaro's.", "AKARO"),
    #        ),
    #    correct_answers=("SAI",),
    #    )

    c5_answers["choice bad end c2 change"] = PlayerQuestion(
        type="choice",
        prompt="Your choice changed Miiya into Shiroya, and...",
        choices=(
            ("Naomi's death.", "NAOMI"),
            ("Katei's absence.", "KATEI"),
            ("The appearance of Isla's friend.", "ISLA"),
            ),
        correct_answers=("KATEI",),
        )


    #c5_answers["text two people elevator"] = PlayerQuestion(
    #    type="text",
    #    prompt="Who were the two people in the elevator?",
    #    text_bg="bg text28",
    #    correct_answers=("NAOMI C AND SHIROYA A", "SHIROYA A AND NAOMI C"),
    #    )

    c5_answers["choice erina a death"] = PlayerQuestion(
        type="choice",
        #prompt="Over thirty minutes later, a new dead body was found near the hallway C stairs.",
        prompt="30 minutes later, a body was found near the stairs.",
        choices=(
            ("Erina A's.", "A"),
            ("Erina B's.", "B"),
            ("Erina C's.", "C"),
            ),
        correct_answers=("A",),
        )

    c5_answers["char erina a killer"] = PlayerQuestion(
        type="character",
        prompt="Who killed Erina A?",
        show_timeline=True,
        correct_answers=("MIIYA C",),
        )

    c5_answers["choice atsuki c report erina"] = PlayerQuestion(
        type="choice",
        #prompt="Atsuki reported details surrounding Erina's death. In reality...",
        prompt="Atsuki reported details surrounding Erina's death.",
        choices=(
            ("Atsuki was lying.", "LYING"),
            ("Someone they hadn't found was the killer.", "MYSTERY PERSON X"),
            ("A Sekimeiya had been used.", "SEKIMEIYA"),
            ),
        correct_answers=("SEKIMEIYA",),
        )

    #c5_answers["choice past sekimeiya after atsuki"] = PlayerQuestion(
    #    type="choice",
    #    prompt="What happened to the Past Sekimeiya in World A after Atsuki A touched it?",
    #    choices=(
    #        ("Someone else touched the Past Sekimeiya.", "TOUCHED"),
    #        ("No one else touched the Past Sekimeiya.", "NOT TOUCHED"),
    #        ),
    #    correct_answers=("NOT TOUCHED",),
    #    )

    c5_answers["choice erina a killer appear"] = PlayerQuestion(
        type="choice",
        #prompt="How did Erina's killer show up before her and push her off the stairs?",
        prompt="How did Erina's killer appear at the stairs?",
        choices=(
            ("Erina traveled through time after she saw who she thought was the killer.", "ERINA TRAVELED"),
            ("Her killer world switched in front of her.", "WORLD SWITCH"),
            ("Her killer had traveled from the past.", "KILLER TRAVELED"),
            ),
        correct_answers=("KILLER TRAVELED",),
        )

    #c5_answers["choice atsuki lie about footprints"] = PlayerQuestion(
    #    type="choice",
    #    prompt="Did Atsuki make that connection? Did he choose to omit the fact that he hadn't heard Miiya's footsteps above him?",
    #    choices=(
    #        ("Yes.", "YES"),
    #        ("No.", "NO"),
    #        ),
    #    correct_answers=("NO",),
    #    )

    c5_answers["choice world switch before search"] = PlayerQuestion(
        type="choice",
        prompt="But the search didn't yield any results...",
        choices=(
            ("Because they world switched before it ended.", "WORLD SWITCHED"),
            ("Because there was nobody to find.", "NOBODY TO FIND"),
            ("Because someone who could've been found world switched before they were found.", "SOMEONE CAN WORLD SWITCH"),
            ("Because someone who could've been found traveled to the past.", "SOMEONE TRAVELED TO PAST"),
            ),
        correct_answers=("WORLD SWITCHED",),
        )

    c5_answers["choice world switch at office"] = PlayerQuestion(
        type="choice",
        prompt="The C group world switched...",
        choices=(
            ("In the attic.", "ATTIC"),
            ("On an office floor.", "OFFICE FLOOR"),
            ("On the crystal floor.", "CRYSTAL FLOOR"),
            ),
        correct_answers=("OFFICE FLOOR",),
        )

    c5_answers["char naomi c world switch"] = PlayerQuestion(
        type="character",
        prompt="Who else world switched to world B?",
        show_timeline=True,
        correct_answers=("NAOMI C",),
        )

    c5_answers["choice naomi c alive"] = PlayerQuestion(
        type="choice",
        prompt="Naomi C, who was in the lobby, world switched...",
        choices=(
            ("Even though she was dead.", "DEAD"),
            ("Because she was still alive.", "ALIVE"),
            ("Because she had a twin.", "TWIN"),
            ),
        correct_answers=("ALIVE",),
        )

    c5_answers["map 2f sekimeiya position"] = PlayerQuestion(
        type="map",
        #prompt="On the second floor, where was the Future Sekimeiya when the world switch occurred?",
        prompt="At the world switch, the Future Sekimeiya was in...",
        map_number=4,
        correct_answers=("OUTSIDE PARTITIONS",),
        )

    #c5_answers["choice sekimeiya cabinet bedsheet"] = PlayerQuestion(
    #    type="choice",
    #    prompt="Which Sekimeiya was in the cabinet?",
    #    choices=(
    #        ("The Past Sekimeiya.", "PAST"),
    #        ("The Future Sekimeiya.", "FUTURE"),
    #        ("The fake Sekimeiya.", "FAKE"),
    #        ),
    #    correct_answers=("PAST",),
    #    )

    c5_answers["choice miiya sleep switch"] = PlayerQuestion(
        type="choice",
        #prompt="And a long time later, Miiya had the urge to lie down. She went to the attic, where she fell asleep.",
        prompt="She fell asleep in the attic.",
        choices=(
            ("When she woke up, she world switched again.", "MIIYA SWITCHED"),
            ("When she woke up, she realized that Shiroya had world switched to her world.", "SHIROYA SWITCHED"),
            ("While she slept, she had a nightmare.", "NIGHTMARE"),
            ),
        correct_answers=("MIIYA SWITCHED",),
        )

    c5_answers["choice miiya sleep switch problem"] = PlayerQuestion(
        type="choice",
        prompt="What's wrong with Miiya's world switch?",
        choices=(
            ("The world where she appeared.", "WORLD"),
            ("That the light turned on.", "LIGHT"),
            ("That Atsuki didn't world switch with her.", "ATSUKI"),
            ),
        correct_answers=("WORLD",),
        )

    c5_answers["choice miiya sleep switch problem2"] = PlayerQuestion(
        type="choice",
        prompt="Why did Miiya go from world C to world B?",
        choices=(
            ("While she slept, she went to world A first.", "WENT TO A FIRST"),
            ("She never left world A.", "NEVER LEFT A"),
            ("Shiroya was not in world B.", "SHIROYA NOT IN B"),
            ("There's another reason.", "ANOTHER REASON"),
            ),
        correct_answers=("ANOTHER REASON",),
        )

    c5_answers["choice backward world switch"] = PlayerQuestion(
        type="choice",
        prompt="Another backward world switch happened...",
        choices=(
            ("When Shiroya and Naomi went to world A.", "SHIROYA A"),
            ("When Sai went to world A.", "SAI A"),
            ("When Shiroya and Atsuki went to world C.", "SHIROYA C"),
            ),
        correct_answers=("SAI A",),
        )

    c5_answers["choice backward world switch2"] = PlayerQuestion(
        type="choice",
        prompt="A third backward world switch happened...",
        choices=(
            ("When Atsuki and Erina returned to world B.", "ATSUKI RETURN TO B"),
            ("When Erina, Shiroya, and Atsuki went to world C.", "ATSUKI TO C"),
            ("When Shiroya returned to world B.", "SHIROYA RETURN TO B"),
            ),
        correct_answers=("ATSUKI RETURN TO B",),
        )

    c5_answers["choice backward world switch3"] = PlayerQuestion(
        type="choice",
        prompt="What is common between these three examples?",
        choices=(
            ("Both Sekimeiya were very close.", "SEKIMEIYA CLOSE"),
            ("Nobody touched the Sekimeiya in their world.", "NOBODY TOUCHED"),
            ("It was the second time they had world switched.", "SECOND TIME"),
            ),
        correct_answers=("NOBODY TOUCHED",),
        )

    c5_answers["choice backward world switch4"] = PlayerQuestion(
        type="choice",
        prompt="Is there another shared similarity?",
        choices=(
            ("The Sekimeiya had gathered energy for too long.", "TOO MUCH ENERGY"),
            ("It happened at specific intervals of time.", "TIME INTERVAL"),
            ("The world switch was activated from the previous world.", "PREVIOUS WORLD"),
            ),
        correct_answers=("PREVIOUS WORLD",),
        )

    c5_answers["char erina atsuki pulled"] = PlayerQuestion(
        type="character",
        prompt="Who pulled Erina and Atsuki from world B?",
        show_timeline=True,
        correct_answers=("ATSUKI A",),
        )

    c5_answers["char screwdriver"] = PlayerQuestion(
        type="character",
        prompt="Miiya and _'s fingerprints were on the screwdriver.",
        show_timeline=True,
        correct_answers=("NAOMI C",),
        )


    ####################
    ## Post-Game Answers
    ####################
    if 'post' not in persistent.analytics_logged:
        persistent.analytics_logged['post'] = python_dict()

    postgame_answers = PlayerQuestionsContainer(persistent.analytics_logged['post'])

    postgame_answers["Choice Replay"] = PlayerQuestion(
        type="choice",
        prompt="Would you ever replay?",
        choices=(
            ("Yes", "YES"),
            ("Maybe", "PROBABLY"),
            ("Probably not", "PROBABLY NOT"),
            ("No", "NO"),
            ),
        )

    postgame_answers["Choice SolveMystery"] = PlayerQuestion(
        type="choice",
        prompt="Did you try to solve the mysteries?",
        choices=(
            ("Yes", "YES"),
            ("I tried initially, but later let things play out", "INITIALLY"),
            ("I started trying later", "LATER"),
            ("No", "NO"),
            ),
        )

    postgame_answers["Choice SpoilerKnowledge"] = PlayerQuestion(
        type="choice",
        prompt="How much did you know before playing?",
        choices=(
            ("Nothing", "NOTHING"),
            ("The game involves time travel/minor event spoilers", "MINOR"),
            ("Major character or plot spoilers", "BIG SPOILIES"),
            ),
        )

    postgame_answers["Choice FirstPlot"] = PlayerQuestion(
        type="choice",
        prompt="Is this one of your first plot-focused VNs?",
        choices=(
            ("Yes", "YES"),
            ("First plot VN without gameplay", "GAMEPLAY"),
            ("No", "NO"),
            ),
        )

    postgame_answers["Choice References"] = PlayerQuestion(
        type="choice",
        prompt="Did you notice references to other works?",
        choices=(
            ("Many", "MANY"),
            ("A few", "FEW"),
            ("No", "NO"),
            ),
        )

    postgame_answers["Choice DiscoveryVector"] = PlayerQuestion(
        type="choice",
        prompt="How did you find out about this game?",
        choices=(
            ("Word of mouth / Friend recommendation", "FRIEND"),
            ("Social media", "SOCIAL"),
            ("Game store", "STORE"),
            ("Article", "ARTICLE"),
            ("Other", "OTHER"),
            ),
        )


    postgame_answers["Choice IslaPronounce"] = PlayerQuestion(
        type="choice",
        prompt="How do you pronounce Isla?",
        choices=(
            ("Ai-la", "AILA"),
            ("Is-la", "ISSLA"),
            ("Iz-la", "IZLA"),
            ("Ee-su-ra", "EESURA"),
            ("Other", "OTHER"),
            ),
        )

    postgame_answers["Choice FavSekimeiya"] = PlayerQuestion(
        type="choice",
        prompt="Favorite Sekimeiya",
        choices=(
            ("Past", "PAST"),
            ("Future", "FUTURE"),
            ("Fake", "FAKE"),
            ),
        )

    postgame_answers["Rank Chapter"] = PlayerQuestion(
        type="rank",
        prompt="Chapter Rank",
        choices=(
            ("Ch 1", "1"),
            ("Ch 2", "2"),
            ("Ch 3", "3"),
            ("Ch 4", "4"),
            ("Ch 5", "5"),
            ),
        )

    postgame_answers["Rank Character"] = PlayerQuestion(
        type="rank",
        prompt="Character Rank",
        choices=(
            ("Akaro", "AKARO"),
            ("Atsuki", "ATSUKI"),
            ("Erina", "ERINA"),
            ("Isla", "ISLA"),
            ("Katei", "KATEI"),
            ("Miiya", "MIIYA"),
            ("Naomi", "NAOMI"),
            ("Sai", "SAI"),
            ("Shiroya", "SHIROYA"),
            ),
        )

    postgame_answers["Rank SpecialFunction"] = PlayerQuestion(
        type="rank",
        prompt="Special Function Rank",
        choices=(
            ("Chart", "CHART"),
            ("Map", "MAP"),
            ("Notes", "NOTES"),
            ("Playtime", "TIME"),
            ("Search", "SEARCH"),
            ("Stats", "STATS"),
            ),
        )


    ####################
    ## Post-Game Answers
    ####################
    pref_answers = PlayerQuestionsContainer(persistent.analytics_retrieved['prefs'])

    pref_answers["Fullscreen"] = PlayerQuestion(
        type="choice",
        prompt="Fullscreen",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Resolution"] = PlayerQuestion(
        type="text",
        prompt="Resolution",
        )



    pref_answers["Sprite Darken"] = PlayerQuestion(
        type="choice",
        prompt="Darken Sprites When Not Speaking",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Sprite Darken Fade"] = PlayerQuestion(
        type="choice",
        prompt="Darken Sprites With Fade",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Sprite Darken Amount"] = PlayerQuestion(
        type="num_range",
        prompt="Fade Sprites When They Darken",
        min_range = 0,
        min_text = "Darkest",
        max_range = 100,
        max_text = "Lightest",
    )




    pref_answers["Skip Unseen"] = PlayerQuestion(
        type="choice",
        prompt="Skip Unseen Text",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Skip Choices"] = PlayerQuestion(
        type="choice",
        prompt="Skip After Choices",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Transitions"] = PlayerQuestion(
        type="choice",
        prompt="Transitions",
        choices=(
            ("Enabled", "2"),
            ("Disabled", "0"),
        ),
    )



    pref_answers["Volume Music"] = PlayerQuestion(
        type="num_range",
        prompt="Volume - Music",
        min_range = 0,
        min_text = "Lowest",
        max_range = 100,
        max_text = "Highest",
    )

    pref_answers["Volume SFX"] = PlayerQuestion(
        type="num_range",
        prompt="Volume - SFX",
        min_range = 0,
        min_text = "Lowest",
        max_range = 100,
        max_text = "Highest",
    )

    pref_answers["Volume System"] = PlayerQuestion(
        type="num_range",
        prompt="Volume - System",
        min_range = 0,
        min_text = "Lowest",
        max_range = 100,
        max_text = "Highest",
    )

    pref_answers["Volume Mute Defocus"] = PlayerQuestion(
        type="choice",
        prompt="Mute if the Game Isn't Focused",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )



    pref_answers["Minimap"] = PlayerQuestion(
        type="choice",
        prompt="Always Display Minimap",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Map Prev Positions"] = PlayerQuestion(
        type="choice",
        prompt="Display Previous Map Positions",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Click Short Pauses"] = PlayerQuestion(
        type="choice",
        prompt="Click Through Short Pauses",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    #pref_answers["C5 Questions Enabled"] = PlayerQuestion(
    #    type="choice",
    #    prompt="Enable Questions in Chapter 5",
    #    choices=(
    #        ("Yes", "true"),
    #        ("No", "false"),
    #    ),
    #)


    pref_answers["Textbox Style"] = PlayerQuestion(
        type="choice",
        prompt="Textbox Style",
        choices=(
            ("Style 1", "1"),
            ("Style 2", "2"),
            ("Style 3", "3"),
            ("Style 4", "4"),
        ),
    )

    pref_answers["Textbox Width"] = PlayerQuestion(
        type="num_range",
        prompt="Textbox Width",
        min_range = 0,
        min_text = "Narrowest",
        max_range = 100,
        max_text = "Widest",
    )

    pref_answers["Textbox Opacity"] = PlayerQuestion(
        type="num_range",
        prompt="Textbox Opacity",
        min_range = 0,
        min_text = "Transparent",
        max_range = 100,
        max_text = "Opaque",
    )



    pref_answers["Text Outline"] = PlayerQuestion(
        type="choice",
        prompt="Text Outline",
        choices=(
            ("Style 1", "1"),
            ("Style 2", "2"),
            ("Style 3", "3"),
        ),
    )

    pref_answers["Text Speed"] = PlayerQuestion(
        type="num_range",
        prompt="Text Speed",
        min_range = 1,
        min_text = "Slowest",
        max_range = 201,
        max_text = "Fastest",
        special_value = 0,
        special_text = "Instant"
    )

    pref_answers["Text Auto"] = PlayerQuestion(
        type="num_range",
        prompt="Auto Delay",
        min_range = 1,
        min_text = "Fastest",
        max_range = 10,
        max_text = "Slowest",
    )



    pref_answers["Font"] = PlayerQuestion(
        type="choice",
        prompt="Font",
        choices=(
            ("Regular", "fonts/Cabin-Regular2.ttf"),
            ("Medium", "fonts/Cabin-Medium2.ttf"),
            ("Bold", "fonts/Cabin-Bold2.ttf"),
            ("DejaVuSans", "DejaVuSans.ttf"),
            ("Han Light (Simplified Chinese)", "fonts/SourceHanSansSC-Light-2.otf"),
        ),
    )

    pref_answers["24 Hour Format"] = PlayerQuestion(
        type="choice",
        prompt="Time Format",
        choices=(
            ("24-Hour", "true"),
            ("12-Hour", "false"),
        ),
    )



    pref_answers["Speaker Indicator"] = PlayerQuestion(
        type="choice",
        prompt="Speaker Indicator",
        choices=(
            ("Symbol", "symbol"),
            ("None", "none"),
        ),
    )

    pref_answers["Color Text"] = PlayerQuestion(
        type="choice",
        prompt="Colored Text",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    pref_answers["Color Speaker"] = PlayerQuestion(
        type="choice",
        prompt="Colored Speaker Indicator",
        choices=(
            ("Yes", "true"),
            ("No", "false"),
        ),
    )

    ####################
    ## Time Answers
    ####################
    time_answers = PlayerQuestionsContainer(persistent.analytics_retrieved['playtimes'])

    time_answers["game"] = PlayerQuestion(
        type="time",
        prompt="In-Game"
    )

    time_answers["search"] = PlayerQuestion(
        type="time",
        prompt="Search Screen"
    )

    time_answers["notes"] = PlayerQuestion(
        type="time",
        prompt="Notes Screen"
    )

    time_answers["other"] = PlayerQuestion(
        type="time",
        prompt="Other Screens"
    )

    time_answers["total"] = PlayerQuestion(
        type="time",
        prompt="Total Time (Focused)"
    )

    time_answers["unfocused"] = PlayerQuestion(
        type="time",
        prompt="Unfocused Time"
    )

    time_answers["all"] = PlayerQuestion(
        type="time",
        prompt="Total Time (Focused + Unfocused)"
    )

    time_answers["C1"] = PlayerQuestion(
        type="time",
        prompt="Chapter 1"
    )

    time_answers["C2"] = PlayerQuestion(
        type="time",
        prompt="Chapter 2"
    )

    time_answers["C3"] = PlayerQuestion(
        type="time",
        prompt="Chapter 3"
    )

    time_answers["C4"] = PlayerQuestion(
        type="time",
        prompt="Chapter 4"
    )

    time_answers["C5"] = PlayerQuestion(
        type="time",
        prompt="Chapter 5"
    )

    ####################
    ## Other Answers - Demographics, platform, etc
    ####################
    other_answers = PlayerQuestionsContainer(persistent.analytics_retrieved['other'])

    other_answers["Country"] = PlayerQuestion(
        type="text",
        prompt="Country",
    )

    other_answers["Correct Percentage"] = PlayerQuestion(
        type="num_range",
        prompt="Questions Answered Correctly",
    )

    other_answers["Platform"] = PlayerQuestion(
        type="text",
        prompt="Platform",
    )

    #other_answers["Pirate"] = PlayerQuestion(
    #    type="choice",
    #    prompt="Status",
    #    choices=(
    #        ("Genuine", "false"),
    #        ("Pirated", "true"),
    #    ),
    #)


    """
    c5_answers["char "] = PlayerQuestion(
        type="character",
        prompt="",
        show_timeline=True,
        correct_answers=("",),
        )

    c5_answers["map "] = PlayerQuestion(
        type="map",
        prompt="",
        map_number=1,
        correct_answers=("",),
        )

    c5_answers["text "] = PlayerQuestion(
        type="text",
        prompt="",
        hint_text="",
        text_bg="bg text",
        correct_answers=("",),
        )

    c5_answers["choice "] = PlayerQuestion(
        type="choice",
        prompt="",
        choices=(
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("full", "short"),
            ),
        correct_answers=("",),
        )

    postgame_answers["rank "] = PlayerQuestion(
        type="rank",
        prompt="",
        choices=(
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ),
        )

    pref_answers[""] = PlayerQuestion(
        type="num_range",
        prompt="",
        min_range = 0,
        min_text = "Minimum",
        max_range = 100,
        max_text = "Maximum",
        special_value = 0,
        special_text = "Special",
    )
    """

    def ShowQuestion(name):
        c5_answers.ShowQuestion(name)

    def MarkQuestion(name):
        persistent.analytics_logged['c5 answers'][name] = True