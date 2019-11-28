# coding: utf-8
"""A tornado based Jupyter lab server."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# ----------------------------------------------------------------------------
# Module globals
# ----------------------------------------------------------------------------
import os

DEV_NOTE = """You're running JupyterLab from source.
If you're working on the TypeScript sources of JupyterLab, try running

    jupyter lab --dev-mode --watch


to have the system incrementally watch and build JupyterLab for you, as you
make changes.
"""

CORE_NOTE = """
Running the core application with no additional extensions or settings
"""


def load_jupyter_server_extension(nbapp):
    """Load the JupyterLab server extension.
    """
    # Delay imports to speed up jlpmapp
    from json import dumps
    from jupyterlab_launcher import add_handlers, LabConfig
    from notebook.utils import url_path_join as ujoin, url_escape
    from notebook._version import version_info
    from tornado.ioloop import IOLoop
    from markupsafe import Markup
    from .build_handler import build_path, Builder, BuildHandler
    from .demo_handler import demo_build_path, DemoBuilder, DemoHandler
    from .tianchi_game_handler import tianchi_game_path, TianchiGameBuilder, TianchiGameHandler
    from .tianchi_upload_handler import tianchi_upload_path, TianchiUploadBuilder, TianchiUploadHandler
    from .tianchi_user_handler import tianchi_user_path, TianchiUserBuilder, TianchiUserHandler
    from .tianchi_game_list_handler import tianchi_game_list_path, TianchiGameListBuilder, TianchiGameListHandler
    from .progress_handler import progress_build_path, ProgressHandler, ProgressBuilder
    from .notebook_proxy import notebook_proxy_path, NotebookProxyBuilder, NotebookProxyHandler
    from .community_download_dataset_handler import community_dataset_download_path, CommunityDatasetDownloadBuilder, \
        CommunityDatasetDownloadHandler
    from .community_download_notebook_handler import community_notebook_download_path, CommunityNotebookDownloadBuilder, \
        CommunityNotebookDownloadHandler
    from .file_exists_handler import file_exists_path, FileExistBuilder, FileExistHandler
    from .community_upload_notebook_handler import community_upload_notebook_path, CommunityNotebookUploadBuilder, CommunityNotebookUploadHandler
    from .dsw.handlers import file_upload_path, FileUploadHanler, FileUploadBuilder
    from jupyterlab.extension_manager_handler import (
        extensions_handler_path, ExtensionManager, ExtensionHandler
    )
    from .commands import (
        get_app_dir, get_user_settings_dir, watch, ensure_dev, watch_dev,
        pjoin, DEV_DIR, HERE, get_app_info, ensure_core, get_workspaces_dir
    )
    from .git_oper_handler import git_oper_path, GitOperBuilder, GitOperHandler

    web_app = nbapp.web_app
    logger = nbapp.log
    config = LabConfig()
    app_dir = getattr(nbapp, 'app_dir', get_app_dir())
    user_settings_dir = getattr(
        nbapp, 'user_settings_dir', get_user_settings_dir()
    )
    workspaces_dir = getattr(
        nbapp, 'workspaces_dir', get_workspaces_dir()
    )

    # Print messages.
    logger.info('JupyterLab extension loaded from %s' % HERE)
    logger.info('JupyterLab application directory is %s' % app_dir)

    config.app_name = 'JupyterLab'
    config.app_namespace = 'jupyterlab'
    config.page_url = '/lab'
    config.cache_files = True

    # Check for core mode.
    core_mode = False
    if getattr(nbapp, 'core_mode', False) or app_dir.startswith(HERE):
        core_mode = True
        logger.info('Running JupyterLab in core mode')

    # Check for dev mode.
    dev_mode = False
    if getattr(nbapp, 'dev_mode', False) or app_dir.startswith(DEV_DIR):
        dev_mode = True
        logger.info('Running JupyterLab in dev mode')

    # Check for watch.
    watch_mode = getattr(nbapp, 'watch', False)

    if watch_mode and core_mode:
        logger.warn('Cannot watch in core mode, did you mean --dev-mode?')
        watch_mode = False

    if core_mode and dev_mode:
        logger.warn('Conflicting modes, choosing dev_mode over core_mode')
        core_mode = False

    page_config = web_app.settings.setdefault('page_config_data', dict())
    page_config['buildAvailable'] = not core_mode and not dev_mode
    page_config['buildCheck'] = not core_mode and not dev_mode
    page_config['token'] = nbapp.token
    page_config['devMode'] = dev_mode
    # Export the version info tuple to a JSON array. This gets printed
    # inside double quote marks, so we render it to a JSON string of the
    # JSON data (so that we can call JSON.parse on the frontend on it).
    # We also have to wrap it in `Markup` so that it isn't escaped
    # by Jinja. Otherwise, if the version has string parts these will be
    # escaped and then will have to be unescaped on the frontend.
    page_config['notebookVersion'] = Markup(dumps(dumps(version_info))[1:-1])

    if nbapp.file_to_run and type(nbapp).__name__ == "LabApp":
        relpath = os.path.relpath(nbapp.file_to_run, nbapp.notebook_dir)
        uri = url_escape(ujoin('/lab/tree', *relpath.split(os.sep)))
        nbapp.default_url = uri
        nbapp.file_to_run = ''

    if core_mode:
        app_dir = HERE
        logger.info(CORE_NOTE.strip())
        ensure_core(logger)

    elif dev_mode:
        app_dir = DEV_DIR
        ensure_dev(logger)
        if not watch_mode:
            logger.info(DEV_NOTE)

    config.app_settings_dir = pjoin(app_dir, 'settings')
    config.schemas_dir = pjoin(app_dir, 'schemas')
    config.themes_dir = pjoin(app_dir, 'themes')
    config.workspaces_dir = workspaces_dir
    info = get_app_info(app_dir)
    config.app_version = info['version']
    public_url = info['publicUrl']
    if public_url:
        config.public_url = public_url
    else:
        config.static_dir = app_dir
    # logger.info('public_url is %s', public_url)
    # config.static_dir = pjoin(app_dir, 'static')
    # logger.info('config.static_dir is %s', config.static_dir)

    # if dev_mode:
    config.static_dir = pjoin(app_dir, 'static')

    config.user_settings_dir = user_settings_dir

    # The templates end up in the built static directory.
    config.templates_dir = pjoin(app_dir, 'static')

    if watch_mode:
        logger.info('Starting JupyterLab watch mode...')

        # Set the ioloop in case the watch fails.
        nbapp.ioloop = IOLoop.current()
        if dev_mode:
            watch_dev(logger)
        else:
            watch(app_dir, logger)
            page_config['buildAvailable'] = False

        config.cache_files = False

    base_url = web_app.settings['base_url']
    build_url = ujoin(base_url, build_path)
    builder = Builder(logger, core_mode, app_dir)
    build_handler = (build_url, BuildHandler, {'builder': builder})
    handlers = [build_handler]

    demo_url = ujoin(base_url, demo_build_path)
    demo_builder = DemoBuilder(logger, core_mode, app_dir)
    demo_handler = (demo_url, DemoHandler, {'builder': demo_builder})
    handlers.append(demo_handler)

    progress_url = ujoin(base_url, progress_build_path)
    progress_builder = ProgressBuilder(logger, core_mode, app_dir)
    progress_handler = (progress_url, ProgressHandler, {'builder': progress_builder})
    handlers.append(progress_handler)

    # tianchi_download_url = ujoin(base_url, tianchi_download_path)
    # tianchi_download_builder = TianchiDownloadBuilder(logger, core_mode, app_dir)
    # tianchi_download_handler = (tianchi_download_url, TianchiDownloadHandler, {'builder': tianchi_download_builder})
    # handlers.append(tianchi_download_handler)

    tianchi_game_url = ujoin(base_url, tianchi_game_path)
    tianchi_game_builder = TianchiGameBuilder(logger, core_mode, app_dir)
    tianchi_game_handler = (tianchi_game_url, TianchiGameHandler, {'builder': tianchi_game_builder})
    handlers.append(tianchi_game_handler)

    tianchi_upload_url = ujoin(base_url, tianchi_upload_path)
    tianchi_upload_builder = TianchiUploadBuilder(logger, core_mode, app_dir)
    tianchi_upload_handler = (tianchi_upload_url, TianchiUploadHandler, {'builder': tianchi_upload_builder})
    handlers.append(tianchi_upload_handler)

    tianchi_user_url = ujoin(base_url, tianchi_user_path)
    tianchi_user_builder = TianchiUserBuilder(logger, core_mode, app_dir)
    tianchi_user_handler = (tianchi_user_url, TianchiUserHandler, {'builder': tianchi_user_builder})
    handlers.append(tianchi_user_handler)

    tianchi_game_list_url = ujoin(base_url, tianchi_game_list_path)
    tianchi_game_list_builder = TianchiGameListBuilder(logger, core_mode, app_dir)
    tianchi_game_list_handler = (tianchi_game_list_url, TianchiGameListHandler, {'builder': tianchi_game_list_builder})
    handlers.append(tianchi_game_list_handler)

    notebook_proxy_url = ujoin(base_url, notebook_proxy_path)
    notebook_proxy_builder = NotebookProxyBuilder(logger, core_mode, app_dir)
    notebook_proxy_handler = (notebook_proxy_url, NotebookProxyHandler, {'builder': notebook_proxy_builder})
    handlers.append(notebook_proxy_handler)

    community_dataset_download_url = ujoin(base_url, community_dataset_download_path)
    community_dataset_download_builder = CommunityDatasetDownloadBuilder(logger, core_mode, app_dir)
    community_dataset_download_handler = (
    community_dataset_download_url, CommunityDatasetDownloadHandler, {'builder': community_dataset_download_builder})
    handlers.append(community_dataset_download_handler)

    community_notebook_download_url = ujoin(base_url, community_notebook_download_path)
    community_notebook_download_builder = CommunityNotebookDownloadBuilder(logger, core_mode, app_dir)
    community_notebook_download_handler = (
    community_notebook_download_url, CommunityNotebookDownloadHandler, {'builder': community_notebook_download_builder})
    handlers.append(community_notebook_download_handler)

    file_exists_url = ujoin(base_url, file_exists_path)
    file_exists_builder = FileExistBuilder(logger, core_mode, app_dir)
    file_exists_handler = (
        file_exists_url, FileExistHandler, {'builder': file_exists_builder})
    handlers.append(file_exists_handler)

    community_upload_notebook_url = ujoin(base_url, community_upload_notebook_path)
    community_upload_notebook_builder = CommunityNotebookUploadBuilder(logger, core_mode, app_dir)
    community_upload_notebook_handler = (
        community_upload_notebook_url, CommunityNotebookUploadHandler,
        {'builder': community_upload_notebook_builder})
    handlers.append(community_upload_notebook_handler)

    # large file upload
    file_upload = ujoin(base_url, file_upload_path)
    file_upload_builder = FileUploadBuilder(logger, core_mode, app_dir)
    file_upload_handler = (
        file_upload, FileUploadHanler, {'builder': file_upload_builder})
    handlers.append(file_upload_handler)

    git_oper_url = ujoin(base_url, git_oper_path)
    git_oper_builder = GitOperBuilder(logger, core_mode, app_dir)
    git_oper_handler = (git_oper_url, GitOperHandler, {'builder': git_oper_builder})
    handlers.append(git_oper_handler)

    from jupyterlab.custom_file_handler import CustomFileHandler
    handlers.append(
        (r"/files/(.*)", CustomFileHandler, {})
    )

    if not core_mode:
        ext_url = ujoin(base_url, extensions_handler_path)
        ext_manager = ExtensionManager(logger, app_dir)
        ext_handler = (ext_url, ExtensionHandler, {'manager': ext_manager})
        handlers.append(ext_handler)

    # Must add before the launcher handlers to avoid shadowing.
    logger.info('now handlers is')
    logger.info(handlers)
    web_app.add_handlers('.*$', handlers)

    add_handlers(web_app, config)
