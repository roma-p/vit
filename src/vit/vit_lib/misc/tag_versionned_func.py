import re


def generate_tag_auto_name_prefix(asset, branch):
    return "{}-{}-v".format(asset, branch)


def generate_tag_auto_regexp(asset, branch):
    return "{}[0-9].[0-9].[0-9]".format(
        generate_tag_auto_name_prefix(asset, branch)
    )


def generate_tag_auto_name_by_branch(asset, branch, major, minor, patch):
    return "{}{}.{}.{}".format(
        generate_tag_auto_name_prefix(asset, branch),
        major, minor, patch
    )


def get_version_from_tag_auto(tag_name):
    ret = re.findall("[0-9]", tag_name)
    return tuple([int(i) for i in ret])


def check_is_auto_tag(tag_name):
    regxp = "(.+?(?=-v))-v[0-9].[0-9].[0-9]"
    return bool(re.match(regxp, tag_name))


def check_is_auto_tag_of_branch(asset_name, branch, tag_name):
    regxp = generate_tag_auto_regexp(asset_name, branch)
    return bool(re.match(regxp, tag_name))


def increment_version(index_to_increment, *version_numbers):
    version_numbers = list(version_numbers)
    version_numbers[index_to_increment] += 1
    for i in range(index_to_increment + 1, len(version_numbers)):
        version_numbers[i] = 0
    return tuple(version_numbers)
