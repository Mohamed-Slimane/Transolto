import keyboard as keyboard
import polib as polib

import wx
from deep_translator import GoogleTranslator
from wx.adv import HyperlinkCtrl
from wx.lib.agw import hyperlink

MAIN_WINDOW_ID = wx.Window.NewControlId()
MAIN_FRAME_ID = wx.Window.NewControlId()
MAIN_PANEL_ID = wx.Window.NewControlId()

CONTROL_PANEL_ID = wx.Window.NewControlId()
CONTENT_PANEL_ID = wx.Window.NewControlId()

DOWNLOAD_WINDOW_ID = wx.Window.NewControlId()
DOWNLOAD_FRAME_ID = wx.Window.NewControlId()

URL_ID = wx.Window.NewControlId()
DOWNLOAD_ID = wx.Window.NewControlId()
SELECTOR_ID = wx.Window.NewControlId()

FILE_MENU_ID = wx.Window.NewControlId()
BTN_OPEN_FILE_ID = wx.Window.NewControlId()
BTN_SAVE_FILE_ID = wx.Window.NewControlId()
BTN_CLOSE_APP_ID = wx.Window.NewControlId()
BTN_ABOUT_ID = wx.Window.NewControlId()

TRANS_MENU_ID = wx.Window.NewControlId()
BTN_TRANS_ID = wx.Window.NewControlId()

SETTINGS_MENU_ID = wx.Window.NewControlId()
BTN_SETTINGS_ID = wx.Window.NewControlId()


