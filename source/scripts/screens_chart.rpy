## @TODO: Reduce resource consumption for smoother zoom. Caused by creating new graphics. Confirmed with renpy.profile_screen("chart", update=True, debug=True)


init python:
    persistent.chart_timeline = "A"
    persistent.chart_zoom = 0.25
    persistent.chart_zoom_level = 2
    persistent.chart_pos = 0
    persistent.chart_selected = "All"
    persistent.chart_offsets = [0, 0]


init -10 python:
    import os
    import xml.etree.ElementTree as etree
    import pygame
    from collections import OrderedDict

    class TimelineChart(python_object):
        def __init__(self):
            self.fname = os.path.join('scripts', 'processing', 'timelines.drawio').replace("\\","/")
            self.nodes = python_dict()
            self.arrows = python_dict()
            self.max_dim = python_dict()
            self.character_enabled = python_dict()
            self.xoffset = 0
            self.yoffset = -228
            
            
            tree = etree.fromstring(renpy.loader.load(self.fname).read())
            
            for idx, t in enumerate(["A", "B", "C"]):
                self.nodes[t] = python_dict()
                self.arrows[t] = python_list()
                self.max_dim[t] = [0,0]
                
                arrow_cells = python_list()
                cells = tree[idx][0][0]
                
                ## Process all the nodes
                for c in cells:
                    if (c.tag == "object") or ("value" in c.attrib and c.attrib["value"] != ""):
                        if (c.tag == "object"):
                            ## Node with description information
                            node = TimelineNode(self, c, isObject=True)
                        else:
                            ## Node with no description information
                            node = TimelineNode(self, c, isObject=False)
                        
                        if node.x+node.w > self.max_dim[t][0]: self.max_dim[t][0] = node.x+node.w
                        if node.y+node.h > self.max_dim[t][1]: self.max_dim[t][1] = node.y+node.h
                        if node.h >= 500:
                            continue
                        
                        self.nodes[t][node.id] = node
                        for c in node.chars:
                            if c[0] not in self.character_enabled.keys() and c[0] not in ["...", "?"]:
                                self.character_enabled[c[0]] = True
                    
                    elif len(c)>0:
                        ## Arrow
                        arrow_cells.append(c)
                
                ## Process all the arrows
                for a in arrow_cells:
                    #self.arrows[t].append(TimelineArrow(a, self.nodes[t]))
                    try:
                        temp = TimelineArrow(a, self.nodes[t])
                        if len(temp.positions) == 0:
                            continue
                            
                        for p in temp.positions:
                            if p[0] > self.max_dim[t][0]: self.max_dim[t][0] = p[0]
                            if p[1] > self.max_dim[t][1]: self.max_dim[t][1] = p[1]
                    
                        self.arrows[t].append(temp)
                    except Exception as e:
                        raise Exception(a.attrib["id"], str(e))
                        
            self.character_enabled = OrderedDict(sorted(self.character_enabled.items()))
        
        def EnableAllCharacters(self):
            persistent.chart_selected = "All"
            for k in self.character_enabled.keys():
                self.character_enabled[k] = True
                
        def EnableCharacter(self, chr):
            persistent.chart_selected = chr
            for k in self.character_enabled.keys():
                if k==chr: self.character_enabled[k] = True
                else: self.character_enabled[k] = False
                
        def NodeEnabled(self, node):
            for c in node.chars:
                if c[0] in self.character_enabled and self.character_enabled[c[0]]:
                    return True
                    
            return False
    
    class ToggleChartCharacter(Action, FieldEquality):
        identity_fields = [ "dict", ]
        equality_fields = [ "key", "true_value", "false_value" ]

        def __init__(self, key):
            self.key = key

        def __call__(self):
            if self.key == "All":
                tc.EnableAllCharacters()
            else:
                tc.EnableCharacter(self.key)
            
            renpy.restart_interaction()

        def get_selected(self):
            if self.key == "All":
                return all(tc.character_enabled.values())
            
            return tc.character_enabled[self.key]
    
    class TimelineArrow(python_object):
        def __init__(self, arrow_info, nodes):
            self.id = arrow_info.attrib["id"]
            self.positions = python_list()
            
            self.source_id = None
            self.target_id = None
            self.type = None
            self.chars = python_list()
            
            ## Check if this isn't an arrow
            if "source" not in arrow_info.attrib and "target" not in arrow_info.attrib:
                return
            
            styles = arrow_info.attrib["style"].split(";")
            self.styles = python_dict()
            for s in styles:
                if s == "": continue
                val = s.split("=")
                self.styles[val[0]] = val[1]
               
            if "strokeColor" in self.styles:
                if self.styles["strokeColor"].upper() == "#B09500":
                    self.type = "past"
                elif self.styles["strokeColor"].upper() == "#B85450":
                    self.type = "future"
                elif self.styles["strokeColor"] == "#000000":
                    pass
                else:
                    raise Exception(self.id, "Invalid color")
            
            ## Get start point
            if "source" in arrow_info.attrib:
                self.source_id = arrow_info.attrib["source"]
                if "exitX" not in self.styles:
                    self.styles["exitX"] = "1.0"
                    self.styles["exitY"] = "0.5"
                
                x1 = int(nodes[self.source_id].x + nodes[self.source_id].w/2)
                y1 = int(nodes[self.source_id].y + nodes[self.source_id].h/2)
            else:
                temp = arrow_info[0].find("./*[@as='sourcePoint']")
                x1 = getCellAttrib(temp, "x")
                y1 = getCellAttrib(temp, "y")
            
            self.positions.append([x1,y1,None])
            
            ## Get end point
            if "target" in arrow_info.attrib:
                self.target_id = arrow_info.attrib["target"]
                if "entryX" not in self.styles:
                    self.styles["entryX"] = "0.0"
                    self.styles["entryY"] = "0.5"
                    
                x2 = int(nodes[self.target_id].x + nodes[self.target_id].w/2)
                y2 = int(nodes[self.target_id].y + nodes[self.target_id].h/2)
            else:
                temp = arrow_info[0].find("./*[@as='targetPoint']")
                x2 = getCellAttrib(temp, "x")
                y2 = getCellAttrib(temp, "y")
                
            
            ## Get middle points if needed
            temp = arrow_info[0].find("./Array")
            if temp is not None:
                for p in temp:
                    self.positions.append([getCellAttrib(p,"x"),getCellAttrib(p,"y"),None])
            else:
                ## Get a center point if the two lines aren't on the same level
                if self.source_id and self.target_id:
                    if x1 != x2 and y1 != y2:
                        if ("exitX" in self.styles and self.styles["exitX"] == "0.5") or ("entryY" in self.styles and self.styles["entryY"] == "0.5"):
                            ## Coming off the top or bottom
                            self.positions.append([x1,y2,None])
                        else:
                            ## Coming off the side
                            self.positions.append([x2,y1,None])
                else:
                    if x1 != x2 and y1 != y2:
                        if ("exitX" in self.styles and self.styles["exitX"] == "0.5") or ("entryY" in self.styles and self.styles["entryY"] == "0.5"):
                            ## Coming off the top or bottom
                            self.positions.append([x1,y2,None])
                        else:
                            ## Coming off the side
                            self.positions.append([x2,y1,None])
                    
            self.positions.append([x2,y2,None])
            
            ## Let's determine which corner goes where
            def sub_pos(p1,p2):
                return (p2[0]-p1[0], p2[1]-p1[1])
            
            idx = 1
            if len(self.positions)>2:
                for p1,p2,p3 in zip(self.positions[0:-2], self.positions[1:-1], self.positions[2:]):
                    x1, y1 = sub_pos(p1,p2)
                    x2, y2 = sub_pos(p2,p3)
                    
                    corner = None
                    if x1>0:
                        if y2>0: corner=4
                        else: corner=1
                    elif x1<0:
                        if y2>0: corner=3
                        else: corner=2
                    elif y1>0:
                        if x2>0: corner=2
                        else: corner=1
                    else:
                        if x2>0: corner=3
                        else: corner=4
                        
                    self.positions[idx][2] = corner
                    idx += 1
                    
            ## Get characters traveling on this line
            if self.source_id and self.target_id:
                if nodes[self.target_id].end:
                    ## Lines going to the far right
                    self.chars = nodes[self.source_id].chars
                
                else:
                    chars1 = nodes[self.source_id].chars
                    chars2 = nodes[self.target_id].chars
                    
                    idx1=0
                    idx2=0
                    
                    while idx1<len(chars1) and idx2<len(chars2):
                        if chars1[idx1][0]+chars1[idx1][1] == chars2[idx2][0]+chars2[idx2][1]:
                            ## Add connections only if the iteration number makes sense
                            if self.type is None and chars1[idx1][2] == chars2[idx2][2]:
                                self.chars.append((chars1[idx1][0], chars1[idx1][1]))
                            elif self.type and chars1[idx1][2] < chars2[idx2][2]:
                                self.chars.append((chars1[idx1][0], chars1[idx1][1]))
                            
                        if chars1[idx1][0]+chars1[idx1][1]+chars1[idx1][2] < chars2[idx2][0]+chars2[idx2][1]+chars2[idx2][2]:
                            idx1 += 1
                        else: idx2 += 1
    
    def SaveChartOffsets():
        widget = renpy.get_widget(None, "chart_vp")
        if widget is not None and len(widget.offsets)>0:
            persistent.chart_offsets = widget.offsets[0]
    
    def ZoomAction(zoom_factor):
        x, y = GetMousePos()
        x -= 55 ## Remove frame margin
        y -= 140 ## Remove frame margin
        
        widget = renpy.get_widget(None, "chart_vp")
        rend = widget.render(0,0,0,0) # Render so that the offsets update accordingly
        
        offset = widget.offsets[0]
        widget.set_xoffset(int(zoom_factor*(x-offset[0])-x))
        widget.set_yoffset(int(zoom_factor*(y-offset[1])-y))

    def ClickWorldSplit(source_node):
        ## Move the chart so the player's eyes stay in place after clicking the world split
        widget = renpy.get_widget(None, "chart_vp")
        if len(widget.offsets)>0:
            xoffset = abs(widget.offsets[0][0])
        else:
            xoffset = 0
        
        new_timeline = source_node.world_split
        new_node = tc.nodes[new_timeline][source_node.link]
        
        widget.set_xoffset(int(xoffset+(new_node.x-source_node.x)*persistent.chart_zoom))
    
    def getCellAttrib(cell, a):
        if a in cell.attrib:
            return int(round(float(cell.attrib[a])))
        return 0
    
    def ChartNode(name):
        ## Do nothing. This is a placeholder function so we can scan the script and find the landing point
        return
    
    def StopChartDragging():
        renpy.display.focus.grab = None
    
    class TimelineNode(python_object):
        def __init__(self, chart, cell, isObject):
            self.id = cell.attrib["id"]
            self.description = ""
            self.timeline = 0
            self.chars = python_list()
            self.raw_chars = python_list()
            self.world_split = None
            self.link = None
            self.end = False
            self.time = None
            self.info = None
            self.death = False
            self.clickable = False
            self.jumps = python_dict()
            
            self.display = python_list()
            
            try:
                if isObject:
                    if "chars" in cell.attrib:
                        self.world_split = cell.attrib["label"]
                        self.raw_chars = cell.attrib["chars"].split(", ")
                        if "link" in cell.attrib:
                            self.link = cell.attrib["link"]
                    elif "time" in cell.attrib:
                        self.time = cell.attrib["time"]
                    elif "death" in cell.attrib:
                        self.death = True
                        self.raw_chars = cell.attrib["death"].split(", ")
                    elif "info" in cell.attrib:
                        self.info = python_list()
                        temp_info = cell.attrib["label"].replace("&gt;", ">").split("<br>")
                        for temp in temp_info:
                            self.info.append(temp.split(":")) 
                    else:
                        self.raw_chars = cell.attrib["label"].split(", ")
                    
                    for att in cell.attrib:
                        if att[-1] in ["A", "B", "C"]:
                            self.jumps[att] = cell.attrib[att]
                    
                    self.x = getCellAttrib(cell[0][0], "x")+chart.xoffset
                    self.y = getCellAttrib(cell[0][0], "y")+chart.yoffset
                    self.w = getCellAttrib(cell[0][0], "width")
                    
                    if self.info:
                        self.y += 34
                    elif self.time:
                        self.y += 74
                    
                    if self.info:
                        self.h = self.w
                    else:
                        self.h = getCellAttrib(cell[0][0], "height")
                    
                    if "desc" in cell.attrib:
                        self.description = cell.attrib["desc"]
                    
                    
                else:
                    if cell.attrib["value"] == "End":
                        self.end = True
                    else:
                        self.raw_chars = cell.attrib["value"].split(", ")
                    self.x = getCellAttrib(cell[0], "x")+chart.xoffset
                    self.y = getCellAttrib(cell[0], "y")+chart.yoffset
                    self.w = getCellAttrib(cell[0], "width")
                    self.h = getCellAttrib(cell[0], "height")
                
                self.raw_chars.sort()
                for chr in self.raw_chars:
                    val = chr.split(" ")
                    if len(val)==1:
                        continue
                        #raise Exception("No timeline marker found", self.id, val[0])
                    elif self.world_split:
                        self.chars.append((val[0], val[1][0], val[1][1:], None))
                    else:
                        ## Select the appropriate color based on the mix of people in the node
                        if val[1] == "":
                            raise Exception(val[0])
                        elif val[1][0] == "A":
                            self.timeline |= 0x4
                        elif val[1][0] == "B":
                            self.timeline |= 0x2
                        elif val[1][0] == "C":
                            self.timeline |= 0x1

                        jmp = None
                        if val[0]+val[1][0] in self.jumps:
                            jmp = self.jumps[val[0]+val[1][0]]

                            for chr2 in self.chars:
                                if chr2[3] == jmp:
                                    jmp = None
                                    break

                        self.chars.append((val[0], val[1][0], val[1][1:], jmp))

            except Exception as e:
                raise Exception(self.id, self.raw_chars, str(e))
            
            
            ## Pre-compute the displayable text
            ## Level 0-1
            temp1 = python_list() ## name
            temp2 = python_list() ## timeline
            
            for c in self.chars:
                temp1.append(c[0])
                if c[3] is not None:
                    self.clickable = True
                    temp2.append(c[1]+"*")
                else:
                    temp2.append(c[1])
                
            temp1 = "\n".join(temp1)
            temp2 = "\n".join(temp2)
            self.display.append([temp1, temp2])
            
            ## Level 2-3
            temp1 = python_list() ## name column 1
            temp2 = python_list() ## name column 2
            
            counter = 1
            for c in self.chars:
                if counter:
                    temp1.append(c[0][0:2])
                else:
                    temp2.append(c[0][0:2])
                counter = 1-counter
                
            temp1 = "\n".join(temp1)
            temp2 = "\n".join(temp2)
            self.display.append([temp1, temp2])
    
    tc = TimelineChart()

