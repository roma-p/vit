import time
from vit.vit_lib.log import get_log_data


def get_log_lines(local_path, asset_path):
    ret = []
    log_data = get_log_data(local_path, asset_path)
    sorted_date = sorted(log_data.keys(), reverse=True)
    for date in sorted_date:
        event_data = log_data[date]
        if "tag" in event_data:
            func = _gen_tag_log
        else:
            func = _gen_commit_log
        ret += func(date, event_data)
    return tuple(ret)


def _gen_commit_log(date, event_data):
    ret = []
    ret.append("commit {}".format(event_data["commit"]))
    ret.append(_gen_auhtor_line(event_data["user"]))
    ret.append(_gen_date_line(date))
    ret.append(_gen_mess_line(event_data["message"]))
    ret.append("")
    return ret


def _gen_tag_log(date, event_data):
    ret = []
    ret.append("tag {} -> {} ".format(event_data["tag"], event_data["commit"]))
    if "user" in event_data:
        ret.append(_gen_auhtor_line(event_data["user"]))
        ret.append(_gen_date_line(date))
        ret.append(_gen_mess_line(event_data["message"]))
    else:
        ret.append(_gen_date_line(date))
    ret.append("")
    return ret


def _gen_auhtor_line(author):
    return "Author:\t{}".format(author)


def _gen_date_line(epoch_date):
    formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_date))
    return "Date:\t{}".format(formatted_date)


def _gen_mess_line(mess):
    return "\t{}".format(mess)
