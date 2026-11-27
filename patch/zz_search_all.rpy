# 让游戏内搜索覆盖全书文本。
#
# 原理：screens_search.rpy 的 UpdateMessages 只遍历 persistent._seen_ever
# （即「已读」记录），所以只有读过的行才会进搜索。
# 这里在启动时把搜索索引里的每一条都标成已读，等于解锁全书搜索。
#
# 副作用：游戏会把所有文本视为已读，「跳过未读」会连没看过的也一起跳。
# 想恢复原状，删掉本文件并重启即可。

init 999 python:

    def dsh_unlock_search():
        try:
            keys = list(search.all_entries.keys())
            for key in keys:
                persistent._seen_ever[key] = True
            try:
                search.UpdateMessages(update_gui=False)
            except Exception as e:
                print("dsh_unlock_search: UpdateMessages failed:", e)
            try:
                renpy.save_persistent()
            except Exception:
                pass
            print("dsh_unlock_search: marked %d lines as seen" % len(keys))
        except Exception as e:
            print("dsh_unlock_search failed:", e)

    dsh_unlock_search()

    config.after_load_callbacks.append(dsh_unlock_search)