style arrow:
    background "gui/chart/arrow3.png"
    hover_background "gui/chart/arrow4.png"
    xsize 46
    ysize 46
    hover_sound "sounds/sys2.wav"
    activate_sound "sounds/sys13.wav"
style arrow2:
    background "gui/chart/arrow.png"
    hover_background "gui/chart/arrow2.png"
    xsize 46
    ysize 46
    hover_sound "sounds/sys2.wav"
    activate_sound "sounds/sys13.wav"
style access:
    background "gui/chart/access.png"
    hover_background "gui/chart/access2.png"
    xsize 310
    ysize 50
    hover_sound "sounds/sys2.wav"
    activate_sound "sounds/sys6.wav"

transform dissolve_tf:
    on show:
        alpha 0
        linear 0.2 alpha 1.0
    on hide:
        linear 0.2 alpha 0.0

transform dissolve_tf_squared:
    on show:
        alpha 0
        easein_circ 0.2 alpha 1.0
    on hide:
        #pause 0.2
        easeout_circ 0.2 alpha 0.0

define tutorial = 1

screen chart_tutorial:    
    tag menu

    use game_menu(_("Chart_tutorial"), padded=(40, 85, 40, 30)):
        style_prefix "chart_tutorial"        
    
    showif tutorial == 1:
        add "images/chart_tutorial1.png" at dissolve_tf_squared
    showif tutorial == 2:
        add "images/chart_tutorial2.png" at dissolve_tf_squared
    showif tutorial == 3:
        add "images/chart_tutorial3.png" at dissolve_tf_squared
    showif tutorial == 4:
        add "images/chart_tutorial4.png" at dissolve_tf_squared
    showif tutorial == 5:
        add "images/chart_tutorial5.png" at dissolve_tf_squared
    showif tutorial == 6:
        add "images/chart_tutorial6.png" at dissolve_tf_squared
    showif tutorial == 7:
        add "images/chart_tutorial7.png" at dissolve_tf_squared
    showif tutorial == 8:
        add "images/chart_tutorial8.png" at dissolve_tf_squared
    showif tutorial == 9:
        add "images/chart_tutorial9.png" at dissolve_tf_squared
    showif tutorial == 10:
        add "images/chart_tutorial10.png" at dissolve_tf_squared
    showif tutorial == 11:
        add "images/chart_tutorial11.png" at dissolve_tf_squared
    showif tutorial == 12:
        add "images/chart_tutorial12.png" at dissolve_tf_squared
    showif tutorial == 13:
        add "images/chart_tutorial13.png" at dissolve_tf_squared
    showif tutorial == 14:
        add "images/chart_tutorial14.png" at dissolve_tf_squared
    showif tutorial == 15:
        add "images/chart_tutorial15.png" at dissolve_tf_squared
    showif tutorial == 16:
        add "images/chart_tutorial16.png" at dissolve_tf_squared
    
    showif not tutorial == 1:
        button:
            style "arrow"
            at dissolve_tf
            yalign 0.87
            xoffset 70                
            action SetVariable("tutorial", tutorial-1)
    else:
        if persistent.chart:
            button:
                style "access"
                at dissolve_tf
                yalign 0.84
                xalign 0.5
                action [Function(EnableMenu, "chart"), ShowMenu('chart')], SetVariable("persistent.chart", True), SetVariable("tutorial", 1)
    
    showif not tutorial == 16:
        button:
            style "arrow2"
            at dissolve_tf
            yalign 0.87
            xoffset 1165
            action SetVariable("tutorial", tutorial+1)
    else:
        button:
            style "access"
            at dissolve_tf
            yalign 0.84
            xalign 0.5
            action [Function(EnableMenu, "chart"), ShowMenu('chart')], SetVariable("persistent.chart", True), SetVariable("tutorial", 1)
    
