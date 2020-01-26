'''
ToDo:
* Implement search
X Implement links
X App Icon
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.config import Config
import webbrowser
import config
from congress import Congress

class ListScreen(Screen):
    pass

class DetailScreen(Screen):
    API_KEY = config.APP_CONFIG['api_key']
    PHOTO_URL = config.APP_CONFIG['photo_url']

    def on_pre_enter(self):
        self.getPersonDetail()

    def getPersonDetail(self):
        self.congress = Congress(self.API_KEY)
        senator = self.congress.members.get(App.member_id)
        
        '''
        https://theunitedstates.io/images/congress/[size]/[bioguide].jpg
        [size] can be one of:
        original - As originally downloaded. Typically, 675x825, but it can vary.
        450x550
        225x275
        '''

        try:
            photo_url = self.PHOTO_URL + App.member_id + '.jpg'
            self.ids.head_shot.source = photo_url
        except Exception as e:
            pass

        try:
            self.txtName.text = str(senator['first_name']) + ' ' + str(senator['last_name'])
            self.txtState.text = str(senator['roles'][0]['state'])
            self.txtParty.text = str(senator['roles'][0]['party'])
            self.txtChamber.text = str(senator['roles'][0]['chamber'])
            self.txtBirthday.text = str(senator['date_of_birth'])
            self.txtPhone.text = str(senator['roles'][0]['phone'])
            self.txtAddress.text = str(senator['roles'][0]['office'])
            self.txtVotes.text =  str(senator['roles'][0]['missed_votes_pct']) + '%'

            if senator['url']:
                self.lblWeb.text = '[ref=web]Web[/ref]'
                self.lblWeb.bind(on_ref_press=lambda self, x:webbrowser.open(str(senator['url'])))
            
            if senator['govtrack_id']:
                self.lblGovTrack.text = '[ref=govtrack]GovTrack[/ref]'
                url_name = str(senator['first_name']+ '_' + str(senator['last_name']))
                gt_url = 'https://www.govtrack.us/congress/members/' + url_name + '/'
                self.lblGovTrack.bind(on_ref_press=lambda self, x:webbrowser.open(gt_url + str(senator['govtrack_id'])))

            if senator['votesmart_id']:
                self.lblVoteSmart.text = '[ref=votesmart]VoteSmart[/ref]'
                vs_url = 'https://votesmart.org/candidate/'
                self.lblVoteSmart.bind(on_ref_press=lambda self, x:webbrowser.open(vs_url + str(senator['votesmart_id'])))
            
            if senator['crp_id']:
                self.lblCrp.text = '[ref=crp]CRP[/ref]'
                crp_url = 'https://www.opensecrets.org/members-of-congress/summary?cid='
                self.lblCrp.bind(on_ref_press=lambda self, x:webbrowser.open(crp_url + str(senator['crp_id'])))
            
        except KeyError:
            pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    pass
    
class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''

        # TCK ToDo: index will always be zero after a search
        self.selected = is_selected
        if is_selected:
            App.giIndex = index
            if rv.parent.parent.current_tab.text == "Senate":
                App.member_id = OpenCongress.dictSenate[index]
            else:
                App.member_id = OpenCongress.dictHouse[index]

            rv.parent.parent.parent.parent.manager.current = 'detail'
            
class OpenCongress(BoxLayout):
    API_KEY = config.APP_CONFIG['api_key']
    dictSenate = {}
    dictHouse = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.congress = Congress(self.API_KEY)

        rvSenate = ObjectProperty(None)
        rvHouse = ObjectProperty(None)

    def getChamberList(self, chamber):
        # Clear search box
        # self.search_text.text = ""

        # Clear lists for search
        if chamber == 'senate':
            self.rvSenate.data = []
        else:
            self.rvHouse.data = []

        all_members = self.congress.members.filter(chamber)
        num_results = int(all_members[0]['num_results'])
        member_list = all_members[0]['members']

        i = 0
        while i < num_results:
            first_name = member_list[i]['first_name']
            last_name = member_list[i]['last_name']
            state = member_list[i]['state']
            party = member_list[i]['party']
            memberLine = str.format('%s %s (%s) %s' % (first_name, last_name, party, state))

            if chamber == 'senate':
                self.dictSenate[i] = member_list[i]['id']
                self.rvSenate.data.append({'text': memberLine})
            else:
                self.dictHouse[i] = member_list[i]['id']
                self.rvHouse.data.append({'text': memberLine})

            i += 1

    def searchChamber(self, search_text):
        chamber = self.tabbed_panel.current_tab.text
        if chamber == 'Senate':
            self.full_list = self.rvSenate.data
            data_items = [list(i.values())[0] for i in self.full_list]  # unpack the list of dictionaries to get the data
            s = sorted(data_items, key=lambda x: x.count(search_text), reverse=True)
            s = s[0:1]
            self.rvSenate.data = [{'text': item} for item in s]  # repack the dictionary

            # Remove brackets and quotes
            search_string = str(s).replace('[','').replace(']','')
            search_string = eval(search_string)

            _index = data_items.index(search_string)
            App.member_id = self.dictSenate[_index]
            print('member_id from search: {}'.format(App.member_id))

        else:
            self.full_list = self.rvHouse.data
            data_items = [list(i.values())[0] for i in self.full_list]  # unpack the list of dictionaries to get the data
            s = sorted(data_items, key=lambda x: x.count(search_text), reverse=True)
            s = s[0:1]
            self.rvHouse.data = [{'text': item} for item in s]  # repack the dictionary

class OpenCongressApp(App):
    giIndex = 0
    member_id = StringProperty('')

    def on_start(self):
        self.icon = './data/dome.png'
        p = self.root.ids.sm.get_screen('list').ids.open_congress

        p.getChamberList('senate')
        p.getChamberList('house')

if __name__ == '__main__':
    OpenCongressApp().run()
