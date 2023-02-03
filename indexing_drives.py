import os, re, string


def log_folder_tree(log_file, path, parent_is_last=1, depth_limit=-1, tab_width=1):
    """
    以树状打印输出文件夹下的文件, 并返回文件夹内的所有文件
    :param tab_width: 空格宽度
    :param path: 文件夹路径
    :param depth_limit: 要输出文件夹的层数, -1为输出全部文件及文件夹
    :param parent_is_last: 递归调用上级文件夹是否是最后一个文件(夹), 控制输出 │ 树干
    :return: 返回path下的所有文件的数组
    """
    files = []
    if len(str(parent_is_last)) - 1 == depth_limit:
        return

    try:
        items = os.listdir(path)
    except PermissionError as e:
        return

    for index, i in enumerate(items):
        is_last = index == len(items) - 1
        i_path = path + "/" + i
        for k in str(parent_is_last)[1:]:
            if k == "0":
                log_file.write("│" + "\t" * tab_width)
            if k == "1":
                log_file.write("\t" * tab_width)
        if is_last:
            log_file.write("└── ")
        else:
            log_file.write("├── ")
        if os.path.isdir(i_path):
            log_file.write(i + '\n')
            log_folder_tree(log_file, path=i_path, depth_limit=depth_limit, parent_is_last=(parent_is_last * 10 + 1) if is_last else (parent_is_last * 10))
        else:
            log_file.write(i_path.split("/")[-1] + '\n')



def index_drives(drive_letter):
    if drive_letter not in string.ascii_letters and not os.path.exists('drive_letter' + ':'):
        print('{}不是有效盘符\n'.format(drive_letter))
        return

    print('正在建立{}盘的索引......'.format(drive_letter))

    log_file = open("{}.txt".format(drive_letter.upper()), mode="w", encoding='utf-8')
    log_folder_tree(log_file, drive_letter + ':\\')
    log_file.close()

    print('已成功建立{}盘的索引，数据保存在{}中\n'.format(drive_letter, "{}.txt".format(drive_letter.upper())))
    


def search_files(drive_letter, search_key):
    log_file = open("{}.txt".format(drive_letter.upper()), 'r', encoding='utf-8')
    files = log_file.read()[:-1].split('\n')
    log_file.close()

    format_data = []                                # 此元组的格式为 (file_index, file_name, deepth, parent_index)
    last_deepth_index = {0: -1}                     # 达到某个deepth的最新文件的index，以便倒推parent
    search_files = []
    for index, file in enumerate(files):
        file_name = re.search(r'^│*?[├└]── (.+?)$', file.replace('\t', '')).group(1)
        deepth = file.count('\t') + 1
        parent_index = last_deepth_index[deepth - 1]
        last_deepth_index[deepth] = index
        format_data.append((index, file_name, deepth, parent_index))

        res = re.search(re.escape(search_key), file_name)
        if res:
            search_files.append(index)

    print('\n检索到{}条满足条件的结果：'.format(len(search_files)))

    for i in search_files:
        file_index, file_name, deepth, parent_index = format_data[i]
        parent = parent_index

        file_path = file_name
        while (parent != -1):
            parent_data = format_data[parent]
            file_path = parent_data[1] + '\\' + file_path
            parent = format_data[parent][3]
        file_path = drive_letter + ':\\' + file_path
        print(file_path)      
    print()


def list_drive_letter():
    for i in range(ord('A'), ord('Z')):
        if os.path.isdir(chr(i) + ':'):
            print(chr(i), end='\t')


def which_drive_can_search():
    cnt = 0
    for vol in range(ord('A'), ord('Z')):
        if os.path.exists(os.path.join(os.getcwd(), '{}.txt'.format(chr(vol)))):
            print(chr(vol), end='\t')
            cnt += 1
    if cnt == 0:
        print('当前暂无已索引过的驱动器')


if __name__ == '__main__':
    stop = False

    while not stop:
        choose = input('--------------------文件查找小工具--------------------\n1: 建立索引\n2: 查找文件\n0：退出\n您的选择：')

        if choose == '1':
            print('\n当前可用驱动器：')
            list_drive_letter()
            drive_letter = input('\n请输入要建立索引的盘符：')
            index_drives(drive_letter)

        elif choose == '2':
            print('\n当前已索引过的驱动器：')
            which_drive_can_search()
            dirve_letter = input('\n目标盘符：')
            search_key = input('查找关键字：')
            search_files(dirve_letter, search_key.upper())
        
        elif choose == '0':
            stop = True

        else:
            print('输入错误\n')