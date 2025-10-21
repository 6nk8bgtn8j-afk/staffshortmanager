# -*- coding: utf-8 -*-
import os
import json
import platform
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App

DATA_FILE = "employees.json"

Builder.load_string('''
<EmployeeItem@Button>:
    background_color: (0.9, 0.9, 0.9, 1)
    color: (0, 0, 0, 1)
    font_name: 'CN'
    font_size: '16sp'
    size_hint_y: None
    height: '40dp'

<MainLayout>:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'

    Label:
        text: '员工短号管理'
        font_name: 'CN'
        font_size: '24sp'
        size_hint_y: None
        height: '50dp'
        bold: True

    TextInput:
        id: search_field
        hint_text: '搜索姓名或短号...'
        font_name: 'CN'
        font_size: '16sp'
        size_hint_y: None
        height: '40dp'
        multiline: False
        on_text: root.app.refresh_list(self.text)

    ScrollView:
        GridLayout:
            id: container
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: '5dp'

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: '50dp'
        spacing: '10dp'

        TextInput:
            id: name_field
            hint_text: '姓名'
            font_name: 'CN'
            font_size: '16sp'
            multiline: False

        TextInput:
            id: short_field
            hint_text: '短号'
            font_name: 'CN'
            font_size: '16sp'
            multiline: False

        Button:
            text: '添加'
            font_name: 'CN'
            font_size: '14sp'
            on_release: root.app.add_employee()
''')


class MainLayout(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app


class EmployeeApp(App):
    def build(self):
        """构建界面并注册中文字体"""
        self.register_chinese_font()
        self.title = "员工短号管理"
        self.data = []
        self.dialog = None
        self.main_layout = MainLayout(app=self)
        return self.main_layout

    def register_chinese_font(self):
        """安全注册中文字体"""
        system = platform.system()
        print(f"检测到操作系统: {system}")

        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(name="CN", fn_regular=font_path)
                    print(f"✅ 成功注册字体: {font_path}")
                    return
                except Exception as e:
                    print(f"❌ 字体注册失败 {font_path}: {e}")

        print("⚠️ 所有字体注册尝试都失败，使用默认字体")
        LabelBase.register(name="CN", fn_regular="")

    def on_start(self):
        """程序启动时加载数据"""
        self.load_data()

    def load_data(self):
        """从 JSON 加载数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.data = []
        else:
            self.data = []
        self.refresh_list()

    def save_data(self):
        """保存 JSON"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def refresh_list(self, query=""):
        """刷新员工列表，可搜索"""
        container = self.main_layout.ids.container
        container.clear_widgets()
        container.height = 0

        for emp in self.data:
            if query.lower() in emp["name"].lower() or query in emp["short"]:
                item = Button(
                    text=f"{emp['name']} - {emp['short']}",
                    on_release=lambda x, e=emp: self.show_edit_dialog(e),
                )
                item.font_name = "CN"
                item.font_size = '16sp'
                container.add_widget(item)
                container.height += item.height + 5

    def clear_inputs(self):
        """清空输入框"""
        self.main_layout.ids.name_field.text = ""
        self.main_layout.ids.short_field.text = ""

    def add_employee(self):
        """新增员工"""
        name = self.main_layout.ids.name_field.text.strip()
        short = self.main_layout.ids.short_field.text.strip()
        if not name or not short:
            self.show_message("请输入姓名和短号")
            return
        self.data.append({"name": name, "short": short})
        self.save_data()
        self.refresh_list()
        self.clear_inputs()

    def show_message(self, msg):
        """提示框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=msg, font_name='CN', font_size='16sp'))

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn = Button(text='确定', font_name='CN', font_size='14sp')
        btn_layout.add_widget(btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='提示',
            content=content,
            size_hint=(0.6, 0.4)
        )
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_edit_dialog(self, emp):
        """显示编辑对话框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_field = TextInput(
            text=emp["name"],
            hint_text="姓名",
            font_name="CN",
            font_size='16sp',
            multiline=False
        )
        short_field = TextInput(
            text=emp["short"],
            hint_text="短号",
            font_name="CN",
            font_size='16sp',
            multiline=False
        )

        content.add_widget(Label(text='编辑员工信息', font_name='CN', font_size='18sp', bold=True))
        content.add_widget(name_field)
        content.add_widget(short_field)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        delete_btn = Button(text='删除', font_name='CN', font_size='14sp')
        save_btn = Button(text='保存', font_name='CN', font_size='14sp')

        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.6)
        )

        def update_employee(instance):
            emp["name"] = name_field.text.strip()
            emp["short"] = short_field.text.strip()
            self.save_data()
            self.refresh_list()
            popup.dismiss()

        def delete_employee(instance):
            self.data.remove(emp)
            self.save_data()
            self.refresh_list()
            popup.dismiss()

        save_btn.bind(on_release=update_employee)
        delete_btn.bind(on_release=delete_employee)

        popup.open()


if __name__ == "__main__":
    EmployeeApp().run()