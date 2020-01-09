'''
ToDo:
* Implement links
* Implement search
* App Icon
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

import config
from congress import Congress

class ListScreen(Screen):
    pass

class DetailScreen(Screen):
    API_KEY = config.APP_CONFIG['api_key']
    PHOTO_URL = config.APP_CONFIG['photo_url']

    def on_pre_enter(self):
        # member_id = App.member_id
        # print("In on_pre_enter: " + member_id)
        # self.ids.state.text = member_id 
        self.getPersonDetail()

    def getPersonDetail(self):
        self.congress = Congress(self.API_KEY)
        senator = self.congress.members.get(App.member_id)
        
        # https://theunitedstates.io/images/congress/[size]/[bioguide].jpg
        # [size] can be one of:
        # original - As originally downloaded. Typically, 675x825, but it can vary.
        # 450x550
        # 225x275

        try:
            url = self.PHOTO_URL + App.member_id + '.jpg'
            self.ids.head_shot.source = url
        except Exception as e:
            pass

        try:
            self.ids.name.text = str(senator['first_name']) + ' ' + str(senator['last_name'])
            self.ids.state.text = str(senator['roles'][0]['state'])
            self.ids.party.text = str(senator['roles'][0]['party'])
            self.ids.chamber.text = str(senator['roles'][0]['chamber'])
            self.ids.birthday.text = str(senator['date_of_birth'])
            self.ids.phone.text = str(senator['roles'][0]['phone'])
            self.ids.address.text = str(senator['roles'][0]['office'])
            self.ids.votes.text =  str(senator['roles'][0]['missed_votes_pct']) + '%'

        #     if senator['url']:
        #         self.person_detail.lblWeb.setText('<a href=' + senator['url'] + '>Web</a>')
        #         self.person_detail.lblWeb.setOpenExternalLinks(True)
        #     else:
        #         self.person_detail.lblWeb.setText('Web')
            
        #     if senator['govtrack_id']:
        #         url_name = str(senator['first_name']+ '_' + str(senator['last_name']))
        #         url = 'https://www.govtrack.us/congress/members/' + url_name + '/'
        #         self.person_detail.lblGovTrack.setText('<a href=' + url + str(senator['govtrack_id']) + '>GovTrack</a>')
        #         self.person_detail.lblGovTrack.setOpenExternalLinks(True)
        #     else:
        #         self.person_detail.lblGovTrack.setText('GovTrack')
            
        #     if senator['votesmart_id']:
        #         url = 'https://votesmart.org/candidate/'
        #         self.person_detail.lblVoteSmart.setText('<a href=' + url + str(senator['votesmart_id']) + '>VoteSmart</a>')
        #         self.person_detail.lblVoteSmart.setOpenExternalLinks(True)
        #     else:
        #         self.person_detail.lblVoteSmart.setText('VoteSmart')
            
        #     if senator['crp_id']:
        #         # url = 'https://www.opensecrets.org/members-of-congress/summary?cid='
        #         # Need to escape the = sign with &#61;
        #         url = 'https://www.opensecrets.org/members-of-congress/summary?cid&#61;'
        #         crp_link = '<a href=' + url + str(senator['crp_id']) + '>CRP</a>'
        #         self.person_detail.lblCrp.setText(crp_link)
        #         self.person_detail.lblCrp.setOpenExternalLinks(True)
        #     else:
        #         self.person_detail.lblCrp.setText('CRP')
            
        except KeyError:
            pass

class ScreenManagement(ScreenManager):
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
        self.selected = is_selected
        if is_selected:
            App.giIndex = index
            if rv.parent.parent.current_tab.text == "Senate":
                App.member_id = rv.parent.parent.parent.dictSenate[index]
            else:
                App.member_id = rv.parent.parent.parent.dictHouse[index]

            rv.parent.parent.parent.parent.manager.current = 'detail'
            
class OpenCongress(BoxLayout):
    API_KEY = config.APP_CONFIG['api_key']
    dictSenate = {}
    dictHouse = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.congress = Congress(self.API_KEY)

        # TCK
        tabbed_panel = ObjectProperty(None)
        rvSenate = ObjectProperty(None)
        rvHouse = ObjectProperty(None)

    def getChamberList(self, chamber):
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

class OpenCongressApp(App):
    giIndex = 0
    member_id = StringProperty('')

    def on_start(self):
        p = self.root.ids.sm.get_screen('list').ids.open_congress

        p.getChamberList('senate')
        p.getChamberList('house')

if __name__ == '__main__':
    OpenCongressApp().run()

