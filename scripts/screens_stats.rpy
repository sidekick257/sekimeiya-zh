init -10 python:
    from collections import OrderedDict
    import store
    from store import persistent, config, preferences
    from store import Window, HBox, VBox, Frame, Text, TextButton, Button, Bar, Null, Image
    from store import SetDict, SetField, Action, DictEquality, Function, NullAction

    store.statistics_current_page = python_dict()
    store.statistics_changed_page = python_dict()

    class Histogram(renpy.display.layout.MultiBox):
        width = 500
        title_height = 53
        page_button_height = 33

        bar_width = 30
        bar_height = 360
        bar_spacing = 10

        color_selected = "#0F0"
        color_neutral = "#FFF"

        cache = python_dict()
        def __new__(cls, question_name=None, *args, **kwargs):
            """ Initilize the class and start processing """
            if question_name in Histogram.cache:
                return Histogram.cache[question_name]

            rv = super(Histogram, cls).__new__(cls)
            if question_name:
                cls.cache[question_name] = rv
            return rv

        def __copy__(self):
            return self

        def __init__(self, question_name, data, selected_answer=None, correct_answers=None, answers_obj=None, type=None, is_postgame=False, is_answer_page=True, total_count=0, title="", title_action=None, **kwargs):
            """
            ## data is of the form {"Bar name": count}
            """
            self.answers_obj = answers_obj or store.c5_answers

            if correct_answers is None:
                correct_answers = python_list()
            if data is None:
                data = {"No data": 1}

            self.question_name = question_name
            self.question_obj = self.answers_obj.GetQuestion(self.question_name)
            self.selected_answer = selected_answer
            self.correct_answers = correct_answers
            self.is_postgame = is_postgame
            self.is_answer_page = is_answer_page
            self.total_count = total_count
            self.horizontal_bars = True
            self.show_bars = True
            self.title = title
            self.title_action = title_action

            if self.question_name not in store.statistics_current_page:
                store.statistics_current_page[self.question_name] = 0
            if self.question_name not in store.statistics_changed_page:
                store.statistics_changed_page[self.question_name] = False
            self.page = store.statistics_current_page[self.question_name]

            self.type = type or self.question_obj.type
            if self.type == "rank":
                self.data = OrderedDict(sorted(data.items(), key=lambda kv: kv[1]))
                self.max_value = len(self.data)
                self.sum_value = self.total_count
            elif self.type == "num_range":
                self.data = data
                self.max_value = max(1,max(self.data.values()))
                self.sum_value = sum(self.data.values())
            elif self.type == "time":
                self.data = data
            else:
                self.data = OrderedDict(sorted(data.items(), key=lambda kv: -kv[1]))
                self.max_value = max(1,max(self.data.values()))
                self.sum_value = sum(self.data.values())

            if is_postgame:
                self.top_count = len(self.question_obj.choices)
                if self.question_data.type=="choice":
                    self.max_pages = 1
                else:
                    self.max_pages = len(self.data)+1 #len(self.question_obj.choices)+1
            elif self.answers_obj == pref_answers:
                self.max_pages = 1
                if self.question_obj.type == "num_range":
                    self.top_count = len(self.data)
                else:
                    self.top_count = 5
            elif self.answers_obj == other_answers:
                self.max_pages = 1
                self.top_count = 5
                if self.question_obj.type in ["text", "num_range"]:
                    self.top_count = 10
                if self.question_name == "Pirate":
                    self.selected_answer = str(persistent.copy_detected).lower()
            elif self.answers_obj == time_answers:
                self.max_pages = 1
                if 'count' in self.data:
                    self.sum_value = self.data["count"]
                else:
                    ## Happens if we haven't gotten updated data yet
                    self.sum_value = 0

            else:
                self.top_count = 5
                self.max_pages = 2

            if self.type=="time" or (not self.is_postgame and self.page == 1):
                self.height = 140
            else:
                self.height = min(self.top_count, len(self.data))*(self.bar_width+self.bar_spacing) + self.page_button_height
            self.height += self.title_height

            # Pass additional properties on to the renpy.Displayable constructor.
            layout = "fixed"
            if self.type == "question":
                layout = "vertical"

            if self.is_postgame:
                kwargs["spacing"] = 5

            super(Histogram, self).__init__(layout=layout, xsize=self.width, ysize=self.height, **kwargs)

            self.createNavigation()
            if not self.is_postgame:
                if self.type == "time":
                    self.createTimeData()
                elif self.page == 0:
                    self.createHistogram()
                else:
                    self.createTimeData()

        def clearCacheEntry(self):
            del self.cache[self.question_name]

        def PageChanged(self):
            store.statistics_changed_page[self.question_name] = True

        def createNavigation(self):
            self.add(Button(
                Window(
                    Text(self.title, style="histogram_title_text"),
                    background=None,
                    xfill=True,
                    padding=(0,0,0,0),
                ),
                background = None,
                hover_background = "#fff2",
                xoffset = -2,
                action = self.title_action,
            ))

            ############
            ## Total votes, page buttons
            ############
            if self.is_postgame and not self.is_answer_page:
                ypos = 0
                self.add(Null(height=10))
            else:
                ypos = self.title_height
                self.add(Text("Total: {:1.0f}".format(self.sum_value), style="histogram_total_text", xpos=26, ypos=ypos))

            if self.is_postgame and self.is_answer_page and self.page==0:
                self.add(TextButton("Change Answer", action=Function(self.changeAnswer), xalign=0.5, ypos=ypos-3))

            if self.is_answer_page and self.max_pages>1:
                if self.page > 0:
                    if self.max_pages==2:
                        xpos=428
                    else:
                        xpos=368


                    button = TextButton(
                        "Prev",
                        xpos=xpos,
                        ypos=ypos,
                        yoffset=-3,
                        )
                    ## Done this way so we can reference the button and force a refresh when clicked
                    button.action = [Function(self.PageChanged), SetDict(store.statistics_current_page, self.question_name, self.page-1), Function(button.per_interact)]

                    self.add(button)


                if self.page < self.max_pages-1:
                    button = TextButton(
                        "Next",
                        xpos=428,
                        ypos=ypos,
                        yoffset=-3,
                        )
                    ## Done this way so we can reference the button and force a refresh when clicked
                    button.action = [Function(self.PageChanged), SetDict(store.statistics_current_page, self.question_name, self.page+1), Function(button.per_interact)]

                    self.add(button)

        def createHistogram(self):
            #############
            ## Get the top 5 answers.
            ## The player's seleceted answer MUST be in this list, as well as at least one correct answer
            ## If it's very low occurance, force it into the lowest places
            ############
            displayed_data = OrderedDict()

            if self.is_postgame:
                ## Postgame
                for label, val in self.data.items():
                    displayed_data[label] = val

            else:
                ## C5 Answer
                got_player_choice = False
                got_correct_answer = False

                ## Make sure the correct answer and selected answers are displayed
                forced_answers = python_list()
                for label, val in self.data.items():
                    if got_player_choice and got_correct_answer:
                        break

                    is_player_choice = False
                    is_correct_answer = False
                    if label==self.selected_answer:
                        is_player_choice = True
                    if label in self.correct_answers:
                        is_correct_answer = True

                    if is_player_choice and not got_player_choice:
                        forced_answers.append(label)
                        got_player_choice = True
                    if is_correct_answer and not got_correct_answer:
                        if label not in forced_answers:
                            forced_answers.append(label)
                        got_correct_answer = True

                for label, val in self.data.items():
                    if len(displayed_data) == self.top_count:
                        break
                    if len(displayed_data) < self.top_count-len(forced_answers):
                        displayed_data[label] = val
                    else:
                        displayed_data[forced_answers[0]] = self.data[forced_answers[0]]

                    if label in forced_answers:
                        del forced_answers[0]

            ############
            ## Bars, text, and percentage
            ############
            for idx, label in enumerate(displayed_data):
                val = displayed_data[label]
                if label == self.selected_answer:
                    color = self.color_selected
                    bar_type = "selected"
                else:
                    color = self.color_neutral
                    bar_type = "neutral"

                if self.horizontal_bars:
                    if self.type == "rank" and self.page==0:
                        width = max(10, int(self.bar_height* (1-(val-1)/self.max_value)))
                    else:
                        width = max(10, int(self.bar_height* val/self.max_value))
                    height = self.bar_width

                    xpos = 70
                    ypos = idx*(self.bar_width+self.bar_spacing) + self.page_button_height
                    ypos += self.title_height

                    if self.type == "rank" and self.page == 0:
                        ## Score out of 10
                        self.add(
                            Window(Text(
                                "{:2.1f}".format(val),
                                style="histogram_axis_text",
                                ),
                            style="histogram_axis",
                            xpos=0,
                            ypos=ypos)
                        )
                    else:
                        ## Percentage of respondents
                        self.add(
                            Window(Text(
                                "{:2.0f}%".format(100.0*val/self.sum_value),
                                style="histogram_axis_text",
                                ),
                            style="histogram_axis",
                            xpos=0,
                            ypos=ypos)
                        )
                else:
                    height = max(10, int(self.bar_height* val/self.max_value))
                    width = self.bar_width
                    xpos = idx*(self.bar_width+self.bar_spacing)
                    ypos = self.bar_height

                if self.show_bars:
                    bar = Frame("gui/stats/bar_{}.png".format(bar_type), 10, 10, xsize=width, ysize=height, xpos=xpos, ypos=ypos)
                    #bar = Solid(color, xsize=width, ysize=height, xpos=xpos, ypos=ypos)
                    self.add(bar)

                if self.horizontal_bars:
                    if self.type == "rank" and self.page > 0:
                        answer_full = label
                    else:
                        answer_full = self.answers_obj.GetAnswerFromRaw(self.question_name, label)

                    if len(answer_full)>=50:
                        answer_display = answer_full[0:45]+"..."
                    else:
                        answer_display = answer_full

                    if label in self.correct_answers:
                        hbox = HBox(style="histogram_bar_hbox", spacing=4, xpos=xpos+10, ypos=ypos)
                        hbox.add(Image("gui/stats/correct.png", yoffset=8))

                        hbox.add(Text(answer_display, style="histogram_bar_text"))
                        self.add(hbox)
                    else:
                        self.add(Text(answer_display, style="histogram_bar_text", xpos=xpos+10, ypos=ypos))

            store.statistics_changed_page[self.question_name] = False

        def createTimeData(self):
            if self.type == "time":
                if self.question_name not in persistent.analytics_retrieved['playtimes']:
                    return

                time_data = persistent.analytics_retrieved["playtimes"][self.question_name]
                your_time = 0
                if self.question_name in persistent.playtime:
                    your_time = persistent.playtime[self.question_name]

                table_data = (
                    ("You",
                        "{:,.0f} min".format(your_time/60.0),
                        "({:,.2f} hr)".format(your_time/3600.0)
                    ),
                    ("Percentile (25%)",
                        "{:,.0f} min".format(time_data["p25"]/60.0),
                        "({:,.2f} hr)".format(time_data["p25"]/3600.0),
                    ),
                    ("Percentile (50%)",
                        "{:,.0f} min".format(time_data["median"]/60.0),
                        "({:,.2f} hr)".format(time_data["median"]/3600.0),
                    ),
                    ("Percentile (75%)",
                        "{:,.0f} min".format(time_data["p75"]/60.0),
                        "({:,.2f} hr)".format(time_data["p75"]/3600.0),
                    ),
                    # ("Average",
                    #     "{:,.0f} min".format(time_data["avg"]/60.0),
                    #     "({:,.2f} hr)".format(time_data["avg"]/3600.0)
                    # ),
                    # ("Std Dev",
                    #     "{:,.0f} min".format(time_data["stddev"]/60.0),
                    #     "({:,.2f} hr)".format(time_data["stddev"]/3600.0)
                    # ),
                )

            else:
                if self.question_name not in persistent.analytics_retrieved["c5 answers times"]:
                    return

                time_data = persistent.analytics_retrieved["c5 answers times"][self.question_name]
                your_time = 0
                if self.question_name in persistent.c5_times:
                    your_time = persistent.c5_times[self.question_name]


                table_data = (
                    ("You",
                        "{:,.0f} sec".format(your_time),
                        "({:,.2f} min)".format(your_time/60.0)
                    ),
                    ("Percentile (25%)",
                        "{:,.0f} sec".format(time_data["p25"]),
                        "({:,.2f} min)".format(time_data["p25"]/60.0),
                    ),
                    ("Percentile (50%)",
                        "{:,.0f} sec".format(time_data["median"]),
                        "({:,.2f} min)".format(time_data["median"]/60.0),
                    ),
                    ("Percentile (75%)",
                        "{:,.0f} sec".format(time_data["p75"]),
                        "({:,.2f} min)".format(time_data["p75"]/60.0),
                    ),
                    # ("Average",
                    #     "{:,.0f} sec".format(time_data["avg"]),
                    #     "({:,.2f} min)".format(time_data["avg"]/60.0)
                    # ),
                    # ("Std Dev",
                    #     "{:,.0f} sec".format(time_data["stddev"]),
                    #     "({:,.2f} min)".format(time_data["stddev"]/60.0)
                    # ),
                )

            ypos = self.title_height
            w_vbox = VBox(xalign=0.5, ypos=ypos)
            w_vbox.add(Window(Text("Time Taken", style="stats_heading_text"), style="stats_heading"))
            for name, minutes, hours in table_data:
                w_vbox.add(HBox())
                w_vbox.child.add(Window(Text(name, style="stats_table_header_text"), style="stats_table_header"))
                w_vbox.child.add(Window(Text(minutes, style="stats_table_header_text"), style="stats_table_cell1"))
                w_vbox.child.add(Text(hours, style="stats_table_cell_text"))

            self.add(w_vbox)

    class RankingVoteDisplayable(Histogram):
        cache = python_dict()
        def __new__(cls, question_name, *args, **kwargs):
            """ Initilize the class and start processing """
            if question_name in RankingVoteDisplayable.cache:
                return RankingVoteDisplayable.cache[question_name]

            rv = super(RankingVoteDisplayable, cls).__new__(cls)
            cls.cache[question_name] = rv
            return rv

        def __copy__(self):
            return self

        def __init__(self, question_name, **kwargs):
            self.question_name = question_name
            self.question_data = store.postgame_answers.GetQuestion(question_name)

            if question_name in persistent.analytics_retrieved["post"]:
                data = persistent.analytics_retrieved["post"][question_name]

                if self.question_data.type == "rank":
                    ## Get the average score for each
                    avgs = python_dict()
                    for key, score_dict in data.items():
                        sum = 0
                        count = 0
                        for score, score_count in score_dict.items():
                            sum += int(score)*score_count
                            count += score_count

                        avgs[key] = 1.0*sum/count

                    data = avgs
                    kwargs["total_count"] = count
                else:
                    ## Make sure all answers exist
                    for choice in self.question_data.choices:
                        if choice[1] not in data:
                            data[choice[1]] = 0
            else:
                count = None
                data = {"": 1}

            # Pass additional properties on to the renpy.Displayable constructor.
            if self.question_name in persistent.analytics_logged["post"] or config.developer:
                if config.developer:
                    kwargs["selected_answer"] = None
                elif self.question_data.type == "choice":
                    kwargs["selected_answer"] = persistent.analytics_logged["post"][self.question_name]
                else:
                    kwargs["selected_answer"] = None

                super(RankingVoteDisplayable, self).__init__(
                    question_name,
                    data,
                    answers_obj = store.postgame_answers,
                    is_postgame = True,
                    is_answer_page = True,
                    title = self.question_data.prompt,
                    **kwargs
                    )
                self.createAnswer()
            else:
                super(RankingVoteDisplayable, self).__init__(
                    question_name,
                    data,
                    selected_answer=None,
                    type="question",
                    answers_obj = store.postgame_answers,
                    is_postgame = True,
                    is_answer_page = False,
                    title =  self.question_data.prompt,
                    **kwargs
                    )
                self.createQuestion()

        def createQuestion(self):
            if self.question_data.type == "rank":
                self.add(Text("Best to worst", size=14, color="#FFFB", xpos=212, xanchor=0.5))
                for choice in self.question_data.choices:
                    w_hbox = HBox(style="notes_hbox", spacing=12)
                    w_hbox.add(
                        Window(
                            Text(choice[0], xalign=1.0),
                            xsize=100,
                            yalign=0.5,
                            yoffset=6,
                            padding=(10,0,10,0),
                            background=None
                        )
                    )
                    if choice[1] in self.question_data.ranking:
                        w_hbox.add(
                            TextButton(
                                str(self.question_data.ranking[choice[1]]),
                                style="postgame_rank_button",
                                text_style="postgame_rank_button_text",
                            )
                        )
                    else:
                        w_hbox.add(
                            TextButton(
                                "?",
                                style="postgame_rank_button",
                                text_style="postgame_rank_button_text",
                                action = [SetDict(self.question_data.ranking, choice[1], len(self.question_data.ranking)+1), Function(self.clearCacheEntry)]
                            )
                        )
                    self.add(w_hbox)
                self.add(Null(height=20))

                w_hbox = HBox(style="notes_hbox", spacing=32, xpos=135)
                is_sensitive = len(self.question_data.ranking) == len(self.question_data.choices)
                w_hbox.add(TextButton("Submit", action=Function(self.sendAnswers), sensitive=is_sensitive))
                w_hbox.add(TextButton("Clear", action=[SetField(self.question_data, "ranking", python_dict()), Function(self.clearCacheEntry)], selected=False))
                self.add(w_hbox)

            elif self.question_data.type == "choice":
                for choice in self.question_data.choices:
                    self.add(
                        TextButton(
                            choice[0],
                            style="postgame_choice_button",
                            text_style="postgame_choice_button_text",
                            action=Function(self.sendAnswers, choice[1])
                        )
                    )

        def createAnswer(self):
            if True: #store.statistics_changed_page[self.question_name]:
                if self.question_name in persistent.analytics_retrieved["post"]:
                    if self.question_data.type == "rank":
                        data = persistent.analytics_retrieved["post"][self.question_name]
                        data_keys = sorted(data.keys())

                        if self.page == 0:
                            ## Get the average score for each rank
                            avgs = python_dict()
                            for key, score_dict in data.items():
                                sum = 0
                                count = 0
                                for score, score_count in score_dict.items():
                                    sum += int(score)*score_count
                                    count += score_count

                                avgs[key] = 1.0*sum/count

                            self.selected_answer = None
                            self.data = OrderedDict(sorted(avgs.items(), key=lambda kv: kv[1]))
                            self.max_value = len(data)
                            self.sum_value = self.total_count
                        else:
                            ## Get data for individual ranked options
                            ind_key = data_keys[self.page-1]
                            ind_data = data[ind_key]
                            self.max_value = 1
                            self.sum_value = 1

                            for idx in range(1, len(data_keys)+1):
                                key = str(idx)
                                if key in ind_data:
                                    val = ind_data[key]
                                    self.max_value = max(self.max_value, val)
                                    self.sum_value += val
                                else:
                                    ind_data[key] = 0

                            if "0" in ind_data:
                                del ind_data["0"]

                            self.data = OrderedDict(sorted(ind_data.items(), key=lambda kv: kv[0]))
                            if config.developer:
                                self.selected_answer = None
                            else:
                                self.selected_answer = str(persistent.analytics_logged["post"][self.question_name][ind_key])

                            ## Add the title for this page
                            subtitle = self.answers_obj.GetAnswerFromRaw(self.question_name, data_keys[self.page-1])
                            self.add(Window(Text(subtitle, style="stats_heading_text"), style="stats_heading", ypos=self.title_height-3))

            self.createHistogram()

        def changeAnswer(self):
            if self.question_name in persistent.analytics_logged["post"]:
                del persistent.analytics_logged["post"][self.question_name]
            self.clearCacheEntry()

        def sendAnswers(self, item=None):
            content = python_dict()
            pers_dict = persistent.analytics_logged["post"]

            if self.question_data.type == "rank":
                pers_dict[self.question_name] = python_dict()

                for choice in self.question_data.choices:
                    key = "Post {} {}".format(self.question_name, choice[1])
                    content[key] = self.question_data.ranking[choice[1]]
                    pers_dict[self.question_name][choice[1]] = content[key]

                ## Add the user's data in the retrieved data without needing to pull server data again
                if self.question_name not in persistent.analytics_retrieved["post"]:
                    rv = python_dict()
                    for choice in self.question_data.choices:
                        rv[choice[1]] = python_dict()
                    persistent.analytics_retrieved["post"][self.question_name] = rv

                retr_dict = persistent.analytics_retrieved["post"][self.question_name]
                for choice in self.question_data.choices:
                    score = str(self.question_data.ranking[choice[1]])
                    if choice[1] not in retr_dict:
                        retr_dict[choice[1]] = python_dict()

                    if score not in retr_dict[choice[1]]:
                        retr_dict[choice[1]][score] = 1
                    else:
                        retr_dict[choice[1]][score] += 1

            elif self.question_data.type == "choice":
                for choice in self.question_data.choices:
                    key = "Post {}".format(self.question_name)
                    content[key] = item
                    pers_dict[self.question_name] = content[key]

                ## Add the user's data in the retrieved data without needing to pull server data again
                if self.question_name not in persistent.analytics_retrieved["post"]:
                    rv = python_dict()
                    for choice in self.question_data.choices:
                        rv[choice[1]] = 0
                    persistent.analytics_retrieved["post"][self.question_name] = rv

                if item not in persistent.analytics_retrieved["post"][self.question_name]:
                    persistent.analytics_retrieved["post"][self.question_name][item] = 1
                else:
                    persistent.analytics_retrieved["post"][self.question_name][item] += 1

            store.analytics.SendPostGameVote(content)
            self.clearCacheEntry()

    class JumpToQuestion(Action, DictEquality):
        def __init__(self, question_name, confirm=True):
            self.question_name = question_name
            self.confirm = confirm

        def __call__(self):
            if self.confirm:
                store.layout.yesno_screen("Jump to this question?", store.JumpToQuestion(self.question_name, confirm=False))
                return

            found_node = None

            idx_start = renpy.game.script.all_stmts.index(search.start_node)
            idx_end = renpy.game.script.all_stmts.index(search.end_node)

            for idx in range(idx_start, idx_end):
                node = renpy.game.script.all_stmts[idx]

                if type(node)==renpy.ast.Python:
                    if self.question_name in node.code.source:
                        found_node = node
                        break

            if found_node is None:
                idx_start = renpy.game.script.all_stmts.index(search.start_node_tips)
                idx_end = renpy.game.script.all_stmts.index(search.end_node_tips)

                for idx in range(idx_start, idx_end):
                    node = renpy.game.script.all_stmts[idx]

                    if type(node)==renpy.ast.Python:
                        if self.question_name in node.code.source:
                            found_node = node
                            break

            JumpToScriptNode(found_node, confirm=False)()


    class StatisticsRow(renpy.display.layout.MultiBox):
        def __init__(self, answer_container, entry_idx, **kwargs):
            window_width = 500
            window_height = 150
            windows = python_list()

            for q_idx in range(entry_idx, entry_idx+2):
                if len(answer_container.questions.values())-1 < q_idx:
                    break

                q_key = answer_container.questions.keys()[q_idx]
                question = answer_container.GetQuestion(q_key)

                if answer_container == postgame_answers:
                    w_vbox = RankingVoteDisplayable(q_key)

                elif answer_container == pref_answers:
                    w_vbox = Histogram(
                        title = question.prompt,
                        question_name = q_key,
                        data = pref_answers.GetPreferenceData(q_key),
                        selected_answer = pref_answers.GetSelectedPreference(q_key),
                        answers_obj = answer_container,
                        #correct_answers = question.correct_answers ##@TODO: Display default values
                        )

                elif answer_container == time_answers:
                    data = None
                    if q_key in persistent.analytics_retrieved['playtimes']:
                        data = persistent.analytics_retrieved['playtimes'][q_key]
                    w_vbox = Histogram(
                        title = question.prompt,
                        question_name = q_key,
                        data = data,
                        answers_obj = answer_container,
                        )

                elif answer_container == other_answers:
                    data = None
                    if q_key in persistent.analytics_retrieved['other']:
                        data = persistent.analytics_retrieved['other'][q_key]
                    w_vbox = Histogram(
                        title = question.prompt,
                        question_name = q_key,
                        data = data,
                        answers_obj = answer_container,
                        )

                else:
                    w_vbox = VBox()

                    ## Button with the question to jump
                    if answer_container.GetAnswerRaw(q_key) is None and not config.developer:
                        title = "{:1.0f}- ???".format(q_idx+1)
                        action = None
                    else:
                        title = "{:1.0f}: {}".format(q_idx+1, question.prompt)
                        action = JumpToQuestion(q_key)

                    if answer_container.GetAnswerRaw(q_key) is None and not config.developer:
                        w_vbox.add(Null(width=Histogram.width, height=4))
                        w_vbox.add(Text("<Answer to unlock>", xalign=0.5, style="histogram_title_text"))

                    elif "c5 answers" not in persistent.analytics_retrieved or q_key not in persistent.analytics_retrieved["c5 answers"]:
                        ## No data retrieved, we're the only player
                        w_vbox.add(Histogram(
                            title = title,
                            title_action = action,
                            question_name = q_key,
                            data = answer_container.CreateSingleAnswer(q_key),
                            selected_answer = answer_container.GetAnswerRaw(q_key),
                            correct_answers = question.correct_answers
                            )
                        )

                    else:
                        w_vbox.add(Histogram(
                            title = title,
                            title_action = action,
                            question_name = q_key,
                            data = persistent.analytics_retrieved["c5 answers"][q_key],
                            selected_answer = answer_container.GetAnswerRaw(q_key),
                            correct_answers = question.correct_answers
                            )
                        )

                ## Compute window height to make all frames equal height
                w_window_natural = Window(
                    w_vbox,
                    style="stats_frame",
                    xsize = window_width,
                    )

                window_height = max(window_height, int(w_window_natural.render(window_width,0,0,0).height))

                w_window = Window(
                    w_vbox,
                    style="stats_frame",
                    xsize = window_width,
                    ysize = 1.0
                    )
                windows.append(w_window)

            super(StatisticsRow, self).__init__(layout="horizontal", spacing=10, ysize=window_height, **kwargs)

            for w in windows:
                self.add(w)

## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When
## this screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen stats_menu:

    style_prefix "stats"
    key "game_menu" action Return()

    add "gui/stats/background.png":
        xalign 0.55
        yalign 0.5

    window:
        background "gui/subheading2.png"
        yoffset 61
        padding (0,0,0,0)
        xfill True

        hbox:
            xalign 0.5
            yoffset 9.05
            spacing 55

            hbox:
                textbutton _(" 1 ") action ShowMenu("answers_screen1") text_size 23
                text "-" style "stats_button_text" size 23
                textbutton _(" 2 ") action ShowMenu("answers_screen2") text_size 23
                text "-" style "stats_button_text" size 23
                textbutton _(" 3 ") action ShowMenu("answers_screen3") text_size 23
                text "-" style "stats_button_text" size 23
                textbutton _(" 4 ") action ShowMenu("answers_screen4") text_size 23
                text "-" style "stats_button_text" size 23
                textbutton _(" 5 ") action ShowMenu("answers_screen5") text_size 23
            textbutton _("POST-GAME") action ShowMenu("answers_screen_post") text_size 23
            textbutton _("SETTINGS") action ShowMenu("answers_screen_pref") text_size 23
            textbutton _("TIME") action ShowMenu("answers_screen_time") text_size 23
            textbutton _("OTHER") action ShowMenu("answers_screen_other") text_size 23

    viewport:
        mousewheel True
        scrollbars "vertical"
        xsize 1100-11
        xalign 0.5
        xoffset -17
        ypos 106
        ysize 561

        hbox:
            null width 56
            frame:
                background None
                padding (0,5,0,5)
                xalign 0.5

                vbox:
                    spacing 10
                    transclude

                    null height 10

    window:
        background None
        padding (10,0,10,0)
        xalign 0.5
        xsize 520
        yanchor 0.5
        ypos 696

        if persistent.last_updated_stats > 0:
            text "Last Updated: {0}-{1}-{2}, {3:02.0f}:{4:02.0f}:{5:02.0f}".format(*time.localtime(persistent.last_updated_stats)):
                size 16
                xalign 0.5
        else:
            text "Last Updated: Never":
                size 16
                xalign 0.5

    button:
        style "return_to_title_button"
        xalign 0.93
        yalign 0.9939
        action Return()