class MainWindow(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Transolto', size=(900, 700))
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("images/icon.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.target_language = 'en'
        self.trans = None
        self.file_path = None
        self.target_index = 'empty'
        wx.Frame.CenterOnScreen(self)

        # اللوحة الأساسية
        self.panel = wx.Panel(self, MAIN_PANEL_ID)
        self.panel.SetBackgroundColour("White")
        self.panel.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        # حدث تخجيم الساسة والتحديثات
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnSize)

        # شريط الحالة
        status_bar = self.CreateStatusBar()

        # Create menubar
        menubar = wx.MenuBar()

        # File Menu
        self.file_menu = wx.Menu()
        self.file_menu.Append(BTN_OPEN_FILE_ID, "Open (ctrl+o)", "Open po files")
        self.Bind(wx.EVT_MENU, self.open_file, id=BTN_OPEN_FILE_ID)

        self.file_menu.Append(BTN_SAVE_FILE_ID, "Save (ctrl+s)", "")
        self.Bind(wx.EVT_MENU, self.save_file, None, BTN_SAVE_FILE_ID)

        self.file_menu.Append(BTN_CLOSE_APP_ID, "Exit", "")
        self.Bind(wx.EVT_MENU, self.close_app, None, BTN_CLOSE_APP_ID)
        # End File Menu

        # File Menu
        self.trans_menu = wx.Menu()
        self.trans_menu.Append(BTN_TRANS_ID, "Pre-translate", "Robot translate with google translate")
        self.Bind(wx.EVT_MENU, self.PreTrans, id=BTN_TRANS_ID)

        # About
        self.about_menu = wx.Menu()
        self.about_menu.Append(BTN_ABOUT_ID, "Transolto", "")
        self.Bind(wx.EVT_MENU, self.about_window, id=BTN_ABOUT_ID)

        # App
        self.control_panel = wx.Panel(self.panel)
        self.content_panel = wx.Panel(self.panel)

        self.primary_panel = wx.Panel(self.content_panel)
        self.secondary_panel = wx.Panel(self.content_panel)
        self.secondary_panel.SetBackgroundColour('#f4f5fb')

        # التحجيم الرئيسي
        sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.control_panel, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)
        sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 0)
        self.panel.SetSizer(sizer)
        # Control sizer
        control_rsz = wx.BoxSizer(wx.HORIZONTAL)
        self.control_panel.SetSizer(control_rsz)

        # تحجيم المحتوى
        self.content_rsz = wx.BoxSizer(wx.HORIZONTAL)
        self.content_rsz.Add(self.primary_panel, 3, wx.EXPAND)
        self.content_rsz.Add(self.secondary_panel, 1, wx.EXPAND)
        self.content_panel.SetSizer(self.content_rsz)

        # تحجيم الجداول
        self.primary_rsz = wx.BoxSizer(wx.VERTICAL)
        self.primary_panel.SetSizer(self.primary_rsz)

        # تحجيم الشريط الجانبي
        self.secondary_rsz = wx.BoxSizer(wx.VERTICAL)
        self.secondary_panel.SetSizer(self.secondary_rsz)

        # عناصر الجداول

        # جدول الكلمات
        self.table = wx.ListCtrl(self.primary_panel, style=wx.LC_REPORT | wx.BORDER)
        self.table.InsertColumn(0, ".", width=20)
        self.table.InsertColumn(1, "Text")
        self.table.InsertColumn(2, "Translation", format=wx.LIST_FORMAT_RIGHT)
        self.primary_rsz.Add(self.table, 5, wx.EXPAND)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.TableOnClick, self.table)

        # النص المصدر
        self.source_label = wx.StaticText(self.primary_panel, label='Source text')
        self.primary_rsz.Add(self.source_label, 0, wx.EXPAND | wx.ALL, 7)
        # ---
        self.source = wx.TextCtrl(self.primary_panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        self.primary_rsz.Add(self.source, 1, wx.EXPAND, 0)

        # الترجمة
        self.target_label = wx.StaticText(self.primary_panel, label='Translate')
        self.primary_rsz.Add(self.target_label, 0, wx.EXPAND | wx.ALL, 7)
        # ---
        self.target = wx.TextCtrl(self.primary_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        self.primary_rsz.Add(self.target, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_TEXT, self.OnTargetChange, self.target)

        # السايد بار
        self.trans_label = wx.StaticText(self.secondary_panel, label='Google Translator')
        self.secondary_rsz.Add(self.trans_label, 0, wx.EXPAND | wx.ALL, 5)

        # Menubar appends
        menubar.Append(self.file_menu, "File")
        menubar.Append(self.trans_menu, "Translate")
        menubar.Append(self.about_menu, "About")
        self.SetMenuBar(menubar)
        # End Menubar appends

    def close_app(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Close', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_YES:
            self.Destroy()
            # self.Close()

    def open_file(self, event):
        try:
            # نافذة تحديد الملف
            openFileDialog = wx.FileDialog(self, "Open", "", "", "Python files (*.po)|*.po",
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            # عرض النافذة
            openFileDialog.ShowModal()
            # جلب مسار الملف
            self.file_path = openFileDialog.GetPath()
            # تعريف الملف
            self.pofile = polib.pofile(self.file_path, encoding='utf8')

            # حذف البيانات من الجدول
            self.table.DeleteAllItems()

            # محاولة التعرف على اللغة العربية وجعل إتجاه النص من اليمين لليسار
            try:
                self.target_language = self.pofile.metadata['Language']
                if self.target_language == 'ar':
                    self.target.SetLayoutDirection(wx.Layout_RightToLeft)
                    self.target_label.SetLayoutDirection(wx.Layout_RightToLeft)

            except:
                self.target.SetLayoutDirection(wx.Layout_LeftToRight)
                self.target_label.SetLayoutDirection(wx.Layout_LeftToRight)

            # تعريف الاندكس لبدأ لوب الجدول
            index = -1
            # عمل لوب لمحتويات الملف ووضعها في الجدول
            for i in self.pofile:
                index += 1
                self.table.InsertItem(index, str(index + 1))
                self.table.SetItem(index, 1, i.msgid)
                self.table.SetItem(index, 2, i.msgstr)

            # إغلاق العارض
            openFileDialog.Destroy()

            # إرجاع قيمة الاندكس
            if self.target_index != 'empty':
                self.target_index = 'empty'

            # تفريغ الحقول الخاصة بالتحرير
            self.Layout()
            self.table.Layout()
            self.source.SetValue('')
            self.target.SetValue('')
        except Exception as e:
            wx.MessageDialog(None, str(e), 'Error', wx.OK | wx.ICON_ERROR).ShowModal()

    def save_file(self, event):

        try:
            # قتح الملف القديم الذي يجري التعديل عليه
            po_file = polib.pofile(self.file_path, encoding='utf8')

            # إنشاء ملف جديد للكتابة عليه
            new_po = polib.POFile()
            # حقن المعلومات في الملف الجديد
            new_po.metadata = po_file.metadata

            # عمل لوب للبيانات من الجدول وحقنها في الملف الجديد
            for row in range(self.table.GetItemCount()):
                entry = polib.POEntry(
                    msgid=u'{}'.format(self.table.GetItem(row, 1).GetText()),
                    msgstr=u'{}'.format(self.table.GetItem(row, 2).GetText()),
                )
                new_po.append(entry)

            # حفظ الملف الجديد بصيغة PO
            new_po.save(self.file_path)
            # حفظ الملف الجديد بصيغة MO
            new_po.save_as_mofile(self.file_path.replace('.po', '.mo'))
            self.Layout()
        except Exception as e:
            wx.MessageDialog(None, str(e), 'Error', wx.OK | wx.ICON_ERROR).ShowModal()

    def on_key_down(self, event):
        if keyboard.is_pressed('ctrl+s'):
            self.save_file(self)
        elif keyboard.is_pressed('ctrl+o'):
            self.open_file(self)
        else:
            event.Skip()

    # وضيفة لإعادة تحجيم محتويات الجدول
    def OnSize(self, event):
        table_width = self.table.Size[0] - 5
        self.table.SetColumnWidth(0, 30)
        self.table.SetColumnWidth(1, int(table_width / 2) - 15)
        self.table.SetColumnWidth(2, int(table_width / 2) - 15)
        self.table.PostSizeEventToParent()
        self.Layout()

    # وضيفة كل ما تم النقر على عنصر جديد في الجدول
    def TableOnClick(self, event):
        index = event.GetIndex()
        source_text = self.table.GetItem(index, 1)
        target_text = self.table.GetItem(index, 2)

        self.target_index = index
        self.source.SetValue(str(source_text.GetText()))
        self.target.SetValue(str(target_text.GetText()))

        try:
            # عناصر الشريط الجنبي
            if self.trans:
                self.trans.Destroy()
            # ترجمة جوجل
            translated = GoogleTranslator(source='auto', target=self.target_language).translate(
                str(source_text.GetText()))

            # إنشاء حقل النص المترجم في الشريط الجانبي
            self.trans = wx.StaticText(self.secondary_panel, label=str(translated))
            self.trans.Wrap(self.secondary_panel.Size[0] - 10)
            self.secondary_rsz.Add(self.trans, 0, wx.EXPAND | wx.ALL, 5)
            self.panel.Layout()
            self.trans.Bind(wx.EVT_LEFT_DOWN, self.onTansBtn)

        except Exception as e:
            wx.MessageDialog(None, str(e), 'Error', wx.OK | wx.ICON_ERROR).ShowModal()

    def onTansBtn(self, event):
        self.target.SetValue(str(self.trans.GetLabel()))

    # تحديث محتوى الصف في حال الكتابة في صندوق التحرير
    def OnTargetChange(self, event):
        text = event.GetString()
        if self.target_index != 'empty':
            self.table.SetItem(self.target_index, 2, text)

    def PreTrans(self, event):
        try:
            if self.table.GetItemCount() > 0:
                # عمل لوب للبيانات من الجدول
                for row in range(self.table.GetItemCount()):
                    source_text = self.table.GetItem(row, 1).GetText()
                    # ترجمة جوجل
                    translated = GoogleTranslator(source='auto', target=self.target_language).translate(
                        str(source_text))
                    self.table.SetItem(row, 2, str(translated))
                    self.table.Select(row - 1, 0)
                    self.table.Select(row)
                    self.table.Layout()
                    self.table.Update()
                    self.table.Refresh()
                wx.MessageDialog(None, 'Pre-Translate completed', 'Success', wx.OK | wx.ICON_INFORMATION).ShowModal()
            else:
                wx.MessageDialog(None, 'No text to translate', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
        except Exception as e:
            wx.MessageDialog(None, str(e), 'Error', wx.OK | wx.ICON_ERROR).ShowModal()

    def about_window(self, event):
        # wx.MessageBox('With ♥ by Dever', 'About', wx.OK | wx.ICON_INFORMATION)
        dlg = AboutWindow(self, wx.ID_ANY, title='About')
        dlg.ShowModal()


class AboutWindow(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        # using wx.adv.HyperlinkCtrl
        self.transolto = HyperlinkCtrl(self, wx.ID_ANY, "Transolto", "http://ufly.cc/692fef45")
        self.text = wx.StaticText(self, label='V1.0 with ♥ by')
        self.dever = HyperlinkCtrl(self, wx.ID_ANY, "Dever", "http://ufly.cc/dever")

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetSize((400, 100))
        self.transolto.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.dever.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))

    def __do_layout(self):
        grid_sizer_7 = wx.BoxSizer()
        grid_sizer_7.Add(self.transolto, 0, wx.CENTER | wx.ALL, 5)
        grid_sizer_7.Add(self.text, 0, wx.CENTER, 0)
        grid_sizer_7.Add(self.dever, 0, wx.CENTER | wx.ALL, 5)
        self.SetSizer(grid_sizer_7)
        self.Layout()


app = wx.PySimpleApp()
main_frame = MainWindow(parent=None, id=MAIN_FRAME_ID)
main_frame.Show()
app.MainLoop()
