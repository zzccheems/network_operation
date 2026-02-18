def render_tpl(tpl_path,**kwargs):
    """
    渲染配置模板
    :param tpl_path:接受模板文件路径
    :param kwargs:接受关键字参数
    :return:
    """
    with open(tpl_path,'r',encoding="UTF-8") as f:
        tpl_connect=f.read()
    cmd_content=tpl_connect.format(**kwargs)
    cmd_list=[cmd.strip() for cmd in cmd_content.split("\n") if cmd.strip()]
    return cmd_list