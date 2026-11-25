define devbook_page = 1
define unlocked_devbook = renpy.loadable("devbook/button.png")

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

transform tf_devbook_move_down:
    yalign 0.0
    ease 0.2 yalign 1.0

transform tf_devbook_move_up:
    yalign 1.0
    ease 0.2 yalign 0.0

screen devbook:
    predict False 
    tag menu
    
    python:
        left_action = If(devbook_page==1, None, SetVariable("devbook_page", devbook_page-1))
        right_action = If(devbook_page==47, None, SetVariable("devbook_page", devbook_page+1))
    
    key "game_menu" action Return()
    key "focus_left" action left_action
    key "focus_right" action right_action
    key "viewport_up" action left_action
    key "viewport_down" action right_action

    style_prefix "devbook"   
    
    add "images/bg thinking4.png"
    
    button:
        xalign 0.5
        padding (0,0,0,0)
        at dissolve_tf_squared
        action Show("devbook_zoomed", transition=Dissolve(0.1), page_num=devbook_page)
        
        if renpy.get_physical_size()[1] > 720: #Use higher quality image if we have a big screen
            add "devbook/HDevelopmentBook-{:02d}.png".format(devbook_page) zoom 0.3273
        else:
            add "devbook/DevelopmentBook-{:02d}.png".format(devbook_page)
        
    text _("Find this book in higher quality in the game's folder") style "nvl_label3" xanchor 0.0 xpos 23 yalign 0.985
    showif devbook_page > 1:
        button:
            xalign 0.2
            xoffset 10
            style "arrow"
            at dissolve_tf
            yalign 0.87
            action left_action

    showif devbook_page < 47:
        button:
            xalign 0.8
            style "arrow2"
            at dissolve_tf
            yalign 0.87   
            xoffset -10        
            action right_action
    
    button:
        style "return_to_title_button"
        xalign 0.965
        yalign 0.984
        action Return()

screen devbook_zoomed(page_num, moving=False, at_top=True):
    tag menu
    
    add "images/bg thinking4.png"
    
    python:
        return_to_devbook = Show("devbook", transition=Dissolve(0.1))
        
        if at_top:
            fwd_action = Show("devbook_zoomed", page_num=page_num, moving=True, at_top=False)
            if page_num == 1:
                bkw_action = return_to_devbook
            else:
                bkw_action = [Show("devbook_zoomed", page_num=page_num-1, at_top=False, transition=Dissolve(0.1)), SetVariable("devbook_page", devbook_page-1)]
        
        else:
            if page_num == 47:
                fwd_action = return_to_devbook
            else:
                fwd_action = [Show("devbook_zoomed", page_num=page_num+1, at_top=True, transition=Dissolve(0.1)), SetVariable("devbook_page", devbook_page+1)]

            bkw_action = Show("devbook_zoomed", page_num=page_num, moving=True, at_top=True)
    
    key "viewport_up" action bkw_action
    key "viewport_down" action fwd_action
    
    button:
        xsize 1280
        ysize 720
        padding (0,0,0,0)
        activate_sound None
        action fwd_action
        alternate return_to_devbook
        
        add "devbook/HDevelopmentBook-{:02d}.png".format(page_num):
            xalign 0.5
            zoom 0.633 #0.753 #0.6545
            if moving:
                if at_top:
                    at tf_devbook_move_up
                else:
                    at tf_devbook_move_down
            else:
                if at_top:
                    yalign 0.0
                else:
                    yalign 1.0

    button:
        style "return_to_zoomout"
        xalign 1.0
        xoffset -105
        yalign 1.0
        yoffset -5
        action return_to_devbook

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

style return_to_title_button:
    hover_sound "sounds/sys2.wav"
    background "gui/music/button.png"
    hover_background "gui/music/button_hover.png"
    activate_sound "sounds/sys3.wav"
    padding (0, 0, 0, 0)
    xsize 300
    ysize 37   

style return_to_zoomout:
    hover_sound "sounds/sys2.wav"
    background "devbook/button.png"
    hover_background "devbook/button_hover.png"
    activate_sound "sounds/sys3.wav"
    padding (0, 0, 0, 0)
    xsize 140
    ysize 37  

style gallery_button:
    xsize 273
    ysize 178 
    activate_sound "sounds/sys20.wav"

style gallery_page_button:
    background "gui/gallery/diamond.png"
    hover_background "gui/gallery/diamond2.png"
    selected_background "gui/gallery/diamond2.png"
    xsize 55
    ysize 70
