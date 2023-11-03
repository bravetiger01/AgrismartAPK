import kivymd
from kivymd.app import MDApp 
from kivy.lang import Builder 
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDIconButton
from kivy.uix.image import Image
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.scrollview import MDScrollView
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.clock import Clock 
import sqlite3
import re 
import cv2 

Window.size=(360,640)

class SplashScreen(MDScreen):
    def on_enter(self, *args):
        Clock.schedule_once(self.switch_to_home, 10)
    def switch_to_home(self, dt):
        self.manager.current="Login"

class LoginScreen(MDScreen):
    def sign_in(self):
        username = self.ids.username.text
        password = self.ids.password.text

        con = sqlite3.connect("ssip.db")
        cur = con.cursor()
        query = '''
        SELECT * FROM ssiptb WHERE username=? AND password=?'''
        cur.execute(query, (username, password))
        result=cur.fetchone()

        if result is None or not username or not password:
            retry= MDFlatButton(text="Retry", on_press=self.close_retry)
            self.dialog = MDDialog(title = "Error", text = "Invalid Username or Password", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        else:
            self.username=username
            self.manager.get_screen("Home").useracc(username)
            self.manager.current="Home"
            self.manager.transition.direction="left"

    def close_retry(self, obj):
        self.dialog.dismiss()

class SignUpScreen(MDScreen):

    def insert_data(self):
        username = self.ids.username.text
        email = self.ids.email.text
        password = self.ids.password.text
        cfmpassword = self.ids.cfmpassword.text

        if not username or not email or not password or not cfmpassword:
            retry= MDFlatButton(text="Retry", on_press=self.close_retry2)
            self.dialog = MDDialog(title = "Error", text = "Please fill in all the details", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif password!=cfmpassword:
            retry= MDFlatButton(text="Retry", on_press=self.close_retry2)
            self.dialog = MDDialog(title = "Error", text = "Password and Confirm Password do not match", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif len(password)<8:
            retry= MDFlatButton(text="Retry", on_press=self.close_retry2)
            self.dialog = MDDialog(title = "Error", text = "Password must contain 8 characters", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif not self.is_valid_email(email):
            close= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Invalid Email", size_hint = (0.7,0.2), buttons=[close])
            self.dialog.open()
        else:
            self.username = username
            self.email = email
            self.password = password

            con = sqlite3.connect("ssip.db")
            cur = con.cursor()
            insert_query = '''
            INSERT INTO ssiptb (username, email, password)
            VALUES (?, ?, ?)
            
        '''
            cur.execute(insert_query, (username, email, password))
            con.commit()
            con.close()

            self.manager.current="Home"
            self.manager.transition.direction="left"

    def close1(self, obj):
        self.dialog.dismiss()

    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

class HomeScreen(MDScreen):

    def useracc(self,username):
        self.username=username

    def delete(self):
        dialog = MDDialog(
            title='Delete Account',
            text='Are you sure you want to delete your account?',
            buttons=[MDFlatButton(text='Yes', on_release=self.on_yes),
                MDFlatButton(text='No', on_press=lambda x: dialog.dismiss())])
        dialog.open()
        self.dialog=dialog
    
    def on_yes(self, obj): 
        con = sqlite3.connect("ssip.db")
        cur = con.cursor()
        query = '''
        DELETE FROM ssiptb WHERE username=?'''
        cur.execute(query, (self.username,))
        con.commit()
        con.close()

        self.dialog.dismiss()

        self.manager.current="Login" 
        self.manager.transition.direction="left"

class Scan(MDScreen):
    def __init__(self, **kwargs):
        super(Scan, self).__init__(**kwargs)
        self.frame = None 

    def on_enter(self):
        self.capture = cv2.VideoCapture(0)
        layout = MDBoxLayout(orientation="vertical")
        self.image = Image()
        layout.add_widget(self.image)
        self.saveimg=MDIconButton(icon="circle-slice-8", icon_size="60sp", pos_hint={"center_x":0.5, "center_y":0.5})
        self.saveimg.bind(on_press=self.capture_image)
        layout.add_widget(self.saveimg)
        self.add_widget(layout)
        Clock.schedule_interval(self.load_video, 1.0 / 30.0)

    def load_video(self, *args):
        ret, frame = self.capture.read()
        self.frame=frame
        if ret:
            buffer = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.image.texture = texture
            
    def capture_image(self, instance):
        img_name="D:\Vanshi\ssip\disease.png"
        cv2.imwrite(img_name, self.frame)

class ShopScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDGridLayout(cols=2) 
    def rentout(self):
        self.manager.current="RentOut" 
        self.manager.transition.direction="left"
    def display(self):
        self.layout = MDGridLayout(pos_hint={"center_y":0.4}, cols=2, spacing=30, padding=10, adaptive_height=True, adaptive_width=True)

        con = sqlite3.connect("ssip.db")
        print("Database connection established.")
        cur = con.cursor()
        query = '''SELECT * FROM img'''
        cur.execute(query)
        data = cur.fetchall()

        if data:
            print(data[0])
        else:
            print("No data found for the given criteria")

        self.layout.clear_widgets()
        for i in data:
            print(i)
            img_source=i[7]
            card_layout = MDFloatLayout(pos_hint = {"center_y": 0.33})
            fit_image = Image(source=img_source, size_hint=(None, None), size=("120dp", "120dp"), pos_hint={"center_x": 0.5, "center_y":0.85})
            label = MDLabel(text=f"₹{i[6]}", theme_text_color="Custom", text_color="#86D176", halign="center", pos_hint={"center_x": 0.5, "center_y": 0.3})

            card_layout.add_widget(fit_image)
            card_layout.add_widget(label)

            card = MDCard(size_hint=(None, None), size=("150dp", "150dp"), on_press=lambda x, i=i: self.open_card_screen(i))
            card.add_widget(card_layout)
            self.layout.add_widget(card)

        scroll_view = MDScrollView()
        scroll_view.pos_hint = {"center_y": 0.33}
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    def open_card_screen(self, i):
        app = MDApp.get_running_app()
        card_screen = CardScreen(name=f"card_{i[0]}")
        img=Image(source=i[7], size_hint=(None, None), size=("200dp", "200dp"), pos_hint={"center_x":0.5, "center_y":0.7})
        name=MDLabel(text=f"Name: {i[0]}", pos_hint={"center_x":0.7, "center_y":0.65}, theme_text_color="Custom", text_color=[0,0,0,0])
        add=MDLabel(text=f"Address: {i[1]}", pos_hint={"center_x":0.7, "center_y":0.6}, theme_text_color="Custom", text_color=[0,0,0,0])
        email=MDLabel(text=f"Email: {i[2]}", pos_hint={"center_x":0.7, "center_y":0.55}, theme_text_color="Custom", text_color="#000000")
        phno=MDLabel(text=f"Contact No: {i[3]}", pos_hint={"center_x":0.7, "center_y":0.5}, theme_text_color="Custom", text_color="#000000")
        pname=MDLabel(text=f"Product Name: {i[4]}", pos_hint={"center_x":0.7, "center_y":0.45}, theme_text_color="Custom", text_color="#000000")
        pdscrp=MDLabel(text=f"Product Description: {i[5]}", pos_hint={"center_x":0.7, "center_y":0.4}, theme_text_color="Custom", text_color="#000000")
        price=MDLabel(text=f"Price: {i[6]}", pos_hint={"center_x":0.7, "center_y":0.35}, theme_text_color="Custom", text_color="#000000")
        card_screen.add_widget(img)
        card_screen.add_widget(name)
        card_screen.add_widget(add)
        card_screen.add_widget(email)
        card_screen.add_widget(phno)
        card_screen.add_widget(pname)
        card_screen.add_widget(pdscrp)
        card_screen.add_widget(price)
        app.root.add_widget(card_screen)
        app.root.current = f"card_{i[0]}"

class CardScreen(MDScreen):
    pass

class Img(MDScreen):
    pass

class RentOut(MDScreen):
    path = ""
    def select_image(self):
        img_screen = self.manager.get_screen("Img")
        selected_file = img_screen.ids.filechooser.selection
        if selected_file:
            self.path = selected_file[0]
            self.manager.get_screen("RentOut").save()
            
    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def is_valid_phone_number(self, phno):
        pattern = r'^[789]\d{9}$'
        return re.match(pattern, phno) is not None

    def save(self):
        name=self.ids.name.text
        address=self.ids.name.text
        email=self.ids.email.text
        price=self.ids.price.text
        pname=self.ids.pname.text
        pdscrp=self.ids.pdscrp.text
        phno=self.ids.phno.text

        if not name or not address or not email or not price or not pname or not pdscrp or not phno or not self.path.strip():
            close= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Please fill in all the details", 
                                   size_hint = (0.7,0.2), buttons=[close])
            self.dialog.open()
            
        elif len(phno)<10 or not self.is_valid_phone_number(phno):
            close= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Invalid Phone Number", size_hint = (0.7,0.2), buttons=[close])
            self.dialog.open()
            
        elif not self.is_valid_email(email):
            close= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Invalid Email", size_hint = (0.7,0.2), buttons=[close])
            self.dialog.open()

        else:
            path=str(self.path)
            print(path)
            con = sqlite3.connect("ssip.db")
            cursor = con.cursor()
            cursor.execute("INSERT INTO img (name, address, email, phno, pname, pdscrp, price, path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, address, email, phno, pname, pdscrp, price, path))
            print("Data inserted successfully.")
            con.commit()
            con.close()

            Snackbar(text="Successfully Submitted!").open()

            self.pname=pname
            self.pdscrp=pdscrp
            self.phno=phno
            self.path=path
            self.manager.current="Shop"
            self.manager.get_screen("Shop").display()

    def close1(self, obj):
        self.dialog.dismiss()
 
class Policies(MDScreen):
    def policy(self):
        grid_layout= MDGridLayout(cols=1, spacing=10, pos_hint={"center_y":0.4})

        con = sqlite3.connect("ssip.db")
        cur = con.cursor()
        query = '''SELECT * FROM policy'''
        cur.execute(query)
        data = cur.fetchall()

        for i in data:
            item = OneLineListItem(text=i[0],theme_text_color="Custom",text_color="#000000",on_press=lambda x, i=i: self.show_policy_details(i))
            grid_layout.add_widget(item)
        self.add_widget(grid_layout)

    def show_policy_details(self, i):
        app = MDApp.get_running_app()
        screen_name = f"policy_{i[0]}"
        pdetail_screen = PolicyDetailScreen(name=screen_name)

        layout=MDGridLayout(cols=1, pos_hint={"center_y":0.4}) 
        
        pdetail=MDLabel(text=i[1], theme_text_color="Custom", text_color="#000000",  halign="justify", pos_hint={"center_x": 0.5, "center_y": 0.3})
        layout.add_widget(pdetail)

        scroll_view = MDScrollView(pos_hint={"center_y": 0.33})
        scroll_view.add_widget(layout)

        pdetail_screen.add_widget(scroll_view)
        app.root.add_widget(pdetail_screen)
        app.root.current = f"policy_{i[0]}"

class PolicyDetailScreen(MDScreen):
    pass

class ssipApp(MDApp): 
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette= "Green"
        return Builder.load_file("ssip.kv")

if __name__=='__main__':
    ssipApp().run()