from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import config
from congress import Congress

class OpenCongress(BoxLayout):
    API_KEY = config.APP_CONFIG['api_key']

    def __init__(self):
        super().__init__()

        self.congress = Congress(self.API_KEY)
        self.getChamberList('senate')

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

            self.rv.data.append({'value': memberLine})

            # if chamber == 'senate':
            #     self.dictSenate[i] = member_list[i]['id']
            #     self.ui.listSenate.addItem(memberLine)
            # else:
            #     self.dictHouse[i] = member_list[i]['id']
            #     self.ui.listHouse.addItem(memberLine)
            i += 1

class OpenCongressApp(App):
    def build(self):
        return OpenCongress()

if __name__ == '__main__':
    OpenCongressApp().run()
