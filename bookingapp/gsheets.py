# -*- coding: utf-8 -*-

from googleapiclient.discovery import build


class GSheetSlotRequest:

    def __init__(self, sheet_id: str = '1Atr4sHOFmiIMxOY6rz2HjH4F6JD#&#ziXsN9G8s'):
        """Init API connection object"""

        # If modifying these scopes, delete the file token.pickle.
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # The ID and range of a sample spreadsheet.
        self.SPREADSHEET_ID = sheet_id

        service = build('sheets', 'v4', developerKey='AIJH94-L1caaR_4v3ZgcKC9FhfeVHldF8unmAA')
        self.sheets = service.spreadsheets()

    def get(self, request_range):
        """Execute a request to the API and return raw data"""

        result = self.sheets.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                          range=request_range).execute()

        values = result.get('values', [])

        if not values:
            raise NoDataError(self.SPREADSHEET_ID, range)
        else:
            return values

    def get_slots_for_teacher_d(self, teacher_name):
        """Get, format and return time slots for teacher as dict:
        {'7:30': [1, 1, 1, 1, 1, 0, 0],
        ...
        '19:30': [1, 1, 1, 1, 1, 0, 0]}

        where time slots are keys and rows represent this time slot
        on a particular day of the week (mon-sun)"""

        time_slot_range = '!A2:H27'
        request_range = teacher_name + time_slot_range

        response = self.get(request_range)

        slots_d = {}

        for row in response:

            # Pad incomplete rows with empty values
            for i in range(0, 8 - len(row)):
                row.append('')

            # Transform string values into ints
            for j in range(1, len(row)):
                if row[j] != '':
                    row[j] = 1
                else:
                    row[j] = 0

            slots_d[row[0]] = row[1:8]

        return slots_d

    def get_slots_for_teacher_m(self, teacher_name, time_slot_range):
        """Get, format and return time slots for teacher as matrix:
             7:30 ...                                                                  19:30
        mon: [[0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        tue:  [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        wed:  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        thu:  [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        fri:  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        sat:  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        sun:  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        """

        response = self.get(teacher_name + time_slot_range)

        slots_m = []

        for row in response:

            # Pad incomplete rows with empty values
            for i in range(0, 8 - len(row)):
                row.append('')

            # Transform string values into ints
            for j in range(1, len(row)):
                if row[j] != '':
                    row[j] = 1
                else:
                    row[j] = 0

            # Remove leftmost column containing slot labels
            row.pop(0)

            # Append row to matrix
            slots_m.append(row)

        # Transpose matrix
        slots_m = [[c for c in r] for r in zip(*slots_m)]

        return slots_m

    def get_corrected_slots_for_teacher_m(self, teacher_name, time_slot_range):
        """ convert 30 minutes to 1 hour """
        rez = self.get_slots_for_teacher_m(teacher_name, time_slot_range)
        for column in rez:
            for j in range(0, len(column)):
                if column[j] == 1 and j > 0:
                    if column[j - 1] == 0:
                        column[j + 1] = 1
        return rez

    def get_teacher_names(self) -> list:
        """Fetch, filter and return names of all teachers in the spreadsheet"""

        metadata = self.sheets.get(spreadsheetId=self.SPREADSHEET_ID).execute()
        sheet_list = metadata.get('sheets', '')

        teacher_names: list = []

        for sheet in sheet_list:
            sheet_name: str = sheet['properties']['title']

            # Some hidden or system sheets start with '__'. Ignore them
            if sheet_name[0:2] != '__':
                teacher_names.append(sheet_name.lower())

        return teacher_names

    def get_slots_for_all_teachers(self):
        """Returns structured time slots for all teachers like so:

        teacher_time_slots = {
            'teacher1' : {
                '9:00' : [1, 1, 1, 1, 1, 0, 0]
                ...
            }
            ...
        }

        , so teacher_time_slots['teacher1']['12:00'] will return [] of slots
        for each day of the week (Mon-Sun)

        """

        teacher_time_slots = {}

        for teacher in self.get_teacher_names():
            teacher_time_slots[teacher] = self.get_slots_for_teacher_m(teacher)

        return teacher_time_slots


class NoDataError(Exception):

    def __init__(self, spreadsheet_id, request_range):
        print("Error: No data was returned from the request!")
        print("Spreadsheet id: %s" % spreadsheet_id)
        print("Range: %s" % request_range)


def test():
    """Testing function. Remove."""
    api = GSheetSlotRequest('1Atr4sHOFmiIMxOY6rz2Hj*#GDLF*$iXsN9G8s')
    teachers = api.get_teacher_names()
    print('teachers ', teachers)
    teacher_time_slots: list = api.get_slots_for_all_teachers()
    teacher: str = 'Yura'
    # print(api.get_slots_for_teacher_m(teacher))
    print(api.get_corrected_slots_for_teacher_m('nazar'))
    teachers: list = api.get_teacher_names()

