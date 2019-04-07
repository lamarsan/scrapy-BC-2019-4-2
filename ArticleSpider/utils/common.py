import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    # 从字符串中提取出数字
    # answer_num
    match_re = re.match("(.*)个.*", text)
    if match_re:
        nums = int(match_re.group(1).replace(",", "").strip())
    # comment_num
    elif re.match("(.*)条.*", text):
        match_re = re.match("(.*)条.*", text)
        nums = int(match_re.group(1).replace(",", "").strip())
    else:
        if text != "添加评论":
            nums = int(text.replace(",", "").strip())
        else:
            nums = 0
    return nums


if __name__ == "__main__":
    re1 = re.match("(.*)个.*", "1,650 个回答")
    re2 = re.match(".*?,(\d+).*", "48,886,123")
    re = re1.group(1).replace(",", "").strip()
    print(re)
    print(re2.group(1))
