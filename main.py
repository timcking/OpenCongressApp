from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

import config
from congress import Congress

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    
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
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

class OpenCongress(BoxLayout):
    API_KEY = config.APP_CONFIG['api_key']
    dictSenate = {}
    dictHouse = {}

    def __init__(self, **kwargs):
        # super(OpenCongress, self).__init__(**kwargs)
        super().__init__()

        self.congress = Congress(self.API_KEY)
        self.getChamberList('senate')
        self.getChamberList('house')

    def getChamberList(self, chamber):
        all_members = self.congress.members.filter(chamber)

        # print (all_members)
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
                self.rv.data.append({'text': memberLine})
            else:
                self.dictHouse[i] = member_list[i]['id']
                self.rv2.data.append({'text': memberLine})

            i += 1

class OpenCongressApp(App):
    def build(self):
        return OpenCongress()

if __name__ == '__main__':
    OpenCongressApp().run()