screen chart():
    predict False ## Avoid predicting this screen
    tag menu
    
    default popup_node = None
    default popup_text = ""
    default legend_visible = False
    default hovered_node = None
    default hovered_visible = False
    default filter_visible = False
    
    key "viewport_up" action If(persistent.chart_zoom_level>0, [Function(ZoomAction, 2.0), SetVariable("persistent.chart_zoom", persistent.chart_zoom*2.0), SetVariable("persistent.chart_zoom_level", persistent.chart_zoom_level-1)], NullAction())
    key "viewport_down" action If(persistent.chart_zoom_level<2, [Function(ZoomAction, 0.5), SetVariable("persistent.chart_zoom", persistent.chart_zoom*0.5), SetVariable("persistent.chart_zoom_level", persistent.chart_zoom_level+1)], NullAction())
    key "game_menu" action [Hide('chart', transition=config.exit_transition), Return()] #Need to proc `on "hide"`
    for ac in ["replaced", "hide"]:
        on ac action Function(SaveChartOffsets)

    use game_menu(_("Chart"), padded=(40, 85, 40, 30)):
        style_prefix "chart"
        
        frame:
            background Frame("gui/chart/frame_{}.png".format(persistent.chart_timeline), 25, 25)
            viewport:
                id "chart_vp"
                draggable True
                arrowkeys True
                xinitial -persistent.chart_offsets[0]
                yinitial -persistent.chart_offsets[1]
                
                scrollbars "horizontal"
                
                frame:
                    padding (0,0,0,0)
                    if filter_visible:
                        key "mousedown_1" action SetScreenVariable("filter_visible", False)
                
                    background Tile("gui/chart/grid.png")
                    xsize int(tc.max_dim[persistent.chart_timeline][0]*persistent.chart_zoom)
                    ysize int(max(500, persistent.chart_zoom*(tc.max_dim[persistent.chart_timeline][1])))
                    
                    ## Draw arrows
                    if persistent.chart_selected != "All":
                        add Transform("gui/chart/{}_{}.png".format(persistent.chart_timeline, persistent.chart_zoom_level), alpha=0.4):
                            xpos int(persistent.chart_zoom*tc.xoffset)
                            ypos int(persistent.chart_zoom*tc.yoffset)
                            if persistent.chart_zoom_level==2:
                                yoffset 7
                        add "gui/chart/{}_{}_{}.png".format(persistent.chart_timeline, persistent.chart_zoom_level, persistent.chart_selected):
                            xpos int(persistent.chart_zoom*tc.xoffset)
                            ypos int(persistent.chart_zoom*tc.yoffset)
                            if persistent.chart_zoom_level==2:
                                yoffset 7
                    else:
                        add "gui/chart/{}_{}.png".format(persistent.chart_timeline, persistent.chart_zoom_level):
                            xpos int(persistent.chart_zoom*tc.xoffset)
                            ypos int(persistent.chart_zoom*tc.yoffset)
                            if persistent.chart_zoom_level==2:
                                yoffset 7
                        
                    
                    ## Draw nodes
                    for node in tc.nodes[persistent.chart_timeline].values():
                        if node.time:
                            text node.time:
                                xpos int(persistent.chart_zoom*node.x)
                                ypos int(persistent.chart_zoom*node.y)
                                size persistent.chart_zoom*56 xalign 0.2
                            
                        elif node.info:
                            button:
                                if persistent.chart_zoom_level==2:
                                    background "gui/chart/node0b.png"
                                    hover_background "gui/chart/node0b_hover.png"
                                else:
                                    background Frame("gui/chart/node0.png", 10, 10)
                                    hover_background Frame("gui/chart/node0_hover.png", 10, 10)
                                
                                xpos  int(persistent.chart_zoom*node.x)
                                xminimum int(persistent.chart_zoom*node.w)
                                ypos  int(persistent.chart_zoom*(node.y+(node.h-80)/2))
                                ysize int(persistent.chart_zoom*80)
                                
                                hovered [SetScreenVariable("hovered_node", node), SetScreenVariable("hovered_visible", True)]
                                unhovered [SetScreenVariable("hovered_visible", False)]
                                
                                action NullAction()
                                
                                text ""
                        elif node.death:
                            button:
                                if tc.NodeEnabled(node):
                                    background Transform("gui/chart/death.png", zoom=persistent.chart_zoom)
                                else:
                                    background Transform("gui/chart/death.png", zoom=persistent.chart_zoom, alpha=0.2)
                                    #background Transform("gui/chart/death_off.png", zoom=persistent.chart_zoom)
                                xpos int(persistent.chart_zoom*node.x)
                                ypos int(persistent.chart_zoom*node.y)
                                if persistent.chart_zoom_level==2:
                                    yoffset 7
                                xminimum int(persistent.chart_zoom*node.w)
                                yminimum int(persistent.chart_zoom*node.h)
                                #padding (5, 5, 5, 5)
                                
                                hovered [SetScreenVariable("hovered_node", node), SetScreenVariable("hovered_visible", True)]
                                unhovered [SetScreenVariable("hovered_visible", False)]
                                
                                action NullAction()
                                
                                text ""
                        elif node.end:
                            pass
                        else:
                            button:
                                if persistent.chart_zoom_level==2:
                                    if tc.NodeEnabled(node):
                                        background "gui/chart/node{}b.png".format(node.timeline)
                                    else:
                                        background Transform("gui/chart/node{}b.png".format(node.timeline), alpha=0.2)
                                    hover_background "gui/chart/node{}b_hover.png".format(node.timeline)
                                else:
                                    if tc.NodeEnabled(node):
                                        background Frame("gui/chart/node{}.png".format(node.timeline), 10, 10)
                                    else:
                                        background Transform(Frame("gui/chart/node{}.png".format(node.timeline), 10, 10), alpha=0.2)
                                        #background Frame("gui/chart/node{}_off.png".format(node.timeline), 10, 10)
                                    hover_background Frame("gui/chart/node{}_hover.png".format(node.timeline), 10, 10)
                                
                                hovered [SetScreenVariable("hovered_node", node), SetScreenVariable("hovered_visible", True)]
                                unhovered [SetScreenVariable("hovered_visible", False)]
                                
                                xpos int(persistent.chart_zoom*node.x)
                                xminimum int(persistent.chart_zoom*node.w)
                                if persistent.chart_zoom_level == 2:
                                    ypos  int(persistent.chart_zoom*(node.y+(node.h-20)/2))
                                    ysize 20
                                else:
                                    ypos  int(persistent.chart_zoom*node.y)
                                    ysize int(persistent.chart_zoom*node.h)
                                    
                                padding (5, 5, 5, 5)
                                
                                
                                ## Add node text
                                if node.world_split:
                                    action [Function(ClickWorldSplit, node), SetVariable("persistent.chart_timeline", node.world_split)]
                                    padding (0, 0, 0, 0)
                                    fixed:
                                        if node.world_split == "C" and persistent.chart_zoom_level == 2:
                                            xalign 0.4
                                        else:
                                            xalign 0.5
                                        yalign 0.05
                                        xsize int(node.w*persistent.chart_zoom/2)
                                        ysize int(node.h*persistent.chart_zoom/2)
                                        
                                        text node.world_split size 56*persistent.chart_zoom:
                                            if not tc.NodeEnabled(node):
                                                color "#fff8"
                                else:
                                    if persistent.chart_zoom_level == 0:
                                        hbox:
                                            spacing 5
                                            xalign 0.5
                                            yalign 0.5
                                            text node.display[0][0] size 16*persistent.chart_zoom:
                                                if not tc.NodeEnabled(node):
                                                    color "#fff8"
                                            text node.display[0][1] size 16*persistent.chart_zoom:
                                                if not tc.NodeEnabled(node):
                                                    color "#fff8"
                                    elif persistent.chart_zoom_level == 1:
                                        padding (2, 2, 2, 2)
                                        hbox:
                                            spacing 2
                                            xalign 0.5
                                            yalign 0.5
                                            text node.display[1][0] size 25*persistent.chart_zoom yalign 0.0:
                                                if not tc.NodeEnabled(node):
                                                    color "#fff8"
                                            if node.display[1][1] != "":
                                                text node.display[1][1] size 25*persistent.chart_zoom yalign 0.0:
                                                    if not tc.NodeEnabled(node):
                                                        color "#fff8"
                                    elif persistent.chart_zoom_level == 2 and node.clickable:
                                        add "gui/chart/pov_indicator.png" xpos -4 ypos -4
                                        #text "*" xpos -1 ypos -3 xsize 5 size 15.9 color "#fff" outlines [(2,"#0009",0,0)]
                                        #text "" size 8
                                    else:
                                        add Solid("#0000", xsize=1, ysize=1)
                                    
                                    if node.clickable:
                                        action [Show("chart_jump", node=node, transition=Dissolve(0.2)), Function(SaveChartOffsets)]
                                    else:
                                        action NullAction()
                                        #action [SetScreenVariable("popup_node", node), SetScreenVariable("popup_text", node.description)]
    
    fixed:
        xalign 0.15
        ypos 63
        
        add "gui/subheading2.png"
        textbutton "View Tutorial":
            xalign 0.5 
            text_ypos 7
            ypos 15
            activate_sound "sounds/sys15.wav"
            action [Function(EnableMenu, "chart_tutorial"), ShowMenu('chart_tutorial')]
        hbox:
            spacing 60
            xpos 50
            ypos 15
            textbutton "World A" text_ypos 7 action SetVariable("persistent.chart_timeline", "A") activate_sound "sounds/sys20.wav"
            textbutton "World B" text_ypos 7 action SetVariable("persistent.chart_timeline", "B") activate_sound "sounds/sys14.wav"
            textbutton "World C" text_ypos 7 action SetVariable("persistent.chart_timeline", "C") activate_sound "sounds/sys19.wav"
            
        textbutton "Selected: {}".format(persistent.chart_selected):
            action ToggleScreenVariable("filter_visible")
            xpos 800
            ypos 15
            text_ypos 7
        
        textbutton "Legend":
            action ToggleScreenVariable("legend_visible")
            xpos 1100
            ypos 15
            activate_sound "sounds/sys11.wav"
            text_ypos 7
    
    showif legend_visible:
        vbox:
            xalign 0.98 yalign 0.86
            add "gui/chart/legend.png" zoom 0.5 alpha 0.8:
                at tf_dropdown_menu
            
    showif filter_visible:
        vbox:
            ## I have to do it this way because adri's alignment breaks otherwise. kill me.
            xpos 793 ypos 95
            style_prefix "chart_popup"
            
            frame:
                at tf_dropdown_menu
                xsize 110
            
                vbox:
                    textbutton _("All") action [ToggleChartCharacter("All"), SetScreenVariable("filter_visible", False)]
                    for k in tc.character_enabled.keys():
                        textbutton _(k) action [ToggleChartCharacter(k), SetScreenVariable("filter_visible", False)]
    
    showif hovered_visible:
        python:
            widget = renpy.get_widget(None, "chart_vp")
            rend = widget.render(0,0,0,0) # Render so that the offsets update accordingly
            
            if len(widget.offsets)>0:
                offset = widget.offsets[0]
            else:
                offset = (0,0)
                    
        if hovered_node:
            if hovered_node.info:
                frame:
                    style_prefix "chart_popup"
                    #at tf_dropdown_menu
                    xpos int((hovered_node.x+hovered_node.w)*persistent.chart_zoom +offset[0] +55)
                    ypos int(hovered_node.y*persistent.chart_zoom +offset[1] +130)
                    padding (10,10,10,10)
                    
                    hbox:
                        xalign 0.5
                        yalign 0.5
                        spacing 0

                        vbox:
                            for row in hovered_node.info:
                                text row[0] size 14 xalign 1.0
                        vbox:
                            hbox:
                                null width 8
                                add Solid("#fff8", xsize=1, ysize=int(17.5*len(hovered_node.info)))
                        vbox:
                            for row in hovered_node.info:
                                text row[1] size 14 xalign 0.0
        
            elif hovered_node.death or (persistent.chart_zoom_level >= 1 and not hovered_node.world_split):
                frame:
                    style_prefix "chart_popup"
                    #at tf_dropdown_menu
                    xpos int((hovered_node.x+hovered_node.w)*persistent.chart_zoom +offset[0] +55)
                    ypos int(hovered_node.y*persistent.chart_zoom +offset[1] +130)
                    padding (10,10,10,10)
                    
                    hbox:
                        spacing 5
                        xalign 0.5
                        yalign 0.5
                        text hovered_node.display[0][0] size 16
                        text hovered_node.display[0][1] size 16

    on "replace" action Function(StopChartDragging)

style chart_text:
    outlines [(1,"#0009",0,0)]

style chart_popup_frame is popup_frame

screen chart_jump(node):
    modal True
    predict False
    
    for k in ['game_menu', 'dismiss']:
        key k action [Hide('chart_jump', transition=Dissolve(0.2)), ShowMenu('chart')]
    
    window:
        background "#0008"
        xsize 1.0
        ysize 1.0
        
        frame:
            style_prefix "chart_popup"
            xalign 0.5
            yalign 0.5
            padding (15,15,15,15)

            vbox:
                xalign 0.5
                xsize 200
                yalign 0.5

                for char in node.chars:
                    if char[3]:
                        textbutton "Jump to {} {}".format(char[0], char[1]):
                            action [Hide('chart_jump'), JumpFromChart(char[3])]
                            if store._in_replay:
                                activate_sound "sounds/sys18.wav"
                            else:
                                activate_sound "sounds/sys8.wav"
                textbutton "Cancel":
                    action Hide('chart_jump')
                