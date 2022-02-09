
import tomli
import tomli_w
import glob


def get_data(tomls_folder='kipro_tomls'):
    path_lst = glob.glob(f"{tomls_folder}/*.toml")
    f_lst = [open(path,'r',encoding='utf-8') for path in path_lst]
    lines_lst = [f.read() for f in f_lst]
    [f.close() for f in f_lst]
    res = '\n'.join(lines_lst)
    return tomli.loads(res)

def disable_account(user,app,tomls_folder='kipro_tomls'):
    path = f'{tomls_folder}/{user}.toml'
    with open(path,'rb+') as f:
        r = tomli.load(f)
        r[app][0]['status'] = 0
        f.seek(0)
        tomli_w.dump(r,f)
