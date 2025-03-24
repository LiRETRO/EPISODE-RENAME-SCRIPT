import os
import re

chinese_num_map = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18
}

def file_name_matcher(file_name, force_rename = False):
    # 忽略已按规则命名的文件
    pat = r'S(\d{1,4})E(\d{1,4}(\.5)?)'
    res = re.match(pat, file_name)
    if res:
        if force_rename:
            season, ep = res[1], res[2]
            return season, ep
        else:
            return None, None
    # 匹配规则
    # S01E01, S01EP01
    pat = r'[Ss](\d{1,4})(?:[Ee]|[Ee][Pp])(\d{1,4}(\.5)?)'
    res = re.findall(pat, file_name.upper())
    if res:
        season, ep = res[0][0], res[0][1]
        return season, ep
    # 匹配中文
    pattern = r'第([\u4e00-\u9fa5\d]+)季.*?(?<!\d)(\d{1,4})(?!\d)'
    match = re.search(pattern, file_name)
    if match:
        season = match.group(1)  # 季数
        if not season.isdigit():
            season = chinese_num_map.get(season, None)
        ep = match.group(2)  # 集数
        return season, ep
    return None, None

def get_season(parent_folder_name):
    """
    获取季数
    """

    season = None
    if parent_folder_name == 'Specials':
        # 兼容SP
        return '0'
    patterns = [
        # 规则1: Season + 数字（如 Season 1）
        r'(?i)season[\s\-_]*(\d+)',
        # 规则2: S + 数字（如 S01）
        r'(?i)S[\s\-_]*(\d+)',
        # 规则3: 中文季数（如 第3季，第二季）
        r'第[\s\-_]*([\u4e00-\u9fa5\d]+)[\s\-_]*季', 
        # 规则4: 独立数字（如 1）
        r'(?<!\d)(\d{1,2})(?!\d)',
    ]
    try:
        for pattern in patterns:
            match = re.search(pattern, parent_folder_name)
            if match:
                num_str = match.group(1)
                # 转换中文数字
                season = chinese_to_arabic(num_str)
                break
        # if 'season' in parent_folder_name.lower():
        #     s = str(int(parent_folder_name.lower().replace('season', '').strip()))
        #     season = s.zfill(2)
        # elif parent_folder_name.lower()[0] == 's':
        #     season = str(int(parent_folder_name[1:])).strip().zfill(2)
    except:
        pass

    return season

def chinese_to_arabic(num_str):
    # 如果直接是阿拉伯数字，直接转换
    if num_str.isdigit():
        return int(num_str)
    
    # 处理中文数字
    total = 0
    for char in num_str:
        if char in chinese_num_map:
            total = total * 10 + chinese_num_map[char]
        else:
            return None  # 包含非法字符
    return total

if __name__ == "__main__":
    test_cases = [
    "Game of Thrones Season 1",
    "Breaking Bad S02",
    "权力的游戏 第3季",
    "Stranger Things [S04]",
    "The Mandalorian 2",  # 独立数字
    "S05-Archive",        # S + 数字 + 分隔符
    "Friends_S6",         # 下划线分隔
    "Season.3",
    "琅琊榜第3季",        # 阿拉伯数字 -> 3
    "庆余年第十季",       # 中文数字 -> 3
    "S05",                # 英文简写 -> 5
    "Season 十",          # 中文数字 -> 10
    "权力的游戏2",        # 独立数字 -> 2
    "无效示例第廿季",     # 非法中文数字 -> None
    ]

    for name in test_cases:
        season = get_season(name)
        print(f"文件夹: {name} -> 季数: {season}")


def get_season_cascaded(full_path):
    """
    逐级向上解析目录季数
    """
    full_path = os.path.abspath(full_path).replace('\\', '/').replace('//', '/')
    parent_folder_names = full_path.split('/')[::-1]
    season = None
    for parent_folder_name in parent_folder_names:
        season = get_season(parent_folder_name)
        if season:
            break
    return season


def get_season_path(file_path):
    """
    获取season目录
    """
    b = os.path.dirname(file_path.replace('\\', '/'))
    season_path = None
    while b:
        if not '/' in b:
            break
        b, fo = b.rsplit('/', 1)
        offset = None
        if get_season(fo):
            season_path = b + '/' + fo
    return season_path