screen answers_screen(page=1):
    tag menu
    predict False

    style_prefix "stats"

    python:
        total_answers, correct_answers, percentage_correct = c5_answers.GetScore()

        divisions = 5
        row_count = max(100//2, len(c5_answers.questions)//2)
        rows_per_page = row_count//divisions
        lower = rows_per_page*(page-1)
        if page == divisions:
            upper = row_count+1
        else:
            upper = rows_per_page*page

    use stats_menu:
        null height 10
        text "You answered {} out of {} ({:0.0f}%) questions correctly.".format(correct_answers, total_answers, percentage_correct) style "histogram_title_text"
        null height 10

        for idx in range(lower, upper):
            add StatisticsRow(c5_answers, idx*2)

screen answers_screen1:
    tag menu
    predict False
    style_prefix "stats"
    use answers_screen(1)

screen answers_screen2:
    tag menu
    predict False
    style_prefix "stats"
    use answers_screen(2)

screen answers_screen3:
    tag menu
    predict False
    style_prefix "stats"
    use answers_screen(3)

screen answers_screen4:
    tag menu
    predict False
    style_prefix "stats"
    use answers_screen(4)

screen answers_screen5:
    tag menu
    predict False
    style_prefix "stats"
    use answers_screen(5)

screen answers_screen_post:
    tag menu
    predict False

    style_prefix "stats"

    use stats_menu:
        for idx in range(len(postgame_answers.questions)//2+1):
            add StatisticsRow(postgame_answers, idx*2)

screen answers_screen_pref:
    tag menu
    predict False

    style_prefix "stats"

    use stats_menu:
        for idx in range(len(pref_answers.questions)//2+1):
            add StatisticsRow(pref_answers, idx*2)

screen answers_screen_other:
    tag menu
    predict False

    style_prefix "stats"

    use stats_menu:
        for idx in range(len(other_answers.questions)//2+1):
            add StatisticsRow(other_answers, idx*2)

screen answers_screen_time:
    tag menu
    predict False

    style_prefix "stats"

    use stats_menu:
        for idx in range(len(time_answers.questions)//2+1):
            add StatisticsRow(time_answers, idx*2)

    text "Time data only extracted from players who\ntook 10 or more hours to complete the game":
        size 14
        xalign 0.9
        yalign 0.02


style stats_frame:
    background Frame("gui/titled_frame2.png", gui.titled_frame_borders, tile=gui.frame_tile)
    padding (5,5,5,15)

style histogram_title_text:
    xalign 0.5
    size 18
    color "#fff"
    xfill True

style histogram_bar_text:
    size 16
    yoffset 2
    layout "nobreak"
    color "#fff"
    outlines [(2, "#0002", 0, 0), (1, "#000b", 0, 0)]
    #outlines gui.dialogue_outline[gui.preference("dialogue_outline_idx")]

style histogram_total_text:
    size 14
    color "#fff"

style histogram_axis:
    xsize 65
    ysize 20
    background None
    padding (0,0,0,0)

style histogram_axis_text is histogram_bar_text:
    xalign 1.0

style postgame_choice_button is button:
    background Frame("gui/button/round_button_idle.png", 10, 10)
    hover_background Frame("gui/button/round_button_hover.png", 10, 10)
    padding (10,5,10,10)
    xsize 488

style postgame_choice_button_text is histogram_bar_text

style postgame_rank_button is button:
    background Frame("gui/button/round_button_idle.png", 10, 10)
    hover_background Frame("gui/button/round_button_hover.png", 10, 10)
    ypos 6
    padding (10,5,10,5)
    xsize 200

style postgame_rank_button_text is button_text:
    size 20
    xalign 0.5
    yoffset 3
    insensitive_color "#ff9d"

style stats_heading:
    background None
    yoffset -5
    padding (20,0,20,5)
    xalign 0.5

style stats_table_heading_text is histogram_bar_text:
    xalign 0.5

style stats_table_header:
    background None
    padding (0,0,0,0)
    xsize 150

style stats_table_cell1:
    background None
    padding (0,0,15,0)
    xsize 110

style stats_table_header_text is histogram_axis_text
style stats_table_cell_text is histogram_bar_text