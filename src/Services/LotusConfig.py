from PyQt5.QtGui import QIcon
class LotusConfig:
    # TODO: change these hardcoded paths to relative paths, based on repo's final location
    _icons = {
        "LOTUS": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-lotus-16.png",

        "INSERT_LINE": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-add-16.png",
        "ENABLE_EDIT": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-edit-file-16.png",
        "INSERT_COMMENT": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-comment-16.png",
        "ERASE": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-delete-16.png",
        "UNDO": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-undo-16.png",
        "REDO": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-redo-16.png",
        "SAVE": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-save-16.png",

        "YES": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-yes-button-16.png",
        "CANCEL": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-cancel-16.png",

        "TOGGLE_THEME": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/icons/icons8-night-16.png",
    }
    _stylesheets = {
        "DARK_MODE": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/stylesheets/DARK_MODE.css",
        "LIGHT_MODE": "/nfs/site/disks/hshow_wa_01/nadavzoh/work/exercises/Lotus/stylesheets/LIGHT_MODE.css"
    }
    def __init__(self):
        pass

    @staticmethod
    def get_icon(icon_name):
        return QIcon(LotusConfig._icons[icon_name])

    @staticmethod
    def get_stylesheet(stylesheet_name):
        return LotusConfig._stylesheets[stylesheet_name]
