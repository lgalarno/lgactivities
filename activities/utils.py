from django.conf import settings

from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.session_message import SessionMessage

from os import path


def virtualride_in_fit(fp):
    result = True
    try:
        fit_file = FitFile.from_file(fp)
        builder = FitFileBuilder(auto_define=True)
        include_record = True
        for record in fit_file.records:
            message = record.message
            if message.global_id == SessionMessage.ID:
                if record.is_definition:
                    include_record = False
                else:
                    new_message = SessionMessage()
                    for f in message.fields:
                        if f.get_value():
                            setattr(new_message, f.name, f.get_value())
                    new_message.sub_sport = 58
                    message = new_message
            if include_record:
                builder.add(message)
            else:
                include_record = True
        modified_file = builder.build()
        out_path = path.join(path.dirname(fp), 'new_' + path.basename(fp))
        modified_file.to_file(out_path)
    except Exception as e:
        result = False
        out_path = e
    return out_path, result


def fit_to_csv(fp):
    """
    """
    result = True
    try:
        fit_file = FitFile.from_file(fp)
        fn_csv = fp.replace('fit', 'csv')
        fit_file.to_csv(fn_csv)
    except Exception as e:
        result = False
        fn_csv = e
    return fn_csv, result


# def get_fit_file(u, activity):
#     e, access_token = get_token(user=u)
#     if not e:
#         header = {'Authorization': f'Bearer {access_token}'}
#         param = {}
#         url = f'https://www.strava.com/activities/{activity}/export_gpx'
#         r = requests.get(url, headers=header, params=param, verify=False)
#         print(r)
#         if 'errors' in r:
#             e = formaterror(r['errors'])
#             return e
#         else:
#             with open('/media/luc/DataFast/owncloud/public_html/lgactivities/media/files/temp.fit', 'wb') as f:
#                 f.write(r.content)
#             return True
